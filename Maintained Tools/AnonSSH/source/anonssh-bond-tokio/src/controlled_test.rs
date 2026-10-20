use std::future::Future;
use std::io;
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::Duration;

use anonssh_bond::{
    BulkChunkConfig, FailureDomain, LaneConfig, LaneId, SchedulerConfig, SenderConfig, StreamId,
    TrafficClass,
};
use sha2::{Digest, Sha256};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt, ReadBuf};
use tokio::net::TcpStream;
use tokio::time::{Instant, Sleep};

use crate::{BondRuntime, BondRuntimeConfig, BondRuntimeError, RuntimeLane};

const SLOW_BYTES_PER_SECOND: u64 = 512 * 1024;
const FAST_BYTES_PER_SECOND: u64 = 1024 * 1024;
const BASELINE_BYTES: usize = 512 * 1024;
const BOND_BYTES: usize = 3 * 1024 * 1024;
const REALTIME_BYTES: usize = 2 * 1024;
const PACE_QUANTUM: usize = 32 * 1024;
const OPERATION_TIMEOUT: Duration = Duration::from_secs(30);
const REQUIRED_EFFICIENCY_BASIS_POINTS: u64 = 8_000;
const REQUIRED_ADAPTIVE_FIXED_BASIS_POINTS: u64 = 9_000;
const MAX_REALTIME_LATENCY: Duration = Duration::from_millis(250);

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ControlledGoodputReport {
    pub slow_baseline_bps: u64,
    pub fast_baseline_bps: u64,
    pub aggregate_baseline_bps: u64,
    pub fixed_chunk_goodput_bps: u64,
    pub bonded_goodput_bps: u64,
    pub efficiency_basis_points: u64,
    pub adaptive_vs_fixed_basis_points: u64,
    pub payload_bytes: usize,
    pub payload_sha256: String,
    pub bulk_lanes_used: usize,
    pub fixed_new_data_frames: u64,
    pub adaptive_new_data_frames: u64,
    pub adaptive_bulk_chunk_pressure_limit: usize,
    pub realtime_payload_bytes: usize,
    pub realtime_latency_micros: u64,
}

struct BondCaseReport {
    goodput_bps: u64,
    payload_sha256: String,
    bulk_lanes_used: usize,
    #[cfg(test)]
    bulk_lane_acknowledged_bytes: Vec<u64>,
    new_data_frames: u64,
    bulk_chunk_pressure_limit: usize,
    realtime_latency: Duration,
}

pub async fn controlled_goodput_self_test() -> Result<ControlledGoodputReport, BondRuntimeError> {
    let slow_baseline = measure_lane(SLOW_BYTES_PER_SECOND).await?;
    let fast_baseline = measure_lane(FAST_BYTES_PER_SECOND).await?;
    let aggregate_baseline = slow_baseline
        .checked_add(fast_baseline)
        .ok_or(BondRuntimeError::CounterOverflow)?;

    let fixed = measure_bond_case(0x4142_5043, BulkChunkConfig::fixed(PACE_QUANTUM)).await?;
    let adaptive = measure_bond_case(0x4142_5044, BulkChunkConfig::default()).await?;
    let efficiency_basis_points = ((adaptive.goodput_bps as u128) * 10_000
        / aggregate_baseline as u128)
        .min(u64::MAX as u128) as u64;
    if efficiency_basis_points < REQUIRED_EFFICIENCY_BASIS_POINTS {
        return Err(test_error(format!(
            "controlled bond efficiency was {}.{:02}%, below 80%",
            efficiency_basis_points / 100,
            efficiency_basis_points % 100
        )));
    }
    let adaptive_vs_fixed_basis_points = ((adaptive.goodput_bps as u128) * 10_000
        / fixed.goodput_bps as u128)
        .min(u64::MAX as u128) as u64;
    if adaptive_vs_fixed_basis_points < REQUIRED_ADAPTIVE_FIXED_BASIS_POINTS {
        return Err(test_error(format!(
            "adaptive chunk goodput was {}.{:02}% of the fixed baseline, below 90%",
            adaptive_vs_fixed_basis_points / 100,
            adaptive_vs_fixed_basis_points % 100
        )));
    }

    Ok(ControlledGoodputReport {
        slow_baseline_bps: slow_baseline,
        fast_baseline_bps: fast_baseline,
        aggregate_baseline_bps: aggregate_baseline,
        fixed_chunk_goodput_bps: fixed.goodput_bps,
        bonded_goodput_bps: adaptive.goodput_bps,
        efficiency_basis_points,
        adaptive_vs_fixed_basis_points,
        payload_bytes: BOND_BYTES,
        payload_sha256: adaptive.payload_sha256,
        bulk_lanes_used: adaptive.bulk_lanes_used,
        fixed_new_data_frames: fixed.new_data_frames,
        adaptive_new_data_frames: adaptive.new_data_frames,
        adaptive_bulk_chunk_pressure_limit: adaptive.bulk_chunk_pressure_limit,
        realtime_payload_bytes: REALTIME_BYTES,
        realtime_latency_micros: u64::try_from(adaptive.realtime_latency.as_micros())
            .unwrap_or(u64::MAX),
    })
}

async fn measure_bond_case(
    session_id: u64,
    bulk_chunk: BulkChunkConfig,
) -> Result<BondCaseReport, BondRuntimeError> {
    measure_bond_case_with_rates(
        session_id,
        bulk_chunk,
        &[SLOW_BYTES_PER_SECOND, FAST_BYTES_PER_SECOND],
        BOND_BYTES,
    )
    .await
}

async fn measure_bond_case_with_rates(
    session_id: u64,
    bulk_chunk: BulkChunkConfig,
    bulk_rates: &[u64],
    payload_bytes: usize,
) -> Result<BondCaseReport, BondRuntimeError> {
    if bulk_rates.is_empty() || payload_bytes == 0 {
        return Err(test_error(
            "controlled bond requires bulk lanes and a non-empty payload",
        ));
    }
    let realtime = lane(1, 1, 5, 100_000_000)?;
    let (realtime_client, realtime_server) = loopback_pair().await?;
    let mut client_lanes = vec![RuntimeLane::new_for_test(
        realtime,
        realtime_client,
        [1; 32],
        [2; 32],
    )];
    let mut server_lanes = vec![RuntimeLane::new_for_test(
        realtime,
        realtime_server,
        [2; 32],
        [1; 32],
    )];
    for (index, bytes_per_second) in bulk_rates.iter().copied().enumerate() {
        let lane_number = u32::try_from(index + 2)
            .map_err(|_| test_error("controlled lane count exceeds the lane ID space"))?;
        let key_index = index
            .checked_mul(2)
            .and_then(|value| value.checked_add(3))
            .ok_or_else(|| test_error("controlled test key overflow"))?;
        let send_key = u8::try_from(key_index)
            .map_err(|_| test_error("controlled lane count exceeds the test key space"))?;
        let receive_key = send_key
            .checked_add(1)
            .ok_or_else(|| test_error("controlled test key overflow"))?;
        let config = lane(
            lane_number,
            u64::from(lane_number),
            20,
            bytes_per_second
                .checked_mul(8)
                .ok_or_else(|| test_error("controlled lane rate overflow"))?,
        )?;
        let (client_io, server_io) = loopback_pair().await?;
        client_lanes.push(RuntimeLane::new_for_test(
            config,
            PacedStream::new(client_io, bytes_per_second)?,
            [send_key; 32],
            [receive_key; 32],
        ));
        server_lanes.push(RuntimeLane::new_for_test(
            config,
            server_io,
            [receive_key; 32],
            [send_key; 32],
        ));
    }
    let transfer_window = payload_bytes
        .checked_next_power_of_two()
        .ok_or_else(|| test_error("controlled payload window overflow"))?
        .max(4 * 1024 * 1024);
    let config = BondRuntimeConfig {
        session_id,
        scheduler: SchedulerConfig::default(),
        sender: SenderConfig {
            max_chunk_payload: PACE_QUANTUM,
            bulk_chunk,
            max_unacknowledged_bytes: transfer_window,
            max_unacknowledged_chunks: 1_024,
            redundant_realtime: false,
        },
        max_reorder_bytes_per_stream: transfer_window,
        max_receive_streams: 4,
        stream_receive_window: transfer_window,
        max_ack_ranges: 16,
        require_stream_open: false,
        retransmit_after: Duration::from_secs(10),
        retransmit_scan_interval: Duration::from_millis(100),
    };
    let client = BondRuntime::spawn(config, client_lanes)?;
    let mut server = BondRuntime::spawn(config, server_lanes)?;
    let payload: Vec<u8> = (0..payload_bytes)
        .map(|index| ((index * 67 + 29) % 251) as u8)
        .collect();
    let stream = StreamId::new(1)?;
    let realtime_stream = StreamId::new(2)?;
    let realtime_payload = vec![0x5c; REALTIME_BYTES];
    let started = Instant::now();
    client
        .send(stream, TrafficClass::Bulk, payload.clone())
        .await?;
    let realtime_started = Instant::now();
    client
        .send(
            realtime_stream,
            TrafficClass::Realtime,
            realtime_payload.clone(),
        )
        .await?;
    let (received, received_realtime, realtime_latency) = receive_bulk_and_realtime(
        &mut server,
        stream,
        payload.len(),
        realtime_stream,
        realtime_payload.len(),
        realtime_started,
    )
    .await?;
    let elapsed = started.elapsed();
    if Sha256::digest(&received) != Sha256::digest(&payload) {
        return Err(test_error("controlled bond payload hash mismatch"));
    }
    if received_realtime != realtime_payload {
        return Err(test_error("controlled real-time payload mismatch"));
    }
    if realtime_latency > MAX_REALTIME_LATENCY {
        return Err(test_error(format!(
            "controlled real-time latency was {} ms, above 250 ms",
            realtime_latency.as_millis()
        )));
    }
    let stats = wait_until_acknowledged(&client).await?;
    let bulk_lanes_used = stats
        .lanes
        .iter()
        .filter(|lane| !lane.reserved_for_low_latency && lane.bytes_scheduled > 0)
        .count();
    #[cfg(test)]
    let bulk_lane_acknowledged_bytes = stats
        .lanes
        .iter()
        .filter(|lane| !lane.reserved_for_low_latency)
        .map(|lane| lane.bytes_acknowledged)
        .collect::<Vec<_>>();
    let realtime_bytes = stats
        .lanes
        .iter()
        .find(|lane| lane.id == realtime.id)
        .ok_or(BondRuntimeError::NoLanes)?
        .bytes_scheduled;
    if bulk_lanes_used != bulk_rates.len() || realtime_bytes != realtime_payload.len() as u64 {
        return Err(test_error(
            "controlled traffic did not preserve the protected lane",
        ));
    }
    if stats.unacknowledged_bytes != 0 {
        return Err(test_error(
            "controlled bulk transfer retained unacknowledged bytes",
        ));
    }

    let bonded_goodput = bits_per_second(payload.len(), elapsed)?;
    let report = BondCaseReport {
        goodput_bps: bonded_goodput,
        payload_sha256: format!("{:x}", Sha256::digest(&payload)),
        bulk_lanes_used,
        #[cfg(test)]
        bulk_lane_acknowledged_bytes,
        new_data_frames: stats.new_data_frames,
        bulk_chunk_pressure_limit: stats.bulk_chunk_pressure_limit,
        realtime_latency,
    };
    client.shutdown().await?;
    server.shutdown().await?;
    Ok(report)
}

async fn measure_lane(bytes_per_second: u64) -> Result<u64, BondRuntimeError> {
    measure_lane_bytes(bytes_per_second, BASELINE_BYTES).await
}

async fn measure_lane_bytes(
    bytes_per_second: u64,
    payload_bytes: usize,
) -> Result<u64, BondRuntimeError> {
    let (sender, mut receiver) = loopback_pair().await?;
    let mut sender = PacedStream::new(sender, bytes_per_second)?;
    let payload = vec![0xa5; payload_bytes];
    let started = Instant::now();
    tokio::time::timeout(OPERATION_TIMEOUT, async {
        let write = async {
            sender.write_all(&payload).await?;
            sender.flush().await
        };
        let read = async {
            let mut received = vec![0_u8; payload.len()];
            receiver.read_exact(&mut received).await?;
            if received != payload {
                return Err(io::Error::other("controlled baseline payload mismatch"));
            }
            Ok(())
        };
        let (write, read) = tokio::join!(write, read);
        write?;
        read
    })
    .await
    .map_err(|_| test_error("controlled baseline transfer timed out"))?
    .map_err(|error| test_error(error.to_string()))?;
    bits_per_second(payload_bytes, started.elapsed())
}

async fn receive_bulk_and_realtime(
    runtime: &mut BondRuntime,
    bulk_stream: StreamId,
    bulk_expected: usize,
    realtime_stream: StreamId,
    realtime_expected: usize,
    realtime_started: Instant,
) -> Result<(Vec<u8>, Vec<u8>, Duration), BondRuntimeError> {
    tokio::time::timeout(OPERATION_TIMEOUT, async {
        let mut bulk = Vec::with_capacity(bulk_expected);
        let mut realtime = Vec::with_capacity(realtime_expected);
        let mut realtime_latency = None;
        while bulk.len() < bulk_expected || realtime.len() < realtime_expected {
            let received = runtime.receive().await.ok_or(BondRuntimeError::Stopped)?;
            if received.stream_id == bulk_stream {
                bulk.extend_from_slice(&received.bytes);
            } else if received.stream_id == realtime_stream {
                realtime.extend_from_slice(&received.bytes);
                if realtime.len() >= realtime_expected && realtime_latency.is_none() {
                    realtime_latency = Some(realtime_started.elapsed());
                }
            } else {
                return Err(test_error("controlled runtime delivered an unknown stream"));
            }
        }
        if bulk.len() != bulk_expected || realtime.len() != realtime_expected {
            return Err(test_error("controlled runtime delivered excess bytes"));
        }
        Ok((
            bulk,
            realtime,
            realtime_latency.ok_or_else(|| test_error("real-time stream was not delivered"))?,
        ))
    })
    .await
    .map_err(|_| test_error("controlled bond transfer timed out"))?
}

async fn wait_until_acknowledged(
    runtime: &BondRuntime,
) -> Result<crate::BondRuntimeStats, BondRuntimeError> {
    tokio::time::timeout(OPERATION_TIMEOUT, async {
        loop {
            let stats = runtime.statistics().await?;
            if stats.unacknowledged_bytes == 0 {
                return Ok(stats);
            }
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
    })
    .await
    .map_err(|_| test_error("controlled bond acknowledgements timed out"))?
}

async fn loopback_pair() -> Result<(TcpStream, TcpStream), BondRuntimeError> {
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0")
        .await
        .map_err(io_runtime_error)?;
    let address = listener.local_addr().map_err(io_runtime_error)?;
    let (client, accepted) = tokio::join!(TcpStream::connect(address), listener.accept());
    let client = client.map_err(io_runtime_error)?;
    let (server, _) = accepted.map_err(io_runtime_error)?;
    client.set_nodelay(true).map_err(io_runtime_error)?;
    server.set_nodelay(true).map_err(io_runtime_error)?;
    Ok((client, server))
}

fn lane(id: u32, domain: u64, rtt_ms: u64, rate_bps: u64) -> Result<LaneConfig, BondRuntimeError> {
    Ok(LaneConfig::new(
        LaneId::new(id)?,
        FailureDomain::new(domain)?,
        Duration::from_millis(rtt_ms),
        rate_bps,
    )?)
}

fn bits_per_second(bytes: usize, elapsed: Duration) -> Result<u64, BondRuntimeError> {
    let micros = elapsed.as_micros();
    if micros == 0 {
        return Err(test_error("controlled transfer elapsed time was zero"));
    }
    Ok(((bytes as u128) * 8 * 1_000_000 / micros).min(u64::MAX as u128) as u64)
}

fn io_runtime_error(error: io::Error) -> BondRuntimeError {
    BondRuntimeError::LaneIo(error.to_string())
}

fn test_error(message: impl Into<String>) -> BondRuntimeError {
    BondRuntimeError::LaneIo(message.into())
}

struct PacedStream<T> {
    inner: T,
    bytes_per_second: u64,
    delay: Option<Pin<Box<Sleep>>>,
    pending_allowance: usize,
    allowance: usize,
}

impl<T> PacedStream<T> {
    fn new(inner: T, bytes_per_second: u64) -> Result<Self, BondRuntimeError> {
        if bytes_per_second == 0 {
            return Err(test_error("controlled lane rate must be non-zero"));
        }
        Ok(Self {
            inner,
            bytes_per_second,
            delay: None,
            pending_allowance: 0,
            allowance: 0,
        })
    }

    fn poll_allowance(&mut self, cx: &mut Context<'_>, requested: usize) -> Poll<()> {
        if self.allowance > 0 || requested == 0 {
            return Poll::Ready(());
        }
        if self.delay.is_none() {
            self.pending_allowance = requested.min(PACE_QUANTUM);
            let nanos = (self.pending_allowance as u128)
                .saturating_mul(1_000_000_000)
                .div_ceil(self.bytes_per_second as u128)
                .min(u64::MAX as u128) as u64;
            self.delay = Some(Box::pin(tokio::time::sleep(Duration::from_nanos(nanos))));
        }
        let delay = self.delay.as_mut().expect("pace delay exists");
        match delay.as_mut().poll(cx) {
            Poll::Pending => Poll::Pending,
            Poll::Ready(()) => {
                self.allowance = self.pending_allowance;
                self.pending_allowance = 0;
                self.delay = None;
                Poll::Ready(())
            }
        }
    }
}

impl<T> AsyncRead for PacedStream<T>
where
    T: AsyncRead + Unpin,
{
    fn poll_read(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buffer: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        Pin::new(&mut self.get_mut().inner).poll_read(cx, buffer)
    }
}

impl<T> AsyncWrite for PacedStream<T>
where
    T: AsyncWrite + Unpin,
{
    fn poll_write(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buffer: &[u8],
    ) -> Poll<io::Result<usize>> {
        let this = self.get_mut();
        if this.poll_allowance(cx, buffer.len()).is_pending() {
            return Poll::Pending;
        }
        let limit = buffer.len().min(this.allowance);
        match Pin::new(&mut this.inner).poll_write(cx, &buffer[..limit]) {
            Poll::Ready(Ok(written)) => {
                this.allowance = this.allowance.saturating_sub(written);
                Poll::Ready(Ok(written))
            }
            result => result,
        }
    }

    fn poll_flush(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<io::Result<()>> {
        Pin::new(&mut self.get_mut().inner).poll_flush(cx)
    }

    fn poll_shutdown(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<io::Result<()>> {
        Pin::new(&mut self.get_mut().inner).poll_shutdown(cx)
    }
}

#[cfg(test)]
mod tests {
    use super::{
        controlled_goodput_self_test, measure_bond_case_with_rates, measure_lane_bytes,
        BulkChunkConfig,
    };

    const SIX_LANE_BASELINE_BYTES: usize = 256 * 1024;
    // The slowest lane needs several pacing epochs before the scheduler's
    // measured allocation reaches steady state. Keep this long enough that
    // executor jitter cannot dominate the aggregate-efficiency assertion.
    const SIX_LANE_BOND_BYTES: usize = 12 * 1024 * 1024;
    const SIX_LANE_BYTES_PER_SECOND: [u64; 6] = [
        256 * 1024,
        384 * 1024,
        512 * 1024,
        768 * 1024,
        1024 * 1024,
        1536 * 1024,
    ];

    #[tokio::test]
    async fn preserves_controlled_aggregate_capacity() {
        let report = controlled_goodput_self_test().await.unwrap();
        assert!(report.efficiency_basis_points >= 8_000);
        assert!(report.adaptive_vs_fixed_basis_points >= 9_000);
        assert_eq!(report.bulk_lanes_used, 2);
        assert!(report.adaptive_new_data_frames >= report.fixed_new_data_frames);
        assert!((16 * 1024..=64 * 1024).contains(&report.adaptive_bulk_chunk_pressure_limit));
        assert!(report.realtime_latency_micros < 250_000);
    }

    #[tokio::test]
    async fn six_asymmetric_lanes_preserve_aggregate_capacity() {
        let mut baselines = Vec::with_capacity(SIX_LANE_BYTES_PER_SECOND.len());
        for rate in SIX_LANE_BYTES_PER_SECOND {
            baselines.push(
                measure_lane_bytes(rate, SIX_LANE_BASELINE_BYTES)
                    .await
                    .unwrap(),
            );
        }
        let aggregate_baseline = baselines.iter().copied().sum::<u64>();
        let report = measure_bond_case_with_rates(
            0x4142_5045,
            BulkChunkConfig::default(),
            &SIX_LANE_BYTES_PER_SECOND,
            SIX_LANE_BOND_BYTES,
        )
        .await
        .unwrap();
        let efficiency_basis_points =
            ((report.goodput_bps as u128) * 10_000 / aggregate_baseline as u128) as u64;

        assert!(
            efficiency_basis_points >= 8_000,
            "six-lane efficiency was {}.{:02}%",
            efficiency_basis_points / 100,
            efficiency_basis_points % 100
        );
        assert_eq!(report.bulk_lanes_used, SIX_LANE_BYTES_PER_SECOND.len());
        assert_eq!(
            report.bulk_lane_acknowledged_bytes.len(),
            SIX_LANE_BYTES_PER_SECOND.len()
        );
        for (index, (&acknowledged, &baseline)) in report
            .bulk_lane_acknowledged_bytes
            .iter()
            .zip(&baselines)
            .enumerate()
        {
            let expected =
                (SIX_LANE_BOND_BYTES as u128) * (baseline as u128) / (aggregate_baseline as u128);
            assert!(
                (acknowledged as u128) * 10 >= expected * 6,
                "lane {} received {} bytes, below 60% of its capacity share {}",
                index + 1,
                acknowledged,
                expected
            );
        }
        assert!(
            report.bulk_lane_acknowledged_bytes[5] > report.bulk_lane_acknowledged_bytes[0] * 3,
            "six-lane allocation did not favor measured capacity"
        );
    }
}
