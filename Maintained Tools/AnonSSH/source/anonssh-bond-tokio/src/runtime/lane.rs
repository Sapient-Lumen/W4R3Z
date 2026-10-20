use std::time::Duration;

use anonssh_bond::{Frame, FrameFlags, FrameKind, LaneConfig, LaneId};
use tokio::io::{AsyncRead, AsyncWrite, AsyncWriteExt};
use tokio::sync::mpsc;
use tokio::task::JoinHandle;
use tokio::time::timeout;

use crate::handshake::{AuthenticatedLane, BondProtocolVersion, ServerIncarnation};
use crate::record::{LaneRecordKeys, RecordOpener};

use super::{BondRuntimeError, Event, LaneQueueCapacities};

pub(super) trait LaneIo: AsyncRead + AsyncWrite + Send + Unpin + 'static {}
impl<T> LaneIo for T where T: AsyncRead + AsyncWrite + Send + Unpin + 'static {}

pub struct RuntimeLane {
    pub config: LaneConfig,
    pub(super) protocol_version: BondProtocolVersion,
    pub(super) server_incarnation: Option<ServerIncarnation>,
    pub(super) io: Box<dyn LaneIo>,
    pub(super) record_keys: LaneRecordKeys,
}

impl RuntimeLane {
    pub fn from_authenticated<T>(config: LaneConfig, lane: AuthenticatedLane<T>) -> Self
    where
        T: AsyncRead + AsyncWrite + Send + Unpin + 'static,
    {
        let server_incarnation = lane
            .server_incarnation()
            .expect("authenticated lane has a valid server incarnation");
        let (io, record_keys, protocol_version) = lane.into_parts();
        Self {
            config,
            protocol_version,
            server_incarnation,
            io: Box::new(io),
            record_keys,
        }
    }

    pub(crate) fn new_for_test<T>(
        config: LaneConfig,
        io: T,
        send_key: [u8; 32],
        receive_key: [u8; 32],
    ) -> Self
    where
        T: AsyncRead + AsyncWrite + Send + Unpin + 'static,
    {
        Self {
            config,
            protocol_version: BondProtocolVersion::V6,
            server_incarnation: Some(ServerIncarnation::from_u64(1).unwrap()),
            io: Box::new(io),
            record_keys: LaneRecordKeys::new(send_key, receive_key),
        }
    }

    #[cfg(test)]
    pub(crate) fn with_protocol_version_for_test(
        mut self,
        protocol_version: BondProtocolVersion,
    ) -> Self {
        self.protocol_version = protocol_version;
        self.server_incarnation = (protocol_version >= BondProtocolVersion::V5)
            .then(|| ServerIncarnation::from_u64(1).unwrap());
        self
    }

    #[cfg(test)]
    pub(crate) fn with_server_incarnation_for_test(mut self, incarnation: u64) -> Self {
        self.server_incarnation = Some(ServerIncarnation::from_u64(incarnation).unwrap());
        self
    }
}

pub(super) struct LaneHandle {
    pub(super) generation: u64,
    latency_sensitive_outbound: mpsc::Sender<Frame>,
    bulk_outbound: mpsc::Sender<Frame>,
    reader: JoinHandle<()>,
    writer: JoinHandle<()>,
}

impl LaneHandle {
    pub(super) fn try_send(
        &self,
        frame: Frame,
        latency_sensitive: bool,
    ) -> Result<(), mpsc::error::TrySendError<Frame>> {
        if latency_sensitive {
            self.latency_sensitive_outbound.try_send(frame)
        } else {
            self.bulk_outbound.try_send(frame)
        }
    }
}

impl Drop for LaneHandle {
    fn drop(&mut self) {
        self.reader.abort();
        self.writer.abort();
    }
}

pub(super) fn spawn_lane(
    lane_id: LaneId,
    generation: u64,
    io: Box<dyn LaneIo>,
    record_keys: LaneRecordKeys,
    event_tx: mpsc::Sender<Event>,
    queue_capacities: LaneQueueCapacities,
    write_timeout: Duration,
) -> LaneHandle {
    let (mut reader, mut writer) = tokio::io::split(io);
    let (mut sealer, mut opener) = record_keys.into_records();
    let (latency_sensitive_outbound, mut latency_sensitive_rx) =
        mpsc::channel::<Frame>(queue_capacities.latency_sensitive);
    let (bulk_outbound, mut bulk_rx) = mpsc::channel::<Frame>(queue_capacities.bulk);
    let reader_events = event_tx.clone();
    let reader = tokio::spawn(async move {
        loop {
            match read_frame(&mut reader, &mut opener).await {
                Ok(frame) => {
                    if reader_events
                        .send(Event::Inbound {
                            lane_id,
                            generation,
                            frame,
                        })
                        .await
                        .is_err()
                    {
                        return;
                    }
                }
                Err(_) => {
                    let _ = reader_events
                        .send(Event::LaneClosed {
                            lane_id,
                            generation,
                        })
                        .await;
                    return;
                }
            }
        }
    });
    let writer = tokio::spawn(async move {
        let mut record = Vec::new();
        while let Some(frame) = next_outbound(&mut latency_sensitive_rx, &mut bulk_rx).await {
            let ping_token = (frame.header.kind == FrameKind::Ping).then_some(frame.header.offset);
            let session_close_ack = (frame.header.kind == FrameKind::SessionClose)
                .then_some(frame.header.flags.contains(FrameFlags::ACKNOWLEDGEMENT));
            if sealer.seal_frame_into(&frame, &mut record).is_err() {
                break;
            }
            if !matches!(
                timeout(write_timeout, writer.write_all(&record)).await,
                Ok(Ok(()))
            ) {
                break;
            }
            if let Some(token) = ping_token {
                if event_tx
                    .send(Event::PingWritten {
                        lane_id,
                        generation,
                        token,
                    })
                    .await
                    .is_err()
                {
                    return;
                }
            }
            if let Some(acknowledgement) = session_close_ack {
                if event_tx
                    .send(Event::SessionCloseWritten {
                        lane_id,
                        generation,
                        acknowledgement,
                    })
                    .await
                    .is_err()
                {
                    return;
                }
            }
        }
        let _ = event_tx
            .send(Event::LaneClosed {
                lane_id,
                generation,
            })
            .await;
    });
    LaneHandle {
        generation,
        latency_sensitive_outbound,
        bulk_outbound,
        reader,
        writer,
    }
}

async fn next_outbound(
    latency_sensitive: &mut mpsc::Receiver<Frame>,
    bulk: &mut mpsc::Receiver<Frame>,
) -> Option<Frame> {
    loop {
        let latency_sensitive_open =
            !latency_sensitive.is_closed() || !latency_sensitive.is_empty();
        tokio::select! {
            biased;
            frame = latency_sensitive.recv(), if latency_sensitive_open => {
                if frame.is_some() {
                    return frame;
                }
            }
            frame = bulk.recv() => return frame,
        }
    }
}

async fn read_frame<R>(reader: &mut R, opener: &mut RecordOpener) -> Result<Frame, BondRuntimeError>
where
    R: AsyncRead + Unpin,
{
    let plaintext = opener.open(reader).await?;
    let plaintext_len = plaintext.len();
    let (frame, consumed) = Frame::decode_owned(plaintext)?;
    if consumed != plaintext_len {
        return Err(BondRuntimeError::TrailingRecordData);
    }
    Ok(frame)
}

#[cfg(test)]
mod tests {
    use anonssh_bond::{Frame, FrameFlags, FrameKind};
    use bytes::Bytes;
    use tokio::sync::mpsc;

    use super::next_outbound;

    fn frame(kind: FrameKind, offset: u64) -> Frame {
        Frame::new(
            kind,
            FrameFlags::NONE,
            1,
            1,
            offset,
            Bytes::from_static(b"payload"),
        )
        .unwrap()
    }

    #[tokio::test]
    async fn latency_sensitive_frames_precede_queued_bulk() {
        let (latency_tx, mut latency_rx) = mpsc::channel(2);
        let (bulk_tx, mut bulk_rx) = mpsc::channel(2);
        bulk_tx.try_send(frame(FrameKind::Data, 0)).unwrap();
        bulk_tx.try_send(frame(FrameKind::Data, 7)).unwrap();
        latency_tx
            .try_send(frame(FrameKind::Acknowledgement, 14))
            .unwrap();

        assert_eq!(
            next_outbound(&mut latency_rx, &mut bulk_rx)
                .await
                .unwrap()
                .header
                .kind,
            FrameKind::Acknowledgement
        );
        assert_eq!(
            next_outbound(&mut latency_rx, &mut bulk_rx)
                .await
                .unwrap()
                .header
                .offset,
            0
        );
        assert_eq!(
            next_outbound(&mut latency_rx, &mut bulk_rx)
                .await
                .unwrap()
                .header
                .offset,
            7
        );
    }
}
