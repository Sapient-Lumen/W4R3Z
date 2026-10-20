use std::error::Error;
use std::fmt;

use crate::handshake::{
    self, BondProtocolVersion, BondProtocolVersions, BondSessionKey, LaneJoin, PreparedClientLane,
    ServerIncarnation,
};
use crate::record::LaneRecordKeys;
use anonssh_bond::{FailureDomain, Frame, FrameFlags, FrameKind, LaneId};

pub const TRANSPORT_FUZZ_SEED: u64 = 0x414e_4f4e_5353_4802;
pub const DEFAULT_TRANSPORT_FUZZ_CASES: u32 = 1_024;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct FuzzCounts {
    pub cases: u32,
    pub accepted: u32,
    pub rejected: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct TransportFuzzReport {
    pub seed: u64,
    pub handshake_hello: FuzzCounts,
    pub handshake_accept: FuzzCounts,
    pub encrypted_record: FuzzCounts,
}

pub async fn embedded_transport_fuzz_test() -> Result<TransportFuzzReport, TransportFuzzError> {
    transport_fuzz_test(TRANSPORT_FUZZ_SEED, DEFAULT_TRANSPORT_FUZZ_CASES).await
}

pub async fn transport_fuzz_test(
    seed: u64,
    cases_per_parser: u32,
) -> Result<TransportFuzzReport, TransportFuzzError> {
    if seed == 0 || cases_per_parser < 16 {
        return Err(TransportFuzzError::InvalidConfiguration);
    }
    let key = BondSessionKey::new([0x31; 32]);
    let join = LaneJoin::new(
        41,
        LaneId::new(2).map_err(|_| TransportFuzzError::SeedConstruction("join"))?,
        FailureDomain::new(9).map_err(|_| TransportFuzzError::SeedConstruction("join"))?,
    )
    .map_err(|_| TransportFuzzError::SeedConstruction("join"))?;
    let prepared = PreparedClientLane::new(&key, join)
        .map_err(|_| TransportFuzzError::SeedConstruction("hello"))?;
    let hello: [u8; handshake::HELLO_LEN] = prepared
        .initial_payload()
        .try_into()
        .map_err(|_| TransportFuzzError::SeedConstruction("hello"))?;
    let (_, client_nonce, _) = handshake::decode_hello(&key, &hello)
        .map_err(|_| TransportFuzzError::SeedConstruction("hello"))?;
    let server_nonce = handshake::encode_server_version_selection(
        [0x5a; 32],
        BondProtocolVersions::CURRENT,
        Some(BondProtocolVersion::V6),
        ServerIncarnation::from_u64(7)
            .map_err(|_| TransportFuzzError::SeedConstruction("accept"))?,
    );
    let accept = handshake::encode_accept(
        &key,
        join,
        client_nonce,
        server_nonce,
        &hello,
        &[0xa5; 1_088],
    )
    .map_err(|_| TransportFuzzError::SeedConstruction("accept"))?;

    let handshake_hello = fuzz_hello(seed, cases_per_parser, &key, &hello)?;
    let handshake_accept = fuzz_accept(
        seed.rotate_left(17),
        cases_per_parser,
        &key,
        join,
        client_nonce,
        &hello,
        &accept,
    )?;
    let encrypted_record = fuzz_records(seed.rotate_left(31), cases_per_parser).await?;
    Ok(TransportFuzzReport {
        seed,
        handshake_hello,
        handshake_accept,
        encrypted_record,
    })
}

fn fuzz_hello(
    seed: u64,
    cases: u32,
    key: &BondSessionKey,
    valid: &[u8; handshake::HELLO_LEN],
) -> Result<FuzzCounts, TransportFuzzError> {
    let mut random = DeterministicRandom::new(seed);
    count_cases("handshake-hello", cases, |case| {
        let mut wire = *valid;
        match case % 8 {
            0 | 7 => {}
            1 => mutate_one(&mut wire[..handshake::HELLO_BODY_LEN], &mut random),
            2 => mutate_one(&mut wire[handshake::HELLO_BODY_LEN..], &mut random),
            3 => {
                wire[4..12].fill(0);
                retag_hello(key, &mut wire)?;
            }
            4 => {
                wire[12..16].fill(0);
                retag_hello(key, &mut wire)?;
            }
            5 => {
                wire[32..40].fill(0);
                retag_hello(key, &mut wire)?;
            }
            6 => random.fill(&mut wire),
            _ => unreachable!(),
        }
        parse_hello(key, &wire)
    })
}

fn parse_hello(
    key: &BondSessionKey,
    wire: &[u8; handshake::HELLO_LEN],
) -> Result<ParseOutcome, TransportFuzzError> {
    let Ok((join, client_nonce, encapsulation_key)) = handshake::decode_hello(key, wire) else {
        return Ok(ParseOutcome::Rejected);
    };
    if handshake::client_version_mask(&client_nonce).is_err()
        || handshake::client_join_sequence(&client_nonce).is_err()
    {
        return Ok(ParseOutcome::Rejected);
    }
    let encoded = handshake::encode_hello(key, join, client_nonce, &encapsulation_key)
        .map_err(|_| TransportFuzzError::Invariant("accepted hello did not encode"))?;
    if encoded != *wire {
        return Err(TransportFuzzError::Invariant("hello was not canonical"));
    }
    Ok(ParseOutcome::Accepted)
}

#[allow(clippy::too_many_arguments)]
fn fuzz_accept(
    seed: u64,
    cases: u32,
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; 32],
    hello: &[u8; handshake::HELLO_LEN],
    valid: &[u8; handshake::ACCEPT_LEN],
) -> Result<FuzzCounts, TransportFuzzError> {
    let mut random = DeterministicRandom::new(seed);
    count_cases("handshake-accept", cases, |case| {
        let mut wire = *valid;
        match case % 8 {
            0 | 7 => {}
            1 => mutate_one(&mut wire[..handshake::ACCEPT_BODY_LEN], &mut random),
            2 => mutate_one(&mut wire[handshake::ACCEPT_BODY_LEN..], &mut random),
            3 => {
                wire[4..12].fill(0);
                retag_accept(key, hello, &mut wire)?;
            }
            4 => {
                let server_nonce_start = 4 + 20 + 32;
                wire[server_nonce_start + 16] = 99;
                retag_accept(key, hello, &mut wire)?;
            }
            5 => {
                let server_nonce_start = 4 + 20 + 32;
                wire[server_nonce_start + 16] = BondProtocolVersion::V1.get();
                retag_accept(key, hello, &mut wire)?;
            }
            6 => random.fill(&mut wire),
            _ => unreachable!(),
        }
        parse_accept(key, join, client_nonce, hello, &wire)
    })
}

fn parse_accept(
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; 32],
    hello: &[u8; handshake::HELLO_LEN],
    wire: &[u8; handshake::ACCEPT_LEN],
) -> Result<ParseOutcome, TransportFuzzError> {
    let Ok((server_nonce, ciphertext)) =
        handshake::decode_accept(key, join, client_nonce, hello, wire)
    else {
        return Ok(ParseOutcome::Rejected);
    };
    let Ok(version) =
        handshake::select_client_protocol_version(BondProtocolVersions::CURRENT, &server_nonce)
    else {
        return Ok(ParseOutcome::Rejected);
    };
    if version >= BondProtocolVersion::V5 {
        let incarnation = u64::from_be_bytes(
            server_nonce[17..25]
                .try_into()
                .map_err(|_| TransportFuzzError::Invariant("invalid incarnation slice"))?,
        );
        if ServerIncarnation::from_u64(incarnation).is_err() {
            return Ok(ParseOutcome::Rejected);
        }
    }
    let encoded = handshake::encode_accept(
        key,
        join,
        client_nonce,
        server_nonce,
        hello,
        ciphertext.as_ref(),
    )
    .map_err(|_| TransportFuzzError::Invariant("accepted response did not encode"))?;
    if encoded != *wire {
        return Err(TransportFuzzError::Invariant("response was not canonical"));
    }
    Ok(ParseOutcome::Accepted)
}

async fn fuzz_records(seed: u64, cases: u32) -> Result<FuzzCounts, TransportFuzzError> {
    let frame = Frame::new(FrameKind::Data, FrameFlags::NONE, 17, 3, 0, vec![0x6d; 512])
        .map_err(|_| TransportFuzzError::SeedConstruction("record"))?;
    let expected = frame
        .encode()
        .map_err(|_| TransportFuzzError::SeedConstruction("record"))?;
    let (mut sealer, _) = LaneRecordKeys::new([0x44; 32], [0x44; 32]).into_records();
    let mut valid = Vec::new();
    sealer
        .seal_frame_into(&frame, &mut valid)
        .map_err(|_| TransportFuzzError::SeedConstruction("record"))?;
    let mut random = DeterministicRandom::new(seed);
    let mut counts = FuzzCounts {
        cases,
        accepted: 0,
        rejected: 0,
    };
    for case in 0..cases {
        let mut input = valid.clone();
        match case % 8 {
            0 | 7 => {}
            1 => input.truncate(random.bounded(input.len())),
            2 => mutate_one(&mut input[..20], &mut random),
            3 => mutate_one(&mut input[20..], &mut random),
            4 => input[12..16].copy_from_slice(&u32::MAX.to_be_bytes()),
            5 => input[4..12].copy_from_slice(&1_u64.to_be_bytes()),
            6 => random.fill(&mut input),
            _ => unreachable!(),
        }
        let (_, mut opener) = LaneRecordKeys::new([0x44; 32], [0x44; 32]).into_records();
        let mut reader = input.as_slice();
        match opener.open(&mut reader).await {
            Ok(plaintext) => {
                if plaintext.as_ref() != expected {
                    return Err(TransportFuzzError::Invariant(
                        "record opened to unexpected plaintext",
                    ));
                }
                let (decoded, consumed) = Frame::decode_owned(plaintext).map_err(|_| {
                    TransportFuzzError::Invariant("record plaintext is not a frame")
                })?;
                if decoded != frame || consumed != expected.len() {
                    return Err(TransportFuzzError::Invariant(
                        "record frame round trip changed value",
                    ));
                }
                counts.accepted += 1;
            }
            Err(_) => counts.rejected += 1,
        }
    }
    require_mixed("encrypted-record", counts)
}

fn retag_hello(
    key: &BondSessionKey,
    wire: &mut [u8; handshake::HELLO_LEN],
) -> Result<(), TransportFuzzError> {
    let tag = handshake::authentication_tag(
        key,
        handshake::CLIENT_DOMAIN,
        &wire[..handshake::HELLO_BODY_LEN],
    )
    .map_err(|_| TransportFuzzError::SeedConstruction("hello tag"))?;
    wire[handshake::HELLO_BODY_LEN..].copy_from_slice(&tag);
    Ok(())
}

fn retag_accept(
    key: &BondSessionKey,
    hello: &[u8; handshake::HELLO_LEN],
    wire: &mut [u8; handshake::ACCEPT_LEN],
) -> Result<(), TransportFuzzError> {
    let tag = handshake::authentication_tag_parts(
        key,
        handshake::SERVER_DOMAIN,
        &[
            &hello[..handshake::HELLO_BODY_LEN],
            &wire[..handshake::ACCEPT_BODY_LEN],
        ],
    )
    .map_err(|_| TransportFuzzError::SeedConstruction("accept tag"))?;
    wire[handshake::ACCEPT_BODY_LEN..].copy_from_slice(&tag);
    Ok(())
}

fn count_cases(
    family: &'static str,
    cases: u32,
    mut run: impl FnMut(u32) -> Result<ParseOutcome, TransportFuzzError>,
) -> Result<FuzzCounts, TransportFuzzError> {
    let mut counts = FuzzCounts {
        cases,
        accepted: 0,
        rejected: 0,
    };
    for case in 0..cases {
        match run(case)? {
            ParseOutcome::Accepted => counts.accepted += 1,
            ParseOutcome::Rejected => counts.rejected += 1,
        }
    }
    require_mixed(family, counts)
}

fn require_mixed(
    family: &'static str,
    counts: FuzzCounts,
) -> Result<FuzzCounts, TransportFuzzError> {
    if counts.accepted == 0 || counts.rejected == 0 {
        Err(TransportFuzzError::MissingCoverage {
            family,
            accepted: counts.accepted,
            rejected: counts.rejected,
        })
    } else {
        Ok(counts)
    }
}

fn mutate_one(bytes: &mut [u8], random: &mut DeterministicRandom) {
    if !bytes.is_empty() {
        let index = random.bounded(bytes.len());
        bytes[index] ^= 1 << random.bounded(8);
    }
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
pub enum TransportFuzzError {
    InvalidConfiguration,
    SeedConstruction(&'static str),
    Invariant(&'static str),
    MissingCoverage {
        family: &'static str,
        accepted: u32,
        rejected: u32,
    },
}

impl fmt::Display for TransportFuzzError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidConfiguration => write!(formatter, "invalid transport fuzz configuration"),
            Self::SeedConstruction(family) => {
                write!(formatter, "failed to construct {family} fuzz seed")
            }
            Self::Invariant(message) => write!(formatter, "transport fuzz invariant failed: {message}"),
            Self::MissingCoverage {
                family,
                accepted,
                rejected,
            } => write!(
                formatter,
                "transport fuzz family {family} lacks mixed coverage (accepted={accepted}, rejected={rejected})"
            ),
        }
    }
}

impl Error for TransportFuzzError {}

#[cfg(test)]
mod tests {
    #[tokio::test]
    async fn deterministic_transport_campaign_has_mixed_coverage() {
        let first = super::transport_fuzz_test(super::TRANSPORT_FUZZ_SEED, 128)
            .await
            .unwrap();
        let second = super::transport_fuzz_test(super::TRANSPORT_FUZZ_SEED, 128)
            .await
            .unwrap();
        assert_eq!(first, second);
        for counts in [
            first.handshake_hello,
            first.handshake_accept,
            first.encrypted_record,
        ] {
            assert_eq!(counts.accepted + counts.rejected, counts.cases);
            assert!(counts.accepted > 0);
            assert!(counts.rejected > 0);
        }
    }
}
