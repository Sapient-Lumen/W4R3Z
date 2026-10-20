use std::collections::BTreeSet;
use std::error::Error;
use std::fmt;

use crate::{FailureDomain, LaneId, SchedulerError};

pub const MAX_TOPOLOGY_DESCRIPTORS: usize = 32;
pub const MAX_ENDPOINT_BYTES: usize = 1_024;
const PREFIX_LEN: usize = 12;
const DESCRIPTOR_PREFIX_LEN: usize = 20;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(u8)]
pub enum EndpointProvider {
    Tor = 1,
    I2p = 2,
    Tcp = 3,
}

impl EndpointProvider {
    fn scheme(self) -> &'static str {
        match self {
            Self::Tor => "tor://",
            Self::I2p => "i2p://",
            Self::Tcp => "tcp://",
        }
    }
}

impl TryFrom<u8> for EndpointProvider {
    type Error = TopologyError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            1 => Ok(Self::Tor),
            2 => Ok(Self::I2p),
            3 => Ok(Self::Tcp),
            _ => Err(TopologyError::UnknownProvider(value)),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(u8)]
pub enum TopologyAction {
    Add = 1,
    Replace = 2,
    Drain = 3,
}

impl TryFrom<u8> for TopologyAction {
    type Error = TopologyError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            1 => Ok(Self::Add),
            2 => Ok(Self::Replace),
            3 => Ok(Self::Drain),
            _ => Err(TopologyError::UnknownAction(value)),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct EndpointDescriptor {
    pub lane_id: LaneId,
    pub failure_domain: FailureDomain,
    pub provider: EndpointProvider,
    pub action: TopologyAction,
    pub endpoint: String,
}

impl EndpointDescriptor {
    pub fn new(
        lane_id: LaneId,
        failure_domain: FailureDomain,
        provider: EndpointProvider,
        action: TopologyAction,
        endpoint: impl Into<String>,
    ) -> Result<Self, TopologyError> {
        let descriptor = Self {
            lane_id,
            failure_domain,
            provider,
            action,
            endpoint: endpoint.into(),
        };
        descriptor.validate()?;
        Ok(descriptor)
    }

    fn validate(&self) -> Result<(), TopologyError> {
        let bytes = self.endpoint.as_bytes();
        if bytes.is_empty() || bytes.len() > MAX_ENDPOINT_BYTES {
            return Err(TopologyError::InvalidEndpointLength(bytes.len()));
        }
        if !self.endpoint.starts_with(self.provider.scheme())
            || bytes
                .iter()
                .any(|byte| byte.is_ascii_control() || byte.is_ascii_whitespace())
        {
            return Err(TopologyError::InvalidEndpoint);
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TopologyAdvertisement {
    pub generation: u64,
    pub descriptors: Vec<EndpointDescriptor>,
}

impl TopologyAdvertisement {
    pub fn new(
        generation: u64,
        descriptors: Vec<EndpointDescriptor>,
    ) -> Result<Self, TopologyError> {
        let advertisement = Self {
            generation,
            descriptors,
        };
        advertisement.validate()?;
        Ok(advertisement)
    }

    pub fn encode_payload(&self) -> Result<Vec<u8>, TopologyError> {
        self.validate()?;
        let mut payload = Vec::with_capacity(PREFIX_LEN);
        payload.extend_from_slice(&self.generation.to_be_bytes());
        payload.extend_from_slice(&(self.descriptors.len() as u16).to_be_bytes());
        payload.extend_from_slice(&[0_u8; 2]);
        for descriptor in &self.descriptors {
            let endpoint = descriptor.endpoint.as_bytes();
            let endpoint_len =
                u16::try_from(endpoint.len()).map_err(|_| TopologyError::LengthOverflow)?;
            payload.extend_from_slice(&descriptor.lane_id.get().to_be_bytes());
            payload.extend_from_slice(&descriptor.failure_domain.get().to_be_bytes());
            payload.push(descriptor.provider as u8);
            payload.push(descriptor.action as u8);
            payload.extend_from_slice(&endpoint_len.to_be_bytes());
            payload.extend_from_slice(&[0_u8; 4]);
            payload.extend_from_slice(endpoint);
        }
        Ok(payload)
    }

    pub fn decode_payload(payload: &[u8]) -> Result<Self, TopologyError> {
        if payload.len() < PREFIX_LEN {
            return Err(TopologyError::Truncated);
        }
        if payload[10..12] != [0_u8; 2] {
            return Err(TopologyError::NonZeroReserved);
        }
        let generation = u64::from_be_bytes(payload[..8].try_into().expect("fixed generation"));
        let count = u16::from_be_bytes(payload[8..10].try_into().expect("fixed count")) as usize;
        if count == 0 || count > MAX_TOPOLOGY_DESCRIPTORS {
            return Err(TopologyError::InvalidDescriptorCount(count));
        }
        let mut cursor = PREFIX_LEN;
        let mut descriptors = Vec::with_capacity(count);
        for _ in 0..count {
            let prefix_end = cursor
                .checked_add(DESCRIPTOR_PREFIX_LEN)
                .ok_or(TopologyError::LengthOverflow)?;
            if prefix_end > payload.len() {
                return Err(TopologyError::Truncated);
            }
            let prefix = &payload[cursor..prefix_end];
            if prefix[16..20] != [0_u8; 4] {
                return Err(TopologyError::NonZeroReserved);
            }
            let lane_id = LaneId::new(u32::from_be_bytes(
                prefix[..4].try_into().expect("fixed lane ID"),
            ))?;
            let failure_domain = FailureDomain::new(u64::from_be_bytes(
                prefix[4..12].try_into().expect("fixed failure domain"),
            ))?;
            let provider = EndpointProvider::try_from(prefix[12])?;
            let action = TopologyAction::try_from(prefix[13])?;
            let endpoint_len =
                u16::from_be_bytes(prefix[14..16].try_into().expect("fixed endpoint length"))
                    as usize;
            if endpoint_len == 0 || endpoint_len > MAX_ENDPOINT_BYTES {
                return Err(TopologyError::InvalidEndpointLength(endpoint_len));
            }
            let endpoint_end = prefix_end
                .checked_add(endpoint_len)
                .ok_or(TopologyError::LengthOverflow)?;
            if endpoint_end > payload.len() {
                return Err(TopologyError::Truncated);
            }
            let endpoint = std::str::from_utf8(&payload[prefix_end..endpoint_end])
                .map_err(|_| TopologyError::InvalidEndpoint)?;
            descriptors.push(EndpointDescriptor::new(
                lane_id,
                failure_domain,
                provider,
                action,
                endpoint,
            )?);
            cursor = endpoint_end;
        }
        if cursor != payload.len() {
            return Err(TopologyError::TrailingData);
        }
        Self::new(generation, descriptors)
    }

    fn validate(&self) -> Result<(), TopologyError> {
        if self.generation == 0 {
            return Err(TopologyError::ZeroGeneration);
        }
        if self.descriptors.is_empty() || self.descriptors.len() > MAX_TOPOLOGY_DESCRIPTORS {
            return Err(TopologyError::InvalidDescriptorCount(
                self.descriptors.len(),
            ));
        }
        let mut lane_ids = BTreeSet::new();
        for descriptor in &self.descriptors {
            descriptor.validate()?;
            if !lane_ids.insert(descriptor.lane_id) {
                return Err(TopologyError::DuplicateLane(descriptor.lane_id));
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug)]
pub struct TopologyPolicy {
    max_descriptors: usize,
    max_lane_id: u32,
    allowed_providers: BTreeSet<EndpointProvider>,
    allowed_failure_domains: BTreeSet<FailureDomain>,
    allowed_actions: BTreeSet<TopologyAction>,
}

impl TopologyPolicy {
    pub fn new(
        max_descriptors: usize,
        max_lane_id: u32,
        allowed_providers: impl IntoIterator<Item = EndpointProvider>,
        allowed_failure_domains: impl IntoIterator<Item = FailureDomain>,
        allowed_actions: impl IntoIterator<Item = TopologyAction>,
    ) -> Result<Self, TopologyError> {
        let allowed_providers = allowed_providers.into_iter().collect::<BTreeSet<_>>();
        let allowed_failure_domains = allowed_failure_domains.into_iter().collect::<BTreeSet<_>>();
        let allowed_actions = allowed_actions.into_iter().collect::<BTreeSet<_>>();
        if max_descriptors == 0 || max_descriptors > MAX_TOPOLOGY_DESCRIPTORS {
            return Err(TopologyError::InvalidDescriptorCount(max_descriptors));
        }
        if max_lane_id == 0
            || allowed_providers.is_empty()
            || allowed_failure_domains.is_empty()
            || allowed_actions.is_empty()
        {
            return Err(TopologyError::InvalidPolicy);
        }
        Ok(Self {
            max_descriptors,
            max_lane_id,
            allowed_providers,
            allowed_failure_domains,
            allowed_actions,
        })
    }

    pub fn validate(&self, advertisement: &TopologyAdvertisement) -> Result<(), TopologyError> {
        advertisement.validate()?;
        if advertisement.descriptors.len() > self.max_descriptors {
            return Err(TopologyError::PolicyDescriptorLimit);
        }
        for descriptor in &advertisement.descriptors {
            if descriptor.lane_id.get() > self.max_lane_id {
                return Err(TopologyError::PolicyLaneLimit(descriptor.lane_id));
            }
            if !self.allowed_providers.contains(&descriptor.provider) {
                return Err(TopologyError::ProviderDenied(descriptor.provider));
            }
            if !self
                .allowed_failure_domains
                .contains(&descriptor.failure_domain)
            {
                return Err(TopologyError::FailureDomainDenied(
                    descriptor.failure_domain,
                ));
            }
            if !self.allowed_actions.contains(&descriptor.action) {
                return Err(TopologyError::ActionDenied(descriptor.action));
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum TopologyError {
    ZeroGeneration,
    InvalidDescriptorCount(usize),
    InvalidEndpointLength(usize),
    InvalidEndpoint,
    UnknownProvider(u8),
    UnknownAction(u8),
    DuplicateLane(LaneId),
    NonZeroReserved,
    Truncated,
    TrailingData,
    LengthOverflow,
    InvalidPolicy,
    PolicyDescriptorLimit,
    PolicyLaneLimit(LaneId),
    ProviderDenied(EndpointProvider),
    FailureDomainDenied(FailureDomain),
    ActionDenied(TopologyAction),
    Scheduler(SchedulerError),
}

impl From<SchedulerError> for TopologyError {
    fn from(value: SchedulerError) -> Self {
        Self::Scheduler(value)
    }
}

impl fmt::Display for TopologyError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroGeneration => write!(formatter, "topology generation must be non-zero"),
            Self::InvalidDescriptorCount(count) => {
                write!(formatter, "invalid topology descriptor count {count}")
            }
            Self::InvalidEndpointLength(length) => {
                write!(formatter, "invalid topology endpoint length {length}")
            }
            Self::InvalidEndpoint => write!(formatter, "invalid topology endpoint"),
            Self::UnknownProvider(value) => write!(formatter, "unknown topology provider {value}"),
            Self::UnknownAction(value) => write!(formatter, "unknown topology action {value}"),
            Self::DuplicateLane(id) => write!(formatter, "topology repeats lane {}", id.get()),
            Self::NonZeroReserved => write!(formatter, "topology reserved bytes are non-zero"),
            Self::Truncated => write!(formatter, "topology payload is truncated"),
            Self::TrailingData => write!(formatter, "topology payload has trailing data"),
            Self::LengthOverflow => write!(formatter, "topology payload length overflow"),
            Self::InvalidPolicy => write!(formatter, "invalid topology policy"),
            Self::PolicyDescriptorLimit => {
                write!(formatter, "topology exceeds local descriptor policy")
            }
            Self::PolicyLaneLimit(id) => {
                write!(formatter, "topology lane {} exceeds local policy", id.get())
            }
            Self::ProviderDenied(provider) => {
                write!(formatter, "topology provider {provider:?} is denied")
            }
            Self::FailureDomainDenied(domain) => write!(
                formatter,
                "topology failure domain {} is denied",
                domain.get()
            ),
            Self::ActionDenied(action) => {
                write!(formatter, "topology action {action:?} is denied")
            }
            Self::Scheduler(error) => error.fmt(formatter),
        }
    }
}

impl Error for TopologyError {}

#[cfg(test)]
mod tests {
    use super::{
        EndpointDescriptor, EndpointProvider, TopologyAction, TopologyAdvertisement, TopologyError,
        TopologyPolicy,
    };
    use crate::{FailureDomain, LaneId};

    fn descriptor(provider: EndpointProvider) -> EndpointDescriptor {
        let endpoint = match provider {
            EndpointProvider::Tor => "tor://example.onion:22424",
            EndpointProvider::I2p => "i2p://example.b32.i2p:22424",
            EndpointProvider::Tcp => "tcp://127.0.0.1:22424",
        };
        EndpointDescriptor::new(
            LaneId::new(5).unwrap(),
            FailureDomain::new(9).unwrap(),
            provider,
            TopologyAction::Add,
            endpoint,
        )
        .unwrap()
    }

    #[test]
    fn topology_round_trips_and_local_policy_fails_closed() {
        let advertisement =
            TopologyAdvertisement::new(7, vec![descriptor(EndpointProvider::Tcp)]).unwrap();
        let encoded = advertisement.encode_payload().unwrap();
        assert_eq!(
            TopologyAdvertisement::decode_payload(&encoded).unwrap(),
            advertisement
        );

        let policy = TopologyPolicy::new(
            1,
            8,
            [EndpointProvider::Tcp],
            [FailureDomain::new(9).unwrap()],
            [TopologyAction::Add],
        )
        .unwrap();
        policy.validate(&advertisement).unwrap();
        let denied = TopologyPolicy::new(
            1,
            8,
            [EndpointProvider::I2p],
            [FailureDomain::new(9).unwrap()],
            [TopologyAction::Add],
        )
        .unwrap();
        assert_eq!(
            denied.validate(&advertisement).unwrap_err(),
            TopologyError::ProviderDenied(EndpointProvider::Tcp)
        );
        let denied_domain = TopologyPolicy::new(
            1,
            8,
            [EndpointProvider::Tcp],
            [FailureDomain::new(10).unwrap()],
            [TopologyAction::Add],
        )
        .unwrap();
        assert_eq!(
            denied_domain.validate(&advertisement).unwrap_err(),
            TopologyError::FailureDomainDenied(FailureDomain::new(9).unwrap())
        );

        let drain = TopologyAdvertisement::new(
            8,
            vec![EndpointDescriptor::new(
                LaneId::new(5).unwrap(),
                FailureDomain::new(9).unwrap(),
                EndpointProvider::Tcp,
                TopologyAction::Drain,
                "tcp://127.0.0.1:22424",
            )
            .unwrap()],
        )
        .unwrap();
        assert_eq!(
            TopologyAdvertisement::decode_payload(&drain.encode_payload().unwrap()).unwrap(),
            drain
        );
        TopologyPolicy::new(
            1,
            8,
            [EndpointProvider::Tcp],
            [FailureDomain::new(9).unwrap()],
            [TopologyAction::Drain],
        )
        .unwrap()
        .validate(&drain)
        .unwrap();

        let mut malformed = encoded;
        malformed[10] = 1;
        assert_eq!(
            TopologyAdvertisement::decode_payload(&malformed).unwrap_err(),
            TopologyError::NonZeroReserved
        );
    }

    #[test]
    fn topology_snapshot_is_bounded_at_thirty_two_lanes() {
        let descriptors = (1_u32..=32)
            .map(|id| {
                EndpointDescriptor::new(
                    LaneId::new(id).unwrap(),
                    FailureDomain::new(u64::from(id)).unwrap(),
                    EndpointProvider::Tcp,
                    TopologyAction::Add,
                    format!("tcp://127.0.0.1:{}", 24_000 + id),
                )
                .unwrap()
            })
            .collect::<Vec<_>>();
        TopologyAdvertisement::new(1, descriptors.clone()).unwrap();

        let mut oversized = descriptors;
        oversized.push(
            EndpointDescriptor::new(
                LaneId::new(33).unwrap(),
                FailureDomain::new(33).unwrap(),
                EndpointProvider::Tcp,
                TopologyAction::Add,
                "tcp://127.0.0.1:24033",
            )
            .unwrap(),
        );
        assert_eq!(
            TopologyAdvertisement::new(1, oversized).unwrap_err(),
            TopologyError::InvalidDescriptorCount(33)
        );
    }
}
