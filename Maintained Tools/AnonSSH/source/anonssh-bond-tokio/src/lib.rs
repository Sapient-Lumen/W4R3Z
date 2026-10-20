#![forbid(unsafe_code)]

mod controlled_test;
mod fuzz;
mod handshake;
mod provider;
mod record;
mod runtime;
mod self_test;
mod session;
mod topology_test;

pub use controlled_test::{controlled_goodput_self_test, ControlledGoodputReport};
pub use fuzz::{
    embedded_transport_fuzz_test, transport_fuzz_test, FuzzCounts, TransportFuzzError,
    TransportFuzzReport, DEFAULT_TRANSPORT_FUZZ_CASES, TRANSPORT_FUZZ_SEED,
};
pub use handshake::{
    authenticate_client_lane, authenticate_server_lane, authenticate_server_lane_unbound,
    authenticate_server_lane_unbound_with_incarnation, authenticate_server_lane_with_incarnation,
    fresh_session_id, prepare_server_lane, AuthenticatedLane, BondProtocolVersion,
    BondProtocolVersions, BondSessionKey, LaneHandshakeError, LaneJoin, LaneJoinRegistry,
    PreparedClientLane, PreparedServerLane, ServerIncarnation,
};
pub use provider::{
    AppliedTopology, BondDialer, BondListener, BondProviderConfig, BondProviderError, BoxLaneIo,
    DialProviderSet, LaneAcceptor, LaneDialProvider, LaneIo, LaneListenProvider, ListenProviderSet,
    LoopbackTcpProvider, ProviderFuture, ProviderLane, ProviderPhase, ProviderPolicy,
    ProviderProgress,
};
pub use record::RecordError;
pub use runtime::{
    BondRuntime, BondRuntimeConfig, BondRuntimeControl, BondRuntimeError, BondRuntimeStats,
    LaneReceiveStats, ReceivedData, RuntimeEvent, RuntimeLane,
};
pub use self_test::{
    embedded_runtime_self_test, protocol_compatibility_self_test, BondRuntimeSelfTestReport,
    ProtocolCompatibilityReport,
};
pub use session::{
    concurrent_progress_self_test, BondSession, BondSessionControl, BondedStream,
    ConcurrentProgressReport, SessionRole,
};
pub use topology_test::{dynamic_topology_self_test, DynamicTopologyReport};
