use std::collections::BTreeMap;
use std::future::Future;
use std::io;
use std::pin::Pin;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::task::{Context, Poll};
use std::time::Duration;

use anonssh_bond::{
    CapabilityAdvertisement, LaneConfig, LaneId, SchedulerError, SenderError, StreamId,
    TopologyAdvertisement, TrafficClass,
};
use bytes::{Bytes, BytesMut};
use sha2::{Digest, Sha256};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt, DuplexStream, ReadBuf};
use tokio::sync::{mpsc, oneshot, watch, Mutex};
use tokio::task::JoinHandle;

use crate::runtime::{
    BondRuntime, BondRuntimeConfig, BondRuntimeControl, BondRuntimeError, BondRuntimeStats,
    RuntimeEvent, RuntimeLane,
};

const RESET_NONE: u64 = u64::MAX;
const RESET_APPLICATION_STALLED: u32 = 1;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SessionRole {
    Dialer,
    Listener,
}

impl SessionRole {
    const fn first_stream_id(self) -> u64 {
        match self {
            Self::Dialer => 1,
            Self::Listener => 2,
        }
    }
}

pub struct BondSession {
    session_id: u64,
    runtime_control: BondRuntimeControl,
    next_stream_id: AtomicU64,
    command_tx: mpsc::Sender<Command>,
    incoming_rx: Mutex<mpsc::Receiver<BondedStream>>,
    topology_rx: Mutex<mpsc::Receiver<TopologyAdvertisement>>,
    capability_rx: Mutex<mpsc::Receiver<CapabilityAdvertisement>>,
    stream_pressure: Arc<StreamPressure>,
    terminal_error_rx: watch::Receiver<Option<String>>,
    task: Option<JoinHandle<Result<(), BondRuntimeError>>>,
}

#[derive(Clone)]
pub struct BondSessionControl {
    session_id: u64,
    runtime_control: BondRuntimeControl,
    stream_pressure: Arc<StreamPressure>,
}

#[derive(Default)]
struct StreamPressure {
    active: AtomicU64,
    events: AtomicU64,
}

impl BondSessionControl {
    pub const fn session_id(&self) -> u64 {
        self.session_id
    }

    pub const fn protocol_version(&self) -> crate::BondProtocolVersion {
        self.runtime_control.protocol_version()
    }

    pub const fn server_incarnation(&self) -> Option<crate::ServerIncarnation> {
        self.runtime_control.server_incarnation()
    }

    pub async fn statistics(&self) -> Result<BondRuntimeStats, BondRuntimeError> {
        let mut stats = self.runtime_control.statistics().await?;
        stats.backpressured_streams = self.stream_pressure.active.load(Ordering::Acquire);
        stats.stream_backpressure_events = self.stream_pressure.events.load(Ordering::Acquire);
        Ok(stats)
    }

    pub async fn terminate(&self, cause: String) -> Result<(), BondRuntimeError> {
        self.runtime_control.terminate(cause).await
    }

    pub async fn fail_lane(&self, lane_id: LaneId) -> Result<(), BondRuntimeError> {
        self.runtime_control.fail_lane(lane_id).await
    }

    pub async fn add_lane(&self, lane: RuntimeLane) -> Result<(), BondRuntimeError> {
        self.runtime_control.add_lane(lane).await
    }

    pub async fn advertise_topology(
        &self,
        advertisement: TopologyAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        let mut send_progress = self.runtime_control.send_progress_receiver();
        loop {
            match self
                .runtime_control
                .advertise_topology(advertisement.clone())
                .await
            {
                Ok(()) => return Ok(()),
                Err(BondRuntimeError::Scheduler(SchedulerError::NoHealthyLane))
                | Err(BondRuntimeError::Sender(SenderError::Scheduler(
                    SchedulerError::NoHealthyLane,
                ))) => send_progress
                    .changed()
                    .await
                    .map_err(|_| self.runtime_control.stopped_error())?,
                Err(error) => return Err(error),
            }
        }
    }

    pub async fn advertise_capabilities(
        &self,
        advertisement: CapabilityAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        let mut send_progress = self.runtime_control.send_progress_receiver();
        loop {
            match self
                .runtime_control
                .advertise_capabilities(advertisement.clone())
                .await
            {
                Ok(()) => return Ok(()),
                Err(BondRuntimeError::Scheduler(SchedulerError::NoHealthyLane))
                | Err(BondRuntimeError::Sender(SenderError::Scheduler(
                    SchedulerError::NoHealthyLane,
                ))) => send_progress
                    .changed()
                    .await
                    .map_err(|_| self.runtime_control.stopped_error())?,
                Err(error) => return Err(error),
            }
        }
    }
}

impl BondSession {
    pub fn spawn(
        config: BondRuntimeConfig,
        lanes: Vec<RuntimeLane>,
        role: SessionRole,
    ) -> Result<Self, BondRuntimeError> {
        if !config.require_stream_open {
            return Err(BondRuntimeError::LifecycleRequired);
        }
        let runtime = BondRuntime::spawn(config, lanes)?;
        let runtime_control = runtime.control();
        let (command_tx, command_rx) = mpsc::channel(64);
        let (incoming_tx, incoming_rx) = mpsc::channel(config.max_receive_streams);
        let (topology_tx, topology_rx) = mpsc::channel(16);
        let (capability_tx, capability_rx) = mpsc::channel(16);
        let stream_pressure = Arc::new(StreamPressure::default());
        let stream_buffers = StreamBufferConfig {
            application_bytes: config.stream_receive_window,
            send_batch_bytes: config
                .sender
                .max_chunk_payload
                .max(config.sender.bulk_chunk.maximum_payload),
            inbound_queue_capacity: inbound_queue_capacity(config),
        };
        let coordinator = Coordinator {
            runtime: Some(runtime),
            role,
            runtime_control: runtime_control.clone(),
            command_tx: command_tx.clone(),
            command_rx,
            incoming_tx,
            topology_tx,
            capability_tx,
            streams: BTreeMap::new(),
            stream_buffers,
            stream_pressure: stream_pressure.clone(),
        };
        let (terminal_error_tx, terminal_error_rx) = watch::channel(None);
        let task = tokio::spawn(async move {
            let result = coordinator.run().await;
            if let Err(error) = &result {
                terminal_error_tx.send_replace(Some(error.terminal_cause()));
            }
            result
        });
        Ok(Self {
            session_id: config.session_id,
            runtime_control,
            next_stream_id: AtomicU64::new(role.first_stream_id()),
            command_tx,
            incoming_rx: Mutex::new(incoming_rx),
            topology_rx: Mutex::new(topology_rx),
            capability_rx: Mutex::new(capability_rx),
            stream_pressure,
            terminal_error_rx,
            task: Some(task),
        })
    }

    pub const fn session_id(&self) -> u64 {
        self.session_id
    }

    pub fn protocol_version(&self) -> crate::BondProtocolVersion {
        self.runtime_control.protocol_version()
    }

    pub fn server_incarnation(&self) -> Option<crate::ServerIncarnation> {
        self.runtime_control.server_incarnation()
    }

    pub fn control(&self) -> BondSessionControl {
        BondSessionControl {
            session_id: self.session_id,
            runtime_control: self.runtime_control.clone(),
            stream_pressure: self.stream_pressure.clone(),
        }
    }

    pub async fn open_stream(&self, class: TrafficClass) -> Result<BondedStream, BondRuntimeError> {
        let stream_id = self
            .next_stream_id
            .fetch_update(Ordering::AcqRel, Ordering::Acquire, |current| {
                current.checked_add(2)
            })
            .map(StreamId::new)
            .map_err(|_| BondRuntimeError::OffsetOverflow)??;
        let (reply_tx, reply_rx) = oneshot::channel();
        self.command_tx
            .send(Command::ReserveStream {
                stream_id,
                class,
                reply: reply_tx,
            })
            .await
            .map_err(|_| self.stopped_error())?;
        let stream = reply_rx.await.map_err(|_| self.stopped_error())??;
        if let Err(error) = self.runtime_control.open_stream(stream_id, class).await {
            let _ = self
                .command_tx
                .send(Command::ForgetStream { stream_id })
                .await;
            return Err(error);
        }
        Ok(stream)
    }

    pub async fn accept_stream(&self) -> Result<BondedStream, BondRuntimeError> {
        self.incoming_rx
            .lock()
            .await
            .recv()
            .await
            .ok_or_else(|| self.stopped_error())
    }

    pub async fn statistics(&self) -> Result<BondRuntimeStats, BondRuntimeError> {
        self.control().statistics().await
    }

    pub async fn fail_lane(&self, lane_id: LaneId) -> Result<(), BondRuntimeError> {
        self.control().fail_lane(lane_id).await
    }

    pub async fn add_lane(&self, lane: RuntimeLane) -> Result<(), BondRuntimeError> {
        self.control().add_lane(lane).await
    }

    pub async fn authorize_lane(&self, config: LaneConfig) -> Result<(), BondRuntimeError> {
        self.runtime_control.declare_lane(config).await
    }

    pub async fn advertise_topology(
        &self,
        advertisement: TopologyAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        self.control().advertise_topology(advertisement).await
    }

    pub async fn accept_topology(&self) -> Result<TopologyAdvertisement, BondRuntimeError> {
        self.topology_rx
            .lock()
            .await
            .recv()
            .await
            .ok_or_else(|| self.stopped_error())
    }

    pub async fn advertise_capabilities(
        &self,
        advertisement: CapabilityAdvertisement,
    ) -> Result<(), BondRuntimeError> {
        self.control().advertise_capabilities(advertisement).await
    }

    pub async fn accept_capabilities(&self) -> Result<CapabilityAdvertisement, BondRuntimeError> {
        self.capability_rx
            .lock()
            .await
            .recv()
            .await
            .ok_or_else(|| self.stopped_error())
    }

    pub async fn shutdown(mut self) -> Result<(), BondRuntimeError> {
        let (reply_tx, reply_rx) = oneshot::channel();
        self.command_tx
            .send(Command::Shutdown { reply: reply_tx })
            .await
            .map_err(|_| self.stopped_error())?;
        let result = reply_rx.await.map_err(|_| self.stopped_error())?;
        let task = self.task.take().ok_or_else(|| self.stopped_error())?;
        let task_result = task
            .await
            .map_err(|error| BondRuntimeError::ActorJoin(error.to_string()))?;
        result.and(task_result)
    }

    fn stopped_error(&self) -> BondRuntimeError {
        match self.terminal_error_rx.borrow().as_ref() {
            Some(error) => BondRuntimeError::StoppedWithCause(error.clone()),
            None => self.runtime_control.stopped_error(),
        }
    }
}

impl Drop for BondSession {
    fn drop(&mut self) {
        if let Some(task) = self.task.take() {
            task.abort();
        }
    }
}

pub struct BondedStream {
    stream_id: StreamId,
    class: TrafficClass,
    io: DuplexStream,
    runtime_control: BondRuntimeControl,
    command_tx: mpsc::Sender<Command>,
    reset_code: Arc<AtomicU64>,
    close_rx: watch::Receiver<CloseState>,
    shutdown_wait: Option<Pin<Box<dyn Future<Output = io::Result<()>> + Send>>>,
    shutdown_complete: bool,
}

impl BondedStream {
    pub const fn stream_id(&self) -> StreamId {
        self.stream_id
    }

    pub const fn traffic_class(&self) -> TrafficClass {
        self.class
    }

    pub async fn reset(&mut self, code: u32) -> Result<(), BondRuntimeError> {
        let result = self
            .runtime_control
            .reset_stream(self.stream_id, code)
            .await;
        if result.is_ok() {
            let _ = self
                .command_tx
                .send(Command::ForgetStream {
                    stream_id: self.stream_id,
                })
                .await;
            self.reset_code.store(code as u64, Ordering::Release);
            let _ = self.io.shutdown().await;
        }
        result
    }

    fn reset_error(&self) -> Option<io::Error> {
        let code = self.reset_code.load(Ordering::Acquire);
        (code != RESET_NONE).then(|| {
            io::Error::new(
                io::ErrorKind::ConnectionReset,
                format!("bond stream reset with code {code}"),
            )
        })
    }

    fn terminal_error(&self) -> Option<io::Error> {
        self.runtime_control.terminal_cause().map(|cause| {
            io::Error::new(
                io::ErrorKind::BrokenPipe,
                format!("bond runtime stopped after: {cause}"),
            )
        })
    }
}

impl AsyncRead for BondedStream {
    fn poll_read(
        mut self: Pin<&mut Self>,
        context: &mut Context<'_>,
        buffer: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        if let Some(error) = self.reset_error() {
            return Poll::Ready(Err(error));
        }
        let before = buffer.filled().len();
        match Pin::new(&mut self.io).poll_read(context, buffer) {
            Poll::Ready(Ok(())) if buffer.filled().len() == before => {
                if let Some(error) = self.reset_error() {
                    Poll::Ready(Err(error))
                } else if let Some(error) = self.terminal_error() {
                    Poll::Ready(Err(error))
                } else {
                    Poll::Ready(Ok(()))
                }
            }
            result => result,
        }
    }
}

impl AsyncWrite for BondedStream {
    fn poll_write(
        mut self: Pin<&mut Self>,
        context: &mut Context<'_>,
        bytes: &[u8],
    ) -> Poll<Result<usize, io::Error>> {
        if let Some(error) = self.reset_error() {
            return Poll::Ready(Err(error));
        }
        if let Some(error) = self.terminal_error() {
            return Poll::Ready(Err(error));
        }
        Pin::new(&mut self.io).poll_write(context, bytes)
    }

    fn poll_flush(
        mut self: Pin<&mut Self>,
        context: &mut Context<'_>,
    ) -> Poll<Result<(), io::Error>> {
        if let Some(error) = self.reset_error() {
            return Poll::Ready(Err(error));
        }
        if let Some(error) = self.terminal_error() {
            return Poll::Ready(Err(error));
        }
        Pin::new(&mut self.io).poll_flush(context)
    }

    fn poll_shutdown(
        mut self: Pin<&mut Self>,
        context: &mut Context<'_>,
    ) -> Poll<Result<(), io::Error>> {
        if self.shutdown_complete {
            return Poll::Ready(Ok(()));
        }
        if let Some(error) = self.reset_error() {
            return Poll::Ready(Err(error));
        }
        if let Some(error) = self.terminal_error() {
            return Poll::Ready(Err(error));
        }
        match Pin::new(&mut self.io).poll_shutdown(context) {
            Poll::Pending => return Poll::Pending,
            Poll::Ready(Err(error)) => return Poll::Ready(Err(error)),
            Poll::Ready(Ok(())) => {}
        }
        if self.shutdown_wait.is_none() {
            let mut close_rx = self.close_rx.clone();
            self.shutdown_wait = Some(Box::pin(async move {
                loop {
                    let state = close_rx.borrow().clone();
                    match state {
                        CloseState::Open => {}
                        CloseState::Acknowledged => return Ok(()),
                        CloseState::Failed(cause) => {
                            return Err(io::Error::new(
                                io::ErrorKind::BrokenPipe,
                                format!("bond stream close failed: {cause}"),
                            ));
                        }
                    }
                    close_rx.changed().await.map_err(|_| {
                        io::Error::new(io::ErrorKind::BrokenPipe, "bond session stopped")
                    })?;
                }
            }));
        }
        let result = self
            .shutdown_wait
            .as_mut()
            .expect("shutdown future exists")
            .as_mut()
            .poll(context);
        match result {
            Poll::Pending => Poll::Pending,
            Poll::Ready(Ok(())) => {
                self.shutdown_wait = None;
                self.shutdown_complete = true;
                Poll::Ready(Ok(()))
            }
            Poll::Ready(Err(error)) => {
                self.shutdown_wait = None;
                Poll::Ready(Err(error))
            }
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
enum CloseState {
    Open,
    Acknowledged,
    Failed(String),
}

enum Inbound {
    Data(Bytes),
    Finished,
    Reset(u32),
}

struct StreamEntry {
    inbound_tx: mpsc::Sender<Inbound>,
    reset_code: Arc<AtomicU64>,
}

#[derive(Clone, Copy)]
struct StreamBufferConfig {
    application_bytes: usize,
    send_batch_bytes: usize,
    inbound_queue_capacity: usize,
}

enum Command {
    ReserveStream {
        stream_id: StreamId,
        class: TrafficClass,
        reply: oneshot::Sender<Result<BondedStream, BondRuntimeError>>,
    },
    ForgetStream {
        stream_id: StreamId,
    },
    Shutdown {
        reply: oneshot::Sender<Result<(), BondRuntimeError>>,
    },
}

struct Coordinator {
    runtime: Option<BondRuntime>,
    role: SessionRole,
    runtime_control: BondRuntimeControl,
    command_tx: mpsc::Sender<Command>,
    command_rx: mpsc::Receiver<Command>,
    incoming_tx: mpsc::Sender<BondedStream>,
    topology_tx: mpsc::Sender<TopologyAdvertisement>,
    capability_tx: mpsc::Sender<CapabilityAdvertisement>,
    streams: BTreeMap<StreamId, StreamEntry>,
    stream_buffers: StreamBufferConfig,
    stream_pressure: Arc<StreamPressure>,
}

impl Coordinator {
    async fn run(mut self) -> Result<(), BondRuntimeError> {
        loop {
            tokio::select! {
                command = self.command_rx.recv() => {
                    let Some(command) = command else { return Ok(()); };
                    if self.handle_command(command).await? {
                        return Ok(());
                    }
                }
                event = self.runtime.as_mut().expect("runtime exists").receive_event_uncredited() => {
                    self.handle_runtime_event(event?).await?;
                }
            }
        }
    }

    async fn handle_command(&mut self, command: Command) -> Result<bool, BondRuntimeError> {
        match command {
            Command::ReserveStream {
                stream_id,
                class,
                reply,
            } => {
                let result = self.reserve_stream(stream_id, class);
                let _ = reply.send(result);
            }
            Command::ForgetStream { stream_id } => {
                self.streams.remove(&stream_id);
            }
            Command::Shutdown { reply } => {
                let runtime = self.runtime.take().ok_or(BondRuntimeError::Stopped)?;
                let result = runtime.shutdown().await;
                let terminal_cause = result.as_ref().err().map(BondRuntimeError::terminal_cause);
                let _ = reply.send(result);
                if let Some(cause) = terminal_cause {
                    return Err(BondRuntimeError::StoppedWithCause(cause));
                }
                return Ok(true);
            }
        }
        Ok(false)
    }

    fn reserve_stream(
        &mut self,
        stream_id: StreamId,
        class: TrafficClass,
    ) -> Result<BondedStream, BondRuntimeError> {
        if self.streams.contains_key(&stream_id) {
            return Err(BondRuntimeError::DuplicateStream(stream_id));
        }
        let (stream, entry) = make_stream(
            stream_id,
            class,
            self.runtime_control.clone(),
            self.command_tx.clone(),
            self.stream_buffers,
            self.stream_pressure.clone(),
        );
        self.streams.insert(stream_id, entry);
        Ok(stream)
    }

    async fn handle_runtime_event(&mut self, event: RuntimeEvent) -> Result<(), BondRuntimeError> {
        match event {
            RuntimeEvent::StreamOpened { stream_id, class } => {
                if stream_id.get() % 2 == self.role.first_stream_id() % 2 {
                    return Err(BondRuntimeError::InvalidRemoteStreamId(stream_id));
                }
                let (stream, entry) = make_stream(
                    stream_id,
                    class,
                    self.runtime_control.clone(),
                    self.command_tx.clone(),
                    self.stream_buffers,
                    self.stream_pressure.clone(),
                );
                if self.streams.insert(stream_id, entry).is_some() {
                    return Err(BondRuntimeError::DuplicateStream(stream_id));
                }
                self.incoming_tx
                    .send(stream)
                    .await
                    .map_err(|_| BondRuntimeError::ApplicationReceiverClosed)?;
            }
            RuntimeEvent::Data(data) => {
                let entry = self
                    .streams
                    .get(&data.stream_id)
                    .ok_or(BondRuntimeError::UnopenedStream(data.stream_id))?;
                match entry.inbound_tx.try_send(Inbound::Data(data.bytes)) {
                    Ok(()) => {}
                    Err(mpsc::error::TrySendError::Full(_)) => {
                        let stream_id = data.stream_id;
                        if let Some(entry) = self.streams.remove(&stream_id) {
                            entry
                                .reset_code
                                .store(RESET_APPLICATION_STALLED as u64, Ordering::Release);
                            let _ = entry
                                .inbound_tx
                                .try_send(Inbound::Reset(RESET_APPLICATION_STALLED));
                        }
                        let control = self.runtime_control.clone();
                        tokio::spawn(async move {
                            let _ = control
                                .reset_stream(stream_id, RESET_APPLICATION_STALLED)
                                .await;
                        });
                    }
                    Err(mpsc::error::TrySendError::Closed(_)) => {
                        let stream_id = data.stream_id;
                        self.streams.remove(&stream_id);
                        let control = self.runtime_control.clone();
                        tokio::spawn(async move {
                            let _ = control
                                .reset_stream(stream_id, RESET_APPLICATION_STALLED)
                                .await;
                        });
                    }
                }
            }
            RuntimeEvent::StreamFinished { stream_id } => {
                let entry = self
                    .streams
                    .get(&stream_id)
                    .ok_or(BondRuntimeError::UnopenedStream(stream_id))?;
                let inbound = entry.inbound_tx.clone();
                tokio::spawn(async move {
                    let _ = inbound.send(Inbound::Finished).await;
                });
            }
            RuntimeEvent::StreamRetired { stream_id } => {
                self.streams.remove(&stream_id);
            }
            RuntimeEvent::StreamReset { stream_id, code } => {
                if let Some(entry) = self.streams.remove(&stream_id) {
                    entry.reset_code.store(code as u64, Ordering::Release);
                    tokio::spawn(async move {
                        let _ = entry.inbound_tx.send(Inbound::Reset(code)).await;
                    });
                }
            }
            RuntimeEvent::TopologyAdvertised(advertisement) => {
                self.topology_tx
                    .try_send(advertisement)
                    .map_err(|error| match error {
                        mpsc::error::TrySendError::Full(_) => BondRuntimeError::TopologyQueueFull,
                        mpsc::error::TrySendError::Closed(_) => {
                            BondRuntimeError::ApplicationReceiverClosed
                        }
                    })?;
            }
            RuntimeEvent::CapabilitiesAdvertised(advertisement) => {
                self.capability_tx
                    .try_send(advertisement)
                    .map_err(|error| match error {
                        mpsc::error::TrySendError::Full(_) => BondRuntimeError::CapabilityQueueFull,
                        mpsc::error::TrySendError::Closed(_) => {
                            BondRuntimeError::ApplicationReceiverClosed
                        }
                    })?;
            }
        }
        Ok(())
    }
}

fn make_stream(
    stream_id: StreamId,
    class: TrafficClass,
    runtime_control: BondRuntimeControl,
    command_tx: mpsc::Sender<Command>,
    buffers: StreamBufferConfig,
    stream_pressure: Arc<StreamPressure>,
) -> (BondedStream, StreamEntry) {
    let (application, bridge) = tokio::io::duplex(buffers.application_bytes);
    let (mut outbound, mut inbound) = tokio::io::split(bridge);
    let (inbound_tx, mut inbound_rx) = mpsc::channel(buffers.inbound_queue_capacity);
    let reset_code = Arc::new(AtomicU64::new(RESET_NONE));
    let inbound_reset = reset_code.clone();
    let entry_reset = reset_code.clone();
    let inbound_control = runtime_control.clone();
    let mut inbound_terminal = runtime_control.terminal_receiver();
    tokio::spawn(async move {
        loop {
            tokio::select! {
                message = inbound_rx.recv() => match message {
                    Some(Inbound::Data(bytes)) => {
                        let write = tokio::select! {
                            write = inbound.write_all(&bytes) => write,
                            _ = inbound_terminal.changed() => {
                                let _ = inbound.shutdown().await;
                                return;
                            }
                        };
                        if write.is_err() {
                            return;
                        }
                        if inbound_control
                            .release_receive_credit(stream_id, bytes.len())
                            .await
                            .is_err()
                        {
                            let _ = inbound.shutdown().await;
                            return;
                        }
                    }
                    Some(Inbound::Finished) => {
                        let _ = inbound.shutdown().await;
                        return;
                    }
                    Some(Inbound::Reset(code)) => {
                        inbound_reset.store(code as u64, Ordering::Release);
                        let _ = inbound.shutdown().await;
                        return;
                    }
                    None => return,
                },
                _ = inbound_terminal.changed() => {
                    let _ = inbound.shutdown().await;
                    return;
                }
            }
        }
    });

    let (close_tx, close_rx) = watch::channel(CloseState::Open);
    let outbound_control = runtime_control.clone();
    let mut outbound_terminal = runtime_control.terminal_receiver();
    tokio::spawn(async move {
        let mut buffer = BytesMut::with_capacity(buffers.send_batch_bytes);
        loop {
            buffer.reserve(buffers.send_batch_bytes);
            tokio::select! {
                read = outbound.read_buf(&mut buffer) => match read {
                    Ok(0) => {
                        let state = match outbound_control.close_stream(stream_id).await {
                            Ok(()) => CloseState::Acknowledged,
                            Err(error) => CloseState::Failed(error.terminal_cause()),
                        };
                        let _ = close_tx.send(state);
                        return;
                    }
                    Ok(count) => {
                        let bytes = buffer.split_to(count).freeze();
                        match send_with_backpressure(
                            &outbound_control,
                            stream_id,
                            class,
                            bytes,
                            &stream_pressure,
                        )
                        .await
                        {
                            Ok(()) => {}
                            Err(error) => {
                                let _ = close_tx.send(CloseState::Failed(error.terminal_cause()));
                                return;
                            }
                        }
                    }
                    Err(error) => {
                        let _ = close_tx.send(CloseState::Failed(error.to_string()));
                        return;
                    }
                },
                _ = outbound_terminal.changed() => {
                    let cause = outbound_terminal
                        .borrow()
                        .clone()
                        .unwrap_or_else(|| "bond runtime stopped".to_owned());
                    let _ = close_tx.send(CloseState::Failed(cause));
                    return;
                }
            }
        }
    });

    (
        BondedStream {
            stream_id,
            class,
            io: application,
            runtime_control,
            command_tx,
            reset_code,
            close_rx,
            shutdown_wait: None,
            shutdown_complete: false,
        },
        StreamEntry {
            inbound_tx,
            reset_code: entry_reset,
        },
    )
}

async fn send_with_backpressure(
    control: &BondRuntimeControl,
    stream_id: StreamId,
    class: TrafficClass,
    bytes: Bytes,
    stream_pressure: &StreamPressure,
) -> Result<(), BondRuntimeError> {
    let mut pressure = None;
    let mut send_progress = control.send_progress_receiver();
    loop {
        match control.send_shared(stream_id, class, bytes.clone()).await {
            Ok(()) => return Ok(()),
            Err(BondRuntimeError::FlowControlBlocked { .. })
            | Err(BondRuntimeError::Sender(SenderError::Backpressure { .. }))
            | Err(BondRuntimeError::Sender(SenderError::ChunkBackpressure { .. }))
            | Err(BondRuntimeError::Sender(SenderError::Scheduler(
                SchedulerError::NoHealthyLane,
            ))) => {
                pressure.get_or_insert_with(|| StreamPressureGuard::activate(stream_pressure));
                send_progress
                    .changed()
                    .await
                    .map_err(|_| control.stopped_error())?;
            }
            Err(error) => return Err(error),
        }
    }
}

struct StreamPressureGuard<'a> {
    pressure: &'a StreamPressure,
}

impl<'a> StreamPressureGuard<'a> {
    fn activate(pressure: &'a StreamPressure) -> Self {
        pressure.active.fetch_add(1, Ordering::AcqRel);
        pressure.events.fetch_add(1, Ordering::AcqRel);
        Self { pressure }
    }
}

impl Drop for StreamPressureGuard<'_> {
    fn drop(&mut self) {
        self.pressure.active.fetch_sub(1, Ordering::AcqRel);
    }
}

fn inbound_queue_capacity(config: BondRuntimeConfig) -> usize {
    let minimum_payload = config
        .sender
        .max_chunk_payload
        .min(config.sender.bulk_chunk.minimum_payload);
    config
        .stream_receive_window
        .div_ceil(minimum_payload)
        .clamp(1, 64)
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ConcurrentProgressReport {
    pub payload_bytes_per_direction: usize,
    pub delayed_read_millis: u64,
    pub data_frames_per_direction: u64,
    pub client_acknowledgement_frames: u64,
    pub server_acknowledgement_frames: u64,
    pub client_window_update_frames: u64,
    pub server_window_update_frames: u64,
    pub client_received_sha256: String,
    pub server_received_sha256: String,
}

pub async fn concurrent_progress_self_test() -> Result<ConcurrentProgressReport, BondRuntimeError> {
    const PAYLOAD_BYTES: usize = 2 * 1024 * 1024;
    const READ_DELAY: Duration = Duration::from_millis(250);
    const PHASE_TIMEOUT: Duration = Duration::from_secs(10);
    let (client_io, server_io) = tokio::io::duplex(64 * 1024);
    let lane = LaneConfig::new(
        LaneId::new(1)?,
        anonssh_bond::FailureDomain::new(1)?,
        Duration::from_millis(5),
        100_000_000,
    )?;
    let config = BondRuntimeConfig {
        session_id: 0x4142_5046,
        scheduler: anonssh_bond::SchedulerConfig::default(),
        sender: anonssh_bond::SenderConfig {
            max_chunk_payload: 1024,
            bulk_chunk: anonssh_bond::BulkChunkConfig::fixed(1024),
            max_unacknowledged_bytes: 64 * 1024,
            max_unacknowledged_chunks: 128,
            redundant_realtime: false,
        },
        max_reorder_bytes_per_stream: 64 * 1024,
        max_receive_streams: 8,
        stream_receive_window: 16 * 1024,
        max_ack_ranges: 8,
        require_stream_open: true,
        retransmit_after: Duration::from_secs(1),
        retransmit_scan_interval: Duration::from_millis(10),
    };
    let client = BondSession::spawn(
        config,
        vec![RuntimeLane::new_for_test(lane, client_io, [1; 32], [2; 32])],
        SessionRole::Dialer,
    )?;
    let server = BondSession::spawn(
        config,
        vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
        SessionRole::Listener,
    )?;
    let client_stream = client.open_stream(TrafficClass::Bulk).await?;
    let server_stream = server.accept_stream().await?;
    let (mut client_read, mut client_write) = tokio::io::split(client_stream);
    let (mut server_read, mut server_write) = tokio::io::split(server_stream);
    let client_payload: Vec<_> = (0..PAYLOAD_BYTES)
        .map(|index| ((index * 31 + 7) % 251) as u8)
        .collect();
    let server_payload: Vec<_> = (0..PAYLOAD_BYTES)
        .map(|index| ((index * 47 + 11) % 251) as u8)
        .collect();

    let transfer = async {
        let client_send = async {
            client_write.write_all(&client_payload).await?;
            client_write.shutdown().await
        };
        let server_send = async {
            server_write.write_all(&server_payload).await?;
            server_write.shutdown().await
        };
        let delayed_receive = async {
            tokio::time::sleep(READ_DELAY).await;
            let client_receive = async {
                let mut received = Vec::new();
                client_read.read_to_end(&mut received).await?;
                Ok::<_, io::Error>(received)
            };
            let server_receive = async {
                let mut received = Vec::new();
                server_read.read_to_end(&mut received).await?;
                Ok::<_, io::Error>(received)
            };
            tokio::join!(client_receive, server_receive)
        };
        tokio::join!(client_send, server_send, delayed_receive)
    };
    let (client_sent, server_sent, (client_received, server_received)) =
        tokio::time::timeout(PHASE_TIMEOUT, transfer)
            .await
            .map_err(|_| {
                BondRuntimeError::LaneIo("bounded full-duplex transfer timed out".into())
            })?;
    client_sent.map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    server_sent.map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    let client_received =
        client_received.map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    let server_received =
        server_received.map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    if client_received != server_payload || server_received != client_payload {
        return Err(BondRuntimeError::LaneIo(
            "bounded full-duplex payload mismatch".into(),
        ));
    }
    let (client_stats, server_stats) = tokio::time::timeout(PHASE_TIMEOUT, async {
        tokio::try_join!(client.statistics(), server.statistics())
    })
    .await
    .map_err(|_| BondRuntimeError::LaneIo("bounded statistics collection timed out".into()))??;
    let data_frames_per_direction = PAYLOAD_BYTES.div_ceil(config.sender.max_chunk_payload) as u64;
    let maximum_batched_control_frames = data_frames_per_direction / 2;
    if client_stats.acknowledgement_frames > maximum_batched_control_frames
        || server_stats.acknowledgement_frames > maximum_batched_control_frames
        || client_stats.window_update_frames > maximum_batched_control_frames
        || server_stats.window_update_frames > maximum_batched_control_frames
    {
        return Err(BondRuntimeError::LaneIo(format!(
            "control frames were not batched: data={data_frames_per_direction}, client_ack={}, server_ack={}, client_window={}, server_window={}",
            client_stats.acknowledgement_frames,
            server_stats.acknowledgement_frames,
            client_stats.window_update_frames,
            server_stats.window_update_frames,
        )));
    }
    let report = ConcurrentProgressReport {
        payload_bytes_per_direction: PAYLOAD_BYTES,
        delayed_read_millis: READ_DELAY.as_millis() as u64,
        data_frames_per_direction,
        client_acknowledgement_frames: client_stats.acknowledgement_frames,
        server_acknowledgement_frames: server_stats.acknowledgement_frames,
        client_window_update_frames: client_stats.window_update_frames,
        server_window_update_frames: server_stats.window_update_frames,
        client_received_sha256: format!("{:x}", Sha256::digest(&client_received)),
        server_received_sha256: format!("{:x}", Sha256::digest(&server_received)),
    };
    tokio::time::timeout(PHASE_TIMEOUT, async {
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown?;
        server_shutdown
    })
    .await
    .map_err(|_| BondRuntimeError::LaneIo("bounded session shutdown timed out".into()))??;
    Ok(report)
}

#[cfg(test)]
mod tests {
    use std::pin::Pin;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::Arc;
    use std::task::{Context, Poll};
    use std::time::Duration;

    use anonssh_bond::{
        CapabilityAdvertisement, CapabilityFeatures, EndpointDescriptor, EndpointProvider,
        FailureDomain, Frame, FrameFlags, FrameKind, LaneConfig, LaneId, ProviderCapability,
        SchedulerConfig, SenderConfig, StreamId, TopologyAction, TopologyAdvertisement,
        TopologyError, TopologyPolicy, TrafficClass,
    };
    use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt, ReadBuf};
    use tokio::net::{TcpListener, TcpStream};
    use tokio::sync::Notify;

    use super::{BondSession, SessionRole};
    use crate::{
        authenticate_client_lane, authenticate_server_lane_with_incarnation, BondProtocolVersion,
        BondRuntime, BondRuntimeConfig, BondRuntimeError, BondSessionKey, LaneJoin, RuntimeEvent,
        RuntimeLane, ServerIncarnation,
    };

    #[derive(Clone, Default)]
    struct WriteGate {
        state: Arc<WriteGateState>,
    }

    #[derive(Default)]
    struct WriteGateState {
        blocked: AtomicBool,
        entered: AtomicBool,
        entered_notify: Notify,
    }

    impl WriteGate {
        fn block(&self) {
            self.state.entered.store(false, Ordering::Release);
            self.state.blocked.store(true, Ordering::Release);
        }

        async fn wait_until_blocked(&self) {
            loop {
                let notified = self.state.entered_notify.notified();
                if self.state.entered.load(Ordering::Acquire) {
                    return;
                }
                notified.await;
            }
        }
    }

    struct GatedIo<T> {
        inner: T,
        gate: WriteGate,
    }

    impl<T> GatedIo<T> {
        fn new(inner: T, gate: WriteGate) -> Self {
            Self { inner, gate }
        }
    }

    impl<T: AsyncRead + Unpin> AsyncRead for GatedIo<T> {
        fn poll_read(
            mut self: Pin<&mut Self>,
            context: &mut Context<'_>,
            buffer: &mut ReadBuf<'_>,
        ) -> Poll<std::io::Result<()>> {
            Pin::new(&mut self.inner).poll_read(context, buffer)
        }
    }

    impl<T: AsyncWrite + Unpin> AsyncWrite for GatedIo<T> {
        fn poll_write(
            mut self: Pin<&mut Self>,
            context: &mut Context<'_>,
            buffer: &[u8],
        ) -> Poll<Result<usize, std::io::Error>> {
            if self.gate.state.blocked.load(Ordering::Acquire) {
                self.gate.state.entered.store(true, Ordering::Release);
                self.gate.state.entered_notify.notify_waiters();
                if self.gate.state.blocked.load(Ordering::Acquire) {
                    return Poll::Pending;
                }
            }
            Pin::new(&mut self.inner).poll_write(context, buffer)
        }

        fn poll_flush(
            mut self: Pin<&mut Self>,
            context: &mut Context<'_>,
        ) -> Poll<Result<(), std::io::Error>> {
            Pin::new(&mut self.inner).poll_flush(context)
        }

        fn poll_shutdown(
            mut self: Pin<&mut Self>,
            context: &mut Context<'_>,
        ) -> Poll<Result<(), std::io::Error>> {
            Pin::new(&mut self.inner).poll_shutdown(context)
        }
    }

    fn test_config() -> BondRuntimeConfig {
        BondRuntimeConfig {
            session_id: 91,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig {
                max_chunk_payload: 1024,
                bulk_chunk: anonssh_bond::BulkChunkConfig::fixed(1024),
                max_unacknowledged_bytes: 64 * 1024,
                max_unacknowledged_chunks: 128,
                redundant_realtime: false,
            },
            max_reorder_bytes_per_stream: 64 * 1024,
            max_receive_streams: 8,
            stream_receive_window: 16 * 1024,
            max_ack_ranges: 8,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(1),
            retransmit_scan_interval: Duration::from_millis(10),
        }
    }

    fn test_lane(id: u32, rtt_ms: u64) -> LaneConfig {
        LaneConfig::new(
            LaneId::new(id).unwrap(),
            FailureDomain::new(id as u64).unwrap(),
            Duration::from_millis(rtt_ms),
            100_000_000,
        )
        .unwrap()
    }

    fn capabilities(generation: u64, queue_delay_micros: u32) -> CapabilityAdvertisement {
        CapabilityAdvertisement::new(
            generation,
            CapabilityFeatures::CURRENT,
            1024 * 1024 * 1024,
            1_000,
            queue_delay_micros,
            8,
            4,
            2,
            vec![
                ProviderCapability::new(EndpointProvider::Tor, 4, 2, 2_000, 5_000, 4_000).unwrap(),
                ProviderCapability::new(EndpointProvider::I2p, 4, 1, 120_000, 40_000, 1_000)
                    .unwrap(),
            ],
        )
        .unwrap()
    }

    fn session_pair() -> (BondSession, BondSession) {
        let (client_io, server_io) = tokio::io::duplex(256 * 1024);
        let lane = test_lane(1, 5);
        let config = test_config();
        (
            BondSession::spawn(
                config,
                vec![RuntimeLane::new_for_test(lane, client_io, [1; 32], [2; 32])],
                SessionRole::Dialer,
            )
            .unwrap(),
            BondSession::spawn(
                config,
                vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
                SessionRole::Listener,
            )
            .unwrap(),
        )
    }

    fn gated_two_lane_session_pair() -> (BondSession, BondSession, WriteGate, WriteGate) {
        let first = test_lane(1, 5);
        let second = test_lane(2, 50);
        let (client_first, server_first) = tokio::io::duplex(256 * 1024);
        let (client_second, server_second) = tokio::io::duplex(256 * 1024);
        let client_gate = WriteGate::default();
        let server_gate = WriteGate::default();
        let config = test_config();
        let client = BondSession::spawn(
            config,
            vec![
                RuntimeLane::new_for_test(
                    first,
                    GatedIo::new(client_first, client_gate.clone()),
                    [1; 32],
                    [2; 32],
                ),
                RuntimeLane::new_for_test(second, client_second, [3; 32], [4; 32]),
            ],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            config,
            vec![
                RuntimeLane::new_for_test(
                    first,
                    GatedIo::new(server_first, server_gate.clone()),
                    [2; 32],
                    [1; 32],
                ),
                RuntimeLane::new_for_test(second, server_second, [4; 32], [3; 32]),
            ],
            SessionRole::Listener,
        )
        .unwrap();
        (client, server, client_gate, server_gate)
    }

    fn redundant_realtime_session_pair() -> (BondSession, BondSession, WriteGate, WriteGate) {
        let first = test_lane(1, 5);
        let second = test_lane(2, 50);
        let (client_first, server_first) = tokio::io::duplex(256 * 1024);
        let (client_second, server_second) = tokio::io::duplex(256 * 1024);
        let first_gate = WriteGate::default();
        let second_gate = WriteGate::default();
        let mut config = test_config();
        config.scheduler.low_latency_lane_count = 2;
        config.sender.redundant_realtime = true;
        let client = BondSession::spawn(
            config,
            vec![
                RuntimeLane::new_for_test(
                    first,
                    GatedIo::new(client_first, first_gate.clone()),
                    [1; 32],
                    [2; 32],
                ),
                RuntimeLane::new_for_test(
                    second,
                    GatedIo::new(client_second, second_gate.clone()),
                    [3; 32],
                    [4; 32],
                ),
            ],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            config,
            vec![
                RuntimeLane::new_for_test(first, server_first, [2; 32], [1; 32]),
                RuntimeLane::new_for_test(second, server_second, [4; 32], [3; 32]),
            ],
            SessionRole::Listener,
        )
        .unwrap();
        (client, server, first_gate, second_gate)
    }

    fn gated_single_lane_session_pair() -> (BondSession, BondSession, WriteGate) {
        let lane = test_lane(1, 5);
        let (client_io, server_io) = tokio::io::duplex(256 * 1024);
        let client_gate = WriteGate::default();
        let config = test_config();
        let client = BondSession::spawn(
            config,
            vec![RuntimeLane::new_for_test(
                lane,
                GatedIo::new(client_io, client_gate.clone()),
                [1; 32],
                [2; 32],
            )],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            config,
            vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
            SessionRole::Listener,
        )
        .unwrap();
        (client, server, client_gate)
    }

    fn eight_lane_session_pair() -> (BondSession, BondSession) {
        let config = BondRuntimeConfig {
            session_id: 92,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig {
                max_chunk_payload: 16 * 1024,
                bulk_chunk: anonssh_bond::BulkChunkConfig::fixed(16 * 1024),
                max_unacknowledged_bytes: 2 * 1024 * 1024,
                max_unacknowledged_chunks: 256,
                redundant_realtime: false,
            },
            max_reorder_bytes_per_stream: 2 * 1024 * 1024,
            max_receive_streams: 8,
            stream_receive_window: 2 * 1024 * 1024,
            max_ack_ranges: 16,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(10),
            retransmit_scan_interval: Duration::from_millis(100),
        };
        let mut client_lanes = Vec::new();
        let mut server_lanes = Vec::new();
        for id in 1_u32..=8 {
            let (client_io, server_io) = tokio::io::duplex(2 * 1024 * 1024);
            let lane = LaneConfig::new(
                LaneId::new(id).unwrap(),
                FailureDomain::new(id as u64).unwrap(),
                Duration::from_millis(u64::from(id) * 5),
                100_000_000,
            )
            .unwrap();
            let forward_key = [id as u8; 32];
            let reverse_key = [(id + 8) as u8; 32];
            client_lanes.push(RuntimeLane::new_for_test(
                lane,
                client_io,
                forward_key,
                reverse_key,
            ));
            server_lanes.push(RuntimeLane::new_for_test(
                lane,
                server_io,
                reverse_key,
                forward_key,
            ));
        }
        (
            BondSession::spawn(config, client_lanes, SessionRole::Dialer).unwrap(),
            BondSession::spawn(config, server_lanes, SessionRole::Listener).unwrap(),
        )
    }

    async fn wait_until_acknowledged(session: &BondSession) {
        tokio::time::timeout(Duration::from_secs(5), async {
            loop {
                if session.statistics().await.unwrap().unacknowledged_bytes == 0 {
                    return;
                }
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        })
        .await
        .expect("session did not acknowledge the payload");
    }

    #[tokio::test]
    async fn public_session_waiters_preserve_the_terminal_runtime_cause() {
        let (client, server) = session_pair();
        let mut opened = tokio::time::timeout(
            Duration::from_secs(2),
            client.open_stream(TrafficClass::Bulk),
        )
        .await
        .expect("initial stream creation remained blocked")
        .unwrap();
        let peer_stream = tokio::time::timeout(Duration::from_secs(2), server.accept_stream())
            .await
            .expect("peer stream acceptance remained blocked")
            .unwrap();
        let unopened_data = Frame::new(
            FrameKind::Data,
            FrameFlags::NONE,
            test_config().session_id,
            2,
            0,
            vec![0x5a],
        )
        .unwrap();

        let waiters = async {
            let mut byte = [0_u8; 1];
            tokio::join!(
                client.accept_topology(),
                client.accept_stream(),
                opened.read(&mut byte),
            )
        };
        let inject_failure = async {
            tokio::task::yield_now().await;
            client
                .runtime_control
                .inject_inbound_for_test(LaneId::new(1).unwrap(), 1, unopened_data)
                .await
                .unwrap();
        };
        let ((topology, stream, read), ()) = tokio::time::timeout(Duration::from_secs(2), async {
            tokio::join!(waiters, inject_failure)
        })
        .await
        .expect("public session waiters did not observe terminal runtime failure");

        for error in [
            topology.unwrap_err(),
            stream
                .err()
                .expect("stream acceptance unexpectedly succeeded"),
            client
                .open_stream(TrafficClass::Bulk)
                .await
                .err()
                .expect("stream creation unexpectedly succeeded"),
        ] {
            assert!(matches!(
                error,
                crate::BondRuntimeError::StoppedWithCause(ref cause)
                    if cause == "bond stream 2 is not open"
            ));
        }
        let read_error = read.expect_err("terminal stream read unexpectedly succeeded");
        assert!(read_error.to_string().contains("bond stream 2 is not open"));
        for error in [
            tokio::time::timeout(Duration::from_secs(2), opened.write_all(b"late write"))
                .await
                .expect("terminal stream write remained blocked")
                .unwrap_err(),
            tokio::time::timeout(Duration::from_secs(2), opened.shutdown())
                .await
                .expect("terminal stream shutdown remained blocked")
                .unwrap_err(),
        ] {
            assert!(error.to_string().contains("bond stream 2 is not open"));
        }
        let shutdown = tokio::time::timeout(Duration::from_secs(2), client.shutdown())
            .await
            .expect("terminal session shutdown remained blocked");
        assert!(matches!(
            shutdown.unwrap_err(),
            crate::BondRuntimeError::StoppedWithCause(ref cause)
                if cause == "bond stream 2 is not open"
        ));
        drop(peer_stream);
        drop(server);
    }

    #[tokio::test]
    async fn public_stream_is_bidirectional_and_acknowledges_half_close() {
        let (client, server) = session_pair();
        let mut client_stream = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut server_stream = server.accept_stream().await.unwrap();
        assert_eq!(client_stream.stream_id(), server_stream.stream_id());

        let payload = vec![0x5a; 48 * 1024];
        let write_payload = payload.clone();
        let client_write = async {
            client_stream.write_all(&write_payload).await.unwrap();
            client_stream.shutdown().await.unwrap();
            client_stream.shutdown().await.unwrap();
        };
        let server_read = async {
            let mut received = Vec::new();
            server_stream.read_to_end(&mut received).await.unwrap();
            received
        };
        let ((), received) = tokio::join!(client_write, server_read);
        assert_eq!(received, payload);

        let response = b"bonded response".repeat(512);
        let write_response = response.clone();
        let server_write = async {
            server_stream.write_all(&write_response).await.unwrap();
            server_stream.shutdown().await.unwrap();
            server_stream.shutdown().await.unwrap();
        };
        let client_read = async {
            let mut received = Vec::new();
            client_stream.read_to_end(&mut received).await.unwrap();
            received
        };
        let ((), received) = tokio::join!(server_write, client_read);
        assert_eq!(
            received.len(),
            response.len(),
            "reverse payload length changed"
        );
        assert_eq!(received, response);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn sequential_streams_outlive_live_and_retired_limits() {
        let (client, server) = session_pair();
        let stream_limit = test_config().max_receive_streams;
        let stream_count = stream_limit * 3;

        for sequence in 0..stream_count {
            let mut client_stream = client.open_stream(TrafficClass::Bulk).await.unwrap();
            let mut server_stream = server.accept_stream().await.unwrap();
            let request = vec![sequence as u8; 1536];
            let expected_request = request.clone();
            let ((), received) = tokio::join!(
                async {
                    client_stream.write_all(&request).await.unwrap();
                    client_stream.shutdown().await.unwrap();
                },
                async {
                    let mut received = Vec::new();
                    server_stream.read_to_end(&mut received).await.unwrap();
                    received
                }
            );
            assert_eq!(received, expected_request);

            let response = vec![0xff - sequence as u8; 1536];
            let expected_response = response.clone();
            let ((), received) = tokio::join!(
                async {
                    server_stream.write_all(&response).await.unwrap();
                    server_stream.shutdown().await.unwrap();
                },
                async {
                    let mut received = Vec::new();
                    client_stream.read_to_end(&mut received).await.unwrap();
                    received
                }
            );
            assert_eq!(received, expected_response);

            let (client_stats, server_stats) =
                tokio::join!(client.statistics(), server.statistics());
            for stats in [client_stats.unwrap(), server_stats.unwrap()] {
                assert_eq!(stats.active_streams, 0);
                assert!(stats.retired_stream_tombstones <= stream_limit);
            }
        }

        let (client_stats, server_stats) = tokio::join!(client.statistics(), server.statistics());
        assert_eq!(
            client_stats.unwrap().retired_stream_tombstones,
            stream_limit
        );
        assert_eq!(
            server_stats.unwrap().retired_stream_tombstones,
            stream_limit
        );
        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn bounded_full_duplex_traffic_makes_progress_in_both_directions() {
        let report = super::concurrent_progress_self_test().await.unwrap();
        assert_eq!(report.payload_bytes_per_direction, 2 * 1024 * 1024);
        assert_eq!(report.delayed_read_millis, 250);
        assert_ne!(report.client_received_sha256, report.server_received_sha256);
    }

    #[tokio::test]
    async fn public_stream_reaches_adaptive_bulk_ceiling() {
        const PAYLOAD_BYTES: usize = 256 * 1024;
        let config = BondRuntimeConfig {
            session_id: 93,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig {
                max_chunk_payload: 16 * 1024,
                bulk_chunk: anonssh_bond::BulkChunkConfig::default(),
                max_unacknowledged_bytes: 1024 * 1024,
                max_unacknowledged_chunks: 128,
                redundant_realtime: false,
            },
            max_reorder_bytes_per_stream: 1024 * 1024,
            max_receive_streams: 8,
            stream_receive_window: 1024 * 1024,
            max_ack_ranges: 8,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(2),
            retransmit_scan_interval: Duration::from_millis(10),
        };
        let lane = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(20),
            100_000_000,
        )
        .unwrap();
        let (client_io, server_io) = tokio::io::duplex(1024 * 1024);
        let client = BondSession::spawn(
            config,
            vec![RuntimeLane::new_for_test(lane, client_io, [1; 32], [2; 32])],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            config,
            vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])],
            SessionRole::Listener,
        )
        .unwrap();
        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        let payload = vec![0x6d; PAYLOAD_BYTES];
        let send = async {
            outbound.write_all(&payload).await.unwrap();
            outbound.shutdown().await.unwrap();
        };
        let receive = async {
            let mut received = Vec::new();
            inbound.read_to_end(&mut received).await.unwrap();
            inbound.shutdown().await.unwrap();
            received
        };
        let ((), received) = tokio::join!(send, receive);
        assert_eq!(received, payload);
        wait_until_acknowledged(&client).await;
        let client_stats = client.statistics().await.unwrap();
        let server_stats = server.statistics().await.unwrap();
        assert_eq!(client_stats.new_data_frames, 4);
        assert_eq!(server_stats.received_by_lane[0].unique_data_frames, 4);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn stalled_reader_accounts_stream_backpressure_without_leaking_active_state() {
        let (client, server) = session_pair();
        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        let payload = vec![0x4b; 128 * 1024];
        let writer = tokio::spawn(async move {
            outbound.write_all(&payload).await.unwrap();
            outbound.shutdown().await.unwrap();
        });

        tokio::time::timeout(Duration::from_secs(5), async {
            loop {
                let stats = client.statistics().await.unwrap();
                if stats.backpressured_streams > 0 && stats.stream_backpressure_events > 0 {
                    break;
                }
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
        })
        .await
        .expect("stalled reader did not apply stream backpressure");

        let mut received = Vec::new();
        inbound.read_to_end(&mut received).await.unwrap();
        inbound.shutdown().await.unwrap();
        writer.await.unwrap();
        assert_eq!(received, vec![0x4b; 128 * 1024]);
        let stats = client.statistics().await.unwrap();
        assert_eq!(stats.backpressured_streams, 0);
        assert!(stats.stream_backpressure_events > 0);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn eight_lane_runtime_uses_bulk_pool_and_realtime_protection() {
        let (client, server) = eight_lane_session_pair();

        let mut bulk_outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut bulk_inbound = server.accept_stream().await.unwrap();
        let bulk = vec![0x6b; 1024 * 1024];
        let expected_bulk = bulk.clone();
        let send_bulk = async {
            bulk_outbound.write_all(&bulk).await.unwrap();
            bulk_outbound.shutdown().await.unwrap();
        };
        let receive_bulk = async {
            let mut bytes = Vec::new();
            bulk_inbound.read_to_end(&mut bytes).await.unwrap();
            bulk_inbound.shutdown().await.unwrap();
            bytes
        };
        let ((), received_bulk) = tokio::join!(send_bulk, receive_bulk);
        assert_eq!(received_bulk, expected_bulk);

        let mut realtime_outbound = client.open_stream(TrafficClass::Realtime).await.unwrap();
        let mut realtime_inbound = server.accept_stream().await.unwrap();
        let realtime = vec![0x72; 64 * 1024];
        let expected_realtime = realtime.clone();
        let send_realtime = async {
            realtime_outbound.write_all(&realtime).await.unwrap();
            realtime_outbound.shutdown().await.unwrap();
        };
        let receive_realtime = async {
            let mut bytes = Vec::new();
            realtime_inbound.read_to_end(&mut bytes).await.unwrap();
            realtime_inbound.shutdown().await.unwrap();
            bytes
        };
        let ((), received_realtime) = tokio::join!(send_realtime, receive_realtime);
        assert_eq!(received_realtime, expected_realtime);

        let client_stats = client.statistics().await.unwrap();
        let server_stats = server.statistics().await.unwrap();
        assert_eq!(client_stats.unacknowledged_bytes, 0);
        assert_eq!(server_stats.received_by_lane.len(), 8);
        let contributing_lanes = server_stats
            .received_by_lane
            .iter()
            .filter(|lane| lane.unique_data_bytes > 0)
            .count();
        assert!(
            contributing_lanes >= 7,
            "bulk and realtime traffic must use at least seven lanes: {:?}",
            server_stats.received_by_lane
        );

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn one_interactive_stream_protects_typing_and_stripes_bulk() {
        let (client, server) = eight_lane_session_pair();
        let mut outbound = client.open_stream(TrafficClass::Interactive).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        assert_eq!(outbound.traffic_class(), TrafficClass::Interactive);
        assert_eq!(inbound.traffic_class(), TrafficClass::Interactive);

        let baseline = client.statistics().await.unwrap();
        let protected = baseline
            .lanes
            .iter()
            .find(|lane| lane.reserved_for_low_latency)
            .unwrap()
            .id;
        let typing = vec![0x74; 256];
        outbound.write_all(&typing).await.unwrap();
        let mut received_typing = vec![0; typing.len()];
        inbound.read_exact(&mut received_typing).await.unwrap();
        assert_eq!(received_typing, typing);
        wait_until_acknowledged(&client).await;
        let after_typing = client.statistics().await.unwrap();
        let protected_before = baseline
            .lanes
            .iter()
            .find(|lane| lane.id == protected)
            .unwrap()
            .bytes_scheduled;
        let protected_after_typing = after_typing
            .lanes
            .iter()
            .find(|lane| lane.id == protected)
            .unwrap()
            .bytes_scheduled;
        assert!(protected_after_typing >= protected_before + typing.len() as u64);
        assert!(after_typing
            .lanes
            .iter()
            .filter(|lane| lane.id != protected)
            .all(|lane| lane.bytes_scheduled
                == baseline
                    .lanes
                    .iter()
                    .find(|before| before.id == lane.id)
                    .unwrap()
                    .bytes_scheduled));

        let bulk = vec![0x62; 1024 * 1024];
        let send = outbound.write_all(&bulk);
        let mut received_bulk = vec![0; bulk.len()];
        let receive = inbound.read_exact(&mut received_bulk);
        let (sent, received) = tokio::join!(send, receive);
        sent.unwrap();
        received.unwrap();
        assert_eq!(received_bulk, bulk);
        wait_until_acknowledged(&client).await;
        let after_bulk = client.statistics().await.unwrap();
        assert!(
            after_bulk
                .lanes
                .iter()
                .filter(|lane| {
                    lane.bytes_scheduled
                        > after_typing
                            .lanes
                            .iter()
                            .find(|before| before.id == lane.id)
                            .unwrap()
                            .bytes_scheduled
                })
                .count()
                >= 2,
            "sustained interactive payload did not use multiple bulk lanes"
        );

        let (outbound_close, inbound_close) = tokio::join!(outbound.shutdown(), inbound.shutdown());
        outbound_close.unwrap();
        inbound_close.unwrap();
        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn realtime_redundancy_delivers_before_a_stalled_primary_recovers() {
        let (client, server, primary_gate, _standby_gate) = redundant_realtime_session_pair();
        let mut outbound = client.open_stream(TrafficClass::Interactive).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        primary_gate.block();

        let typing = vec![0x74; 256];
        outbound.write_all(&typing).await.unwrap();
        tokio::time::timeout(Duration::from_secs(1), primary_gate.wait_until_blocked())
            .await
            .expect("preferred real-time path did not reach its stalled writer");
        let mut received = vec![0; typing.len()];
        tokio::time::timeout(Duration::from_secs(1), inbound.read_exact(&mut received))
            .await
            .expect("protected standby did not win the real-time race")
            .unwrap();
        assert_eq!(received, typing);
        wait_until_acknowledged(&client).await;

        let client_stats = client.statistics().await.unwrap();
        let server_stats = server.statistics().await.unwrap();
        assert_eq!(client_stats.new_data_frames, 1);
        assert_eq!(client_stats.redundant_realtime_frames, 1);
        assert_eq!(client_stats.dropped_redundant_realtime_frames, 0);
        assert_eq!(
            client_stats
                .lanes
                .iter()
                .find(|lane| lane.id == LaneId::new(1).unwrap())
                .unwrap()
                .bytes_acknowledged,
            0
        );
        assert_eq!(
            client_stats
                .lanes
                .iter()
                .find(|lane| lane.id == LaneId::new(2).unwrap())
                .unwrap()
                .bytes_acknowledged,
            typing.len() as u64
        );
        assert_eq!(
            server_stats
                .received_by_lane
                .iter()
                .find(|lane| lane.id == LaneId::new(2).unwrap())
                .unwrap()
                .unique_data_bytes,
            typing.len() as u64
        );

        let first = LaneId::new(1).unwrap();
        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(first), server.fail_lane(first));
        client_failed.unwrap();
        server_failed.unwrap();
        let (outbound_closed, inbound_closed) =
            tokio::join!(outbound.shutdown(), inbound.shutdown());
        outbound_closed.unwrap();
        inbound_closed.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn a_saturated_redundant_queue_never_fails_primary_delivery() {
        let (client, server, _primary_gate, standby_gate) = redundant_realtime_session_pair();
        let mut outbound = client.open_stream(TrafficClass::Interactive).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        standby_gate.block();

        for sequence in 0_u32..512 {
            let token = sequence.to_be_bytes().repeat(8);
            outbound.write_all(&token).await.unwrap();
            let mut received = vec![0; token.len()];
            tokio::time::timeout(Duration::from_secs(1), inbound.read_exact(&mut received))
                .await
                .expect("primary real-time delivery stalled behind its redundant queue")
                .unwrap();
            assert_eq!(received, token);
        }
        tokio::time::timeout(Duration::from_secs(1), standby_gate.wait_until_blocked())
            .await
            .expect("standby writer was not saturated");
        wait_until_acknowledged(&client).await;
        let stats = client.statistics().await.unwrap();
        assert!(stats.redundant_realtime_frames > 0);
        assert!(stats.dropped_redundant_realtime_frames > 0);
        assert_eq!(stats.unacknowledged_bytes, 0);

        let second = LaneId::new(2).unwrap();
        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(second), server.fail_lane(second));
        client_failed.unwrap();
        server_failed.unwrap();
        let (outbound_closed, inbound_closed) =
            tokio::join!(outbound.shutdown(), inbound.shutdown());
        outbound_closed.unwrap();
        inbound_closed.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn legacy_protocol_sessions_keep_realtime_single_copy() {
        let mut config = test_config();
        config.scheduler.low_latency_lane_count = 2;
        config.sender.redundant_realtime = true;
        let mut client_lanes = Vec::new();
        let mut server_lanes = Vec::new();
        for (id, forward, reverse) in [(1, 1, 2), (2, 3, 4)] {
            let lane = test_lane(id, u64::from(id) * 5);
            let (client_io, server_io) = tokio::io::duplex(256 * 1024);
            client_lanes.push(
                RuntimeLane::new_for_test(lane, client_io, [forward; 32], [reverse; 32])
                    .with_protocol_version_for_test(BondProtocolVersion::V2),
            );
            server_lanes.push(
                RuntimeLane::new_for_test(lane, server_io, [reverse; 32], [forward; 32])
                    .with_protocol_version_for_test(BondProtocolVersion::V2),
            );
        }
        let client = BondSession::spawn(config, client_lanes, SessionRole::Dialer).unwrap();
        let server = BondSession::spawn(config, server_lanes, SessionRole::Listener).unwrap();
        let mut outbound = client.open_stream(TrafficClass::Interactive).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        outbound.write_all(b"legacy typing").await.unwrap();
        let mut received = vec![0; b"legacy typing".len()];
        inbound.read_exact(&mut received).await.unwrap();
        assert_eq!(received, b"legacy typing");
        wait_until_acknowledged(&client).await;
        let stats = client.statistics().await.unwrap();
        assert_eq!(stats.new_data_frames, 1);
        assert_eq!(stats.redundant_realtime_frames, 0);

        let (outbound_closed, inbound_closed) =
            tokio::join!(outbound.shutdown(), inbound.shutdown());
        outbound_closed.unwrap();
        inbound_closed.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn failed_declared_lane_can_be_replaced_without_stopping_the_session() {
        let first = test_lane(1, 5);
        let second = test_lane(2, 40);
        let (client_first, server_first) = tokio::io::duplex(256 * 1024);
        let (client_second, server_second) = tokio::io::duplex(256 * 1024);
        let client = BondSession::spawn(
            test_config(),
            vec![
                RuntimeLane::new_for_test(first, client_first, [1; 32], [2; 32]),
                RuntimeLane::new_for_test(second, client_second, [3; 32], [4; 32]),
            ],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            test_config(),
            vec![
                RuntimeLane::new_for_test(first, server_first, [2; 32], [1; 32]),
                RuntimeLane::new_for_test(second, server_second, [4; 32], [3; 32]),
            ],
            SessionRole::Listener,
        )
        .unwrap();

        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(second.id), server.fail_lane(second.id));
        client_failed.unwrap();
        server_failed.unwrap();
        let (client_replacement, server_replacement) = tokio::io::duplex(256 * 1024);
        let (client_added, server_added) = tokio::join!(
            client.add_lane(RuntimeLane::new_for_test(
                second,
                client_replacement,
                [5; 32],
                [6; 32],
            )),
            server.add_lane(RuntimeLane::new_for_test(
                second,
                server_replacement,
                [6; 32],
                [5; 32],
            )),
        );
        client_added.unwrap();
        server_added.unwrap();
        assert!(
            client
                .statistics()
                .await
                .unwrap()
                .lanes
                .iter()
                .find(|lane| lane.id == second.id)
                .unwrap()
                .active
        );

        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        let payload = vec![0xa5; 48 * 1024];
        let write_payload = payload.clone();
        let send = async {
            outbound.write_all(&write_payload).await.unwrap();
            outbound.shutdown().await.unwrap();
        };
        let receive = async {
            let mut received = Vec::new();
            inbound.read_to_end(&mut received).await.unwrap();
            received
        };
        let ((), received) = tokio::join!(send, receive);
        assert_eq!(received, payload);

        let response = b"replacement survived".repeat(64);
        let expected = response.clone();
        let send = async {
            inbound.write_all(&response).await.unwrap();
            inbound.shutdown().await.unwrap();
        };
        let receive = async {
            let mut received = Vec::new();
            outbound.read_to_end(&mut received).await.unwrap();
            received
        };
        let ((), received) = tokio::join!(send, receive);
        assert_eq!(received, expected);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn queued_stream_open_replays_after_its_lane_is_discarded() {
        let (client, server, client_gate, _server_gate) = gated_two_lane_session_pair();
        client_gate.block();
        let mut outbound = {
            let open = client.open_stream(TrafficClass::Bulk);
            tokio::pin!(open);
            tokio::time::timeout(Duration::from_secs(1), async {
                tokio::select! {
                    _ = &mut open => panic!("stream open escaped blocked lane"),
                    () = client_gate.wait_until_blocked() => {}
                }
            })
            .await
            .expect("stream-open record did not reach the blocked writer");

            let first = LaneId::new(1).unwrap();
            let (client_failed, server_failed) =
                tokio::join!(client.fail_lane(first), server.fail_lane(first));
            client_failed.unwrap();
            server_failed.unwrap();
            tokio::time::timeout(Duration::from_secs(2), &mut open)
                .await
                .expect("replayed stream open timed out")
                .unwrap()
        };
        let mut inbound = tokio::time::timeout(Duration::from_secs(2), server.accept_stream())
            .await
            .expect("replayed stream open was not accepted")
            .unwrap();
        assert!(client.statistics().await.unwrap().replayed_control_frames > 0);

        let (outbound_close, inbound_close) = tokio::join!(outbound.shutdown(), inbound.shutdown());
        outbound_close.unwrap();
        inbound_close.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn queued_stream_close_replays_after_its_lane_is_discarded() {
        let (client, server, client_gate, _server_gate) = gated_two_lane_session_pair();
        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        client_gate.block();
        {
            let close = outbound.shutdown();
            tokio::pin!(close);
            tokio::time::timeout(Duration::from_secs(1), async {
                tokio::select! {
                    result = &mut close => panic!("stream close escaped blocked lane: {result:?}"),
                    () = client_gate.wait_until_blocked() => {}
                }
            })
            .await
            .expect("stream-close record did not reach the blocked writer");

            let first = LaneId::new(1).unwrap();
            let (client_failed, server_failed) =
                tokio::join!(client.fail_lane(first), server.fail_lane(first));
            client_failed.unwrap();
            server_failed.unwrap();
            tokio::time::timeout(Duration::from_secs(2), &mut close)
                .await
                .expect("replayed stream close timed out")
                .unwrap();
        }
        let mut received = Vec::new();
        tokio::time::timeout(Duration::from_secs(2), inbound.read_to_end(&mut received))
            .await
            .expect("replayed stream close did not deliver EOF")
            .unwrap();
        assert!(received.is_empty());
        assert!(client.statistics().await.unwrap().replayed_control_frames > 0);

        inbound.shutdown().await.unwrap();
        let mut response = Vec::new();
        outbound.read_to_end(&mut response).await.unwrap();
        assert!(response.is_empty());
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn cumulative_topology_replays_after_its_lane_is_discarded() {
        let (client, server, client_gate, _server_gate) = gated_two_lane_session_pair();
        client_gate.block();
        let advertisement = TopologyAdvertisement::new(
            1,
            vec![EndpointDescriptor::new(
                LaneId::new(3).unwrap(),
                FailureDomain::new(3).unwrap(),
                EndpointProvider::Tcp,
                TopologyAction::Add,
                "tcp://127.0.0.1:24023".to_owned(),
            )
            .unwrap()],
        )
        .unwrap();
        client
            .advertise_topology(advertisement.clone())
            .await
            .unwrap();
        tokio::time::timeout(Duration::from_secs(1), client_gate.wait_until_blocked())
            .await
            .expect("topology record did not reach the blocked writer");

        let first = LaneId::new(1).unwrap();
        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(first), server.fail_lane(first));
        client_failed.unwrap();
        server_failed.unwrap();
        assert_eq!(
            tokio::time::timeout(Duration::from_secs(2), server.accept_topology())
                .await
                .expect("replayed topology timed out")
                .unwrap(),
            advertisement
        );
        assert!(client.statistics().await.unwrap().replayed_control_frames > 0);

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn cumulative_capabilities_replay_after_their_lane_is_discarded() {
        let (client, server, client_gate, _server_gate) = gated_two_lane_session_pair();
        client_gate.block();
        let advertisement = capabilities(1, 12_000);
        client
            .advertise_capabilities(advertisement.clone())
            .await
            .unwrap();
        tokio::time::timeout(Duration::from_secs(1), client_gate.wait_until_blocked())
            .await
            .expect("capability record did not reach the blocked writer");

        let first = LaneId::new(1).unwrap();
        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(first), server.fail_lane(first));
        client_failed.unwrap();
        server_failed.unwrap();
        assert_eq!(
            tokio::time::timeout(Duration::from_secs(2), server.accept_capabilities())
                .await
                .expect("replayed capabilities timed out")
                .unwrap(),
            advertisement
        );
        assert!(client.statistics().await.unwrap().replayed_control_frames > 0);
        assert!(matches!(
            client.advertise_capabilities(capabilities(1, 20_000)).await,
            Err(BondRuntimeError::RegressingCapabilityGeneration {
                previous: 1,
                received: 1,
            })
        ));

        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn protocol_v3_rejects_capabilities_without_breaking_legacy_frames() {
        let (client_io, server_io) = tokio::io::duplex(256 * 1024);
        let lane = test_lane(1, 5);
        let config = test_config();
        let client = BondSession::spawn(
            config,
            vec![RuntimeLane::new_for_test(lane, client_io, [1; 32], [2; 32])
                .with_protocol_version_for_test(BondProtocolVersion::V3)],
            SessionRole::Dialer,
        )
        .unwrap();
        let server = BondSession::spawn(
            config,
            vec![RuntimeLane::new_for_test(lane, server_io, [2; 32], [1; 32])
                .with_protocol_version_for_test(BondProtocolVersion::V3)],
            SessionRole::Listener,
        )
        .unwrap();
        assert!(matches!(
            client.advertise_capabilities(capabilities(1, 10_000)).await,
            Err(BondRuntimeError::CapabilitiesRequireProtocolV4)
        ));

        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        outbound.write_all(b"v3 remains usable").await.unwrap();
        outbound.shutdown().await.unwrap();
        let mut received = Vec::new();
        inbound.read_to_end(&mut received).await.unwrap();
        assert_eq!(received, b"v3 remains usable");
        inbound.shutdown().await.unwrap();
        let mut response = Vec::new();
        outbound.read_to_end(&mut response).await.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn queued_session_close_replays_after_its_lane_is_discarded() {
        let (client, server, client_gate, _server_gate) = gated_two_lane_session_pair();
        let client_control = client.control();
        client_gate.block();
        let shutdown = tokio::spawn(client.shutdown());
        tokio::time::timeout(Duration::from_secs(1), client_gate.wait_until_blocked())
            .await
            .expect("session-close record did not reach the blocked writer");

        let first = LaneId::new(1).unwrap();
        let (client_failed, server_failed) =
            tokio::join!(client_control.fail_lane(first), server.fail_lane(first));
        client_failed.unwrap();
        server_failed.unwrap();
        tokio::time::timeout(Duration::from_secs(2), shutdown)
            .await
            .expect("replayed session close timed out")
            .expect("client shutdown task failed")
            .unwrap();
        tokio::time::timeout(Duration::from_secs(2), server.shutdown())
            .await
            .expect("passive server shutdown timed out")
            .unwrap();
    }

    #[tokio::test]
    async fn crossing_session_closes_survive_an_unwritten_request() {
        let (client, server, _client_gate, server_gate) = gated_two_lane_session_pair();
        let client_control = client.control();
        let server_control = server.control();
        server_gate.block();
        let client_shutdown = tokio::spawn(client.shutdown());
        let server_shutdown = tokio::spawn(server.shutdown());
        tokio::time::timeout(Duration::from_secs(1), server_gate.wait_until_blocked())
            .await
            .expect("crossing server close did not reach the blocked writer");

        let first = LaneId::new(1).unwrap();
        let (client_failed, server_failed) = tokio::join!(
            client_control.fail_lane(first),
            server_control.fail_lane(first)
        );
        client_failed.unwrap();
        server_failed.unwrap();
        let (client_result, server_result) = tokio::time::timeout(Duration::from_secs(2), async {
            tokio::join!(client_shutdown, server_shutdown)
        })
        .await
        .expect("crossing close replay timed out");
        client_result.expect("client shutdown task failed").unwrap();
        server_result.expect("server shutdown task failed").unwrap();
    }

    #[tokio::test]
    async fn absolute_receive_credit_replays_after_its_lane_is_discarded() {
        let first = test_lane(1, 5);
        let second = test_lane(2, 50);
        let (client_first, server_first) = tokio::io::duplex(256 * 1024);
        let (client_second, server_second) = tokio::io::duplex(256 * 1024);
        let server_gate = WriteGate::default();
        let config = test_config();
        let client = BondRuntime::spawn(
            config,
            vec![
                RuntimeLane::new_for_test(first, client_first, [1; 32], [2; 32]),
                RuntimeLane::new_for_test(second, client_second, [3; 32], [4; 32]),
            ],
        )
        .unwrap();
        let mut server = BondRuntime::spawn(
            config,
            vec![
                RuntimeLane::new_for_test(
                    first,
                    GatedIo::new(server_first, server_gate.clone()),
                    [2; 32],
                    [1; 32],
                ),
                RuntimeLane::new_for_test(second, server_second, [4; 32], [3; 32]),
            ],
        )
        .unwrap();
        let stream = StreamId::new(1).unwrap();
        client
            .open_stream(stream, TrafficClass::Bulk)
            .await
            .unwrap();
        assert!(matches!(
            server.receive_event().await.unwrap(),
            RuntimeEvent::StreamOpened { stream_id, .. } if stream_id == stream
        ));

        server_gate.block();
        let initial = vec![0x5a; config.stream_receive_window];
        client
            .send(stream, TrafficClass::Bulk, initial.clone())
            .await
            .unwrap();
        let mut received = Vec::with_capacity(initial.len());
        while received.len() < initial.len() {
            match server.receive_event().await.unwrap() {
                RuntimeEvent::Data(data) if data.stream_id == stream => {
                    received.extend_from_slice(&data.bytes);
                }
                event => panic!("unexpected event while filling receive window: {event:?}"),
            }
        }
        assert_eq!(received, initial);
        tokio::time::timeout(Duration::from_secs(1), server_gate.wait_until_blocked())
            .await
            .expect("window control did not reach the blocked writer");
        assert!(matches!(
            client.send(stream, TrafficClass::Bulk, vec![0x6b]).await,
            Err(BondRuntimeError::FlowControlBlocked { .. })
        ));

        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(first.id), server.fail_lane(first.id));
        client_failed.unwrap();
        server_failed.unwrap();
        tokio::time::timeout(Duration::from_secs(2), async {
            loop {
                match client.send(stream, TrafficClass::Bulk, vec![0x6b]).await {
                    Ok(()) => return,
                    Err(BondRuntimeError::FlowControlBlocked { .. }) => {
                        tokio::time::sleep(Duration::from_millis(1)).await;
                    }
                    Err(error) => panic!("unexpected send error after replay: {error}"),
                }
            }
        })
        .await
        .expect("replayed receive credit did not unblock the sender");
        assert!(matches!(
            server.receive_event().await.unwrap(),
            RuntimeEvent::Data(data) if data.stream_id == stream && data.bytes == vec![0x6b]
        ));
        assert!(server.statistics().await.unwrap().replayed_control_frames > 0);
    }

    #[tokio::test]
    async fn sole_lane_outage_backpressures_and_resumes_full_duplex_streams() {
        let lane = test_lane(1, 5);
        let (client, server) = session_pair();
        let client_stream = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let server_stream = server.accept_stream().await.unwrap();
        let (mut client_read, mut client_write) = tokio::io::split(client_stream);
        let (mut server_read, mut server_write) = tokio::io::split(server_stream);

        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(lane.id), server.fail_lane(lane.id));
        client_failed.unwrap();
        server_failed.unwrap();
        assert_eq!(
            client
                .statistics()
                .await
                .unwrap()
                .lanes
                .iter()
                .filter(|snapshot| snapshot.active)
                .count(),
            0
        );
        assert_eq!(
            server
                .statistics()
                .await
                .unwrap()
                .lanes
                .iter()
                .filter(|snapshot| snapshot.active)
                .count(),
            0
        );

        let client_payload = vec![0xc1; 48 * 1024];
        let server_payload = vec![0x5e; 48 * 1024];
        let expected_client = client_payload.clone();
        let expected_server = server_payload.clone();
        let transfer = async {
            let client_send = async {
                client_write.write_all(&client_payload).await.unwrap();
                client_write.shutdown().await.unwrap();
            };
            let server_send = async {
                server_write.write_all(&server_payload).await.unwrap();
                server_write.shutdown().await.unwrap();
            };
            let client_receive = async {
                let mut bytes = Vec::new();
                client_read.read_to_end(&mut bytes).await.unwrap();
                bytes
            };
            let server_receive = async {
                let mut bytes = Vec::new();
                server_read.read_to_end(&mut bytes).await.unwrap();
                bytes
            };
            tokio::join!(client_send, server_send, client_receive, server_receive)
        };
        let repair = async {
            tokio::time::sleep(Duration::from_millis(100)).await;
            let (client_io, server_io) = tokio::io::duplex(256 * 1024);
            let (client_added, server_added) = tokio::join!(
                client.add_lane(RuntimeLane::new_for_test(lane, client_io, [5; 32], [6; 32],)),
                server.add_lane(RuntimeLane::new_for_test(lane, server_io, [6; 32], [5; 32],)),
            );
            client_added.unwrap();
            server_added.unwrap();
        };
        let (((), (), client_received, server_received), ()) =
            tokio::time::timeout(Duration::from_secs(5), async {
                tokio::join!(transfer, repair)
            })
            .await
            .expect("zero-lane repair did not resume traffic");
        assert_eq!(client_received, expected_server);
        assert_eq!(server_received, expected_client);
        wait_until_acknowledged(&client).await;
        wait_until_acknowledged(&server).await;
        assert!(client.statistics().await.unwrap().window_update_frames > 0);
        assert!(server.statistics().await.unwrap().window_update_frames > 0);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn sole_lane_failure_replays_stranded_payload_and_topology() {
        let lane = test_lane(1, 5);
        let (client, server, client_gate) = gated_single_lane_session_pair();
        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        let payload = vec![0xc7; 48 * 1024];
        let expected_payload = payload.clone();
        client_gate.block();
        {
            let write = outbound.write_all(&payload);
            tokio::pin!(write);
            tokio::time::timeout(Duration::from_secs(1), async {
                tokio::select! {
                    result = &mut write => panic!("stranded payload escaped blocked lane: {result:?}"),
                    () = client_gate.wait_until_blocked() => {}
                }
            })
            .await
            .expect("payload record did not reach the blocked writer");

            let advertised = test_lane(2, 15);
            let topology = TopologyAdvertisement::new(
                1,
                vec![EndpointDescriptor::new(
                    advertised.id,
                    advertised.failure_domain,
                    EndpointProvider::Tcp,
                    TopologyAction::Add,
                    "tcp://127.0.0.1:24022".to_owned(),
                )
                .unwrap()],
            )
            .unwrap();
            client.advertise_topology(topology.clone()).await.unwrap();

            let (client_failed, server_failed) =
                tokio::join!(client.fail_lane(lane.id), server.fail_lane(lane.id));
            client_failed.unwrap();
            server_failed.unwrap();
            assert_eq!(
                client
                    .statistics()
                    .await
                    .unwrap()
                    .lanes
                    .iter()
                    .filter(|snapshot| snapshot.active)
                    .count(),
                0
            );

            let (client_io, server_io) = tokio::io::duplex(256 * 1024);
            let (client_added, server_added) = tokio::join!(
                client.add_lane(RuntimeLane::new_for_test(lane, client_io, [5; 32], [6; 32],)),
                server.add_lane(RuntimeLane::new_for_test(lane, server_io, [6; 32], [5; 32],)),
            );
            client_added.unwrap();
            server_added.unwrap();

            let complete_write = async {
                tokio::time::timeout(Duration::from_secs(2), &mut write)
                    .await
                    .expect("stranded payload did not resume")
                    .unwrap();
            };
            let receive_payload = async {
                let mut received = vec![0; expected_payload.len()];
                inbound.read_exact(&mut received).await.unwrap();
                received
            };
            let ((), received) = tokio::join!(complete_write, receive_payload);
            assert_eq!(received, expected_payload);
            assert_eq!(
                tokio::time::timeout(Duration::from_secs(2), server.accept_topology())
                    .await
                    .expect("deferred topology did not replay")
                    .unwrap(),
                topology
            );
        }
        let stats = client.statistics().await.unwrap();
        assert!(stats.retransmitted_frames > 0);
        assert!(stats.replayed_control_frames > 0);

        let response = b"full duplex survived zero lanes".repeat(256);
        let expected_response = response.clone();
        let send_response = inbound.write_all(&response);
        let mut received_response = vec![0; expected_response.len()];
        let receive_response = outbound.read_exact(&mut received_response);
        let (sent, received) = tokio::join!(send_response, receive_response);
        sent.unwrap();
        received.unwrap();
        assert_eq!(received_response, expected_response);

        let (outbound_close, inbound_close) = tokio::join!(outbound.shutdown(), inbound.shutdown());
        outbound_close.unwrap();
        inbound_close.unwrap();
        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn sole_lane_outage_defers_topology_advertisement_until_repair() {
        let lane = test_lane(1, 5);
        let (client, server) = session_pair();
        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(lane.id), server.fail_lane(lane.id));
        client_failed.unwrap();
        server_failed.unwrap();

        let advertised = test_lane(2, 15);
        let advertisement = TopologyAdvertisement::new(
            1,
            vec![EndpointDescriptor::new(
                advertised.id,
                advertised.failure_domain,
                EndpointProvider::Tcp,
                TopologyAction::Add,
                "tcp://127.0.0.1:24022".to_owned(),
            )
            .unwrap()],
        )
        .unwrap();
        let expected = advertisement.clone();
        let client_control = client.control();
        let server_control = server.control();
        let advertise = client_control.advertise_topology(advertisement);
        tokio::pin!(advertise);
        tokio::select! {
            result = &mut advertise => panic!("topology advertisement completed without a lane: {result:?}"),
            _ = tokio::time::sleep(Duration::from_millis(50)) => {}
        }

        let (client_io, server_io) = tokio::io::duplex(64 * 1024);
        let (client_added, server_added) = tokio::join!(
            client_control.add_lane(RuntimeLane::new_for_test(lane, client_io, [5; 32], [6; 32],)),
            server_control.add_lane(RuntimeLane::new_for_test(lane, server_io, [6; 32], [5; 32],)),
        );
        client_added.unwrap();
        server_added.unwrap();
        tokio::time::timeout(Duration::from_secs(5), advertise)
            .await
            .expect("topology advertisement send did not resume after lane repair")
            .unwrap();
        let received = tokio::time::timeout(Duration::from_secs(5), server.accept_topology())
            .await
            .expect("peer did not receive topology advertisement after lane repair")
            .unwrap();
        assert_eq!(received, expected);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }

    #[tokio::test]
    async fn advertised_unknown_provider_is_policy_authorized_and_added() {
        let (client, server) = session_pair();
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let endpoint = format!("tcp://{}", listener.local_addr().unwrap());
        let lane = test_lane(2, 15);
        let advertisement = TopologyAdvertisement::new(
            1,
            vec![EndpointDescriptor::new(
                lane.id,
                lane.failure_domain,
                EndpointProvider::Tcp,
                TopologyAction::Add,
                endpoint,
            )
            .unwrap()],
        )
        .unwrap();
        server
            .advertise_topology(advertisement.clone())
            .await
            .unwrap();
        let received = client.accept_topology().await.unwrap();
        assert_eq!(received, advertisement);
        let denied = TopologyPolicy::new(
            1,
            8,
            [EndpointProvider::I2p],
            [lane.failure_domain],
            [TopologyAction::Add],
        )
        .unwrap();
        assert_eq!(
            denied.validate(&received).unwrap_err(),
            TopologyError::ProviderDenied(EndpointProvider::Tcp)
        );
        let policy = TopologyPolicy::new(
            1,
            8,
            [EndpointProvider::Tcp],
            [lane.failure_domain],
            [TopologyAction::Add],
        )
        .unwrap();
        policy.validate(&received).unwrap();
        assert!(server.advertise_topology(advertisement).await.is_err());

        let (client_declared, server_declared) =
            tokio::join!(client.authorize_lane(lane), server.authorize_lane(lane));
        client_declared.unwrap();
        server_declared.unwrap();

        let address: std::net::SocketAddr = received.descriptors[0]
            .endpoint
            .strip_prefix("tcp://")
            .unwrap()
            .parse()
            .unwrap();
        let (connected, accepted) = tokio::join!(TcpStream::connect(address), listener.accept());
        let client_io = connected.unwrap();
        let (server_io, _) = accepted.unwrap();
        let key = BondSessionKey::new([9; 32]);
        let join = LaneJoin::new(91, lane.id, lane.failure_domain).unwrap();
        let (client_lane, server_lane) = tokio::join!(
            authenticate_client_lane(client_io, &key, join, Duration::from_secs(2)),
            authenticate_server_lane_with_incarnation(
                server_io,
                &key,
                join,
                ServerIncarnation::from_u64(1).unwrap(),
                Duration::from_secs(2),
            ),
        );
        let (client_added, server_added) = tokio::join!(
            client.add_lane(RuntimeLane::from_authenticated(lane, client_lane.unwrap())),
            server.add_lane(RuntimeLane::from_authenticated(lane, server_lane.unwrap())),
        );
        client_added.unwrap();
        server_added.unwrap();

        let first = LaneId::new(1).unwrap();
        let (client_failed, server_failed) =
            tokio::join!(client.fail_lane(first), server.fail_lane(first));
        client_failed.unwrap();
        server_failed.unwrap();

        let mut outbound = client.open_stream(TrafficClass::Bulk).await.unwrap();
        let mut inbound = server.accept_stream().await.unwrap();
        let payload = b"dynamically advertised encrypted provider".repeat(2048);
        let expected = payload.clone();
        let send = async {
            outbound.write_all(&payload).await.unwrap();
            outbound.shutdown().await.unwrap();
        };
        let receive = async {
            let mut bytes = Vec::new();
            inbound.read_to_end(&mut bytes).await.unwrap();
            bytes
        };
        let ((), received) = tokio::join!(send, receive);
        assert_eq!(received, expected);
        assert!(client
            .statistics()
            .await
            .unwrap()
            .lanes
            .iter()
            .find(|snapshot| snapshot.id == lane.id)
            .is_some_and(|snapshot| snapshot.bytes_scheduled > 0));

        let response = b"topology accepted".repeat(64);
        let expected = response.clone();
        let send = async {
            inbound.write_all(&response).await.unwrap();
            inbound.shutdown().await.unwrap();
        };
        let receive = async {
            let mut bytes = Vec::new();
            outbound.read_to_end(&mut bytes).await.unwrap();
            bytes
        };
        let ((), received) = tokio::join!(send, receive);
        assert_eq!(received, expected);

        let (client_result, server_result) = tokio::join!(client.shutdown(), server.shutdown());
        client_result.unwrap();
        server_result.unwrap();
    }
}
