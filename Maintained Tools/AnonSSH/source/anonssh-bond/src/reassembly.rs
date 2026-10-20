use std::collections::BTreeMap;
use std::error::Error;
use std::fmt;

use bytes::{Bytes, BytesMut};

use crate::AckRange;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Delivery {
    pub bytes: Bytes,
    pub accepted_bytes: usize,
    pub next_offset: u64,
    pub buffered_bytes: usize,
    pub reorder_high_water: usize,
}

#[derive(Debug)]
pub struct Reassembler {
    next_offset: u64,
    max_buffered_bytes: usize,
    buffered_bytes: usize,
    reorder_high_water: usize,
    segments: BTreeMap<u64, Bytes>,
    #[cfg(test)]
    segment_insertions: usize,
}

impl Reassembler {
    pub fn new(start_offset: u64, max_buffered_bytes: usize) -> Result<Self, ReassemblyError> {
        if max_buffered_bytes == 0 {
            return Err(ReassemblyError::ZeroBufferLimit);
        }
        Ok(Self {
            next_offset: start_offset,
            max_buffered_bytes,
            buffered_bytes: 0,
            reorder_high_water: 0,
            segments: BTreeMap::new(),
            #[cfg(test)]
            segment_insertions: 0,
        })
    }

    pub fn insert(&mut self, offset: u64, bytes: &[u8]) -> Result<Delivery, ReassemblyError> {
        self.insert_shared(offset, Bytes::copy_from_slice(bytes))
    }

    pub fn insert_shared(
        &mut self,
        mut offset: u64,
        mut bytes: Bytes,
    ) -> Result<Delivery, ReassemblyError> {
        if bytes.is_empty() {
            return Err(ReassemblyError::EmptySegment);
        }
        let original_end = checked_end(offset, bytes.len())?;
        if original_end <= self.next_offset {
            return Ok(self.delivery(Bytes::new(), 0));
        }
        if offset < self.next_offset {
            let delivered = usize::try_from(self.next_offset - offset)
                .map_err(|_| ReassemblyError::OffsetOverflow)?;
            bytes = bytes.slice(delivered..);
            offset = self.next_offset;
        }
        let end = checked_end(offset, bytes.len())?;

        if let Some(existing) = self.segments.get(&offset) {
            if existing == &bytes {
                return Ok(self.delivery(Bytes::new(), 0));
            }
            return Err(ReassemblyError::ConflictingOverlap);
        }
        if let Some((&previous_offset, previous)) = self.segments.range(..offset).next_back() {
            if checked_end(previous_offset, previous.len())? > offset {
                return Err(ReassemblyError::ConflictingOverlap);
            }
        }
        if self
            .segments
            .range(offset..)
            .next()
            .is_some_and(|(&next_offset, _)| next_offset < end)
        {
            return Err(ReassemblyError::ConflictingOverlap);
        }

        let distance =
            usize::try_from(end - self.next_offset).map_err(|_| ReassemblyError::OffsetOverflow)?;
        if distance > self.max_buffered_bytes {
            return Err(ReassemblyError::ReorderWindowExceeded {
                attempted: distance,
                limit: self.max_buffered_bytes,
            });
        }
        let new_buffered = self
            .buffered_bytes
            .checked_add(bytes.len())
            .ok_or(ReassemblyError::BufferAccountingOverflow)?;
        if new_buffered > self.max_buffered_bytes {
            return Err(ReassemblyError::BufferLimitExceeded {
                attempted: new_buffered,
                limit: self.max_buffered_bytes,
            });
        }
        let accepted_bytes = bytes.len();
        self.reorder_high_water = self.reorder_high_water.max(new_buffered);
        if offset != self.next_offset {
            self.segments.insert(offset, bytes);
            self.buffered_bytes = new_buffered;
            #[cfg(test)]
            {
                self.segment_insertions += 1;
            }
            return Ok(self.delivery(Bytes::new(), accepted_bytes));
        }

        self.next_offset = end;
        let first = bytes;
        let contiguous = if let Some(second) = self.segments.remove(&self.next_offset) {
            self.buffered_bytes -= second.len();
            self.next_offset = checked_end(self.next_offset, second.len())?;
            let mut merged = BytesMut::with_capacity(first.len() + second.len());
            merged.extend_from_slice(&first);
            merged.extend_from_slice(&second);
            while let Some(segment) = self.segments.remove(&self.next_offset) {
                self.buffered_bytes -= segment.len();
                self.next_offset = checked_end(self.next_offset, segment.len())?;
                merged.extend_from_slice(&segment);
            }
            merged.freeze()
        } else {
            first
        };
        Ok(self.delivery(contiguous, accepted_bytes))
    }

    pub const fn next_offset(&self) -> u64 {
        self.next_offset
    }

    pub const fn buffered_bytes(&self) -> usize {
        self.buffered_bytes
    }

    pub const fn reorder_high_water(&self) -> usize {
        self.reorder_high_water
    }

    pub fn acknowledgement_ranges(&self, max_ranges: usize) -> Vec<AckRange> {
        let mut ranges: Vec<AckRange> = Vec::new();
        self.acknowledgement_ranges_into(max_ranges, &mut ranges);
        ranges
    }

    pub fn acknowledgement_ranges_into(&self, max_ranges: usize, ranges: &mut Vec<AckRange>) {
        ranges.clear();
        for (&start, bytes) in &self.segments {
            let end = start + bytes.len() as u64;
            if let Some(previous) = ranges.last_mut() {
                if previous.end == start {
                    previous.end = end;
                    continue;
                }
            }
            if ranges.len() == max_ranges {
                break;
            }
            ranges.push(AckRange { start, end });
        }
    }

    pub fn acknowledgement_range_count(&self, max_ranges: usize) -> usize {
        let mut count = 0;
        let mut previous_end = None;
        for (&start, bytes) in &self.segments {
            let end = start + bytes.len() as u64;
            if previous_end == Some(start) {
                previous_end = Some(end);
                continue;
            }
            if count == max_ranges {
                break;
            }
            count += 1;
            previous_end = Some(end);
        }
        count
    }

    pub fn highest_buffered_end(&self) -> Result<Option<u64>, ReassemblyError> {
        self.segments
            .iter()
            .next_back()
            .map(|(&start, bytes)| checked_end(start, bytes.len()))
            .transpose()
    }

    fn delivery(&self, bytes: Bytes, accepted_bytes: usize) -> Delivery {
        Delivery {
            bytes,
            accepted_bytes,
            next_offset: self.next_offset,
            buffered_bytes: self.buffered_bytes,
            reorder_high_water: self.reorder_high_water,
        }
    }
}

fn checked_end(offset: u64, length: usize) -> Result<u64, ReassemblyError> {
    let length = u64::try_from(length).map_err(|_| ReassemblyError::OffsetOverflow)?;
    offset
        .checked_add(length)
        .ok_or(ReassemblyError::OffsetOverflow)
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ReassemblyError {
    ZeroBufferLimit,
    EmptySegment,
    OffsetOverflow,
    ConflictingOverlap,
    ReorderWindowExceeded { attempted: usize, limit: usize },
    BufferLimitExceeded { attempted: usize, limit: usize },
    BufferAccountingOverflow,
}

impl fmt::Display for ReassemblyError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroBufferLimit => write!(formatter, "reassembly buffer limit must be non-zero"),
            Self::EmptySegment => write!(formatter, "reassembly segment must not be empty"),
            Self::OffsetOverflow => write!(formatter, "reassembly offset overflow"),
            Self::ConflictingOverlap => write!(formatter, "conflicting reassembly overlap"),
            Self::ReorderWindowExceeded { attempted, limit } => write!(
                formatter,
                "reorder window exceeded: attempted {attempted}, limit {limit}"
            ),
            Self::BufferLimitExceeded { attempted, limit } => write!(
                formatter,
                "reassembly buffer exceeded: attempted {attempted}, limit {limit}"
            ),
            Self::BufferAccountingOverflow => write!(formatter, "reassembly accounting overflow"),
        }
    }
}

impl Error for ReassemblyError {}

#[cfg(test)]
mod tests {
    use bytes::Bytes;

    use super::{Reassembler, ReassemblyError};

    #[test]
    fn in_order_delivery_preserves_owned_payload_storage() {
        let mut receiver = Reassembler::new(0, 64).unwrap();
        let payload = Bytes::from_static(b"owned in-order payload");
        let pointer = payload.as_ptr();
        let delivery = receiver.insert_shared(0, payload).unwrap();

        assert_eq!(delivery.bytes, b"owned in-order payload"[..]);
        assert_eq!(delivery.bytes.as_ptr(), pointer);
        assert_eq!(delivery.accepted_bytes, delivery.bytes.len());
        assert_eq!(delivery.buffered_bytes, 0);
        assert_eq!(receiver.segment_insertions, 0);
    }

    #[test]
    fn out_of_order_segments_are_delivered_exactly_once() {
        let mut receiver = Reassembler::new(0, 64).unwrap();
        let second = receiver.insert(5, b" world").unwrap();
        assert!(second.bytes.is_empty());
        assert_eq!(second.accepted_bytes, 6);
        assert_eq!(second.buffered_bytes, 6);
        assert_eq!(receiver.segment_insertions, 1);

        let duplicate = receiver.insert(5, b" world").unwrap();
        assert!(duplicate.bytes.is_empty());
        assert_eq!(duplicate.accepted_bytes, 0);
        assert_eq!(duplicate.buffered_bytes, 6);

        let first = receiver.insert(0, b"hello").unwrap();
        assert_eq!(first.bytes.as_ref(), b"hello world");
        assert_eq!(first.accepted_bytes, 5);
        assert_eq!(first.next_offset, 11);
        assert_eq!(first.buffered_bytes, 0);
        assert_eq!(first.reorder_high_water, 11);

        let old = receiver.insert(0, b"hello").unwrap();
        assert!(old.bytes.is_empty());
        assert_eq!(old.accepted_bytes, 0);
        assert_eq!(old.next_offset, 11);
    }

    #[test]
    fn reordering_and_conflicting_overlap_are_bounded() {
        let mut receiver = Reassembler::new(0, 8).unwrap();
        assert_eq!(
            receiver.insert(8, b"x"),
            Err(ReassemblyError::ReorderWindowExceeded {
                attempted: 9,
                limit: 8
            })
        );
        receiver.insert(4, b"efgh").unwrap();
        assert_eq!(
            receiver.insert(6, b"different"),
            Err(ReassemblyError::ConflictingOverlap)
        );
    }

    #[test]
    fn delivered_prefix_is_trimmed_from_a_retransmission() {
        let mut receiver = Reassembler::new(0, 16).unwrap();
        assert_eq!(receiver.insert(0, b"abcd").unwrap().bytes.as_ref(), b"abcd");
        assert_eq!(receiver.insert(2, b"cdef").unwrap().bytes.as_ref(), b"ef");
        assert_eq!(receiver.next_offset(), 6);
    }

    #[test]
    fn reports_bounded_merged_selective_acknowledgement_ranges() {
        let mut receiver = Reassembler::new(0, 64).unwrap();
        receiver.insert(8, b"ij").unwrap();
        receiver.insert(10, b"kl").unwrap();
        receiver.insert(16, b"qr").unwrap();

        assert_eq!(
            receiver.acknowledgement_ranges(2),
            vec![
                crate::AckRange { start: 8, end: 12 },
                crate::AckRange { start: 16, end: 18 }
            ]
        );
        assert!(receiver.acknowledgement_ranges(0).is_empty());
        assert_eq!(receiver.acknowledgement_range_count(2), 2);
        assert_eq!(receiver.highest_buffered_end().unwrap(), Some(18));

        let mut scratch = Vec::with_capacity(2);
        let capacity = scratch.capacity();
        receiver.acknowledgement_ranges_into(2, &mut scratch);
        assert_eq!(scratch, receiver.acknowledgement_ranges(2));
        receiver.acknowledgement_ranges_into(1, &mut scratch);
        assert_eq!(scratch, vec![crate::AckRange { start: 8, end: 12 }]);
        assert_eq!(scratch.capacity(), capacity);
    }
}
