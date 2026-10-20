#![forbid(unsafe_code)]

mod capability;
mod control;
mod frame;
mod fuzz;
mod reassembly;
mod scaling;
mod scheduler;
mod self_test;
mod sender;
mod topology;

pub use capability::{
    CapabilityAdvertisement, CapabilityError, CapabilityFeatures, CapabilityIntersection,
    ProviderCapability, MAX_CAPABILITY_LANES, MAX_CAPABILITY_PROVIDERS,
};
pub use control::{
    AckRange, ControlError, SelectiveAcknowledgement, StreamOpen, StreamReset, MAX_ACK_RANGES,
};
pub use frame::{
    Frame, FrameDecodeError, FrameFlags, FrameHeader, FrameKind, ProtocolError, HEADER_LEN,
    MAX_FRAME_PAYLOAD,
};
pub use fuzz::{
    embedded_protocol_fuzz_test, protocol_fuzz_test, FuzzCounts, ProtocolFuzzError,
    ProtocolFuzzReport, DEFAULT_PROTOCOL_FUZZ_CASES, PROTOCOL_FUZZ_SEED,
};
pub use reassembly::{Delivery, Reassembler, ReassemblyError};
pub use scaling::{
    AdaptiveScalingController, LaneScalingSample, ProviderId, ResourceUsage, ScalingAction,
    ScalingConfig, ScalingError, ScalingPressure, ScalingReason,
};
pub use scheduler::{
    BondScheduler, DeliverySample, FailureDomain, LaneConfig, LaneId, LaneSnapshot,
    ScheduleDecision, SchedulerConfig, SchedulerError, Timestamp, TrafficClass,
    INTERACTIVE_REALTIME_MAX_BYTES,
};
pub use self_test::{embedded_self_test, BondSelfTestError, BondSelfTestReport};
pub use sender::{
    AcknowledgedChunk, Acknowledgement, BondSender, BulkChunkConfig, ScheduledFrame, SenderConfig,
    SenderError, StreamId, TransmissionReason,
};
pub use topology::{
    EndpointDescriptor, EndpointProvider, TopologyAction, TopologyAdvertisement, TopologyError,
    TopologyPolicy, MAX_ENDPOINT_BYTES, MAX_TOPOLOGY_DESCRIPTORS,
};
