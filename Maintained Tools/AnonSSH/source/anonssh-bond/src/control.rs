use std::error::Error;
use std::fmt;

use bytes::Bytes;

use crate::TrafficClass;

pub const MAX_ACK_RANGES: usize = 32;
const ACK_PREFIX_LEN: usize = 4;
const ACK_RANGE_LEN: usize = 16;
const EMPTY_ACK_PAYLOAD: [u8; ACK_PREFIX_LEN] = [0; ACK_PREFIX_LEN];
const STREAM_OPEN_LEN: usize = 16;
const STREAM_RESET_LEN: usize = 4;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct AckRange {
    pub start: u64,
    pub end: u64,
}

impl AckRange {
    pub fn new(start: u64, end: u64) -> Result<Self, ControlError> {
        if start >= end {
            return Err(ControlError::InvalidAckRange { start, end });
        }
        Ok(Self { start, end })
    }

    pub const fn contains(self, start: u64, end: u64) -> bool {
        self.start <= start && end <= self.end
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SelectiveAcknowledgement {
    pub cumulative: u64,
    pub ranges: Vec<AckRange>,
}

impl SelectiveAcknowledgement {
    pub fn new(cumulative: u64, ranges: Vec<AckRange>) -> Result<Self, ControlError> {
        validate_ack_ranges(cumulative, &ranges)?;
        Ok(Self { cumulative, ranges })
    }

    pub fn encode_payload(&self) -> Result<Vec<u8>, ControlError> {
        Self::encode_payload_parts(self.cumulative, &self.ranges)
    }

    pub fn encode_payload_parts(
        cumulative: u64,
        ranges: &[AckRange],
    ) -> Result<Vec<u8>, ControlError> {
        Ok(Self::encode_payload_shared_parts(cumulative, ranges)?.to_vec())
    }

    pub fn encode_payload_shared_parts(
        cumulative: u64,
        ranges: &[AckRange],
    ) -> Result<Bytes, ControlError> {
        validate_ack_ranges(cumulative, ranges)?;
        if ranges.is_empty() {
            return Ok(Bytes::from_static(&EMPTY_ACK_PAYLOAD));
        }
        let count = u16::try_from(ranges.len())
            .map_err(|_| ControlError::TooManyAckRanges(ranges.len()))?;
        let mut payload = Vec::with_capacity(ACK_PREFIX_LEN + ranges.len() * ACK_RANGE_LEN);
        payload.extend_from_slice(&count.to_be_bytes());
        payload.extend_from_slice(&[0_u8; 2]);
        for range in ranges {
            payload.extend_from_slice(&range.start.to_be_bytes());
            payload.extend_from_slice(&range.end.to_be_bytes());
        }
        Ok(Bytes::from(payload))
    }

    pub fn decode_payload(cumulative: u64, payload: &[u8]) -> Result<Self, ControlError> {
        let mut ranges = Vec::new();
        Self::decode_payload_into(cumulative, payload, &mut ranges)?;
        Ok(Self { cumulative, ranges })
    }

    pub fn decode_payload_into(
        cumulative: u64,
        payload: &[u8],
        ranges: &mut Vec<AckRange>,
    ) -> Result<(), ControlError> {
        ranges.clear();
        if payload.len() < ACK_PREFIX_LEN {
            return Err(ControlError::InvalidAckPayloadLength(payload.len()));
        }
        if payload[2..4] != [0_u8; 2] {
            return Err(ControlError::NonZeroReserved);
        }
        let count = u16::from_be_bytes([payload[0], payload[1]]) as usize;
        if count > MAX_ACK_RANGES {
            return Err(ControlError::TooManyAckRanges(count));
        }
        let expected = ACK_PREFIX_LEN
            .checked_add(
                count
                    .checked_mul(ACK_RANGE_LEN)
                    .ok_or(ControlError::LengthOverflow)?,
            )
            .ok_or(ControlError::LengthOverflow)?;
        if payload.len() != expected {
            return Err(ControlError::InvalidAckPayloadLength(payload.len()));
        }
        ranges.reserve(count);
        let (encoded_ranges, remainder) = payload[ACK_PREFIX_LEN..].as_chunks::<ACK_RANGE_LEN>();
        debug_assert!(remainder.is_empty());
        let mut previous_end = cumulative;
        for encoded in encoded_ranges {
            let start = u64::from_be_bytes(encoded[..8].try_into().expect("fixed range start"));
            let end = u64::from_be_bytes(encoded[8..].try_into().expect("fixed range end"));
            if start < cumulative || start < previous_end || start >= end {
                ranges.clear();
                return Err(ControlError::InvalidAckRange { start, end });
            }
            ranges.push(AckRange { start, end });
            previous_end = end;
        }
        Ok(())
    }
}

pub(crate) fn validate_ack_ranges(
    cumulative: u64,
    ranges: &[AckRange],
) -> Result<(), ControlError> {
    if ranges.len() > MAX_ACK_RANGES {
        return Err(ControlError::TooManyAckRanges(ranges.len()));
    }
    let mut previous_end = cumulative;
    for range in ranges {
        if range.start < cumulative || range.start < previous_end || range.start >= range.end {
            return Err(ControlError::InvalidAckRange {
                start: range.start,
                end: range.end,
            });
        }
        previous_end = range.end;
    }
    Ok(())
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct StreamOpen {
    pub class: TrafficClass,
    pub receive_window_end: u64,
}

impl StreamOpen {
    pub fn new(class: TrafficClass, receive_window_end: u64) -> Result<Self, ControlError> {
        if receive_window_end == 0 {
            return Err(ControlError::ZeroReceiveWindow);
        }
        Ok(Self {
            class,
            receive_window_end,
        })
    }

    pub fn encode_payload(self) -> [u8; STREAM_OPEN_LEN] {
        let mut payload = [0_u8; STREAM_OPEN_LEN];
        payload[0] = match self.class {
            TrafficClass::Control => 1,
            TrafficClass::Realtime => 2,
            TrafficClass::Bulk => 3,
            TrafficClass::Interactive => 4,
        };
        payload[8..].copy_from_slice(&self.receive_window_end.to_be_bytes());
        payload
    }

    pub fn decode_payload(payload: &[u8]) -> Result<Self, ControlError> {
        if payload.len() != STREAM_OPEN_LEN {
            return Err(ControlError::InvalidStreamOpenLength(payload.len()));
        }
        if payload[1..8] != [0_u8; 7] {
            return Err(ControlError::NonZeroReserved);
        }
        let class = match payload[0] {
            1 => TrafficClass::Control,
            2 => TrafficClass::Realtime,
            3 => TrafficClass::Bulk,
            4 => TrafficClass::Interactive,
            value => return Err(ControlError::UnknownTrafficClass(value)),
        };
        let receive_window_end =
            u64::from_be_bytes(payload[8..].try_into().expect("fixed receive window"));
        Self::new(class, receive_window_end)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct StreamReset {
    pub code: u32,
}

impl StreamReset {
    pub const fn new(code: u32) -> Self {
        Self { code }
    }

    pub const fn encode_payload(self) -> [u8; STREAM_RESET_LEN] {
        self.code.to_be_bytes()
    }

    pub fn decode_payload(payload: &[u8]) -> Result<Self, ControlError> {
        if payload.len() != STREAM_RESET_LEN {
            return Err(ControlError::InvalidStreamResetLength(payload.len()));
        }
        Ok(Self {
            code: u32::from_be_bytes(payload.try_into().expect("fixed reset code")),
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ControlError {
    TooManyAckRanges(usize),
    InvalidAckRange { start: u64, end: u64 },
    InvalidAckPayloadLength(usize),
    InvalidStreamOpenLength(usize),
    InvalidStreamResetLength(usize),
    UnknownTrafficClass(u8),
    ZeroReceiveWindow,
    NonZeroReserved,
    LengthOverflow,
}

impl fmt::Display for ControlError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::TooManyAckRanges(count) => {
                write!(formatter, "too many acknowledgement ranges: {count}")
            }
            Self::InvalidAckRange { start, end } => {
                write!(formatter, "invalid acknowledgement range {start}..{end}")
            }
            Self::InvalidAckPayloadLength(length) => {
                write!(formatter, "invalid acknowledgement payload length {length}")
            }
            Self::InvalidStreamOpenLength(length) => {
                write!(formatter, "invalid stream-open payload length {length}")
            }
            Self::InvalidStreamResetLength(length) => {
                write!(formatter, "invalid stream-reset payload length {length}")
            }
            Self::UnknownTrafficClass(value) => write!(formatter, "unknown traffic class {value}"),
            Self::ZeroReceiveWindow => write!(formatter, "stream receive window must be non-zero"),
            Self::NonZeroReserved => {
                write!(formatter, "control payload reserved bytes are non-zero")
            }
            Self::LengthOverflow => write!(formatter, "control payload length overflow"),
        }
    }
}

impl Error for ControlError {}

#[cfg(test)]
mod tests {
    use super::{AckRange, SelectiveAcknowledgement, StreamOpen, StreamReset, MAX_ACK_RANGES};
    use crate::TrafficClass;

    #[test]
    fn selective_acknowledgements_round_trip_and_fail_closed() {
        let acknowledgement = SelectiveAcknowledgement::new(
            100,
            vec![
                AckRange::new(120, 140).unwrap(),
                AckRange::new(160, 200).unwrap(),
            ],
        )
        .unwrap();
        let payload = acknowledgement.encode_payload().unwrap();
        assert_eq!(
            SelectiveAcknowledgement::encode_payload_parts(
                acknowledgement.cumulative,
                &acknowledgement.ranges,
            )
            .unwrap(),
            payload
        );
        assert_eq!(
            SelectiveAcknowledgement::decode_payload(100, &payload).unwrap(),
            acknowledgement
        );

        let mut scratch = Vec::with_capacity(MAX_ACK_RANGES);
        let capacity = scratch.capacity();
        SelectiveAcknowledgement::decode_payload_into(100, &payload, &mut scratch).unwrap();
        assert_eq!(scratch, acknowledgement.ranges);
        assert_eq!(scratch.capacity(), capacity);

        let first_empty = SelectiveAcknowledgement::encode_payload_shared_parts(100, &[]).unwrap();
        let second_empty = SelectiveAcknowledgement::encode_payload_shared_parts(200, &[]).unwrap();
        assert_eq!(first_empty, [0; 4][..]);
        assert_eq!(first_empty.as_ptr(), second_empty.as_ptr());

        let mut reserved = payload.clone();
        reserved[3] = 1;
        assert!(SelectiveAcknowledgement::decode_payload(100, &reserved).is_err());
        assert!(
            SelectiveAcknowledgement::decode_payload_into(100, &reserved, &mut scratch).is_err()
        );
        assert!(scratch.is_empty());
        assert_eq!(scratch.capacity(), capacity);
        assert!(SelectiveAcknowledgement::new(100, vec![AckRange::new(90, 110).unwrap()]).is_err());
        assert!(SelectiveAcknowledgement::new(
            0,
            (0..=MAX_ACK_RANGES)
                .map(|index| AckRange::new(index as u64 * 2, index as u64 * 2 + 1).unwrap())
                .collect()
        )
        .is_err());
    }

    #[test]
    fn stream_control_payloads_are_explicit() {
        let open = StreamOpen::new(TrafficClass::Realtime, 65_536).unwrap();
        assert_eq!(
            StreamOpen::decode_payload(&open.encode_payload()).unwrap(),
            open
        );
        assert!(StreamOpen::decode_payload(&open.encode_payload()[..15]).is_err());
        let interactive = StreamOpen::new(TrafficClass::Interactive, 65_536).unwrap();
        assert_eq!(interactive.encode_payload()[0], 4);
        assert_eq!(
            StreamOpen::decode_payload(&interactive.encode_payload()).unwrap(),
            interactive
        );

        let reset = StreamReset::new(7);
        assert_eq!(
            StreamReset::decode_payload(&reset.encode_payload()).unwrap(),
            reset
        );
        assert!(StreamReset::decode_payload(&[0; 3]).is_err());
    }
}
