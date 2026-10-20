use std::error::Error;
use std::fmt;

use crate::{
    AckRange, CapabilityAdvertisement, CapabilityFeatures, EndpointDescriptor, EndpointProvider,
    FailureDomain, Frame, FrameFlags, FrameKind, LaneId, ProviderCapability,
    SelectiveAcknowledgement, StreamOpen, StreamReset, TopologyAction, TopologyAdvertisement,
    TrafficClass,
};

pub const PROTOCOL_FUZZ_SEED: u64 = 0x414e_4f4e_5353_4801;
pub const DEFAULT_PROTOCOL_FUZZ_CASES: u32 = 2_048;
const MAX_MUTATION_BYTES: usize = 2 * 1024;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct FuzzCounts {
    pub cases: u32,
    pub accepted: u32,
    pub rejected: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ProtocolFuzzReport {
    pub seed: u64,
    pub frame: FuzzCounts,
    pub acknowledgement: FuzzCounts,
    pub stream_control: FuzzCounts,
    pub capability: FuzzCounts,
    pub topology: FuzzCounts,
}

pub fn embedded_protocol_fuzz_test() -> Result<ProtocolFuzzReport, ProtocolFuzzError> {
    protocol_fuzz_test(PROTOCOL_FUZZ_SEED, DEFAULT_PROTOCOL_FUZZ_CASES)
}

pub fn protocol_fuzz_test(
    seed: u64,
    cases_per_parser: u32,
) -> Result<ProtocolFuzzReport, ProtocolFuzzError> {
    if seed == 0 {
        return Err(ProtocolFuzzError::InvalidConfiguration("seed is zero"));
    }
    if cases_per_parser < 16 {
        return Err(ProtocolFuzzError::InvalidConfiguration(
            "fewer than sixteen cases per parser",
        ));
    }

    let mut random = DeterministicRandom::new(seed);
    let frame = exercise(
        "frame",
        &frame_seeds()?,
        cases_per_parser,
        &mut random,
        parse_frame,
    )?;
    let acknowledgement = exercise(
        "acknowledgement",
        &[acknowledgement_seed()?],
        cases_per_parser,
        &mut random,
        parse_acknowledgement,
    )?;
    let stream_control = exercise(
        "stream-control",
        &stream_control_seeds()?,
        cases_per_parser,
        &mut random,
        parse_stream_control,
    )?;
    let capability = exercise(
        "capability",
        &[capability_seed()?],
        cases_per_parser,
        &mut random,
        parse_capability,
    )?;
    let topology = exercise(
        "topology",
        &[topology_seed()?],
        cases_per_parser,
        &mut random,
        parse_topology,
    )?;

    Ok(ProtocolFuzzReport {
        seed,
        frame,
        acknowledgement,
        stream_control,
        capability,
        topology,
    })
}

fn exercise(
    family: &'static str,
    seeds: &[Vec<u8>],
    cases: u32,
    random: &mut DeterministicRandom,
    parse: fn(&[u8]) -> Result<ParseOutcome, ProtocolFuzzError>,
) -> Result<FuzzCounts, ProtocolFuzzError> {
    if seeds.is_empty() {
        return Err(ProtocolFuzzError::InvalidConfiguration(
            "parser corpus is empty",
        ));
    }
    let mut counts = FuzzCounts {
        cases,
        accepted: 0,
        rejected: 0,
    };
    for case in 0..cases {
        let input = mutate(&seeds[case as usize % seeds.len()], case, random);
        match parse(&input)? {
            ParseOutcome::Accepted => counts.accepted += 1,
            ParseOutcome::Rejected => counts.rejected += 1,
        }
    }
    if counts.accepted == 0 || counts.rejected == 0 {
        return Err(ProtocolFuzzError::MissingCoverage {
            family,
            accepted: counts.accepted,
            rejected: counts.rejected,
        });
    }
    Ok(counts)
}

fn mutate(seed: &[u8], case: u32, random: &mut DeterministicRandom) -> Vec<u8> {
    match case % 8 {
        0 => seed.to_vec(),
        1 => seed[..random.bounded(seed.len().saturating_add(1))].to_vec(),
        2 => {
            let mut input = seed.to_vec();
            let extra = 1 + random.bounded(16);
            input.resize(seed.len() + extra, 0);
            random.fill(&mut input[seed.len()..]);
            input
        }
        3 => {
            let mut input = seed.to_vec();
            if !input.is_empty() {
                let index = random.bounded(input.len());
                input[index] ^= 1 << random.bounded(8);
            }
            input
        }
        4 => {
            let mut input = seed.to_vec();
            if !input.is_empty() {
                let index = random.bounded(input.len());
                input[index] = random.next_u64() as u8;
            }
            input
        }
        5 => {
            let mut input = vec![0; random.bounded(MAX_MUTATION_BYTES + 1)];
            random.fill(&mut input);
            input
        }
        6 => vec![0; random.bounded(seed.len().saturating_add(17))],
        _ => {
            let mut input = seed.to_vec();
            let mutations = 1 + random.bounded(8);
            for _ in 0..mutations {
                if input.is_empty() {
                    break;
                }
                let index = random.bounded(input.len());
                input[index] = random.next_u64() as u8;
            }
            input
        }
    }
}

fn frame_seeds() -> Result<Vec<Vec<u8>>, ProtocolFuzzError> {
    let mut seeds = Vec::new();
    for kind in [
        FrameKind::Data,
        FrameKind::Acknowledgement,
        FrameKind::WindowUpdate,
        FrameKind::LaneJoin,
        FrameKind::LaneAccept,
        FrameKind::Ping,
        FrameKind::Pong,
        FrameKind::StreamOpen,
        FrameKind::StreamClose,
        FrameKind::StreamReset,
        FrameKind::EndpointAdvertisement,
        FrameKind::SessionClose,
        FrameKind::CapabilityAdvertisement,
    ] {
        let payload = if kind == FrameKind::Data {
            vec![0x42]
        } else {
            Vec::new()
        };
        let stream_id = if kind == FrameKind::Data { 1 } else { 0 };
        let frame = Frame::new(kind, FrameFlags::NONE, 1, stream_id, 0, payload)
            .map_err(|_| ProtocolFuzzError::SeedConstruction("frame"))?;
        seeds.push(
            frame
                .encode()
                .map_err(|_| ProtocolFuzzError::SeedConstruction("frame"))?,
        );
    }
    Ok(seeds)
}

fn acknowledgement_seed() -> Result<Vec<u8>, ProtocolFuzzError> {
    SelectiveAcknowledgement::new(
        64,
        vec![
            AckRange::new(80, 96)
                .map_err(|_| ProtocolFuzzError::SeedConstruction("acknowledgement"))?,
            AckRange::new(112, 128)
                .map_err(|_| ProtocolFuzzError::SeedConstruction("acknowledgement"))?,
        ],
    )
    .and_then(|acknowledgement| acknowledgement.encode_payload())
    .map_err(|_| ProtocolFuzzError::SeedConstruction("acknowledgement"))
}

fn stream_control_seeds() -> Result<Vec<Vec<u8>>, ProtocolFuzzError> {
    let open = StreamOpen::new(TrafficClass::Interactive, 64 * 1024)
        .map_err(|_| ProtocolFuzzError::SeedConstruction("stream-control"))?;
    let mut open_seed = vec![0];
    open_seed.extend_from_slice(&open.encode_payload());
    let mut reset_seed = vec![1];
    reset_seed.extend_from_slice(&StreamReset::new(7).encode_payload());
    Ok(vec![open_seed, reset_seed])
}

fn capability_seed() -> Result<Vec<u8>, ProtocolFuzzError> {
    let providers = [EndpointProvider::Tor, EndpointProvider::I2p]
        .into_iter()
        .map(|provider| ProviderCapability::new(provider, 4, 2, 1_000, 5_000, 8_000))
        .collect::<Result<Vec<_>, _>>()
        .map_err(|_| ProtocolFuzzError::SeedConstruction("capability"))?;
    CapabilityAdvertisement::new(
        1,
        CapabilityFeatures::CURRENT,
        512 * 1024 * 1024,
        2_000,
        5_000,
        8,
        16,
        4,
        providers,
    )
    .and_then(|advertisement| advertisement.encode_payload())
    .map_err(|_| ProtocolFuzzError::SeedConstruction("capability"))
}

fn topology_seed() -> Result<Vec<u8>, ProtocolFuzzError> {
    let descriptors = vec![
        EndpointDescriptor::new(
            LaneId::new(1).map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))?,
            FailureDomain::new(11).map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))?,
            EndpointProvider::Tor,
            TopologyAction::Add,
            "tor://example.onion:22",
        )
        .map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))?,
        EndpointDescriptor::new(
            LaneId::new(2).map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))?,
            FailureDomain::new(12).map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))?,
            EndpointProvider::I2p,
            TopologyAction::Replace,
            "i2p://example.b32.i2p",
        )
        .map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))?,
    ];
    TopologyAdvertisement::new(1, descriptors)
        .and_then(|advertisement| advertisement.encode_payload())
        .map_err(|_| ProtocolFuzzError::SeedConstruction("topology"))
}

fn parse_frame(input: &[u8]) -> Result<ParseOutcome, ProtocolFuzzError> {
    let Ok((frame, consumed)) = Frame::decode(input) else {
        return Ok(ParseOutcome::Rejected);
    };
    if consumed > input.len() {
        return Err(ProtocolFuzzError::Invariant("frame consumed past input"));
    }
    let encoded = frame
        .encode()
        .map_err(|_| ProtocolFuzzError::Invariant("accepted frame did not encode"))?;
    if encoded != input[..consumed] {
        return Err(ProtocolFuzzError::Invariant("frame was not canonical"));
    }
    let (round_trip, round_trip_consumed) = Frame::decode(&encoded)
        .map_err(|_| ProtocolFuzzError::Invariant("encoded frame did not decode"))?;
    if round_trip != frame || round_trip_consumed != encoded.len() {
        return Err(ProtocolFuzzError::Invariant(
            "frame round trip changed value",
        ));
    }
    Ok(ParseOutcome::Accepted)
}

fn parse_acknowledgement(input: &[u8]) -> Result<ParseOutcome, ProtocolFuzzError> {
    let Ok(value) = SelectiveAcknowledgement::decode_payload(64, input) else {
        return Ok(ParseOutcome::Rejected);
    };
    let encoded = value
        .encode_payload()
        .map_err(|_| ProtocolFuzzError::Invariant("accepted acknowledgement did not encode"))?;
    if encoded != input
        || SelectiveAcknowledgement::decode_payload(64, &encoded).as_ref() != Ok(&value)
    {
        return Err(ProtocolFuzzError::Invariant(
            "acknowledgement was not canonical",
        ));
    }
    Ok(ParseOutcome::Accepted)
}

fn parse_stream_control(input: &[u8]) -> Result<ParseOutcome, ProtocolFuzzError> {
    let Some((&selector, payload)) = input.split_first() else {
        return Ok(ParseOutcome::Rejected);
    };
    match selector {
        0 => {
            let Ok(value) = StreamOpen::decode_payload(payload) else {
                return Ok(ParseOutcome::Rejected);
            };
            if value.encode_payload() != payload {
                return Err(ProtocolFuzzError::Invariant(
                    "stream-open was not canonical",
                ));
            }
        }
        1 => {
            let Ok(value) = StreamReset::decode_payload(payload) else {
                return Ok(ParseOutcome::Rejected);
            };
            if value.encode_payload() != payload {
                return Err(ProtocolFuzzError::Invariant(
                    "stream-reset was not canonical",
                ));
            }
        }
        _ => return Ok(ParseOutcome::Rejected),
    }
    Ok(ParseOutcome::Accepted)
}

fn parse_capability(input: &[u8]) -> Result<ParseOutcome, ProtocolFuzzError> {
    let Ok(value) = CapabilityAdvertisement::decode_payload(input) else {
        return Ok(ParseOutcome::Rejected);
    };
    let encoded = value
        .encode_payload()
        .map_err(|_| ProtocolFuzzError::Invariant("accepted capability did not encode"))?;
    if encoded != input || CapabilityAdvertisement::decode_payload(&encoded).as_ref() != Ok(&value)
    {
        return Err(ProtocolFuzzError::Invariant("capability was not canonical"));
    }
    Ok(ParseOutcome::Accepted)
}

fn parse_topology(input: &[u8]) -> Result<ParseOutcome, ProtocolFuzzError> {
    let Ok(value) = TopologyAdvertisement::decode_payload(input) else {
        return Ok(ParseOutcome::Rejected);
    };
    let encoded = value
        .encode_payload()
        .map_err(|_| ProtocolFuzzError::Invariant("accepted topology did not encode"))?;
    if encoded != input || TopologyAdvertisement::decode_payload(&encoded).as_ref() != Ok(&value) {
        return Err(ProtocolFuzzError::Invariant("topology was not canonical"));
    }
    Ok(ParseOutcome::Accepted)
}

#[derive(Clone, Copy)]
enum ParseOutcome {
    Accepted,
    Rejected,
}

struct DeterministicRandom(u64);

impl DeterministicRandom {
    const fn new(seed: u64) -> Self {
        Self(seed)
    }

    fn next_u64(&mut self) -> u64 {
        let mut value = self.0;
        value ^= value << 13;
        value ^= value >> 7;
        value ^= value << 17;
        self.0 = value;
        value
    }

    fn bounded(&mut self, upper_exclusive: usize) -> usize {
        if upper_exclusive == 0 {
            0
        } else {
            (self.next_u64() as usize) % upper_exclusive
        }
    }

    fn fill(&mut self, output: &mut [u8]) {
        for chunk in output.chunks_mut(8) {
            let bytes = self.next_u64().to_le_bytes();
            chunk.copy_from_slice(&bytes[..chunk.len()]);
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ProtocolFuzzError {
    InvalidConfiguration(&'static str),
    SeedConstruction(&'static str),
    Invariant(&'static str),
    MissingCoverage {
        family: &'static str,
        accepted: u32,
        rejected: u32,
    },
}

impl fmt::Display for ProtocolFuzzError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidConfiguration(message) => {
                write!(formatter, "invalid protocol fuzz configuration: {message}")
            }
            Self::SeedConstruction(family) => {
                write!(formatter, "failed to construct {family} fuzz seed")
            }
            Self::Invariant(message) => write!(formatter, "protocol fuzz invariant failed: {message}"),
            Self::MissingCoverage {
                family,
                accepted,
                rejected,
            } => write!(
                formatter,
                "protocol fuzz family {family} lacks mixed coverage (accepted={accepted}, rejected={rejected})"
            ),
        }
    }
}

impl Error for ProtocolFuzzError {}

#[cfg(test)]
mod tests {
    #[test]
    fn deterministic_protocol_campaign_has_mixed_coverage() {
        let first = super::protocol_fuzz_test(super::PROTOCOL_FUZZ_SEED, 256).unwrap();
        let second = super::protocol_fuzz_test(super::PROTOCOL_FUZZ_SEED, 256).unwrap();
        assert_eq!(first, second);
        for counts in [
            first.frame,
            first.acknowledgement,
            first.stream_control,
            first.capability,
            first.topology,
        ] {
            assert_eq!(counts.accepted + counts.rejected, counts.cases);
            assert!(counts.accepted > 0);
            assert!(counts.rejected > 0);
        }
    }
}
