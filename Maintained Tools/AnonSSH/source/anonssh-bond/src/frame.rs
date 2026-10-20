use std::error::Error;
use std::fmt;

use bytes::Bytes;

const MAGIC: [u8; 4] = *b"ABP1";
pub const HEADER_LEN: usize = 40;
pub const MAX_FRAME_PAYLOAD: usize = 64 * 1024;
const VALID_FLAGS: u8 =
    FrameFlags::END_STREAM.0 | FrameFlags::RETRANSMISSION.0 | FrameFlags::ACKNOWLEDGEMENT.0;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub enum FrameKind {
    Data = 1,
    Acknowledgement = 2,
    WindowUpdate = 3,
    LaneJoin = 4,
    LaneAccept = 5,
    Ping = 6,
    Pong = 7,
    StreamOpen = 8,
    StreamClose = 9,
    StreamReset = 10,
    EndpointAdvertisement = 11,
    SessionClose = 12,
    CapabilityAdvertisement = 13,
}

impl TryFrom<u8> for FrameKind {
    type Error = ProtocolError;

    fn try_from(value: u8) -> Result<Self, Self::Error> {
        match value {
            1 => Ok(Self::Data),
            2 => Ok(Self::Acknowledgement),
            3 => Ok(Self::WindowUpdate),
            4 => Ok(Self::LaneJoin),
            5 => Ok(Self::LaneAccept),
            6 => Ok(Self::Ping),
            7 => Ok(Self::Pong),
            8 => Ok(Self::StreamOpen),
            9 => Ok(Self::StreamClose),
            10 => Ok(Self::StreamReset),
            11 => Ok(Self::EndpointAdvertisement),
            12 => Ok(Self::SessionClose),
            13 => Ok(Self::CapabilityAdvertisement),
            _ => Err(ProtocolError::UnknownFrameKind(value)),
        }
    }
}

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct FrameFlags(u8);

impl FrameFlags {
    pub const NONE: Self = Self(0);
    pub const END_STREAM: Self = Self(1 << 0);
    pub const RETRANSMISSION: Self = Self(1 << 1);
    pub const ACKNOWLEDGEMENT: Self = Self(1 << 2);

    pub const fn bits(self) -> u8 {
        self.0
    }

    pub const fn contains(self, other: Self) -> bool {
        self.0 & other.0 == other.0
    }

    pub const fn union(self, other: Self) -> Self {
        Self(self.0 | other.0)
    }

    fn from_bits(bits: u8) -> Result<Self, ProtocolError> {
        if bits & !VALID_FLAGS == 0 {
            Ok(Self(bits))
        } else {
            Err(ProtocolError::InvalidFlags(bits))
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FrameHeader {
    pub kind: FrameKind,
    pub flags: FrameFlags,
    pub session_id: u64,
    pub stream_id: u64,
    pub offset: u64,
    pub payload_len: u32,
}

impl FrameHeader {
    pub fn new(
        kind: FrameKind,
        flags: FrameFlags,
        session_id: u64,
        stream_id: u64,
        offset: u64,
        payload_len: usize,
    ) -> Result<Self, ProtocolError> {
        let payload_len =
            u32::try_from(payload_len).map_err(|_| ProtocolError::PayloadTooLarge(payload_len))?;
        let header = Self {
            kind,
            flags,
            session_id,
            stream_id,
            offset,
            payload_len,
        };
        header.validate()?;
        Ok(header)
    }

    fn validate(&self) -> Result<(), ProtocolError> {
        if self.session_id == 0 {
            return Err(ProtocolError::ZeroSessionId);
        }
        if self.payload_len as usize > MAX_FRAME_PAYLOAD {
            return Err(ProtocolError::PayloadTooLarge(self.payload_len as usize));
        }
        let allowed_flags = match self.kind {
            FrameKind::Data => FrameFlags::END_STREAM.0 | FrameFlags::RETRANSMISSION.0,
            FrameKind::StreamOpen | FrameKind::StreamClose | FrameKind::SessionClose => {
                FrameFlags::ACKNOWLEDGEMENT.0
            }
            _ => 0,
        };
        if self.flags.bits() & !allowed_flags != 0 {
            return Err(ProtocolError::InvalidFlags(self.flags.bits()));
        }
        if self.kind == FrameKind::Data {
            if self.stream_id == 0 {
                return Err(ProtocolError::ZeroDataStreamId);
            }
            if self.payload_len == 0 {
                return Err(ProtocolError::EmptyDataFrame);
            }
        }
        Ok(())
    }

    pub fn encode(&self) -> Result<[u8; HEADER_LEN], ProtocolError> {
        self.validate()?;
        let mut output = [0_u8; HEADER_LEN];
        output[0..4].copy_from_slice(&MAGIC);
        output[4] = self.kind as u8;
        output[5] = self.flags.bits();
        output[6..8].copy_from_slice(&(HEADER_LEN as u16).to_be_bytes());
        output[8..16].copy_from_slice(&self.session_id.to_be_bytes());
        output[16..24].copy_from_slice(&self.stream_id.to_be_bytes());
        output[24..32].copy_from_slice(&self.offset.to_be_bytes());
        output[32..36].copy_from_slice(&self.payload_len.to_be_bytes());
        Ok(output)
    }

    pub fn decode(input: &[u8]) -> Result<Self, FrameDecodeError> {
        if input.len() < HEADER_LEN {
            return Err(FrameDecodeError::Incomplete {
                needed: HEADER_LEN - input.len(),
            });
        }
        if input[0..4] != MAGIC {
            return Err(ProtocolError::InvalidMagic.into());
        }
        let declared_len = u16::from_be_bytes([input[6], input[7]]) as usize;
        if declared_len != HEADER_LEN {
            return Err(ProtocolError::InvalidHeaderLength(declared_len).into());
        }
        if input[36..40] != [0_u8; 4] {
            return Err(ProtocolError::NonZeroReserved.into());
        }
        let header = Self {
            kind: FrameKind::try_from(input[4])?,
            flags: FrameFlags::from_bits(input[5])?,
            session_id: u64::from_be_bytes(input[8..16].try_into().expect("fixed slice")),
            stream_id: u64::from_be_bytes(input[16..24].try_into().expect("fixed slice")),
            offset: u64::from_be_bytes(input[24..32].try_into().expect("fixed slice")),
            payload_len: u32::from_be_bytes(input[32..36].try_into().expect("fixed slice")),
        };
        header.validate()?;
        Ok(header)
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Frame {
    pub header: FrameHeader,
    pub payload: Bytes,
}

impl Frame {
    pub fn new(
        kind: FrameKind,
        flags: FrameFlags,
        session_id: u64,
        stream_id: u64,
        offset: u64,
        payload: impl Into<Bytes>,
    ) -> Result<Self, ProtocolError> {
        let payload = payload.into();
        let header = FrameHeader::new(kind, flags, session_id, stream_id, offset, payload.len())?;
        Ok(Self { header, payload })
    }

    pub fn encode_header(&self) -> Result<[u8; HEADER_LEN], ProtocolError> {
        self.validate_payload_length()?;
        self.header.encode()
    }

    pub fn encode(&self) -> Result<Vec<u8>, ProtocolError> {
        let header = self.encode_header()?;
        let total = HEADER_LEN
            .checked_add(self.payload.len())
            .ok_or(ProtocolError::LengthOverflow)?;
        let mut output = Vec::with_capacity(total);
        output.extend_from_slice(&header);
        output.extend_from_slice(&self.payload);
        Ok(output)
    }

    pub fn decode(input: &[u8]) -> Result<(Self, usize), FrameDecodeError> {
        let header = FrameHeader::decode(input)?;
        let payload_len = header.payload_len as usize;
        let total = HEADER_LEN
            .checked_add(payload_len)
            .ok_or(ProtocolError::LengthOverflow)?;
        if input.len() < total {
            return Err(FrameDecodeError::Incomplete {
                needed: total - input.len(),
            });
        }
        Ok((
            Self {
                header,
                payload: Bytes::copy_from_slice(&input[HEADER_LEN..total]),
            },
            total,
        ))
    }

    pub fn decode_owned(input: Bytes) -> Result<(Self, usize), FrameDecodeError> {
        let header = FrameHeader::decode(&input)?;
        let payload_len = header.payload_len as usize;
        let total = HEADER_LEN
            .checked_add(payload_len)
            .ok_or(ProtocolError::LengthOverflow)?;
        if input.len() < total {
            return Err(FrameDecodeError::Incomplete {
                needed: total - input.len(),
            });
        }
        let payload = input.slice(HEADER_LEN..total);
        Ok((Self { header, payload }, total))
    }

    fn validate_payload_length(&self) -> Result<(), ProtocolError> {
        if self.header.payload_len as usize != self.payload.len() {
            return Err(ProtocolError::PayloadLengthMismatch {
                declared: self.header.payload_len as usize,
                actual: self.payload.len(),
            });
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum FrameDecodeError {
    Incomplete { needed: usize },
    Protocol(ProtocolError),
}

impl From<ProtocolError> for FrameDecodeError {
    fn from(value: ProtocolError) -> Self {
        Self::Protocol(value)
    }
}

impl fmt::Display for FrameDecodeError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Incomplete { needed } => write!(formatter, "frame needs {needed} more bytes"),
            Self::Protocol(error) => error.fmt(formatter),
        }
    }
}

impl Error for FrameDecodeError {}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ProtocolError {
    InvalidMagic,
    InvalidHeaderLength(usize),
    UnknownFrameKind(u8),
    InvalidFlags(u8),
    NonZeroReserved,
    ZeroSessionId,
    ZeroDataStreamId,
    EmptyDataFrame,
    PayloadTooLarge(usize),
    PayloadLengthMismatch { declared: usize, actual: usize },
    LengthOverflow,
}

impl fmt::Display for ProtocolError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidMagic => write!(formatter, "invalid ABP magic"),
            Self::InvalidHeaderLength(length) => {
                write!(formatter, "invalid ABP header length {length}")
            }
            Self::UnknownFrameKind(kind) => write!(formatter, "unknown ABP frame kind {kind}"),
            Self::InvalidFlags(flags) => write!(formatter, "invalid ABP flags 0x{flags:02x}"),
            Self::NonZeroReserved => write!(formatter, "ABP reserved header field is non-zero"),
            Self::ZeroSessionId => write!(formatter, "ABP session ID must be non-zero"),
            Self::ZeroDataStreamId => write!(formatter, "ABP data stream ID must be non-zero"),
            Self::EmptyDataFrame => write!(formatter, "ABP data frame must not be empty"),
            Self::PayloadTooLarge(length) => {
                write!(formatter, "ABP payload is too large: {length}")
            }
            Self::PayloadLengthMismatch { declared, actual } => write!(
                formatter,
                "ABP payload length mismatch: declared {declared}, actual {actual}"
            ),
            Self::LengthOverflow => write!(formatter, "ABP frame length overflow"),
        }
    }
}

impl Error for ProtocolError {}

#[cfg(test)]
mod tests {
    use bytes::Bytes;

    use super::{
        Frame, FrameDecodeError, FrameFlags, FrameKind, ProtocolError, HEADER_LEN,
        MAX_FRAME_PAYLOAD,
    };

    #[test]
    fn frame_round_trip_is_explicit_and_incremental() {
        let frame = Frame::new(
            FrameKind::Data,
            FrameFlags::END_STREAM,
            7,
            11,
            19,
            b"bonded payload".to_vec(),
        )
        .unwrap();
        let encoded = frame.encode().unwrap();
        assert_eq!(&encoded[..4], b"ABP1");
        assert_eq!(encoded.len(), HEADER_LEN + frame.payload.len());
        assert_eq!(
            Frame::decode(&encoded[..HEADER_LEN + 2]),
            Err(FrameDecodeError::Incomplete {
                needed: frame.payload.len() - 2
            })
        );
        assert_eq!(Frame::decode(&encoded).unwrap(), (frame, encoded.len()));
    }

    #[test]
    fn owned_decode_slices_the_input_allocation() {
        let frame = Frame::new(
            FrameKind::Data,
            FrameFlags::NONE,
            7,
            11,
            0,
            b"shared payload".to_vec(),
        )
        .unwrap();
        let encoded = Bytes::from(frame.encode().unwrap());
        let expected_payload_pointer = encoded[HEADER_LEN..].as_ptr();
        let (decoded, consumed) = Frame::decode_owned(encoded).unwrap();
        assert_eq!(consumed, HEADER_LEN + decoded.payload.len());
        assert_eq!(decoded.payload.as_ptr(), expected_payload_pointer);
    }

    #[test]
    fn malformed_headers_fail_closed() {
        let frame = Frame::new(FrameKind::Data, FrameFlags::NONE, 1, 1, 0, vec![1]).unwrap();
        let encoded = frame.encode().unwrap();

        let mut bad_magic = encoded.clone();
        bad_magic[0] = b'X';
        assert_eq!(
            Frame::decode(&bad_magic),
            Err(FrameDecodeError::Protocol(ProtocolError::InvalidMagic))
        );

        let mut unknown_flags = encoded.clone();
        unknown_flags[5] = 0x80;
        assert_eq!(
            Frame::decode(&unknown_flags),
            Err(FrameDecodeError::Protocol(ProtocolError::InvalidFlags(
                0x80
            )))
        );

        let mut reserved = encoded;
        reserved[39] = 1;
        assert_eq!(
            Frame::decode(&reserved),
            Err(FrameDecodeError::Protocol(ProtocolError::NonZeroReserved))
        );
    }

    #[test]
    fn data_frames_are_bounded_and_addressed() {
        assert!(matches!(
            Frame::new(FrameKind::Data, FrameFlags::NONE, 1, 0, 0, vec![1]),
            Err(ProtocolError::ZeroDataStreamId)
        ));
        assert!(matches!(
            Frame::new(FrameKind::Data, FrameFlags::NONE, 1, 1, 0, Vec::new()),
            Err(ProtocolError::EmptyDataFrame)
        ));
        assert!(matches!(
            Frame::new(
                FrameKind::Data,
                FrameFlags::NONE,
                1,
                1,
                0,
                vec![0; MAX_FRAME_PAYLOAD + 1]
            ),
            Err(ProtocolError::PayloadTooLarge(_))
        ));
    }
}
