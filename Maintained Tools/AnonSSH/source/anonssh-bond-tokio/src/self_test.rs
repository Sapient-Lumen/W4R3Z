use std::time::Duration;

use anonssh_bond::{
    FailureDomain, LaneConfig, LaneId, SchedulerConfig, SenderConfig, StreamId, TrafficClass,
};
use sha2::{Digest, Sha256};
use tokio::io::AsyncWriteExt;

use crate::handshake::{
    authenticate_client_lane, authenticate_client_lane_with_nonce, authenticate_server_lane,
    authenticate_server_lane_with_incarnation, authenticate_server_lane_with_nonce,
    client_version_mask, finish_server_lane_with_nonce, fresh_server_nonce, prepare_server_lane,
    AuthenticatedLane, BondProtocolVersion, BondProtocolVersions, BondSessionKey,
    LaneHandshakeError, LaneJoin, LaneJoinRegistry, PreparedClientLane, ServerIncarnation,
};
use crate::runtime::{BondRuntime, BondRuntimeConfig, BondRuntimeError, RuntimeLane};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BondRuntimeSelfTestReport {
    pub bulk_payload_bytes: usize,
    pub realtime_payload_bytes: usize,
    pub post_failure_payload_bytes: usize,
    pub bulk_lanes_used: usize,
    pub protected_realtime_lane: u32,
    pub failed_lane: u32,
    pub payload_sha256: String,
    pub authenticated_lanes: usize,
    pub protocol_version: u8,
    pub key_establishment: &'static str,
    pub record_protection: &'static str,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ProtocolCompatibilityReport {
    pub current_version: u8,
    pub new_client_v5_server_version: u8,
    pub v5_client_new_server_version: u8,
    pub new_client_v4_server_version: u8,
    pub v4_client_new_server_version: u8,
    pub new_client_v3_server_version: u8,
    pub v3_client_new_server_version: u8,
    pub new_client_v2_server_version: u8,
    pub v2_client_new_server_version: u8,
    pub new_client_legacy_server_version: u8,
    pub legacy_client_new_server_version: u8,
    pub payload_bytes_per_case: usize,
    pub payload_sha256: String,
    pub no_common_rejected: bool,
    pub authenticated_downgrade_rejected: bool,
    pub legacy_handshake_magic: &'static str,
    pub legacy_record_magic: &'static str,
}

pub async fn protocol_compatibility_self_test(
) -> Result<ProtocolCompatibilityReport, BondRuntimeError> {
    let config = lane(1, 20, 20)?;
    let payload = (0..128 * 1024)
        .map(|index| ((index * 17 + 31) % 251) as u8)
        .collect::<Vec<_>>();

    let current_version = transfer_current_pair(0x4142_5002, config, &payload).await?;
    let new_client_v5_server_version = transfer_version_pair(
        0x4142_5009,
        config,
        &payload,
        BondProtocolVersions::CURRENT,
        BondProtocolVersions::V5_COMPATIBLE,
    )
    .await?;
    let v5_client_new_server_version = transfer_version_pair(
        0x4142_500a,
        config,
        &payload,
        BondProtocolVersions::V5_COMPATIBLE,
        BondProtocolVersions::CURRENT,
    )
    .await?;
    let new_client_v4_server_version = transfer_version_pair(
        0x4142_5007,
        config,
        &payload,
        BondProtocolVersions::CURRENT,
        BondProtocolVersions::V4_COMPATIBLE,
    )
    .await?;
    let v4_client_new_server_version = transfer_version_pair(
        0x4142_5008,
        config,
        &payload,
        BondProtocolVersions::V4_COMPATIBLE,
        BondProtocolVersions::CURRENT,
    )
    .await?;
    let new_client_v3_server_version = transfer_version_pair(
        0x4142_5005,
        config,
        &payload,
        BondProtocolVersions::CURRENT,
        BondProtocolVersions::V3_COMPATIBLE,
    )
    .await?;
    let v3_client_new_server_version = transfer_version_pair(
        0x4142_5006,
        config,
        &payload,
        BondProtocolVersions::V3_COMPATIBLE,
        BondProtocolVersions::CURRENT,
    )
    .await?;
    let new_client_v2_server_version = transfer_version_pair(
        0x4142_5003,
        config,
        &payload,
        BondProtocolVersions::CURRENT,
        BondProtocolVersions::V2_COMPATIBLE,
    )
    .await?;
    let v2_client_new_server_version = transfer_version_pair(
        0x4142_5004,
        config,
        &payload,
        BondProtocolVersions::V2_COMPATIBLE,
        BondProtocolVersions::CURRENT,
    )
    .await?;
    let new_client_legacy_server_version =
        transfer_new_client_legacy_server(0x4142_5101, config, &payload).await?;
    let legacy_client_new_server_version =
        transfer_legacy_client_new_server(0x4142_5201, config, &payload).await?;
    let no_common_rejected = no_common_version_is_rejected(0x4142_5301, config).await?;
    let authenticated_downgrade_rejected =
        authenticated_downgrade_is_rejected(0x4142_5401, config).await?;

    if current_version != BondProtocolVersion::V6
        || new_client_v5_server_version != BondProtocolVersion::V5
        || v5_client_new_server_version != BondProtocolVersion::V5
        || new_client_v4_server_version != BondProtocolVersion::V4
        || v4_client_new_server_version != BondProtocolVersion::V4
        || new_client_v3_server_version != BondProtocolVersion::V3
        || v3_client_new_server_version != BondProtocolVersion::V3
        || new_client_v2_server_version != BondProtocolVersion::V2
        || v2_client_new_server_version != BondProtocolVersion::V2
        || new_client_legacy_server_version != BondProtocolVersion::V1
        || legacy_client_new_server_version != BondProtocolVersion::V1
        || !no_common_rejected
        || !authenticated_downgrade_rejected
    {
        return Err(BondRuntimeError::LaneIo(
            "bond protocol compatibility matrix did not satisfy its contract".to_owned(),
        ));
    }

    Ok(ProtocolCompatibilityReport {
        current_version: current_version.get(),
        new_client_v5_server_version: new_client_v5_server_version.get(),
        v5_client_new_server_version: v5_client_new_server_version.get(),
        new_client_v4_server_version: new_client_v4_server_version.get(),
        v4_client_new_server_version: v4_client_new_server_version.get(),
        new_client_v3_server_version: new_client_v3_server_version.get(),
        v3_client_new_server_version: v3_client_new_server_version.get(),
        new_client_v2_server_version: new_client_v2_server_version.get(),
        v2_client_new_server_version: v2_client_new_server_version.get(),
        new_client_legacy_server_version: new_client_legacy_server_version.get(),
        legacy_client_new_server_version: legacy_client_new_server_version.get(),
        payload_bytes_per_case: payload.len(),
        payload_sha256: format!("{:x}", Sha256::digest(&payload)),
        no_common_rejected,
        authenticated_downgrade_rejected,
        legacy_handshake_magic: "ABJ1/ABA1",
        legacy_record_magic: "ABR1",
    })
}

async fn transfer_current_pair(
    session_id: u64,
    config: LaneConfig,
    payload: &[u8],
) -> Result<BondProtocolVersion, BondRuntimeError> {
    transfer_version_pair(
        session_id,
        config,
        payload,
        BondProtocolVersions::CURRENT,
        BondProtocolVersions::CURRENT,
    )
    .await
}

async fn transfer_version_pair(
    session_id: u64,
    config: LaneConfig,
    payload: &[u8],
    client_versions: BondProtocolVersions,
    server_versions: BondProtocolVersions,
) -> Result<BondProtocolVersion, BondRuntimeError> {
    let key = BondSessionKey::new([0x61; 32]);
    let join =
        LaneJoin::new(session_id, config.id, config.failure_domain).map_err(handshake_error)?;
    let prepared = PreparedClientLane::new_with_versions(&key, join, client_versions)
        .map_err(handshake_error)?;
    let initial_payload = prepared.initial_payload().to_vec();
    let (mut client_io, server_io) = loopback_pair().await?;
    let client = async {
        client_io
            .write_all(&initial_payload)
            .await
            .map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
        prepared
            .finish(client_io, &key, Duration::from_secs(1))
            .await
            .map_err(handshake_error)
    };
    let server = async {
        let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1))
            .await
            .map_err(handshake_error)?;
        prepared
            .finish_with_versions(&key, server_versions, Duration::from_secs(1))
            .await
            .map_err(handshake_error)
    };
    let (client, server) = tokio::join!(client, server);
    transfer_authenticated_pair(session_id, config, client?, server?, payload).await
}

async fn transfer_new_client_legacy_server(
    session_id: u64,
    config: LaneConfig,
    payload: &[u8],
) -> Result<BondProtocolVersion, BondRuntimeError> {
    let key = BondSessionKey::new([0x62; 32]);
    let join =
        LaneJoin::new(session_id, config.id, config.failure_domain).map_err(handshake_error)?;
    let (client_io, server_io) = loopback_pair().await?;
    let (client, server) = tokio::join!(
        authenticate_client_lane(client_io, &key, join, Duration::from_secs(1)),
        authenticate_server_lane_with_nonce(
            server_io,
            &key,
            join,
            [0x91; 32],
            Duration::from_secs(1),
        ),
    );
    transfer_authenticated_pair(
        session_id,
        config,
        client.map_err(handshake_error)?,
        server.map_err(handshake_error)?,
        payload,
    )
    .await
}

async fn transfer_legacy_client_new_server(
    session_id: u64,
    config: LaneConfig,
    payload: &[u8],
) -> Result<BondProtocolVersion, BondRuntimeError> {
    let key = BondSessionKey::new([0x63; 32]);
    let join =
        LaneJoin::new(session_id, config.id, config.failure_domain).map_err(handshake_error)?;
    let (client_io, server_io) = loopback_pair().await?;
    let (client, server) = tokio::join!(
        authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join,
            [0x31; 32],
            Duration::from_secs(1),
        ),
        authenticate_server_lane(server_io, &key, join, Duration::from_secs(1)),
    );
    transfer_authenticated_pair(
        session_id,
        config,
        client.map_err(handshake_error)?,
        server.map_err(handshake_error)?,
        payload,
    )
    .await
}

async fn transfer_authenticated_pair(
    session_id: u64,
    config: LaneConfig,
    client_lane: AuthenticatedLane<tokio::net::TcpStream>,
    server_lane: AuthenticatedLane<tokio::net::TcpStream>,
    payload: &[u8],
) -> Result<BondProtocolVersion, BondRuntimeError> {
    let version = client_lane.protocol_version();
    if server_lane.protocol_version() != version {
        return Err(BondRuntimeError::LaneIo(
            "compatibility peers selected different protocol versions".to_owned(),
        ));
    }
    let runtime_config = compatibility_runtime_config(session_id);
    let client = BondRuntime::spawn(
        runtime_config,
        vec![RuntimeLane::from_authenticated(config, client_lane)],
    )?;
    let mut server = BondRuntime::spawn(
        runtime_config,
        vec![RuntimeLane::from_authenticated(config, server_lane)],
    )?;
    let stream_id = StreamId::new(1)?;
    client
        .send(stream_id, TrafficClass::Bulk, payload.to_vec())
        .await?;
    let received = receive_exact(&mut server, stream_id, payload.len()).await?;
    if received != payload {
        return Err(BondRuntimeError::LaneIo(
            "compatibility payload changed in transit".to_owned(),
        ));
    }
    wait_until_acknowledged(&client).await?;
    client.shutdown().await?;
    server.shutdown().await?;
    Ok(version)
}

async fn no_common_version_is_rejected(
    session_id: u64,
    config: LaneConfig,
) -> Result<bool, BondRuntimeError> {
    let key = BondSessionKey::new([0x64; 32]);
    let join =
        LaneJoin::new(session_id, config.id, config.failure_domain).map_err(handshake_error)?;
    let prepared = PreparedClientLane::new_with_versions(
        &key,
        join,
        BondProtocolVersions::only(BondProtocolVersion::V2),
    )
    .map_err(handshake_error)?;
    let hello = prepared.initial_payload().to_vec();
    let (mut client_io, server_io) = loopback_pair().await?;
    let client = async {
        client_io.write_all(&hello).await.map_err(|error| {
            LaneHandshakeError::Io(format!("compatibility write failed: {error}"))
        })?;
        prepared
            .finish(client_io, &key, Duration::from_secs(1))
            .await
    };
    let server = async {
        let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1)).await?;
        prepared
            .finish_with_versions(
                &key,
                BondProtocolVersions::only(BondProtocolVersion::V1),
                Duration::from_secs(1),
            )
            .await
    };
    let (client, server) = tokio::join!(client, server);
    Ok(matches!(
        client,
        Err(LaneHandshakeError::NoCommonProtocolVersion { .. })
    ) && matches!(
        server,
        Err(LaneHandshakeError::NoCommonProtocolVersion { .. })
    ))
}

async fn authenticated_downgrade_is_rejected(
    session_id: u64,
    config: LaneConfig,
) -> Result<bool, BondRuntimeError> {
    let key = BondSessionKey::new([0x65; 32]);
    let join =
        LaneJoin::new(session_id, config.id, config.failure_domain).map_err(handshake_error)?;
    let prepared = PreparedClientLane::new(&key, join).map_err(handshake_error)?;
    let hello = prepared.initial_payload().to_vec();
    let (mut client_io, server_io) = loopback_pair().await?;
    let client = async {
        client_io.write_all(&hello).await.map_err(|error| {
            LaneHandshakeError::Io(format!("compatibility write failed: {error}"))
        })?;
        prepared
            .finish(client_io, &key, Duration::from_secs(1))
            .await
    };
    let server = async {
        let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1)).await?;
        let client_mask = client_version_mask(&prepared.client_nonce())?;
        let (mut nonce, _) = fresh_server_nonce(
            client_mask,
            BondProtocolVersions::CURRENT,
            ServerIncarnation::from_u64(1)?,
        )?;
        nonce[16] = BondProtocolVersion::V1.get();
        finish_server_lane_with_nonce(prepared, &key, nonce, BondProtocolVersion::V1).await
    };
    let (client, server) = tokio::join!(client, server);
    Ok(matches!(client, Err(LaneHandshakeError::ProtocolDowngrade { .. })) && server.is_ok())
}

fn compatibility_runtime_config(session_id: u64) -> BondRuntimeConfig {
    BondRuntimeConfig {
        session_id,
        scheduler: SchedulerConfig::default(),
        sender: SenderConfig::default(),
        max_reorder_bytes_per_stream: 512 * 1024,
        max_receive_streams: 2,
        stream_receive_window: 512 * 1024,
        max_ack_ranges: 8,
        require_stream_open: false,
        retransmit_after: Duration::from_secs(2),
        retransmit_scan_interval: Duration::from_millis(25),
    }
}

pub async fn embedded_runtime_self_test() -> Result<BondRuntimeSelfTestReport, BondRuntimeError> {
    let session_id = 0x4142_5031;
    let configs = [lane(1, 5, 20)?, lane(2, 40, 12)?, lane(3, 70, 4)?];
    let key = BondSessionKey::new([0x5a; 32]);
    let server_incarnation = ServerIncarnation::from_u64(session_id).map_err(handshake_error)?;
    let mut registry = LaneJoinRegistry::new(
        session_id,
        configs
            .iter()
            .map(|config| (config.id, config.failure_domain)),
    )
    .map_err(handshake_error)?;
    let mut client_lanes = Vec::new();
    let mut server_lanes = Vec::new();
    for config in configs {
        let (client, server) = loopback_pair().await?;
        let join =
            LaneJoin::new(session_id, config.id, config.failure_domain).map_err(handshake_error)?;
        let client_auth = authenticate_client_lane(client, &key, join, Duration::from_secs(1));
        let server_auth = authenticate_server_lane_with_incarnation(
            server,
            &key,
            join,
            server_incarnation,
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client_auth, server_auth);
        let client = client.map_err(handshake_error)?;
        let server = server.map_err(handshake_error)?;
        registry.register(&server).map_err(handshake_error)?;
        client_lanes.push(RuntimeLane::from_authenticated(config, client));
        server_lanes.push(RuntimeLane::from_authenticated(config, server));
    }
    if !registry.is_complete() {
        return Err(BondRuntimeError::LaneIo(
            "authenticated lane registry is incomplete".to_owned(),
        ));
    }
    let runtime_config = BondRuntimeConfig {
        session_id,
        scheduler: SchedulerConfig::default(),
        sender: SenderConfig {
            max_chunk_payload: 16 * 1024,
            max_unacknowledged_bytes: 2 * 1024 * 1024,
            ..SenderConfig::default()
        },
        max_reorder_bytes_per_stream: 2 * 1024 * 1024,
        max_receive_streams: 8,
        stream_receive_window: 2 * 1024 * 1024,
        max_ack_ranges: 16,
        require_stream_open: false,
        retransmit_after: Duration::from_secs(5),
        retransmit_scan_interval: Duration::from_millis(100),
    };
    let client = BondRuntime::spawn(runtime_config, client_lanes)?;
    let mut server = BondRuntime::spawn(runtime_config, server_lanes)?;

    let bulk_stream = StreamId::new(1)?;
    let bulk: Vec<_> = (0..512 * 1024).map(|index| (index % 251) as u8).collect();
    client
        .send(bulk_stream, TrafficClass::Bulk, bulk.clone())
        .await?;
    let received_bulk = receive_exact(&mut server, bulk_stream, bulk.len()).await?;
    if Sha256::digest(&received_bulk) != Sha256::digest(&bulk) {
        return Err(BondRuntimeError::LaneIo(
            "runtime bulk transfer hash mismatch".to_owned(),
        ));
    }
    let bulk_stats = wait_until_acknowledged(&client).await?;
    let bulk_lanes_used = bulk_stats
        .lanes
        .iter()
        .filter(|lane| lane.id.get() != 1 && lane.bytes_scheduled > 0)
        .count();
    if bulk_lanes_used != 2
        || bulk_stats
            .lanes
            .iter()
            .any(|lane| lane.id.get() == 1 && lane.bytes_scheduled != 0)
    {
        return Err(BondRuntimeError::LaneIo(
            "runtime bulk transfer did not preserve the low-latency lane".to_owned(),
        ));
    }

    let protected_lane = bulk_stats
        .lanes
        .iter()
        .find(|lane| lane.reserved_for_low_latency)
        .ok_or(BondRuntimeError::NoLanes)?
        .id;
    let protected_before = bulk_stats
        .lanes
        .iter()
        .find(|lane| lane.id == protected_lane)
        .expect("protected lane exists")
        .bytes_scheduled;

    let realtime_stream = StreamId::new(2)?;
    let realtime = b"real-time control payload".repeat(64);
    client
        .send(realtime_stream, TrafficClass::Realtime, realtime.clone())
        .await?;
    let received_realtime = receive_exact(&mut server, realtime_stream, realtime.len()).await?;
    if received_realtime != realtime {
        return Err(BondRuntimeError::LaneIo(
            "runtime real-time transfer mismatch".to_owned(),
        ));
    }
    let realtime_stats = wait_until_acknowledged(&client).await?;
    let realtime_lane = realtime_stats
        .lanes
        .iter()
        .find(|lane| lane.id == protected_lane)
        .ok_or(BondRuntimeError::NoLanes)?;
    if realtime_lane.bytes_scheduled <= protected_before {
        return Err(BondRuntimeError::LaneIo(
            "runtime real-time transfer missed the protected lane".to_owned(),
        ));
    }

    let failed_lane = LaneId::new(2)?;
    client.fail_lane(failed_lane).await?;
    let post_failure_stream = StreamId::new(3)?;
    let post_failure: Vec<_> = (0..128 * 1024)
        .map(|index| (255 - (index % 251)) as u8)
        .collect();
    client
        .send(
            post_failure_stream,
            TrafficClass::Bulk,
            post_failure.clone(),
        )
        .await?;
    let received_after_failure =
        receive_exact(&mut server, post_failure_stream, post_failure.len()).await?;
    if received_after_failure != post_failure {
        return Err(BondRuntimeError::LaneIo(
            "runtime transfer failed after lane loss".to_owned(),
        ));
    }

    let payload_sha256 = format!("{:x}", Sha256::digest(&bulk));
    client.shutdown().await?;
    server.shutdown().await?;
    Ok(BondRuntimeSelfTestReport {
        bulk_payload_bytes: bulk.len(),
        realtime_payload_bytes: realtime.len(),
        post_failure_payload_bytes: post_failure.len(),
        bulk_lanes_used,
        protected_realtime_lane: protected_lane.get(),
        failed_lane: failed_lane.get(),
        payload_sha256,
        authenticated_lanes: configs.len(),
        protocol_version: BondProtocolVersion::V6.get(),
        key_establishment: "ML-KEM-768+PSK-HKDF-SHA256",
        record_protection: "ChaCha20-Poly1305",
    })
}

fn handshake_error(error: crate::handshake::LaneHandshakeError) -> BondRuntimeError {
    BondRuntimeError::LaneIo(error.to_string())
}

async fn loopback_pair() -> Result<(tokio::net::TcpStream, tokio::net::TcpStream), BondRuntimeError>
{
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0")
        .await
        .map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    let address = listener
        .local_addr()
        .map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    let (client, accepted) =
        tokio::join!(tokio::net::TcpStream::connect(address), listener.accept());
    let client = client.map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    let (server, _) = accepted.map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    client
        .set_nodelay(true)
        .map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    server
        .set_nodelay(true)
        .map_err(|error| BondRuntimeError::LaneIo(error.to_string()))?;
    Ok((client, server))
}

async fn receive_exact(
    runtime: &mut BondRuntime,
    stream_id: StreamId,
    length: usize,
) -> Result<Vec<u8>, BondRuntimeError> {
    let mut bytes = Vec::with_capacity(length);
    while bytes.len() < length {
        let received = tokio::time::timeout(Duration::from_secs(10), runtime.receive())
            .await
            .map_err(|_| BondRuntimeError::LaneIo("runtime receive timed out".to_owned()))?
            .ok_or(BondRuntimeError::Stopped)?;
        if received.stream_id != stream_id {
            return Err(BondRuntimeError::LaneIo(
                "runtime delivered an unexpected stream".to_owned(),
            ));
        }
        bytes.extend_from_slice(&received.bytes);
    }
    if bytes.len() != length {
        return Err(BondRuntimeError::LaneIo(
            "runtime delivered too many bytes".to_owned(),
        ));
    }
    Ok(bytes)
}

async fn wait_until_acknowledged(
    runtime: &BondRuntime,
) -> Result<crate::runtime::BondRuntimeStats, BondRuntimeError> {
    tokio::time::timeout(Duration::from_secs(10), async {
        loop {
            let stats = runtime.statistics().await?;
            if stats.unacknowledged_bytes == 0 {
                return Ok(stats);
            }
            tokio::time::sleep(Duration::from_millis(1)).await;
        }
    })
    .await
    .map_err(|_| BondRuntimeError::LaneIo("runtime acknowledgements timed out".to_owned()))?
}

fn lane(id: u32, rtt_ms: u64, rate_mbps: u64) -> Result<LaneConfig, BondRuntimeError> {
    Ok(LaneConfig::new(
        LaneId::new(id)?,
        FailureDomain::new(id as u64)?,
        Duration::from_millis(rtt_ms),
        rate_mbps * 1_000_000,
    )?)
}

#[cfg(test)]
mod tests {
    use super::{embedded_runtime_self_test, protocol_compatibility_self_test};

    #[tokio::test]
    async fn transfers_non_ssh_data_over_real_striped_lanes() {
        let report = embedded_runtime_self_test().await.unwrap();
        assert_eq!(report.bulk_lanes_used, 2);
        assert!(report.protected_realtime_lane > 0);
        assert_eq!(report.failed_lane, 2);
        assert_eq!(report.bulk_payload_bytes, 512 * 1024);
        assert_eq!(report.authenticated_lanes, 3);
        assert_eq!(report.protocol_version, 6);
    }

    #[tokio::test]
    async fn packaged_compatibility_matrix_transfers_exact_payloads() {
        let report = protocol_compatibility_self_test().await.unwrap();
        assert_eq!(report.current_version, 6);
        assert_eq!(report.new_client_v5_server_version, 5);
        assert_eq!(report.v5_client_new_server_version, 5);
        assert_eq!(report.new_client_v4_server_version, 4);
        assert_eq!(report.v4_client_new_server_version, 4);
        assert_eq!(report.new_client_v3_server_version, 3);
        assert_eq!(report.v3_client_new_server_version, 3);
        assert_eq!(report.new_client_v2_server_version, 2);
        assert_eq!(report.v2_client_new_server_version, 2);
        assert_eq!(report.new_client_legacy_server_version, 1);
        assert_eq!(report.legacy_client_new_server_version, 1);
        assert_eq!(report.payload_bytes_per_case, 128 * 1024);
        assert!(report.no_common_rejected);
        assert!(report.authenticated_downgrade_rejected);
    }
}
