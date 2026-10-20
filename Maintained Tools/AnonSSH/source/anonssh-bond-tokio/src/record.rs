use std::error::Error;
use std::fmt;
use std::io::ErrorKind;

use anonssh_bond::Frame;
use bytes::Bytes;
use chacha20poly1305::aead::AeadInPlace;
use chacha20poly1305::{ChaCha20Poly1305, KeyInit, Nonce, Tag};
use tokio::io::{AsyncRead, AsyncReadExt};
use zeroize::Zeroizing;

const RECORD_MAGIC: [u8; 4] = *b"ABR1";
const RECORD_HEADER_LEN: usize = 20;
const AEAD_TAG_LEN: usize = 16;
const MAX_PLAINTEXT_LEN: usize = anonssh_bond::HEADER_LEN + anonssh_bond::MAX_FRAME_PAYLOAD;
const MAX_CIPHERTEXT_LEN: usize = MAX_PLAINTEXT_LEN + AEAD_TAG_LEN;

pub(crate) struct LaneRecordKeys {
    send: Zeroizing<[u8; 32]>,
    receive: Zeroizing<[u8; 32]>,
}

impl LaneRecordKeys {
    pub(crate) fn new(send: [u8; 32], receive: [u8; 32]) -> Self {
        Self {
            send: Zeroizing::new(send),
            receive: Zeroizing::new(receive),
        }
    }

    pub(crate) fn into_records(self) -> (RecordSealer, RecordOpener) {
        (
            RecordSealer::new(*self.send),
            RecordOpener::new(*self.receive),
        )
    }

    #[cfg(test)]
    pub(crate) fn test_bytes(&self) -> ([u8; 32], [u8; 32]) {
        (*self.send, *self.receive)
    }
}

pub(crate) struct RecordSealer {
    cipher: ChaCha20Poly1305,
    next_counter: u64,
}

impl RecordSealer {
    fn new(key: [u8; 32]) -> Self {
        let key = Zeroizing::new(key);
        Self {
            cipher: ChaCha20Poly1305::new_from_slice(&key[..])
                .expect("ChaCha20-Poly1305 accepts a 32-byte key"),
            next_counter: 0,
        }
    }

    #[cfg(test)]
    fn seal(&mut self, plaintext: &[u8]) -> Result<Vec<u8>, RecordError> {
        let mut record = Vec::new();
        self.seal_slices_into(plaintext.len(), &[plaintext], &mut record)?;
        Ok(record)
    }

    #[cfg(test)]
    pub(crate) fn seal_frame(&mut self, frame: &Frame) -> Result<Vec<u8>, RecordError> {
        let mut record = Vec::new();
        self.seal_frame_into(frame, &mut record)?;
        Ok(record)
    }

    pub(crate) fn seal_frame_into(
        &mut self,
        frame: &Frame,
        record: &mut Vec<u8>,
    ) -> Result<(), RecordError> {
        let frame_header = frame
            .encode_header()
            .map_err(|error| RecordError::InvalidFrame(error.to_string()))?;
        let plaintext_len = frame_header
            .len()
            .checked_add(frame.payload.len())
            .ok_or(RecordError::LengthOverflow)?;
        self.seal_slices_into(plaintext_len, &[&frame_header, &frame.payload], record)
    }

    fn seal_slices_into(
        &mut self,
        plaintext_len: usize,
        plaintext_parts: &[&[u8]],
        record: &mut Vec<u8>,
    ) -> Result<(), RecordError> {
        record.clear();
        if plaintext_len > MAX_PLAINTEXT_LEN {
            return Err(RecordError::PlaintextTooLarge(plaintext_len));
        }
        let parts_len = plaintext_parts.iter().try_fold(0_usize, |total, part| {
            total
                .checked_add(part.len())
                .ok_or(RecordError::LengthOverflow)
        })?;
        if parts_len != plaintext_len {
            return Err(RecordError::LengthOverflow);
        }
        let ciphertext_len = plaintext_len
            .checked_add(AEAD_TAG_LEN)
            .ok_or(RecordError::LengthOverflow)?;
        let ciphertext_len =
            u32::try_from(ciphertext_len).map_err(|_| RecordError::LengthOverflow)?;
        let header = encode_header(self.next_counter, ciphertext_len);
        let nonce_bytes = nonce(self.next_counter);
        record.reserve(RECORD_HEADER_LEN + plaintext_len + AEAD_TAG_LEN);
        record.extend_from_slice(&header);
        for part in plaintext_parts {
            record.extend_from_slice(part);
        }
        let tag = self
            .cipher
            .encrypt_in_place_detached(
                Nonce::from_slice(&nonce_bytes),
                &header,
                &mut record[RECORD_HEADER_LEN..],
            )
            .map_err(|_| RecordError::AuthenticationFailed)?;
        record.extend_from_slice(&tag);
        self.next_counter = self
            .next_counter
            .checked_add(1)
            .ok_or(RecordError::CounterExhausted)?;
        Ok(())
    }
}

pub(crate) struct RecordOpener {
    cipher: ChaCha20Poly1305,
    expected_counter: u64,
}

impl RecordOpener {
    fn new(key: [u8; 32]) -> Self {
        let key = Zeroizing::new(key);
        Self {
            cipher: ChaCha20Poly1305::new_from_slice(&key[..])
                .expect("ChaCha20-Poly1305 accepts a 32-byte key"),
            expected_counter: 0,
        }
    }

    pub(crate) async fn open<R>(&mut self, reader: &mut R) -> Result<Bytes, RecordError>
    where
        R: AsyncRead + Unpin,
    {
        let mut header = [0_u8; RECORD_HEADER_LEN];
        reader.read_exact(&mut header).await.map_err(io_error)?;
        let (counter, ciphertext_len) = decode_header(&header)?;
        if counter != self.expected_counter {
            return Err(RecordError::UnexpectedCounter {
                expected: self.expected_counter,
                actual: counter,
            });
        }
        let mut ciphertext = vec![0_u8; ciphertext_len];
        reader.read_exact(&mut ciphertext).await.map_err(io_error)?;
        let nonce_bytes = nonce(counter);
        let tag_offset = ciphertext
            .len()
            .checked_sub(AEAD_TAG_LEN)
            .ok_or(RecordError::InvalidCiphertextLength(ciphertext.len()))?;
        let tag = Tag::clone_from_slice(&ciphertext[tag_offset..]);
        ciphertext.truncate(tag_offset);
        self.cipher
            .decrypt_in_place_detached(
                Nonce::from_slice(&nonce_bytes),
                &header,
                &mut ciphertext,
                &tag,
            )
            .map_err(|_| RecordError::AuthenticationFailed)?;
        self.expected_counter = self
            .expected_counter
            .checked_add(1)
            .ok_or(RecordError::CounterExhausted)?;
        Ok(Bytes::from(ciphertext))
    }
}

fn encode_header(counter: u64, ciphertext_len: u32) -> [u8; RECORD_HEADER_LEN] {
    let mut header = [0_u8; RECORD_HEADER_LEN];
    header[..4].copy_from_slice(&RECORD_MAGIC);
    header[4..12].copy_from_slice(&counter.to_be_bytes());
    header[12..16].copy_from_slice(&ciphertext_len.to_be_bytes());
    header
}

fn decode_header(header: &[u8; RECORD_HEADER_LEN]) -> Result<(u64, usize), RecordError> {
    if header[..4] != RECORD_MAGIC || header[16..] != [0_u8; 4] {
        return Err(RecordError::InvalidHeader);
    }
    let counter = u64::from_be_bytes(header[4..12].try_into().expect("fixed counter"));
    let ciphertext_len =
        u32::from_be_bytes(header[12..16].try_into().expect("fixed length")) as usize;
    if !(AEAD_TAG_LEN..=MAX_CIPHERTEXT_LEN).contains(&ciphertext_len) {
        return Err(RecordError::InvalidCiphertextLength(ciphertext_len));
    }
    Ok((counter, ciphertext_len))
}

fn nonce(counter: u64) -> [u8; 12] {
    let mut bytes = [0_u8; 12];
    bytes[4..].copy_from_slice(&counter.to_be_bytes());
    bytes
}

fn io_error(error: std::io::Error) -> RecordError {
    if error.kind() == ErrorKind::UnexpectedEof {
        RecordError::Truncated
    } else {
        RecordError::Io(error.to_string())
    }
}

#[derive(Debug, Eq, PartialEq)]
pub enum RecordError {
    InvalidHeader,
    InvalidKey,
    InvalidFrame(String),
    PlaintextTooLarge(usize),
    InvalidCiphertextLength(usize),
    LengthOverflow,
    UnexpectedCounter { expected: u64, actual: u64 },
    CounterExhausted,
    AuthenticationFailed,
    Truncated,
    Io(String),
}

impl fmt::Display for RecordError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidHeader => write!(formatter, "invalid encrypted bond record header"),
            Self::InvalidKey => write!(formatter, "invalid encrypted bond record key"),
            Self::InvalidFrame(error) => write!(formatter, "invalid bond frame: {error}"),
            Self::PlaintextTooLarge(length) => {
                write!(formatter, "bond record plaintext is too large: {length}")
            }
            Self::InvalidCiphertextLength(length) => {
                write!(formatter, "invalid bond record ciphertext length {length}")
            }
            Self::LengthOverflow => write!(formatter, "bond record length overflow"),
            Self::UnexpectedCounter { expected, actual } => write!(
                formatter,
                "unexpected bond record counter {actual}; expected {expected}"
            ),
            Self::CounterExhausted => write!(formatter, "bond record counter exhausted"),
            Self::AuthenticationFailed => write!(formatter, "bond record authentication failed"),
            Self::Truncated => write!(formatter, "encrypted bond record was truncated"),
            Self::Io(error) => write!(formatter, "encrypted bond record I/O failed: {error}"),
        }
    }
}

impl Error for RecordError {}

#[cfg(test)]
mod tests {
    use anonssh_bond::{Frame, FrameFlags, FrameKind, HEADER_LEN};
    use tokio::io::AsyncWriteExt;

    use super::{LaneRecordKeys, RecordError};

    #[test]
    fn frame_sealing_reuses_lane_writer_storage() {
        let frame = Frame::new(
            FrameKind::Data,
            FrameFlags::NONE,
            7,
            3,
            0,
            vec![0x5a; 32 * 1024],
        )
        .unwrap();
        let (mut sealer, _) = LaneRecordKeys::new([19; 32], [19; 32]).into_records();
        let mut record = Vec::new();
        sealer.seal_frame_into(&frame, &mut record).unwrap();
        let allocation = record.as_ptr();
        let capacity = record.capacity();

        sealer.seal_frame_into(&frame, &mut record).unwrap();
        assert_eq!(record.as_ptr(), allocation);
        assert_eq!(record.capacity(), capacity);
    }

    #[tokio::test]
    async fn records_reject_tampering_replay_and_truncation() {
        let keys = LaneRecordKeys::new([7; 32], [7; 32]);
        let (mut sealer, mut opener) = keys.into_records();
        let first = sealer.seal(b"secret payload").unwrap();
        let (mut sender, mut receiver) = tokio::io::duplex(4096);
        sender.write_all(&first).await.unwrap();
        assert_eq!(
            opener.open(&mut receiver).await.unwrap().as_ref(),
            b"secret payload"
        );

        sender.write_all(&first).await.unwrap();
        assert_eq!(
            opener.open(&mut receiver).await.unwrap_err(),
            RecordError::UnexpectedCounter {
                expected: 1,
                actual: 0
            }
        );

        let keys = LaneRecordKeys::new([9; 32], [9; 32]);
        let (mut sealer, mut opener) = keys.into_records();
        let mut tampered = sealer.seal(b"authenticated").unwrap();
        *tampered.last_mut().unwrap() ^= 1;
        let (mut sender, mut receiver) = tokio::io::duplex(4096);
        sender.write_all(&tampered).await.unwrap();
        assert_eq!(
            opener.open(&mut receiver).await.unwrap_err(),
            RecordError::AuthenticationFailed
        );

        let (mut foreign_sealer, _) = LaneRecordKeys::new([12; 32], [12; 32]).into_records();
        let (_, mut local_opener) = LaneRecordKeys::new([13; 32], [13; 32]).into_records();
        let substituted = foreign_sealer.seal(b"other session").unwrap();
        let (mut sender, mut receiver) = tokio::io::duplex(4096);
        sender.write_all(&substituted).await.unwrap();
        assert_eq!(
            local_opener.open(&mut receiver).await.unwrap_err(),
            RecordError::AuthenticationFailed
        );

        let keys = LaneRecordKeys::new([11; 32], [11; 32]);
        let (mut sealer, mut opener) = keys.into_records();
        let mut truncated = sealer.seal(b"truncated").unwrap();
        truncated.pop();
        let (mut sender, mut receiver) = tokio::io::duplex(4096);
        sender.write_all(&truncated).await.unwrap();
        drop(sender);
        assert_eq!(
            opener.open(&mut receiver).await.unwrap_err(),
            RecordError::Truncated
        );
    }

    #[tokio::test]
    async fn frame_record_opens_in_place_and_decodes_by_owned_slice() {
        let frame = Frame::new(
            FrameKind::Data,
            FrameFlags::NONE,
            7,
            3,
            0,
            b"one final ciphertext materialization".to_vec(),
        )
        .unwrap();
        let keys = LaneRecordKeys::new([17; 32], [17; 32]);
        let (mut sealer, mut opener) = keys.into_records();
        let record = sealer.seal_frame(&frame).unwrap();
        let (mut sender, mut receiver) = tokio::io::duplex(4096);
        sender.write_all(&record).await.unwrap();

        let plaintext = opener.open(&mut receiver).await.unwrap();
        let payload_pointer = plaintext[HEADER_LEN..].as_ptr();
        let plaintext_len = plaintext.len();
        let (decoded, consumed) = Frame::decode_owned(plaintext).unwrap();
        assert_eq!(consumed, plaintext_len);
        assert_eq!(decoded, frame);
        assert_eq!(decoded.payload.as_ptr(), payload_pointer);
    }
}
