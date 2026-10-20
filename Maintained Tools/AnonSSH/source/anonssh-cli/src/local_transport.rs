use std::time::Duration;

use anonssh_bond::TrafficClass;
use anyhow::{bail, Context, Result};
use serde::{de::DeserializeOwned, Deserialize, Serialize};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};

use crate::application_service::ServiceName;

const MAGIC: [u8; 4] = *b"ALP1";
const VERSION: u8 = 1;
const MAX_RECORD_BYTES: usize = 64 * 1024;
const MAX_REQUEST_ID_BYTES: usize = 64;
const MAX_TARGET_BYTES: usize = 318;
const MAX_MESSAGE_BYTES: usize = 256;
pub const MIN_SETUP_DEADLINE: Duration = Duration::from_secs(1);
pub const MAX_SETUP_DEADLINE: Duration = Duration::from_secs(15 * 60);
pub const DEFAULT_SETUP_DEADLINE: Duration = Duration::from_secs(15 * 60);

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize, clap::ValueEnum)]
#[serde(rename_all = "kebab-case")]
pub enum AlpTrafficClass {
    Control,
    Realtime,
    Interactive,
    Bulk,
}

impl From<AlpTrafficClass> for TrafficClass {
    fn from(value: AlpTrafficClass) -> Self {
        match value {
            AlpTrafficClass::Control => Self::Control,
            AlpTrafficClass::Realtime => Self::Realtime,
            AlpTrafficClass::Interactive => Self::Interactive,
            AlpTrafficClass::Bulk => Self::Bulk,
        }
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize, clap::ValueEnum)]
#[serde(rename_all = "kebab-case")]
pub enum AlpTransport {
    Auto,
    Mixed,
    TorOnly,
    I2pOnly,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AlpDialRequest {
    version: u8,
    operation: String,
    pub request_id: String,
    pub target: String,
    pub service: String,
    pub class: AlpTrafficClass,
    pub transport: AlpTransport,
    pub deadline_millis: u64,
}

impl AlpDialRequest {
    pub fn new(
        request_id: String,
        target: String,
        service: String,
        class: AlpTrafficClass,
        transport: AlpTransport,
        deadline: Duration,
    ) -> Result<Self> {
        let deadline_millis = u64::try_from(deadline.as_millis())
            .context("ALP setup deadline does not fit its wire field")?;
        let request = Self {
            version: VERSION,
            operation: "dial".to_owned(),
            request_id,
            target,
            service,
            class,
            transport,
            deadline_millis,
        };
        request.validate()?;
        Ok(request)
    }

    pub fn validate(&self) -> Result<()> {
        if self.version != VERSION || self.operation != "dial" {
            bail!("unsupported ALP operation or version");
        }
        validate_request_id(&self.request_id)?;
        validate_target(&self.target)?;
        ServiceName::parse(&self.service)?;
        let deadline = self.deadline();
        if !(MIN_SETUP_DEADLINE..=MAX_SETUP_DEADLINE).contains(&deadline) {
            bail!("ALP setup deadline is outside its permitted range");
        }
        Ok(())
    }

    pub const fn deadline(&self) -> Duration {
        Duration::from_millis(self.deadline_millis)
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum AlpErrorCode {
    UnsupportedVersion,
    MalformedRequest,
    UnauthorizedPeer,
    AuthorizationRequired,
    UnknownTarget,
    UnknownService,
    ClassDenied,
    Capacity,
    Timeout,
    PeerIncompatible,
    RouteUnavailable,
    ServiceUnavailable,
    Internal,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
enum AlpResultStatus {
    Ready,
    Error,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct AlpResult {
    version: u8,
    pub request_id: String,
    status: AlpResultStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error_code: Option<AlpErrorCode>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
}

impl AlpResult {
    pub fn ready(request_id: String) -> Result<Self> {
        validate_request_id(&request_id)?;
        Ok(Self {
            version: VERSION,
            request_id,
            status: AlpResultStatus::Ready,
            error_code: None,
            message: None,
        })
    }

    pub fn error(
        request_id: String,
        error_code: AlpErrorCode,
        message: impl Into<String>,
    ) -> Result<Self> {
        validate_request_id(&request_id)?;
        let message = message.into();
        if message.is_empty() || message.len() > MAX_MESSAGE_BYTES || !message.is_ascii() {
            bail!("ALP error message is not bounded ASCII");
        }
        Ok(Self {
            version: VERSION,
            request_id,
            status: AlpResultStatus::Error,
            error_code: Some(error_code),
            message: Some(message),
        })
    }

    pub fn into_ready(self) -> Result<()> {
        if self.version != VERSION {
            bail!("broker returned an unsupported ALP version");
        }
        validate_request_id(&self.request_id)?;
        match (self.status, self.error_code, self.message) {
            (AlpResultStatus::Ready, None, None) => Ok(()),
            (AlpResultStatus::Error, Some(code), Some(message)) => {
                if message.is_empty() || message.len() > MAX_MESSAGE_BYTES || !message.is_ascii() {
                    bail!("broker returned an invalid ALP error message");
                }
                bail!("ALP dial failed: {code:?}: {message}")
            }
            _ => bail!("broker returned an inconsistent ALP result"),
        }
    }
}

pub async fn read_record<T, R>(reader: &mut R) -> Result<T>
where
    T: DeserializeOwned,
    R: AsyncRead + Unpin,
{
    let mut magic = [0_u8; 4];
    reader
        .read_exact(&mut magic)
        .await
        .context("failed to read ALP record magic")?;
    if magic != MAGIC {
        bail!("unsupported ALP framing version");
    }
    let length =
        usize::try_from(reader.read_u32().await?).context("ALP record length overflowed")?;
    if length == 0 || length > MAX_RECORD_BYTES {
        bail!("ALP record length is outside its bound");
    }
    let mut payload = vec![0_u8; length];
    reader
        .read_exact(&mut payload)
        .await
        .context("failed to read ALP record payload")?;
    serde_json::from_slice(&payload).context("ALP record is not strict JSON")
}

pub async fn write_record<T, W>(writer: &mut W, value: &T) -> Result<()>
where
    T: Serialize,
    W: AsyncWrite + Unpin,
{
    let payload = serde_json::to_vec(value).context("failed to encode ALP record")?;
    if payload.is_empty() || payload.len() > MAX_RECORD_BYTES {
        bail!("ALP record exceeds its wire bound");
    }
    writer.write_all(&MAGIC).await?;
    writer
        .write_u32(u32::try_from(payload.len()).context("ALP record is too large")?)
        .await?;
    writer.write_all(&payload).await?;
    writer.flush().await?;
    Ok(())
}

fn validate_request_id(value: &str) -> Result<()> {
    if value.is_empty()
        || value.len() > MAX_REQUEST_ID_BYTES
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_'))
    {
        bail!("ALP request ID is not canonical");
    }
    Ok(())
}

pub fn validate_target(value: &str) -> Result<()> {
    if value.is_empty() || value.len() > MAX_TARGET_BYTES {
        bail!("ALP target length is invalid");
    }
    let (user, machine) = value
        .split_once('@')
        .context("ALP target must be user@machine-id")?;
    if machine.contains('@') {
        bail!("ALP target must contain exactly one '@'");
    }
    validate_target_component(user, 64)?;
    validate_target_component(machine, 253)
}

fn validate_target_component(value: &str, maximum: usize) -> Result<()> {
    if value.is_empty()
        || value.len() > maximum
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-' | b'_'))
        || !value
            .as_bytes()
            .first()
            .is_some_and(u8::is_ascii_alphanumeric)
    {
        bail!("ALP target component is not canonical ASCII");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn request() -> AlpDialRequest {
        AlpDialRequest::new(
            "request-1".to_owned(),
            "alice@home-1".to_owned(),
            "sync.bulk".to_owned(),
            AlpTrafficClass::Bulk,
            AlpTransport::Mixed,
            Duration::from_secs(30),
        )
        .unwrap()
    }

    #[tokio::test]
    async fn dial_and_result_records_round_trip_canonically() {
        let (mut writer, mut reader) = tokio::io::duplex(MAX_RECORD_BYTES + 8);
        let expected = request();
        write_record(&mut writer, &expected).await.unwrap();
        let actual: AlpDialRequest = read_record(&mut reader).await.unwrap();
        actual.validate().unwrap();
        assert_eq!(actual, expected);

        let ready = AlpResult::ready(expected.request_id).unwrap();
        write_record(&mut writer, &ready).await.unwrap();
        read_record::<AlpResult, _>(&mut reader)
            .await
            .unwrap()
            .into_ready()
            .unwrap();
    }

    #[tokio::test]
    async fn malformed_unknown_duplicate_and_oversized_records_fail_closed() {
        for payload in [
            br#"{"version":1,"operation":"dial","request_id":"x","request_id":"y","target":"a@b","service":"ssh","class":"interactive","transport":"mixed","deadline_millis":1000}"#.as_slice(),
            br#"{"version":1,"operation":"dial","request_id":"x","target":"a@b","service":"ssh","class":"interactive","transport":"mixed","deadline_millis":1000,"unknown":true}"#.as_slice(),
            b"not-json".as_slice(),
        ] {
            let (mut writer, mut reader) = tokio::io::duplex(MAX_RECORD_BYTES + 8);
            writer.write_all(&MAGIC).await.unwrap();
            writer.write_u32(payload.len() as u32).await.unwrap();
            writer.write_all(payload).await.unwrap();
            assert!(read_record::<AlpDialRequest, _>(&mut reader).await.is_err());
        }

        let (mut writer, mut reader) = tokio::io::duplex(8);
        writer.write_all(&MAGIC).await.unwrap();
        writer
            .write_u32((MAX_RECORD_BYTES as u32).saturating_add(1))
            .await
            .unwrap();
        assert!(read_record::<AlpDialRequest, _>(&mut reader).await.is_err());
    }

    #[test]
    fn dial_validation_rejects_open_proxy_shapes_and_bad_deadlines() {
        for target in [
            "home",
            "@home",
            "alice@",
            "alice@home@other",
            "alice@/tmp/x",
        ] {
            assert!(validate_target(target).is_err(), "accepted {target:?}");
        }
        assert!(AlpDialRequest::new(
            "x".to_owned(),
            "alice@home".to_owned(),
            "/tmp/socket".to_owned(),
            AlpTrafficClass::Bulk,
            AlpTransport::Mixed,
            Duration::from_secs(30),
        )
        .is_err());
        assert!(AlpDialRequest::new(
            "x".to_owned(),
            "alice@home".to_owned(),
            "sync".to_owned(),
            AlpTrafficClass::Bulk,
            AlpTransport::Mixed,
            Duration::from_millis(1),
        )
        .is_err());
    }
}
