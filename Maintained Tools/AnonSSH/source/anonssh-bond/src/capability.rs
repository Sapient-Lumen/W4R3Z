use std::collections::BTreeMap;
use std::error::Error;
use std::fmt;

use crate::EndpointProvider;

pub const MAX_CAPABILITY_PROVIDERS: usize = 3;
pub const MAX_CAPABILITY_LANES: u16 = 32;
const PREFIX_LEN: usize = 40;
const PROVIDER_LEN: usize = 16;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct CapabilityFeatures(u64);

impl CapabilityFeatures {
    pub const MULTISTREAM: Self = Self(1 << 0);
    pub const ADAPTIVE_TOPOLOGY: Self = Self(1 << 1);
    pub const REALTIME_REDUNDANCY: Self = Self(1 << 2);
    pub const DYNAMIC_CAPABILITIES: Self = Self(1 << 3);
    pub const NATIVE_SERVICES: Self = Self(1 << 4);
    pub const V5_CURRENT: Self = Self(
        Self::MULTISTREAM.0
            | Self::ADAPTIVE_TOPOLOGY.0
            | Self::REALTIME_REDUNDANCY.0
            | Self::DYNAMIC_CAPABILITIES.0,
    );
    pub const CURRENT: Self = Self(Self::V5_CURRENT.0 | Self::NATIVE_SERVICES.0);

    pub const fn from_bits(bits: u64) -> Result<Self, CapabilityError> {
        if bits & !Self::CURRENT.0 == 0 {
            Ok(Self(bits))
        } else {
            Err(CapabilityError::UnknownFeatureBits(bits & !Self::CURRENT.0))
        }
    }

    pub const fn bits(self) -> u64 {
        self.0
    }

    pub const fn intersection(self, other: Self) -> Self {
        Self(self.0 & other.0)
    }

    pub const fn contains(self, other: Self) -> bool {
        self.0 & other.0 == other.0
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ProviderCapability {
    pub provider: EndpointProvider,
    pub candidates: u8,
    pub ready: u8,
    pub startup_millis: u32,
    pub queue_delay_micros: u32,
    pub delivered_kbps: u32,
}

impl ProviderCapability {
    pub fn new(
        provider: EndpointProvider,
        candidates: u8,
        ready: u8,
        startup_millis: u32,
        queue_delay_micros: u32,
        delivered_kbps: u32,
    ) -> Result<Self, CapabilityError> {
        let capability = Self {
            provider,
            candidates,
            ready,
            startup_millis,
            queue_delay_micros,
            delivered_kbps,
        };
        capability.validate()?;
        Ok(capability)
    }

    fn validate(self) -> Result<(), CapabilityError> {
        if self.candidates == 0 || u16::from(self.candidates) > MAX_CAPABILITY_LANES {
            return Err(CapabilityError::InvalidCandidateCount {
                provider: self.provider,
                count: self.candidates,
            });
        }
        if self.ready > self.candidates {
            return Err(CapabilityError::ReadyExceedsCandidates {
                provider: self.provider,
                ready: self.ready,
                candidates: self.candidates,
            });
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CapabilityAdvertisement {
    pub generation: u64,
    pub features: CapabilityFeatures,
    pub memory_ceiling_bytes: u64,
    pub cpu_ceiling_millicores: u32,
    pub queue_delay_micros: u32,
    pub max_active_lanes: u16,
    pub max_sessions: u16,
    pub active_lanes: u16,
    pub providers: Vec<ProviderCapability>,
}

impl CapabilityAdvertisement {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        generation: u64,
        features: CapabilityFeatures,
        memory_ceiling_bytes: u64,
        cpu_ceiling_millicores: u32,
        queue_delay_micros: u32,
        max_active_lanes: u16,
        max_sessions: u16,
        active_lanes: u16,
        providers: Vec<ProviderCapability>,
    ) -> Result<Self, CapabilityError> {
        let advertisement = Self {
            generation,
            features,
            memory_ceiling_bytes,
            cpu_ceiling_millicores,
            queue_delay_micros,
            max_active_lanes,
            max_sessions,
            active_lanes,
            providers,
        };
        advertisement.validate()?;
        Ok(advertisement)
    }

    pub fn encode_payload(&self) -> Result<Vec<u8>, CapabilityError> {
        self.validate()?;
        let mut payload = Vec::with_capacity(PREFIX_LEN + self.providers.len() * PROVIDER_LEN);
        payload.extend_from_slice(&self.generation.to_be_bytes());
        payload.extend_from_slice(&self.features.bits().to_be_bytes());
        payload.extend_from_slice(&self.memory_ceiling_bytes.to_be_bytes());
        payload.extend_from_slice(&self.cpu_ceiling_millicores.to_be_bytes());
        payload.extend_from_slice(&self.queue_delay_micros.to_be_bytes());
        payload.extend_from_slice(&self.max_active_lanes.to_be_bytes());
        payload.extend_from_slice(&self.max_sessions.to_be_bytes());
        payload.extend_from_slice(&self.active_lanes.to_be_bytes());
        payload.push(self.providers.len() as u8);
        payload.push(0);
        for provider in &self.providers {
            payload.push(provider.provider as u8);
            payload.push(provider.candidates);
            payload.push(provider.ready);
            payload.push(0);
            payload.extend_from_slice(&provider.startup_millis.to_be_bytes());
            payload.extend_from_slice(&provider.queue_delay_micros.to_be_bytes());
            payload.extend_from_slice(&provider.delivered_kbps.to_be_bytes());
        }
        Ok(payload)
    }

    pub fn decode_payload(payload: &[u8]) -> Result<Self, CapabilityError> {
        if payload.len() < PREFIX_LEN {
            return Err(CapabilityError::Truncated);
        }
        if payload[39] != 0 {
            return Err(CapabilityError::NonZeroReserved);
        }
        let provider_count = usize::from(payload[38]);
        if provider_count == 0 || provider_count > MAX_CAPABILITY_PROVIDERS {
            return Err(CapabilityError::InvalidProviderCount(provider_count));
        }
        let expected = PREFIX_LEN
            .checked_add(
                provider_count
                    .checked_mul(PROVIDER_LEN)
                    .ok_or(CapabilityError::LengthOverflow)?,
            )
            .ok_or(CapabilityError::LengthOverflow)?;
        if payload.len() < expected {
            return Err(CapabilityError::Truncated);
        }
        if payload.len() != expected {
            return Err(CapabilityError::TrailingData);
        }
        let mut providers = Vec::with_capacity(provider_count);
        let (provider_chunks, remainder) = payload[PREFIX_LEN..].as_chunks::<PROVIDER_LEN>();
        debug_assert!(remainder.is_empty());
        for chunk in provider_chunks {
            if chunk[3] != 0 {
                return Err(CapabilityError::NonZeroReserved);
            }
            providers.push(ProviderCapability::new(
                EndpointProvider::try_from(chunk[0]).map_err(CapabilityError::Topology)?,
                chunk[1],
                chunk[2],
                u32::from_be_bytes(chunk[4..8].try_into().expect("fixed startup")),
                u32::from_be_bytes(chunk[8..12].try_into().expect("fixed queue")),
                u32::from_be_bytes(chunk[12..16].try_into().expect("fixed goodput")),
            )?);
        }
        Self::new(
            u64::from_be_bytes(payload[0..8].try_into().expect("fixed generation")),
            CapabilityFeatures::from_bits(u64::from_be_bytes(
                payload[8..16].try_into().expect("fixed features"),
            ))?,
            u64::from_be_bytes(payload[16..24].try_into().expect("fixed memory")),
            u32::from_be_bytes(payload[24..28].try_into().expect("fixed CPU")),
            u32::from_be_bytes(payload[28..32].try_into().expect("fixed queue")),
            u16::from_be_bytes(payload[32..34].try_into().expect("fixed lane ceiling")),
            u16::from_be_bytes(payload[34..36].try_into().expect("fixed session ceiling")),
            u16::from_be_bytes(payload[36..38].try_into().expect("fixed active lanes")),
            providers,
        )
    }

    pub fn intersect(&self, peer: &Self) -> Result<CapabilityIntersection, CapabilityError> {
        self.validate()?;
        peer.validate()?;
        let remote = peer
            .providers
            .iter()
            .map(|provider| (provider.provider, provider))
            .collect::<BTreeMap<_, _>>();
        let providers = self
            .providers
            .iter()
            .filter_map(|local| {
                let remote = remote.get(&local.provider)?;
                let candidates = local.candidates.min(remote.candidates);
                (candidates > 0).then_some(ProviderCapability {
                    provider: local.provider,
                    candidates,
                    ready: local.ready.min(remote.ready).min(candidates),
                    startup_millis: local.startup_millis.max(remote.startup_millis),
                    queue_delay_micros: local.queue_delay_micros.max(remote.queue_delay_micros),
                    delivered_kbps: local.delivered_kbps.min(remote.delivered_kbps),
                })
            })
            .collect::<Vec<_>>();
        if providers.is_empty() {
            return Err(CapabilityError::EmptyIntersection);
        }
        let candidate_ceiling = providers
            .iter()
            .map(|provider| u16::from(provider.candidates))
            .sum::<u16>();
        let max_active_lanes = self
            .max_active_lanes
            .min(peer.max_active_lanes)
            .min(candidate_ceiling);
        if max_active_lanes == 0 {
            return Err(CapabilityError::EmptyIntersection);
        }
        Ok(CapabilityIntersection {
            features: self.features.intersection(peer.features),
            memory_ceiling_bytes: self.memory_ceiling_bytes.min(peer.memory_ceiling_bytes),
            cpu_ceiling_millicores: self.cpu_ceiling_millicores.min(peer.cpu_ceiling_millicores),
            queue_delay_micros: self.queue_delay_micros.max(peer.queue_delay_micros),
            max_active_lanes,
            max_sessions: self.max_sessions.min(peer.max_sessions),
            active_lanes: self
                .active_lanes
                .min(peer.active_lanes)
                .min(max_active_lanes),
            providers,
        })
    }

    fn validate(&self) -> Result<(), CapabilityError> {
        if self.generation == 0 {
            return Err(CapabilityError::ZeroGeneration);
        }
        CapabilityFeatures::from_bits(self.features.bits())?;
        if self.memory_ceiling_bytes == 0 || self.cpu_ceiling_millicores == 0 {
            return Err(CapabilityError::ZeroResourceCeiling);
        }
        if self.max_active_lanes == 0 || self.max_active_lanes > MAX_CAPABILITY_LANES {
            return Err(CapabilityError::InvalidActiveLaneCeiling(
                self.max_active_lanes,
            ));
        }
        if self.max_sessions == 0 {
            return Err(CapabilityError::ZeroSessionCeiling);
        }
        if self.active_lanes > self.max_active_lanes {
            return Err(CapabilityError::ActiveLanesExceedCeiling {
                active: self.active_lanes,
                ceiling: self.max_active_lanes,
            });
        }
        if self.providers.is_empty() || self.providers.len() > MAX_CAPABILITY_PROVIDERS {
            return Err(CapabilityError::InvalidProviderCount(self.providers.len()));
        }
        let mut seen = BTreeMap::new();
        for provider in &self.providers {
            provider.validate()?;
            if seen.insert(provider.provider, ()).is_some() {
                return Err(CapabilityError::DuplicateProvider(provider.provider));
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CapabilityIntersection {
    pub features: CapabilityFeatures,
    pub memory_ceiling_bytes: u64,
    pub cpu_ceiling_millicores: u32,
    pub queue_delay_micros: u32,
    pub max_active_lanes: u16,
    pub max_sessions: u16,
    pub active_lanes: u16,
    pub providers: Vec<ProviderCapability>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum CapabilityError {
    ZeroGeneration,
    UnknownFeatureBits(u64),
    ZeroResourceCeiling,
    InvalidActiveLaneCeiling(u16),
    ZeroSessionCeiling,
    ActiveLanesExceedCeiling {
        active: u16,
        ceiling: u16,
    },
    InvalidProviderCount(usize),
    InvalidCandidateCount {
        provider: EndpointProvider,
        count: u8,
    },
    ReadyExceedsCandidates {
        provider: EndpointProvider,
        ready: u8,
        candidates: u8,
    },
    DuplicateProvider(EndpointProvider),
    EmptyIntersection,
    NonZeroReserved,
    Truncated,
    TrailingData,
    LengthOverflow,
    Topology(crate::TopologyError),
}

impl fmt::Display for CapabilityError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroGeneration => write!(formatter, "capability generation must be non-zero"),
            Self::UnknownFeatureBits(bits) => {
                write!(formatter, "unknown capability feature bits 0x{bits:x}")
            }
            Self::ZeroResourceCeiling => {
                write!(formatter, "capability resource ceilings must be non-zero")
            }
            Self::InvalidActiveLaneCeiling(count) => {
                write!(formatter, "invalid capability active-lane ceiling {count}")
            }
            Self::ZeroSessionCeiling => {
                write!(formatter, "capability session ceiling must be non-zero")
            }
            Self::ActiveLanesExceedCeiling { active, ceiling } => write!(
                formatter,
                "capability active lanes {active} exceed ceiling {ceiling}"
            ),
            Self::InvalidProviderCount(count) => {
                write!(formatter, "invalid capability provider count {count}")
            }
            Self::InvalidCandidateCount { provider, count } => {
                write!(formatter, "invalid {provider:?} candidate count {count}")
            }
            Self::ReadyExceedsCandidates {
                provider,
                ready,
                candidates,
            } => write!(
                formatter,
                "{provider:?} ready count {ready} exceeds candidate count {candidates}"
            ),
            Self::DuplicateProvider(provider) => {
                write!(formatter, "capability repeats provider {provider:?}")
            }
            Self::EmptyIntersection => {
                write!(formatter, "capability intersection has no usable provider")
            }
            Self::NonZeroReserved => write!(formatter, "capability reserved bytes are non-zero"),
            Self::Truncated => write!(formatter, "capability payload is truncated"),
            Self::TrailingData => write!(formatter, "capability payload has trailing data"),
            Self::LengthOverflow => write!(formatter, "capability payload length overflow"),
            Self::Topology(error) => error.fmt(formatter),
        }
    }
}

impl Error for CapabilityError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Topology(error) => Some(error),
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{CapabilityAdvertisement, CapabilityError, CapabilityFeatures, ProviderCapability};
    use crate::EndpointProvider;

    fn advertisement(generation: u64) -> CapabilityAdvertisement {
        CapabilityAdvertisement::new(
            generation,
            CapabilityFeatures::CURRENT,
            2 * 1024 * 1024 * 1024,
            2_000,
            12_000,
            16,
            8,
            4,
            vec![
                ProviderCapability::new(EndpointProvider::Tor, 8, 4, 2_000, 8_000, 4_000).unwrap(),
                ProviderCapability::new(EndpointProvider::I2p, 8, 2, 120_000, 30_000, 2_000)
                    .unwrap(),
            ],
        )
        .unwrap()
    }

    #[test]
    fn capability_wire_vector_is_canonical_and_round_trips() {
        let advertisement = advertisement(7);
        let encoded = advertisement.encode_payload().unwrap();
        assert_eq!(encoded.len(), 72);
        assert_eq!(&encoded[0..8], &7_u64.to_be_bytes());
        assert_eq!(&encoded[8..16], &31_u64.to_be_bytes());
        assert_eq!(&encoded[38..40], &[2, 0]);
        assert_eq!(
            CapabilityAdvertisement::decode_payload(&encoded).unwrap(),
            advertisement
        );
    }

    #[test]
    fn malformed_capabilities_fail_closed() {
        let mut encoded = advertisement(7).encode_payload().unwrap();
        encoded[39] = 1;
        assert_eq!(
            CapabilityAdvertisement::decode_payload(&encoded),
            Err(CapabilityError::NonZeroReserved)
        );
        encoded[39] = 0;
        encoded.push(0);
        assert_eq!(
            CapabilityAdvertisement::decode_payload(&encoded),
            Err(CapabilityError::TrailingData)
        );
        assert!(CapabilityAdvertisement::new(
            1,
            CapabilityFeatures::CURRENT,
            1,
            1,
            0,
            1,
            1,
            0,
            vec![
                ProviderCapability::new(EndpointProvider::Tor, 1, 1, 0, 0, 0).unwrap(),
                ProviderCapability::new(EndpointProvider::Tor, 1, 1, 0, 0, 0).unwrap(),
            ],
        )
        .is_err());
    }

    #[test]
    fn intersection_uses_bilateral_limits_and_costs() {
        let local = advertisement(1);
        let peer = CapabilityAdvertisement::new(
            4,
            CapabilityFeatures::MULTISTREAM.intersection(CapabilityFeatures::CURRENT),
            512 * 1024 * 1024,
            600,
            40_000,
            6,
            2,
            3,
            vec![
                ProviderCapability::new(EndpointProvider::I2p, 4, 1, 300_000, 80_000, 900).unwrap(),
                ProviderCapability::new(EndpointProvider::Tcp, 2, 2, 1, 1, 10_000).unwrap(),
            ],
        )
        .unwrap();
        let intersection = local.intersect(&peer).unwrap();
        assert_eq!(intersection.memory_ceiling_bytes, 512 * 1024 * 1024);
        assert_eq!(intersection.cpu_ceiling_millicores, 600);
        assert_eq!(intersection.queue_delay_micros, 40_000);
        assert_eq!(intersection.max_active_lanes, 4);
        assert_eq!(intersection.max_sessions, 2);
        assert_eq!(intersection.providers.len(), 1);
        assert_eq!(intersection.providers[0].provider, EndpointProvider::I2p);
        assert_eq!(intersection.providers[0].candidates, 4);
        assert_eq!(intersection.providers[0].ready, 1);
        assert_eq!(intersection.providers[0].startup_millis, 300_000);
        assert_eq!(intersection.providers[0].queue_delay_micros, 80_000);
        assert_eq!(intersection.providers[0].delivered_kbps, 900);
    }
}
