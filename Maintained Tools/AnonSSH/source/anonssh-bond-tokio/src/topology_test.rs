use std::time::Duration;

use anonssh_bond::{
    EndpointDescriptor, EndpointProvider, FailureDomain, LaneConfig, LaneId, SchedulerConfig,
    SenderConfig, StreamId, TopologyAction, TopologyAdvertisement, TopologyPolicy, TrafficClass,
};
use sha2::{Digest, Sha256};
use tokio::net::{TcpListener, TcpStream};

use crate::{
    authenticate_client_lane, authenticate_server_lane_with_incarnation, BondRuntime,
    BondRuntimeConfig, BondRuntimeError, BondSessionKey, LaneJoin, RuntimeEvent, RuntimeLane,
    ServerIncarnation,
};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DynamicTopologyReport {
    pub generation: u64,
    pub provider: &'static str,
    pub added_lane: u32,
    pub payload_bytes: usize,
    pub payload_sha256: String,
    pub denied_policy_rejected: bool,
    pub denied_domain_rejected: bool,
    pub denied_action_rejected: bool,
    pub replay_rejected: bool,
}

pub async fn dynamic_topology_self_test() -> Result<DynamicTopologyReport, BondRuntimeError> {
    let session_id = 0x4142_5054;
    let first = lane(1, 1, 5)?;
    let added = lane(2, 2, 15)?;
    let config = runtime_config(session_id);
    let (client_io, server_io) = tokio::io::duplex(256 * 1024);
    let client = BondRuntime::spawn(
        config,
        vec![RuntimeLane::new_for_test(
            first, client_io, [1; 32], [2; 32],
        )],
    )?;
    let mut server = BondRuntime::spawn(
        config,
        vec![RuntimeLane::new_for_test(
            first, server_io, [2; 32], [1; 32],
        )],
    )?;

    let listener = TcpListener::bind("127.0.0.1:0").await.map_err(io_error)?;
    let endpoint = format!("tcp://{}", listener.local_addr().map_err(io_error)?);
    let advertisement = TopologyAdvertisement::new(
        1,
        vec![EndpointDescriptor::new(
            added.id,
            added.failure_domain,
            EndpointProvider::Tcp,
            TopologyAction::Add,
            endpoint,
        )?],
    )?;
    client.advertise_topology(advertisement.clone()).await?;
    let received = match tokio::time::timeout(Duration::from_secs(2), server.receive_event())
        .await
        .map_err(|_| test_error("dynamic topology announcement timed out"))?
        .ok_or(BondRuntimeError::Stopped)?
    {
        RuntimeEvent::TopologyAdvertised(advertisement) => advertisement,
        _ => return Err(test_error("runtime emitted the wrong topology event")),
    };
    let denied = TopologyPolicy::new(
        1,
        8,
        [EndpointProvider::I2p],
        [added.failure_domain],
        [TopologyAction::Add],
    )?;
    let denied_policy_rejected = denied.validate(&received).is_err();
    if !denied_policy_rejected {
        return Err(test_error(
            "dynamic topology bypassed denied-provider policy",
        ));
    }
    let denied_domain_rejected = TopologyPolicy::new(
        1,
        8,
        [EndpointProvider::Tcp],
        [first.failure_domain],
        [TopologyAction::Add],
    )?
    .validate(&received)
    .is_err();
    if !denied_domain_rejected {
        return Err(test_error("dynamic topology bypassed denied-domain policy"));
    }
    let denied_action_rejected = TopologyPolicy::new(
        1,
        8,
        [EndpointProvider::Tcp],
        [added.failure_domain],
        [TopologyAction::Replace],
    )?
    .validate(&received)
    .is_err();
    if !denied_action_rejected {
        return Err(test_error("dynamic topology bypassed denied-action policy"));
    }
    TopologyPolicy::new(
        1,
        8,
        [EndpointProvider::Tcp],
        [added.failure_domain],
        [TopologyAction::Add],
    )?
    .validate(&received)?;
    let replay_rejected = client.advertise_topology(advertisement).await.is_err();
    if !replay_rejected {
        return Err(test_error(
            "dynamic topology accepted a replayed generation",
        ));
    }

    let (client_declared, server_declared) =
        tokio::join!(client.declare_lane(added), server.declare_lane(added));
    client_declared?;
    server_declared?;
    let address: std::net::SocketAddr = received.descriptors[0]
        .endpoint
        .strip_prefix("tcp://")
        .ok_or_else(|| test_error("dynamic TCP endpoint lost its scheme"))?
        .parse()
        .map_err(|_| test_error("dynamic TCP endpoint is invalid"))?;
    let (connected, accepted) = tokio::join!(TcpStream::connect(address), listener.accept());
    let client_io = connected.map_err(io_error)?;
    let (server_io, _) = accepted.map_err(io_error)?;
    let key = BondSessionKey::new([0x51; 32]);
    let join = LaneJoin::new(session_id, added.id, added.failure_domain)
        .map_err(|error| test_error(error.to_string()))?;
    let server_incarnation =
        ServerIncarnation::from_u64(1).map_err(|error| test_error(error.to_string()))?;
    let (client_lane, server_lane) = tokio::join!(
        authenticate_client_lane(client_io, &key, join, Duration::from_secs(2)),
        authenticate_server_lane_with_incarnation(
            server_io,
            &key,
            join,
            server_incarnation,
            Duration::from_secs(2),
        ),
    );
    let client_lane = client_lane.map_err(|error| test_error(error.to_string()))?;
    let server_lane = server_lane.map_err(|error| test_error(error.to_string()))?;
    let (client_added, server_added) = tokio::join!(
        client.add_lane(RuntimeLane::from_authenticated(added, client_lane)),
        server.add_lane(RuntimeLane::from_authenticated(added, server_lane)),
    );
    client_added?;
    server_added?;
    let (client_failed, server_failed) =
        tokio::join!(client.fail_lane(first.id), server.fail_lane(first.id));
    client_failed?;
    server_failed?;

    let payload: Vec<u8> = (0..128 * 1024)
        .map(|index| ((index * 31 + 17) % 251) as u8)
        .collect();
    let stream_id = StreamId::new(1)?;
    client
        .send(stream_id, TrafficClass::Bulk, payload.clone())
        .await?;
    let mut received_payload = Vec::with_capacity(payload.len());
    while received_payload.len() < payload.len() {
        let data = tokio::time::timeout(Duration::from_secs(2), server.receive())
            .await
            .map_err(|_| test_error("dynamic topology transfer timed out"))?
            .ok_or(BondRuntimeError::Stopped)?;
        if data.stream_id != stream_id {
            return Err(test_error("dynamic topology transfer changed stream ID"));
        }
        received_payload.extend_from_slice(&data.bytes);
    }
    if received_payload != payload {
        return Err(test_error("dynamic topology transfer payload mismatch"));
    }
    let stats = client.statistics().await?;
    if !stats
        .lanes
        .iter()
        .find(|snapshot| snapshot.id == added.id)
        .is_some_and(|snapshot| snapshot.active && snapshot.bytes_scheduled > 0)
    {
        return Err(test_error("advertised lane did not carry payload bytes"));
    }
    client.shutdown().await?;
    server.shutdown().await?;

    Ok(DynamicTopologyReport {
        generation: received.generation,
        provider: "tcp",
        added_lane: added.id.get(),
        payload_bytes: payload.len(),
        payload_sha256: format!("{:x}", Sha256::digest(&payload)),
        denied_policy_rejected,
        denied_domain_rejected,
        denied_action_rejected,
        replay_rejected,
    })
}

fn runtime_config(session_id: u64) -> BondRuntimeConfig {
    BondRuntimeConfig {
        session_id,
        scheduler: SchedulerConfig::default(),
        sender: SenderConfig {
            max_chunk_payload: 4 * 1024,
            bulk_chunk: anonssh_bond::BulkChunkConfig::fixed(4 * 1024),
            max_unacknowledged_bytes: 512 * 1024,
            max_unacknowledged_chunks: 256,
            redundant_realtime: false,
        },
        max_reorder_bytes_per_stream: 512 * 1024,
        max_receive_streams: 4,
        stream_receive_window: 512 * 1024,
        max_ack_ranges: 8,
        require_stream_open: false,
        retransmit_after: Duration::from_secs(1),
        retransmit_scan_interval: Duration::from_millis(10),
    }
}

fn lane(id: u32, failure_domain: u64, rtt_ms: u64) -> Result<LaneConfig, BondRuntimeError> {
    Ok(LaneConfig::new(
        LaneId::new(id)?,
        FailureDomain::new(failure_domain)?,
        Duration::from_millis(rtt_ms),
        100_000_000,
    )?)
}

fn io_error(error: std::io::Error) -> BondRuntimeError {
    BondRuntimeError::LaneIo(error.to_string())
}

fn test_error(message: impl Into<String>) -> BondRuntimeError {
    BondRuntimeError::LaneIo(message.into())
}

#[cfg(test)]
mod tests {
    #[tokio::test]
    async fn adds_an_unknown_provider_from_an_authenticated_advertisement() {
        let report = super::dynamic_topology_self_test().await.unwrap();
        assert_eq!(report.provider, "tcp");
        assert!(report.denied_policy_rejected);
        assert!(report.denied_domain_rejected);
        assert!(report.denied_action_rejected);
        assert!(report.replay_rejected);
        assert!(report.payload_bytes > 0);
    }
}
