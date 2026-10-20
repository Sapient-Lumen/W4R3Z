use std::collections::{BTreeMap, BTreeSet};
use std::error::Error;
use std::fmt;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

use anonssh_bond::{FailureDomain, LaneId, SchedulerError};
use hkdf::Hkdf;
use hmac::{Hmac, Mac};
use ml_kem::kem::{Decapsulate, Encapsulate, Kem, Key, KeyExport};
use ml_kem::ml_kem_768::{DecapsulationKey, EncapsulationKey};
use ml_kem::MlKem768;
use sha2::Sha256;
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};
use tokio::time::timeout;
use zeroize::Zeroizing;

use crate::record::LaneRecordKeys;

const HELLO_MAGIC: [u8; 4] = *b"ABJ1";
const ACCEPT_MAGIC: [u8; 4] = *b"ABA1";
const CLIENT_VERSION_MAGIC: [u8; 8] = *b"ABPVC01\0";
const SERVER_VERSION_MAGIC: [u8; 8] = *b"ABPVS01\0";
const NONCE_LEN: usize = 32;
const TAG_LEN: usize = 32;
const ML_KEM_PUBLIC_KEY_LEN: usize = 1_184;
const ML_KEM_CIPHERTEXT_LEN: usize = 1_088;
const DESCRIPTOR_LEN: usize = 8 + 4 + 8;
pub(crate) const HELLO_BODY_LEN: usize = 4 + DESCRIPTOR_LEN + NONCE_LEN + ML_KEM_PUBLIC_KEY_LEN;
pub(crate) const HELLO_LEN: usize = HELLO_BODY_LEN + TAG_LEN;
pub(crate) const ACCEPT_BODY_LEN: usize =
    4 + DESCRIPTOR_LEN + NONCE_LEN + NONCE_LEN + ML_KEM_CIPHERTEXT_LEN;
pub(crate) const ACCEPT_LEN: usize = ACCEPT_BODY_LEN + TAG_LEN;
pub(crate) const CLIENT_DOMAIN: &[u8] = b"anonssh-abp-client-lane-join-v1\0";
pub(crate) const SERVER_DOMAIN: &[u8] = b"anonssh-abp-server-lane-accept-v1\0";
const KEY_SCHEDULE_INFO: &[u8] = b"anonssh-abp-lane-record-keys-v1\0";
const NEGOTIATED_KEY_SCHEDULE_INFO: &[u8] = b"anonssh-abp-negotiated-version\0";
const CLIENT_JOIN_SEQUENCE_START: usize = 16;
const CLIENT_JOIN_SEQUENCE_END: usize = 24;
const SERVER_INCARNATION_START: usize = 17;
const SERVER_INCARNATION_END: usize = 25;

static NEXT_CLIENT_JOIN_SEQUENCE: AtomicU64 = AtomicU64::new(1);

type HmacSha256 = Hmac<Sha256>;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(u8)]
pub enum BondProtocolVersion {
    V1 = 1,
    V2 = 2,
    V3 = 3,
    V4 = 4,
    V5 = 5,
    V6 = 6,
}

impl BondProtocolVersion {
    pub const fn get(self) -> u8 {
        self as u8
    }

    const fn bit(self) -> u64 {
        1_u64 << (self.get() - 1)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct BondProtocolVersions(u64);

impl BondProtocolVersions {
    pub const LEGACY: Self = Self(BondProtocolVersion::V1.bit());
    pub const V2_COMPATIBLE: Self =
        Self(BondProtocolVersion::V1.bit() | BondProtocolVersion::V2.bit());
    pub const V3_COMPATIBLE: Self = Self(
        BondProtocolVersion::V1.bit()
            | BondProtocolVersion::V2.bit()
            | BondProtocolVersion::V3.bit(),
    );
    pub const V4_COMPATIBLE: Self = Self(
        BondProtocolVersion::V1.bit()
            | BondProtocolVersion::V2.bit()
            | BondProtocolVersion::V3.bit()
            | BondProtocolVersion::V4.bit(),
    );
    pub const V5_COMPATIBLE: Self = Self(
        BondProtocolVersion::V1.bit()
            | BondProtocolVersion::V2.bit()
            | BondProtocolVersion::V3.bit()
            | BondProtocolVersion::V4.bit()
            | BondProtocolVersion::V5.bit(),
    );
    pub const CURRENT: Self = Self(
        BondProtocolVersion::V1.bit()
            | BondProtocolVersion::V2.bit()
            | BondProtocolVersion::V3.bit()
            | BondProtocolVersion::V4.bit()
            | BondProtocolVersion::V5.bit()
            | BondProtocolVersion::V6.bit(),
    );

    pub fn new(
        versions: impl IntoIterator<Item = BondProtocolVersion>,
    ) -> Result<Self, LaneHandshakeError> {
        let mask = versions
            .into_iter()
            .fold(0_u64, |mask, version| mask | version.bit());
        Self::from_mask(mask)
    }

    pub const fn only(version: BondProtocolVersion) -> Self {
        Self(version.bit())
    }

    pub const fn contains(self, version: BondProtocolVersion) -> bool {
        self.0 & version.bit() != 0
    }

    pub const fn wire_mask(self) -> u64 {
        self.0
    }

    fn from_mask(mask: u64) -> Result<Self, LaneHandshakeError> {
        if mask == 0 {
            return Err(LaneHandshakeError::NoSupportedProtocolVersions);
        }
        Ok(Self(mask))
    }

    fn newest_common_mask(self, remote_mask: u64) -> Option<BondProtocolVersion> {
        let common = self.0 & remote_mask;
        if common & BondProtocolVersion::V6.bit() != 0 {
            Some(BondProtocolVersion::V6)
        } else if common & BondProtocolVersion::V5.bit() != 0 {
            Some(BondProtocolVersion::V5)
        } else if common & BondProtocolVersion::V4.bit() != 0 {
            Some(BondProtocolVersion::V4)
        } else if common & BondProtocolVersion::V3.bit() != 0 {
            Some(BondProtocolVersion::V3)
        } else if common & BondProtocolVersion::V2.bit() != 0 {
            Some(BondProtocolVersion::V2)
        } else if common & BondProtocolVersion::V1.bit() != 0 {
            Some(BondProtocolVersion::V1)
        } else {
            None
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ServerIncarnation(u64);

impl ServerIncarnation {
    pub fn fresh() -> Result<Self, LaneHandshakeError> {
        loop {
            let mut bytes = [0_u8; 8];
            fill_random(&mut bytes)?;
            let value = u64::from_be_bytes(bytes);
            if value != 0 {
                return Ok(Self(value));
            }
        }
    }

    pub const fn from_u64(value: u64) -> Result<Self, LaneHandshakeError> {
        if value == 0 {
            Err(LaneHandshakeError::ZeroServerIncarnation)
        } else {
            Ok(Self(value))
        }
    }

    pub const fn get(self) -> u64 {
        self.0
    }
}

pub struct BondSessionKey(Zeroizing<[u8; 32]>);

impl BondSessionKey {
    pub fn new(bytes: [u8; 32]) -> Self {
        Self(Zeroizing::new(bytes))
    }
}

impl fmt::Debug for BondSessionKey {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_tuple("BondSessionKey")
            .field(&"[REDACTED]")
            .finish()
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct LaneJoin {
    pub session_id: u64,
    pub lane_id: LaneId,
    pub failure_domain: FailureDomain,
}

impl LaneJoin {
    pub fn new(
        session_id: u64,
        lane_id: LaneId,
        failure_domain: FailureDomain,
    ) -> Result<Self, LaneHandshakeError> {
        if session_id == 0 {
            return Err(LaneHandshakeError::ZeroSessionId);
        }
        Ok(Self {
            session_id,
            lane_id,
            failure_domain,
        })
    }
}

pub struct AuthenticatedLane<T> {
    pub join: LaneJoin,
    pub client_nonce: [u8; NONCE_LEN],
    pub server_nonce: [u8; NONCE_LEN],
    protocol_version: BondProtocolVersion,
    io: T,
    record_keys: LaneRecordKeys,
}

impl<T> fmt::Debug for AuthenticatedLane<T> {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("AuthenticatedLane")
            .field("join", &self.join)
            .field("client_nonce", &self.client_nonce)
            .field("server_nonce", &self.server_nonce)
            .field("protocol_version", &self.protocol_version)
            .field("io", &"<stream>")
            .finish()
    }
}

impl<T> AuthenticatedLane<T> {
    pub const fn protocol_version(&self) -> BondProtocolVersion {
        self.protocol_version
    }

    pub fn server_incarnation(&self) -> Result<Option<ServerIncarnation>, LaneHandshakeError> {
        if self.protocol_version < BondProtocolVersion::V5 {
            return Ok(None);
        }
        let value = u64::from_be_bytes(
            self.server_nonce[SERVER_INCARNATION_START..SERVER_INCARNATION_END]
                .try_into()
                .expect("fixed server incarnation"),
        );
        ServerIncarnation::from_u64(value).map(Some)
    }

    pub(crate) fn into_parts(self) -> (T, LaneRecordKeys, BondProtocolVersion) {
        (self.io, self.record_keys, self.protocol_version)
    }
}

pub struct PreparedClientLane {
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    decapsulation_key: DecapsulationKey,
    hello: [u8; HELLO_LEN],
    supported_versions: BondProtocolVersions,
}

pub struct PreparedServerLane<T> {
    io: T,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    encapsulation_key: EncapsulationKey,
    hello: [u8; HELLO_LEN],
}

impl<T> fmt::Debug for PreparedServerLane<T> {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("PreparedServerLane")
            .field("join", &self.join)
            .field("client_nonce", &self.client_nonce)
            .field("io", &"<stream>")
            .finish_non_exhaustive()
    }
}

impl<T> PreparedServerLane<T>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    pub const fn join(&self) -> LaneJoin {
        self.join
    }

    pub const fn client_nonce(&self) -> [u8; NONCE_LEN] {
        self.client_nonce
    }

    pub fn client_join_sequence(&self) -> Result<Option<u64>, LaneHandshakeError> {
        client_join_sequence(&self.client_nonce)
    }

    pub async fn finish(
        self,
        key: &BondSessionKey,
        deadline: Duration,
    ) -> Result<AuthenticatedLane<T>, LaneHandshakeError> {
        self.finish_with_versions_and_incarnation(
            key,
            BondProtocolVersions::CURRENT,
            ServerIncarnation::fresh()?,
            deadline,
        )
        .await
    }

    pub async fn finish_with_versions(
        self,
        key: &BondSessionKey,
        supported_versions: BondProtocolVersions,
        deadline: Duration,
    ) -> Result<AuthenticatedLane<T>, LaneHandshakeError> {
        self.finish_with_versions_and_incarnation(
            key,
            supported_versions,
            ServerIncarnation::fresh()?,
            deadline,
        )
        .await
    }

    pub async fn finish_with_versions_and_incarnation(
        self,
        key: &BondSessionKey,
        supported_versions: BondProtocolVersions,
        incarnation: ServerIncarnation,
        deadline: Duration,
    ) -> Result<AuthenticatedLane<T>, LaneHandshakeError> {
        validate_deadline(deadline)?;
        timeout(
            deadline,
            finish_server_lane(self, key, supported_versions, incarnation),
        )
        .await
        .map_err(|_| LaneHandshakeError::TimedOut)?
    }
}

impl PreparedClientLane {
    pub fn new(key: &BondSessionKey, join: LaneJoin) -> Result<Self, LaneHandshakeError> {
        Self::new_with_versions(key, join, BondProtocolVersions::CURRENT)
    }

    pub fn new_with_versions(
        key: &BondSessionKey,
        join: LaneJoin,
        supported_versions: BondProtocolVersions,
    ) -> Result<Self, LaneHandshakeError> {
        let client_nonce = fresh_client_nonce(supported_versions)?;
        let (decapsulation_key, encapsulation_key) = MlKem768::generate_keypair();
        let hello = encode_hello(key, join, client_nonce, &encapsulation_key)?;
        Ok(Self {
            join,
            client_nonce,
            decapsulation_key,
            hello,
            supported_versions,
        })
    }

    pub fn initial_payload(&self) -> &[u8] {
        &self.hello
    }

    pub async fn finish<T>(
        self,
        io: T,
        key: &BondSessionKey,
        deadline: Duration,
    ) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
    where
        T: AsyncRead + AsyncWrite + Unpin,
    {
        validate_deadline(deadline)?;
        timeout(
            deadline,
            finish_client_lane(
                io,
                key,
                self.join,
                self.client_nonce,
                self.decapsulation_key,
                self.hello,
                self.supported_versions,
            ),
        )
        .await
        .map_err(|_| LaneHandshakeError::TimedOut)?
    }
}

pub struct LaneJoinRegistry {
    session_id: u64,
    expected: BTreeMap<LaneId, FailureDomain>,
    accepted_lanes: BTreeSet<LaneId>,
    client_nonces: BTreeSet<[u8; NONCE_LEN]>,
    protocol_version: Option<BondProtocolVersion>,
}

impl LaneJoinRegistry {
    pub fn new(
        session_id: u64,
        expected: impl IntoIterator<Item = (LaneId, FailureDomain)>,
    ) -> Result<Self, LaneHandshakeError> {
        if session_id == 0 {
            return Err(LaneHandshakeError::ZeroSessionId);
        }
        let expected = expected.into_iter().collect::<BTreeMap<_, _>>();
        if expected.is_empty() {
            return Err(LaneHandshakeError::NoExpectedLanes);
        }
        Ok(Self {
            session_id,
            expected,
            accepted_lanes: BTreeSet::new(),
            client_nonces: BTreeSet::new(),
            protocol_version: None,
        })
    }

    pub fn register<T>(&mut self, lane: &AuthenticatedLane<T>) -> Result<(), LaneHandshakeError> {
        if lane.join.session_id != self.session_id {
            return Err(LaneHandshakeError::UnexpectedDescriptor);
        }
        if self.expected.get(&lane.join.lane_id) != Some(&lane.join.failure_domain) {
            return Err(LaneHandshakeError::UnexpectedDescriptor);
        }
        if self.accepted_lanes.contains(&lane.join.lane_id) {
            return Err(LaneHandshakeError::DuplicateLane(lane.join.lane_id));
        }
        if self.client_nonces.contains(&lane.client_nonce) {
            return Err(LaneHandshakeError::ReplayedClientNonce);
        }
        if let Some(expected) = self.protocol_version {
            if lane.protocol_version != expected {
                return Err(LaneHandshakeError::ProtocolVersionMismatch {
                    expected,
                    actual: lane.protocol_version,
                });
            }
        } else {
            self.protocol_version = Some(lane.protocol_version);
        }
        self.accepted_lanes.insert(lane.join.lane_id);
        self.client_nonces.insert(lane.client_nonce);
        Ok(())
    }

    pub fn is_complete(&self) -> bool {
        self.accepted_lanes.len() == self.expected.len()
    }

    pub const fn session_id(&self) -> u64 {
        self.session_id
    }
}

pub fn fresh_session_id() -> Result<u64, LaneHandshakeError> {
    loop {
        let mut bytes = [0_u8; 8];
        fill_random(&mut bytes)?;
        let session_id = u64::from_be_bytes(bytes);
        if session_id != 0 {
            return Ok(session_id);
        }
    }
}

pub async fn authenticate_client_lane<T>(
    io: T,
    key: &BondSessionKey,
    join: LaneJoin,
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    let nonce = fresh_client_nonce(BondProtocolVersions::CURRENT)?;
    authenticate_client_lane_with_versions_and_nonce(
        io,
        key,
        join,
        nonce,
        BondProtocolVersions::CURRENT,
        deadline,
    )
    .await
}

pub async fn authenticate_server_lane<T>(
    io: T,
    key: &BondSessionKey,
    expected: LaneJoin,
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    authenticate_server_lane_with_incarnation(
        io,
        key,
        expected,
        ServerIncarnation::fresh()?,
        deadline,
    )
    .await
}

pub async fn authenticate_server_lane_with_incarnation<T>(
    io: T,
    key: &BondSessionKey,
    expected: LaneJoin,
    incarnation: ServerIncarnation,
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    validate_deadline(deadline)?;
    timeout(deadline, async {
        let prepared = prepare_server_lane_inner(io, key).await?;
        if prepared.join != expected {
            return Err(LaneHandshakeError::UnexpectedDescriptor);
        }
        finish_server_lane(prepared, key, BondProtocolVersions::CURRENT, incarnation).await
    })
    .await
    .map_err(|_| LaneHandshakeError::TimedOut)?
}

pub async fn prepare_server_lane<T>(
    io: T,
    key: &BondSessionKey,
    deadline: Duration,
) -> Result<PreparedServerLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    validate_deadline(deadline)?;
    timeout(deadline, prepare_server_lane_inner(io, key))
        .await
        .map_err(|_| LaneHandshakeError::TimedOut)?
}

pub async fn authenticate_server_lane_unbound<T>(
    io: T,
    key: &BondSessionKey,
    expected_lane: LaneId,
    expected_failure_domain: FailureDomain,
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    authenticate_server_lane_unbound_with_incarnation(
        io,
        key,
        expected_lane,
        expected_failure_domain,
        ServerIncarnation::fresh()?,
        deadline,
    )
    .await
}

pub async fn authenticate_server_lane_unbound_with_incarnation<T>(
    io: T,
    key: &BondSessionKey,
    expected_lane: LaneId,
    expected_failure_domain: FailureDomain,
    incarnation: ServerIncarnation,
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    validate_deadline(deadline)?;
    timeout(deadline, async {
        let prepared = prepare_server_lane_inner(io, key).await?;
        let join = prepared.join;
        if join.lane_id != expected_lane || join.failure_domain != expected_failure_domain {
            return Err(LaneHandshakeError::UnexpectedDescriptor);
        }
        finish_server_lane(prepared, key, BondProtocolVersions::CURRENT, incarnation).await
    })
    .await
    .map_err(|_| LaneHandshakeError::TimedOut)?
}

pub(crate) async fn authenticate_client_lane_with_nonce<T>(
    io: T,
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    authenticate_client_lane_with_versions_and_nonce(
        io,
        key,
        join,
        client_nonce,
        BondProtocolVersions::LEGACY,
        deadline,
    )
    .await
}

async fn authenticate_client_lane_with_versions_and_nonce<T>(
    mut io: T,
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    supported_versions: BondProtocolVersions,
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    validate_deadline(deadline)?;
    timeout(deadline, async {
        let (decapsulation_key, encapsulation_key) = MlKem768::generate_keypair();
        let hello = encode_hello(key, join, client_nonce, &encapsulation_key)?;
        io.write_all(&hello).await.map_err(io_error)?;
        io.flush().await.map_err(io_error)?;
        finish_client_lane(
            io,
            key,
            join,
            client_nonce,
            decapsulation_key,
            hello,
            supported_versions,
        )
        .await
    })
    .await
    .map_err(|_| LaneHandshakeError::TimedOut)?
}

async fn finish_client_lane<T>(
    mut io: T,
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    decapsulation_key: DecapsulationKey,
    hello: [u8; HELLO_LEN],
    supported_versions: BondProtocolVersions,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    let mut accept = [0_u8; ACCEPT_LEN];
    io.read_exact(&mut accept).await.map_err(io_error)?;
    let (server_nonce, ciphertext) = decode_accept(key, join, client_nonce, &hello, &accept)?;
    let protocol_version = select_client_protocol_version(supported_versions, &server_nonce)?;
    let shared_secret = decapsulation_key.decapsulate(&ciphertext);
    let record_keys = derive_record_keys(
        key,
        join,
        client_nonce,
        server_nonce,
        shared_secret.as_ref(),
        protocol_version,
        true,
    )?;
    Ok(AuthenticatedLane {
        join,
        client_nonce,
        server_nonce,
        protocol_version,
        io,
        record_keys,
    })
}

pub(crate) async fn authenticate_server_lane_with_nonce<T>(
    io: T,
    key: &BondSessionKey,
    expected: LaneJoin,
    server_nonce: [u8; NONCE_LEN],
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    validate_deadline(deadline)?;
    timeout(deadline, async {
        let prepared = prepare_server_lane_inner(io, key).await?;
        if prepared.join != expected {
            return Err(LaneHandshakeError::UnexpectedDescriptor);
        }
        finish_server_lane_legacy(prepared, key, server_nonce).await
    })
    .await
    .map_err(|_| LaneHandshakeError::TimedOut)?
}

#[cfg(test)]
async fn authenticate_server_lane_unbound_with_nonce<T>(
    io: T,
    key: &BondSessionKey,
    expected_lane: LaneId,
    expected_failure_domain: FailureDomain,
    server_nonce: [u8; NONCE_LEN],
    deadline: Duration,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    validate_deadline(deadline)?;
    timeout(deadline, async {
        let prepared = prepare_server_lane_inner(io, key).await?;
        let join = prepared.join;
        if join.lane_id != expected_lane || join.failure_domain != expected_failure_domain {
            return Err(LaneHandshakeError::UnexpectedDescriptor);
        }
        finish_server_lane_legacy(prepared, key, server_nonce).await
    })
    .await
    .map_err(|_| LaneHandshakeError::TimedOut)?
}

async fn prepare_server_lane_inner<T>(
    mut io: T,
    key: &BondSessionKey,
) -> Result<PreparedServerLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    let mut hello = [0_u8; HELLO_LEN];
    io.read_exact(&mut hello).await.map_err(io_error)?;
    let (join, client_nonce, encapsulation_key) = decode_hello(key, &hello)?;
    Ok(PreparedServerLane {
        io,
        join,
        client_nonce,
        encapsulation_key,
        hello,
    })
}

async fn finish_server_lane<T>(
    prepared: PreparedServerLane<T>,
    key: &BondSessionKey,
    supported_versions: BondProtocolVersions,
    incarnation: ServerIncarnation,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    let client_mask = client_version_mask(&prepared.client_nonce)?;
    let (server_nonce, selected) =
        fresh_server_nonce(client_mask, supported_versions, incarnation)?;
    let lane = finish_server_lane_with_nonce(
        prepared,
        key,
        server_nonce,
        selected.unwrap_or(BondProtocolVersion::V1),
    )
    .await?;
    selected.ok_or(LaneHandshakeError::NoCommonProtocolVersion {
        local: supported_versions.wire_mask(),
        remote: client_mask,
    })?;
    Ok(lane)
}

async fn finish_server_lane_legacy<T>(
    prepared: PreparedServerLane<T>,
    key: &BondSessionKey,
    mut server_nonce: [u8; NONCE_LEN],
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    avoid_version_marker(&mut server_nonce, &SERVER_VERSION_MAGIC);
    finish_server_lane_with_nonce(prepared, key, server_nonce, BondProtocolVersion::V1).await
}

pub(crate) async fn finish_server_lane_with_nonce<T>(
    mut prepared: PreparedServerLane<T>,
    key: &BondSessionKey,
    server_nonce: [u8; NONCE_LEN],
    protocol_version: BondProtocolVersion,
) -> Result<AuthenticatedLane<T>, LaneHandshakeError>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    let (ciphertext, shared_secret) = prepared.encapsulation_key.encapsulate();
    let accept = encode_accept(
        key,
        prepared.join,
        prepared.client_nonce,
        server_nonce,
        &prepared.hello,
        ciphertext.as_ref(),
    )?;
    prepared.io.write_all(&accept).await.map_err(io_error)?;
    prepared.io.flush().await.map_err(io_error)?;
    let record_keys = derive_record_keys(
        key,
        prepared.join,
        prepared.client_nonce,
        server_nonce,
        shared_secret.as_ref(),
        protocol_version,
        false,
    )?;
    Ok(AuthenticatedLane {
        join: prepared.join,
        client_nonce: prepared.client_nonce,
        server_nonce,
        protocol_version,
        io: prepared.io,
        record_keys,
    })
}

fn fresh_client_nonce(
    supported_versions: BondProtocolVersions,
) -> Result<[u8; NONCE_LEN], LaneHandshakeError> {
    let mut nonce = [0_u8; NONCE_LEN];
    fill_random(&mut nonce)?;
    let join_sequence = if supported_versions.contains(BondProtocolVersion::V3)
        || supported_versions.contains(BondProtocolVersion::V4)
        || supported_versions.contains(BondProtocolVersion::V5)
        || supported_versions.contains(BondProtocolVersion::V6)
    {
        Some(next_client_join_sequence()?)
    } else {
        None
    };
    Ok(encode_client_version_offer(
        nonce,
        supported_versions,
        join_sequence,
    ))
}

fn encode_client_version_offer(
    mut nonce: [u8; NONCE_LEN],
    supported_versions: BondProtocolVersions,
    join_sequence: Option<u64>,
) -> [u8; NONCE_LEN] {
    nonce[..CLIENT_VERSION_MAGIC.len()].copy_from_slice(&CLIENT_VERSION_MAGIC);
    nonce[8..16].copy_from_slice(&supported_versions.wire_mask().to_be_bytes());
    if let Some(sequence) = join_sequence {
        nonce[CLIENT_JOIN_SEQUENCE_START..CLIENT_JOIN_SEQUENCE_END]
            .copy_from_slice(&sequence.to_be_bytes());
    }
    nonce
}

fn next_client_join_sequence() -> Result<u64, LaneHandshakeError> {
    NEXT_CLIENT_JOIN_SEQUENCE
        .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |current| {
            current.checked_add(1)
        })
        .map_err(|_| LaneHandshakeError::ClientJoinSequenceExhausted)
}

pub(crate) fn client_version_mask(
    client_nonce: &[u8; NONCE_LEN],
) -> Result<u64, LaneHandshakeError> {
    if client_nonce[..CLIENT_VERSION_MAGIC.len()] != CLIENT_VERSION_MAGIC {
        return Ok(BondProtocolVersions::LEGACY.wire_mask());
    }
    let mask = u64::from_be_bytes(client_nonce[8..16].try_into().expect("fixed version mask"));
    BondProtocolVersions::from_mask(mask)?;
    Ok(mask)
}

pub(crate) fn client_join_sequence(
    client_nonce: &[u8; NONCE_LEN],
) -> Result<Option<u64>, LaneHandshakeError> {
    let mask = client_version_mask(client_nonce)?;
    if mask
        & (BondProtocolVersion::V3.bit()
            | BondProtocolVersion::V4.bit()
            | BondProtocolVersion::V5.bit()
            | BondProtocolVersion::V6.bit())
        == 0
    {
        return Ok(None);
    }
    let sequence = u64::from_be_bytes(
        client_nonce[CLIENT_JOIN_SEQUENCE_START..CLIENT_JOIN_SEQUENCE_END]
            .try_into()
            .expect("fixed client join sequence"),
    );
    if sequence == 0 {
        return Err(LaneHandshakeError::InvalidClientJoinSequence);
    }
    Ok(Some(sequence))
}

pub(crate) fn fresh_server_nonce(
    client_mask: u64,
    supported_versions: BondProtocolVersions,
    incarnation: ServerIncarnation,
) -> Result<([u8; NONCE_LEN], Option<BondProtocolVersion>), LaneHandshakeError> {
    let mut nonce = [0_u8; NONCE_LEN];
    fill_random(&mut nonce)?;
    let selected = supported_versions.newest_common_mask(client_mask);
    Ok((
        encode_server_version_selection(nonce, supported_versions, selected, incarnation),
        selected,
    ))
}

pub(crate) fn encode_server_version_selection(
    mut nonce: [u8; NONCE_LEN],
    supported_versions: BondProtocolVersions,
    selected: Option<BondProtocolVersion>,
    incarnation: ServerIncarnation,
) -> [u8; NONCE_LEN] {
    nonce[..SERVER_VERSION_MAGIC.len()].copy_from_slice(&SERVER_VERSION_MAGIC);
    nonce[8..16].copy_from_slice(&supported_versions.wire_mask().to_be_bytes());
    nonce[16] = selected.map_or(0, BondProtocolVersion::get);
    if selected.is_some_and(|version| version >= BondProtocolVersion::V5) {
        nonce[SERVER_INCARNATION_START..SERVER_INCARNATION_END]
            .copy_from_slice(&incarnation.get().to_be_bytes());
    }
    nonce
}

pub(crate) fn select_client_protocol_version(
    supported_versions: BondProtocolVersions,
    server_nonce: &[u8; NONCE_LEN],
) -> Result<BondProtocolVersion, LaneHandshakeError> {
    if server_nonce[..SERVER_VERSION_MAGIC.len()] != SERVER_VERSION_MAGIC {
        return if supported_versions.contains(BondProtocolVersion::V1) {
            Ok(BondProtocolVersion::V1)
        } else {
            Err(LaneHandshakeError::NoCommonProtocolVersion {
                local: supported_versions.wire_mask(),
                remote: BondProtocolVersions::LEGACY.wire_mask(),
            })
        };
    }
    let remote = u64::from_be_bytes(server_nonce[8..16].try_into().expect("fixed version mask"));
    BondProtocolVersions::from_mask(remote)?;
    let expected = supported_versions.newest_common_mask(remote);
    let selected = match server_nonce[16] {
        1 => Some(BondProtocolVersion::V1),
        2 => Some(BondProtocolVersion::V2),
        3 => Some(BondProtocolVersion::V3),
        4 => Some(BondProtocolVersion::V4),
        5 => Some(BondProtocolVersion::V5),
        6 => Some(BondProtocolVersion::V6),
        0 => None,
        value => return Err(LaneHandshakeError::InvalidProtocolVersion(value)),
    };
    match (expected, selected) {
        (None, None) => Err(LaneHandshakeError::NoCommonProtocolVersion {
            local: supported_versions.wire_mask(),
            remote,
        }),
        (Some(expected), Some(selected)) if expected == selected => Ok(selected),
        (expected, selected) => Err(LaneHandshakeError::ProtocolDowngrade {
            expected: expected.map(BondProtocolVersion::get),
            selected: selected.map(BondProtocolVersion::get),
        }),
    }
}

fn avoid_version_marker(nonce: &mut [u8; NONCE_LEN], marker: &[u8; 8]) {
    if nonce[..marker.len()] == marker[..] {
        nonce[0] ^= 0xff;
    }
}

pub(crate) fn encode_hello(
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    encapsulation_key: &EncapsulationKey,
) -> Result<[u8; HELLO_LEN], LaneHandshakeError> {
    let mut wire = [0_u8; HELLO_LEN];
    wire[..4].copy_from_slice(&HELLO_MAGIC);
    encode_descriptor(join, &mut wire[4..4 + DESCRIPTOR_LEN]);
    let nonce_start = 4 + DESCRIPTOR_LEN;
    wire[nonce_start..nonce_start + NONCE_LEN].copy_from_slice(&client_nonce);
    let public_key = encapsulation_key.to_bytes();
    wire[nonce_start + NONCE_LEN..HELLO_BODY_LEN].copy_from_slice(public_key.as_ref());
    let tag = authentication_tag(key, CLIENT_DOMAIN, &wire[..HELLO_BODY_LEN])?;
    wire[HELLO_BODY_LEN..].copy_from_slice(&tag);
    Ok(wire)
}

pub(crate) fn decode_hello(
    key: &BondSessionKey,
    wire: &[u8; HELLO_LEN],
) -> Result<(LaneJoin, [u8; NONCE_LEN], EncapsulationKey), LaneHandshakeError> {
    if wire[..4] != HELLO_MAGIC {
        return Err(LaneHandshakeError::InvalidRecord);
    }
    verify_tag(
        key,
        CLIENT_DOMAIN,
        &wire[..HELLO_BODY_LEN],
        &wire[HELLO_BODY_LEN..],
    )?;
    let join = decode_descriptor(&wire[4..4 + DESCRIPTOR_LEN])?;
    let mut client_nonce = [0_u8; NONCE_LEN];
    let nonce_start = 4 + DESCRIPTOR_LEN;
    client_nonce.copy_from_slice(&wire[nonce_start..nonce_start + NONCE_LEN]);
    let public_key =
        Key::<EncapsulationKey>::try_from(&wire[nonce_start + NONCE_LEN..HELLO_BODY_LEN])
            .map_err(|_| LaneHandshakeError::InvalidRecord)?;
    let encapsulation_key =
        EncapsulationKey::new(&public_key).map_err(|_| LaneHandshakeError::InvalidRecord)?;
    Ok((join, client_nonce, encapsulation_key))
}

pub(crate) fn encode_accept(
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    server_nonce: [u8; NONCE_LEN],
    hello: &[u8; HELLO_LEN],
    ciphertext: &[u8],
) -> Result<[u8; ACCEPT_LEN], LaneHandshakeError> {
    if ciphertext.len() != ML_KEM_CIPHERTEXT_LEN {
        return Err(LaneHandshakeError::InvalidRecord);
    }
    let mut wire = [0_u8; ACCEPT_LEN];
    wire[..4].copy_from_slice(&ACCEPT_MAGIC);
    encode_descriptor(join, &mut wire[4..4 + DESCRIPTOR_LEN]);
    let client_start = 4 + DESCRIPTOR_LEN;
    wire[client_start..client_start + NONCE_LEN].copy_from_slice(&client_nonce);
    let server_start = client_start + NONCE_LEN;
    wire[server_start..server_start + NONCE_LEN].copy_from_slice(&server_nonce);
    wire[server_start + NONCE_LEN..ACCEPT_BODY_LEN].copy_from_slice(ciphertext);
    let tag = authentication_tag_parts(
        key,
        SERVER_DOMAIN,
        &[&hello[..HELLO_BODY_LEN], &wire[..ACCEPT_BODY_LEN]],
    )?;
    wire[ACCEPT_BODY_LEN..].copy_from_slice(&tag);
    Ok(wire)
}

pub(crate) fn decode_accept(
    key: &BondSessionKey,
    expected: LaneJoin,
    expected_client_nonce: [u8; NONCE_LEN],
    hello: &[u8; HELLO_LEN],
    wire: &[u8; ACCEPT_LEN],
) -> Result<([u8; NONCE_LEN], ml_kem::kem::Ciphertext<MlKem768>), LaneHandshakeError> {
    if wire[..4] != ACCEPT_MAGIC {
        return Err(LaneHandshakeError::InvalidRecord);
    }
    verify_tag_parts(
        key,
        SERVER_DOMAIN,
        &[&hello[..HELLO_BODY_LEN], &wire[..ACCEPT_BODY_LEN]],
        &wire[ACCEPT_BODY_LEN..],
    )?;
    let join = decode_descriptor(&wire[4..4 + DESCRIPTOR_LEN])?;
    let client_start = 4 + DESCRIPTOR_LEN;
    if join != expected || wire[client_start..client_start + NONCE_LEN] != expected_client_nonce {
        return Err(LaneHandshakeError::UnexpectedDescriptor);
    }
    let mut server_nonce = [0_u8; NONCE_LEN];
    let server_start = client_start + NONCE_LEN;
    server_nonce.copy_from_slice(&wire[server_start..server_start + NONCE_LEN]);
    let ciphertext = ml_kem::kem::Ciphertext::<MlKem768>::try_from(
        &wire[server_start + NONCE_LEN..ACCEPT_BODY_LEN],
    )
    .map_err(|_| LaneHandshakeError::InvalidRecord)?;
    Ok((server_nonce, ciphertext))
}

fn encode_descriptor(join: LaneJoin, output: &mut [u8]) {
    output[..8].copy_from_slice(&join.session_id.to_be_bytes());
    output[8..12].copy_from_slice(&join.lane_id.get().to_be_bytes());
    output[12..20].copy_from_slice(&join.failure_domain.get().to_be_bytes());
}

fn decode_descriptor(input: &[u8]) -> Result<LaneJoin, LaneHandshakeError> {
    let session_id = u64::from_be_bytes(input[..8].try_into().expect("exact session field"));
    let lane_id = u32::from_be_bytes(input[8..12].try_into().expect("exact lane field"));
    let failure_domain = u64::from_be_bytes(input[12..20].try_into().expect("exact domain field"));
    LaneJoin::new(
        session_id,
        LaneId::new(lane_id)?,
        FailureDomain::new(failure_domain)?,
    )
}

pub(crate) fn authentication_tag(
    key: &BondSessionKey,
    domain: &[u8],
    body: &[u8],
) -> Result<[u8; TAG_LEN], LaneHandshakeError> {
    authentication_tag_parts(key, domain, &[body])
}

pub(crate) fn authentication_tag_parts(
    key: &BondSessionKey,
    domain: &[u8],
    parts: &[&[u8]],
) -> Result<[u8; TAG_LEN], LaneHandshakeError> {
    let mut mac = HmacSha256::new_from_slice(&key.0[..])
        .map_err(|_| LaneHandshakeError::AuthenticationFailed)?;
    mac.update(domain);
    for part in parts {
        mac.update(part);
    }
    Ok(mac.finalize().into_bytes().into())
}

fn verify_tag(
    key: &BondSessionKey,
    domain: &[u8],
    body: &[u8],
    tag: &[u8],
) -> Result<(), LaneHandshakeError> {
    verify_tag_parts(key, domain, &[body], tag)
}

fn verify_tag_parts(
    key: &BondSessionKey,
    domain: &[u8],
    parts: &[&[u8]],
    tag: &[u8],
) -> Result<(), LaneHandshakeError> {
    let mut mac = HmacSha256::new_from_slice(&key.0[..])
        .map_err(|_| LaneHandshakeError::AuthenticationFailed)?;
    mac.update(domain);
    for part in parts {
        mac.update(part);
    }
    mac.verify_slice(tag)
        .map_err(|_| LaneHandshakeError::AuthenticationFailed)
}

fn derive_record_keys(
    key: &BondSessionKey,
    join: LaneJoin,
    client_nonce: [u8; NONCE_LEN],
    server_nonce: [u8; NONCE_LEN],
    shared_secret: &[u8],
    protocol_version: BondProtocolVersion,
    client: bool,
) -> Result<LaneRecordKeys, LaneHandshakeError> {
    let hkdf = Hkdf::<Sha256>::new(Some(&key.0[..]), shared_secret);
    let mut descriptor = [0_u8; DESCRIPTOR_LEN];
    encode_descriptor(join, &mut descriptor);
    let mut info =
        Vec::with_capacity(KEY_SCHEDULE_INFO.len() + DESCRIPTOR_LEN + NONCE_LEN + NONCE_LEN);
    info.extend_from_slice(KEY_SCHEDULE_INFO);
    info.extend_from_slice(&descriptor);
    info.extend_from_slice(&client_nonce);
    info.extend_from_slice(&server_nonce);
    if protocol_version != BondProtocolVersion::V1 {
        info.extend_from_slice(NEGOTIATED_KEY_SCHEDULE_INFO);
        info.push(protocol_version.get());
    }
    let mut material = Zeroizing::new([0_u8; 64]);
    hkdf.expand(&info, &mut material[..])
        .map_err(|_| LaneHandshakeError::KeyScheduleFailed)?;
    let mut client_to_server = [0_u8; 32];
    let mut server_to_client = [0_u8; 32];
    client_to_server.copy_from_slice(&material[..32]);
    server_to_client.copy_from_slice(&material[32..]);
    Ok(if client {
        LaneRecordKeys::new(client_to_server, server_to_client)
    } else {
        LaneRecordKeys::new(server_to_client, client_to_server)
    })
}

fn fill_random(output: &mut [u8]) -> Result<(), LaneHandshakeError> {
    getrandom::getrandom(output).map_err(|error| LaneHandshakeError::Random(error.to_string()))
}

fn validate_deadline(deadline: Duration) -> Result<(), LaneHandshakeError> {
    if deadline.is_zero() {
        Err(LaneHandshakeError::ZeroDeadline)
    } else {
        Ok(())
    }
}

fn io_error(error: std::io::Error) -> LaneHandshakeError {
    LaneHandshakeError::Io(error.to_string())
}

#[derive(Debug, Eq, PartialEq)]
pub enum LaneHandshakeError {
    ZeroSessionId,
    ZeroDeadline,
    NoExpectedLanes,
    InvalidRecord,
    UnexpectedDescriptor,
    AuthenticationFailed,
    KeyScheduleFailed,
    NoSupportedProtocolVersions,
    InvalidProtocolVersion(u8),
    InvalidClientJoinSequence,
    ClientJoinSequenceExhausted,
    ZeroServerIncarnation,
    NoCommonProtocolVersion {
        local: u64,
        remote: u64,
    },
    ProtocolDowngrade {
        expected: Option<u8>,
        selected: Option<u8>,
    },
    ProtocolVersionMismatch {
        expected: BondProtocolVersion,
        actual: BondProtocolVersion,
    },
    DuplicateLane(LaneId),
    ReplayedClientNonce,
    TimedOut,
    Random(String),
    Io(String),
    Scheduler(SchedulerError),
}

impl From<SchedulerError> for LaneHandshakeError {
    fn from(error: SchedulerError) -> Self {
        Self::Scheduler(error)
    }
}

impl fmt::Display for LaneHandshakeError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::ZeroSessionId => write!(formatter, "bond session ID must be non-zero"),
            Self::ZeroDeadline => write!(formatter, "lane handshake deadline must be non-zero"),
            Self::NoExpectedLanes => write!(formatter, "lane registry requires expected lanes"),
            Self::InvalidRecord => write!(formatter, "invalid bond lane handshake record"),
            Self::UnexpectedDescriptor => write!(formatter, "unexpected bond lane descriptor"),
            Self::AuthenticationFailed => write!(formatter, "bond lane authentication failed"),
            Self::KeyScheduleFailed => write!(formatter, "bond lane key schedule failed"),
            Self::NoSupportedProtocolVersions => {
                write!(formatter, "bond protocol version set must not be empty")
            }
            Self::InvalidProtocolVersion(version) => {
                write!(formatter, "peer selected unsupported bond protocol version {version}")
            }
            Self::InvalidClientJoinSequence => {
                write!(formatter, "bond protocol v3 client join sequence must be non-zero")
            }
            Self::ClientJoinSequenceExhausted => {
                write!(formatter, "bond client join sequence exhausted")
            }
            Self::ZeroServerIncarnation => {
                write!(formatter, "bond server incarnation must be non-zero")
            }
            Self::NoCommonProtocolVersion { local, remote } => write!(
                formatter,
                "no common bond protocol version (local mask {local:#018x}, peer mask {remote:#018x})"
            ),
            Self::ProtocolDowngrade { expected, selected } => write!(
                formatter,
                "authenticated bond protocol downgrade (expected {expected:?}, selected {selected:?})"
            ),
            Self::ProtocolVersionMismatch { expected, actual } => write!(
                formatter,
                "bond session protocol version mismatch (expected {}, received {})",
                expected.get(),
                actual.get()
            ),
            Self::DuplicateLane(id) => write!(formatter, "bond lane {} joined twice", id.get()),
            Self::ReplayedClientNonce => write!(formatter, "bond client nonce was replayed"),
            Self::TimedOut => write!(formatter, "bond lane handshake timed out"),
            Self::Random(error) => write!(formatter, "OS randomness failed: {error}"),
            Self::Io(error) => write!(formatter, "bond lane handshake I/O failed: {error}"),
            Self::Scheduler(error) => error.fmt(formatter),
        }
    }
}

impl Error for LaneHandshakeError {}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use anonssh_bond::{FailureDomain, LaneId};
    use ml_kem::{kem::Kem, MlKem768};
    use tokio::io::{duplex, AsyncWriteExt, DuplexStream};

    use super::{
        authenticate_client_lane_with_nonce, authenticate_server_lane_unbound_with_nonce,
        authenticate_server_lane_with_nonce, prepare_server_lane, AuthenticatedLane,
        BondProtocolVersion, BondProtocolVersions, BondSessionKey, LaneHandshakeError, LaneJoin,
        LaneJoinRegistry, PreparedClientLane, ServerIncarnation,
    };

    fn join() -> LaneJoin {
        LaneJoin::new(41, LaneId::new(2).unwrap(), FailureDomain::new(9).unwrap()).unwrap()
    }

    #[test]
    fn version_negotiation_nonce_vectors_are_locked() {
        let client_nonce = super::encode_client_version_offer(
            [0xa5; 32],
            BondProtocolVersions::CURRENT,
            Some(0x0102_0304_0506_0708),
        );
        assert_eq!(
            client_nonce,
            [
                65, 66, 80, 86, 67, 48, 49, 0, 0, 0, 0, 0, 0, 0, 0, 63, 1, 2, 3, 4, 5, 6, 7, 8,
                165, 165, 165, 165, 165, 165, 165, 165,
            ]
        );
        assert_eq!(
            super::client_join_sequence(&client_nonce),
            Ok(Some(0x0102_0304_0506_0708))
        );
        let v2_nonce = super::encode_client_version_offer(
            [0xa5; 32],
            BondProtocolVersions::V2_COMPATIBLE,
            None,
        );
        assert_eq!(super::client_join_sequence(&v2_nonce), Ok(None));
        assert_eq!(
            super::encode_server_version_selection(
                [0x5a; 32],
                BondProtocolVersions::CURRENT,
                Some(BondProtocolVersion::V6),
                ServerIncarnation::from_u64(0x0102_0304_0506_0708).unwrap(),
            ),
            [
                65, 66, 80, 86, 83, 48, 49, 0, 0, 0, 0, 0, 0, 0, 0, 63, 6, 1, 2, 3, 4, 5, 6, 7, 8,
                90, 90, 90, 90, 90, 90, 90,
            ]
        );
        assert_eq!(
            BondProtocolVersions::new([]),
            Err(LaneHandshakeError::NoSupportedProtocolVersions)
        );
    }

    async fn negotiate(
        client_versions: BondProtocolVersions,
        server_versions: BondProtocolVersions,
    ) -> (
        Result<AuthenticatedLane<DuplexStream>, LaneHandshakeError>,
        Result<AuthenticatedLane<DuplexStream>, LaneHandshakeError>,
    ) {
        negotiate_with_incarnation(
            client_versions,
            server_versions,
            ServerIncarnation::from_u64(7).unwrap(),
        )
        .await
    }

    async fn negotiate_with_incarnation(
        client_versions: BondProtocolVersions,
        server_versions: BondProtocolVersions,
        incarnation: ServerIncarnation,
    ) -> (
        Result<AuthenticatedLane<DuplexStream>, LaneHandshakeError>,
        Result<AuthenticatedLane<DuplexStream>, LaneHandshakeError>,
    ) {
        let key = BondSessionKey::new([7; 32]);
        let prepared =
            PreparedClientLane::new_with_versions(&key, join(), client_versions).unwrap();
        let initial_payload = prepared.initial_payload().to_vec();
        let (mut client_io, server_io) = duplex(4096);
        let client = async {
            client_io.write_all(&initial_payload).await.unwrap();
            prepared
                .finish(client_io, &key, Duration::from_secs(1))
                .await
        };
        let server = async {
            let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1)).await?;
            prepared
                .finish_with_versions_and_incarnation(
                    &key,
                    server_versions,
                    incarnation,
                    Duration::from_secs(1),
                )
                .await
        };
        tokio::join!(client, server)
    }

    #[tokio::test]
    async fn negotiates_the_newest_common_authenticated_version() {
        let (client, server) =
            negotiate(BondProtocolVersions::CURRENT, BondProtocolVersions::CURRENT).await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V6);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V6);

        let (client, server) = negotiate(
            BondProtocolVersions::CURRENT,
            BondProtocolVersions::V5_COMPATIBLE,
        )
        .await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V5);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V5);

        let (client, server) = negotiate(
            BondProtocolVersions::V5_COMPATIBLE,
            BondProtocolVersions::CURRENT,
        )
        .await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V5);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V5);

        let (client, server) = negotiate(
            BondProtocolVersions::CURRENT,
            BondProtocolVersions::V3_COMPATIBLE,
        )
        .await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V3);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V3);

        let (client, server) = negotiate(
            BondProtocolVersions::CURRENT,
            BondProtocolVersions::V2_COMPATIBLE,
        )
        .await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V2);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V2);

        let (client, server) = negotiate(
            BondProtocolVersions::V2_COMPATIBLE,
            BondProtocolVersions::CURRENT,
        )
        .await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V2);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V2);

        let (client, server) =
            negotiate(BondProtocolVersions::CURRENT, BondProtocolVersions::LEGACY).await;
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V1);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V1);
    }

    #[tokio::test]
    async fn v5_authenticates_server_incarnation_while_v4_remains_unchanged() {
        let first = ServerIncarnation::from_u64(0x1111).unwrap();
        let second = ServerIncarnation::from_u64(0x2222).unwrap();
        let (client, server) = negotiate_with_incarnation(
            BondProtocolVersions::CURRENT,
            BondProtocolVersions::CURRENT,
            first,
        )
        .await;
        assert_eq!(client.unwrap().server_incarnation(), Ok(Some(first)));
        assert_eq!(server.unwrap().server_incarnation(), Ok(Some(first)));

        let (client, server) = negotiate_with_incarnation(
            BondProtocolVersions::CURRENT,
            BondProtocolVersions::CURRENT,
            second,
        )
        .await;
        assert_eq!(client.unwrap().server_incarnation(), Ok(Some(second)));
        assert_eq!(server.unwrap().server_incarnation(), Ok(Some(second)));

        let (client, server) = negotiate_with_incarnation(
            BondProtocolVersions::CURRENT,
            BondProtocolVersions::V4_COMPATIBLE,
            second,
        )
        .await;
        assert_eq!(client.unwrap().server_incarnation(), Ok(None));
        assert_eq!(server.unwrap().server_incarnation(), Ok(None));
    }

    #[tokio::test]
    async fn reports_an_authenticated_no_common_version_result() {
        let local = BondProtocolVersions::only(BondProtocolVersion::V2);
        let remote = BondProtocolVersions::only(BondProtocolVersion::V1);
        let (client, server) = negotiate(local, remote).await;
        assert_eq!(
            client.unwrap_err(),
            LaneHandshakeError::NoCommonProtocolVersion {
                local: local.wire_mask(),
                remote: remote.wire_mask(),
            }
        );
        assert_eq!(
            server.unwrap_err(),
            LaneHandshakeError::NoCommonProtocolVersion {
                local: remote.wire_mask(),
                remote: local.wire_mask(),
            }
        );
    }

    #[tokio::test]
    async fn rejects_an_authenticated_downgrade_below_newest_common() {
        let key = BondSessionKey::new([7; 32]);
        let prepared = PreparedClientLane::new(&key, join()).unwrap();
        let initial_payload = prepared.initial_payload().to_vec();
        let (mut client_io, server_io) = duplex(4096);
        let client = async {
            client_io.write_all(&initial_payload).await.unwrap();
            prepared
                .finish(client_io, &key, Duration::from_secs(1))
                .await
        };
        let server = async {
            let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1)).await?;
            let client_mask = super::client_version_mask(&prepared.client_nonce)?;
            let (mut nonce, _) = super::fresh_server_nonce(
                client_mask,
                BondProtocolVersions::CURRENT,
                ServerIncarnation::from_u64(7).unwrap(),
            )?;
            nonce[16] = BondProtocolVersion::V1.get();
            super::finish_server_lane_with_nonce(prepared, &key, nonce, BondProtocolVersion::V1)
                .await
        };
        let (client, server) = tokio::join!(client, server);
        assert_eq!(
            client.unwrap_err(),
            LaneHandshakeError::ProtocolDowngrade {
                expected: Some(BondProtocolVersion::V6.get()),
                selected: Some(BondProtocolVersion::V1.get()),
            }
        );
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V1);
    }

    #[tokio::test]
    async fn old_client_and_new_server_use_unchanged_v1() {
        let key = BondSessionKey::new([7; 32]);
        let (client_io, server_io) = duplex(4096);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = async {
            let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1)).await?;
            prepared.finish(&key, Duration::from_secs(1)).await
        };
        let (client, server) = tokio::join!(client, server);
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V1);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V1);
    }

    #[tokio::test]
    async fn new_client_and_old_server_use_unchanged_v1() {
        let key = BondSessionKey::new([7; 32]);
        let prepared = PreparedClientLane::new(&key, join()).unwrap();
        let initial_payload = prepared.initial_payload().to_vec();
        let (mut client_io, server_io) = duplex(4096);
        let client = async {
            client_io.write_all(&initial_payload).await.unwrap();
            prepared
                .finish(client_io, &key, Duration::from_secs(1))
                .await
        };
        let server = authenticate_server_lane_with_nonce(
            server_io,
            &key,
            join(),
            [13; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        assert_eq!(client.unwrap().protocol_version(), BondProtocolVersion::V1);
        assert_eq!(server.unwrap().protocol_version(), BondProtocolVersion::V1);
    }

    #[tokio::test]
    async fn mutually_authenticates_and_binds_a_lane() {
        let key = BondSessionKey::new([7; 32]);
        let (client_io, server_io) = duplex(512);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = authenticate_server_lane_with_nonce(
            server_io,
            &key,
            join(),
            [13; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        let client = client.unwrap();
        let server = server.unwrap();
        assert_eq!(client.join, join());
        assert_eq!(server.join, join());
        assert_eq!(client.client_nonce, server.client_nonce);
        assert_eq!(client.server_nonce, server.server_nonce);
    }

    #[tokio::test]
    async fn prepared_client_hello_completes_after_transport_injection() {
        let key = BondSessionKey::new([7; 32]);
        let prepared = PreparedClientLane::new(&key, join()).unwrap();
        let initial_payload = prepared.initial_payload().to_vec();
        let (mut client_io, server_io) = duplex(512);
        let client = async {
            client_io.write_all(&initial_payload).await.unwrap();
            prepared
                .finish(client_io, &key, Duration::from_secs(1))
                .await
        };
        let server = authenticate_server_lane_with_nonce(
            server_io,
            &key,
            join(),
            [13; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        let client = client.unwrap();
        let server = server.unwrap();
        assert_eq!(client.join, join());
        assert_eq!(client.client_nonce, server.client_nonce);
        assert_eq!(client.server_nonce, server.server_nonce);
    }

    #[tokio::test]
    async fn server_can_authenticate_before_routing_a_lane() {
        let key = BondSessionKey::new([7; 32]);
        let (client_io, server_io) = duplex(512);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = async {
            let prepared = prepare_server_lane(server_io, &key, Duration::from_secs(1)).await?;
            assert_eq!(prepared.join(), join());
            assert_eq!(prepared.client_nonce(), [11; 32]);
            prepared.finish(&key, Duration::from_secs(1)).await
        };
        let (client, server) = tokio::join!(client, server);
        let client = client.unwrap();
        let server = server.unwrap();
        assert_eq!(client.join, server.join);
        assert_eq!(client.client_nonce, server.client_nonce);
        assert_eq!(client.server_nonce, server.server_nonce);
    }

    #[tokio::test]
    async fn rejects_wrong_keys_and_descriptors() {
        let (client_io, server_io) = duplex(512);
        let client_key = BondSessionKey::new([7; 32]);
        let server_key = BondSessionKey::new([8; 32]);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &client_key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = authenticate_server_lane_with_nonce(
            server_io,
            &server_key,
            join(),
            [13; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        assert!(client.is_err());
        assert_eq!(
            server.unwrap_err(),
            LaneHandshakeError::AuthenticationFailed
        );

        let (client_io, server_io) = duplex(512);
        let key = BondSessionKey::new([7; 32]);
        let other = LaneJoin::new(
            join().session_id,
            LaneId::new(3).unwrap(),
            join().failure_domain,
        )
        .unwrap();
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = authenticate_server_lane_with_nonce(
            server_io,
            &key,
            other,
            [13; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        assert!(client.is_err());
        assert_eq!(
            server.unwrap_err(),
            LaneHandshakeError::UnexpectedDescriptor
        );
    }

    #[tokio::test]
    async fn rejects_reflection_truncation_and_timeout() {
        let key = BondSessionKey::new([7; 32]);
        let (client_io, mut peer) = duplex(512);
        let (_, encapsulation_key) = MlKem768::generate_keypair();
        let reflected = super::encode_hello(&key, join(), [11; 32], &encapsulation_key).unwrap();
        let peer_task = tokio::spawn(async move {
            let mut hello = [0_u8; super::HELLO_LEN];
            tokio::io::AsyncReadExt::read_exact(&mut peer, &mut hello)
                .await
                .unwrap();
            peer.write_all(&reflected).await.unwrap();
        });
        let error = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        )
        .await
        .unwrap_err();
        assert!(matches!(
            error,
            LaneHandshakeError::Io(_) | LaneHandshakeError::InvalidRecord
        ));
        peer_task.await.unwrap();

        let (mut peer, server_io) = duplex(512);
        peer.write_all(b"short").await.unwrap();
        drop(peer);
        assert!(matches!(
            authenticate_server_lane_with_nonce(
                server_io,
                &key,
                join(),
                [13; 32],
                Duration::from_secs(1),
            )
            .await
            .unwrap_err(),
            LaneHandshakeError::Io(_)
        ));

        let (_peer, server_io) = duplex(512);
        assert_eq!(
            authenticate_server_lane_with_nonce(
                server_io,
                &key,
                join(),
                [13; 32],
                Duration::from_millis(1),
            )
            .await
            .unwrap_err(),
            LaneHandshakeError::TimedOut
        );
    }

    #[tokio::test]
    async fn registry_rejects_duplicate_lanes_and_nonces() {
        let key = BondSessionKey::new([7; 32]);
        let (client_io, server_io) = duplex(512);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = authenticate_server_lane_with_nonce(
            server_io,
            &key,
            join(),
            [13; 32],
            Duration::from_secs(1),
        );
        let (_, server) = tokio::join!(client, server);
        let server = server.unwrap();
        let mut registry =
            LaneJoinRegistry::new(join().session_id, [(join().lane_id, join().failure_domain)])
                .unwrap();
        registry.register(&server).unwrap();
        assert!(registry.is_complete());
        assert_eq!(
            registry.register(&server).unwrap_err(),
            LaneHandshakeError::DuplicateLane(join().lane_id)
        );
    }

    #[tokio::test]
    async fn first_server_lane_authenticates_and_establishes_the_session_epoch() {
        let key = BondSessionKey::new([7; 32]);
        let (client_io, server_io) = duplex(512);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [11; 32],
            Duration::from_secs(1),
        );
        let server = authenticate_server_lane_unbound_with_nonce(
            server_io,
            &key,
            join().lane_id,
            join().failure_domain,
            [13; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        assert_eq!(client.unwrap().join, join());
        assert_eq!(server.unwrap().join, join());

        let (client_io, server_io) = duplex(512);
        let client = authenticate_client_lane_with_nonce(
            client_io,
            &key,
            join(),
            [17; 32],
            Duration::from_secs(1),
        );
        let server = authenticate_server_lane_unbound_with_nonce(
            server_io,
            &key,
            LaneId::new(99).unwrap(),
            join().failure_domain,
            [19; 32],
            Duration::from_secs(1),
        );
        let (client, server) = tokio::join!(client, server);
        assert!(client.is_err());
        assert_eq!(
            server.unwrap_err(),
            LaneHandshakeError::UnexpectedDescriptor
        );
    }

    #[test]
    fn record_key_schedule_has_a_locked_role_separated_vector() {
        let key = BondSessionKey::new([7; 32]);
        let client = super::derive_record_keys(
            &key,
            join(),
            [11; 32],
            [13; 32],
            &[0x42; 32],
            BondProtocolVersion::V1,
            true,
        )
        .unwrap();
        let server = super::derive_record_keys(
            &key,
            join(),
            [11; 32],
            [13; 32],
            &[0x42; 32],
            BondProtocolVersion::V1,
            false,
        )
        .unwrap();
        let (client_send, client_receive) = client.test_bytes();
        let (server_send, server_receive) = server.test_bytes();
        assert_eq!(
            client_send,
            [
                160, 240, 167, 215, 58, 207, 187, 204, 129, 31, 231, 142, 246, 0, 60, 42, 4, 216,
                59, 59, 70, 196, 65, 19, 104, 92, 224, 66, 49, 231, 241, 216,
            ]
        );
        assert_eq!(
            client_receive,
            [
                76, 213, 131, 34, 22, 30, 9, 200, 157, 148, 106, 188, 18, 255, 47, 27, 236, 248,
                140, 5, 106, 226, 108, 22, 106, 227, 107, 244, 53, 4, 95, 142,
            ]
        );
        assert_eq!(client_receive, server_send);
        assert_eq!(client_send, server_receive);
    }
}
