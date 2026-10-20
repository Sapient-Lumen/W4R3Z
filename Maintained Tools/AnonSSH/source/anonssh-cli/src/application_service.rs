use std::fmt;
use std::io;
use std::time::Duration;

use anyhow::{bail, Context, Result};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};

pub const SETUP_TIMEOUT: Duration = Duration::from_secs(15);
pub const SSH_SERVICE: &str = "ssh";
const REQUEST_MAGIC: [u8; 4] = *b"ASP1";
const RESPONSE_MAGIC: [u8; 4] = *b"ASA1";
const PROTOCOL_VERSION: u8 = 1;
const REQUEST_HEADER_LEN: usize = 8;
const RESPONSE_HEADER_LEN: usize = 8;
const MAX_SERVICE_NAME_LEN: usize = 63;
const MAX_REASON_LEN: usize = 127;

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct ServiceName(String);

impl ServiceName {
    pub fn parse(value: &str) -> Result<Self> {
        if value.is_empty() || value.len() > MAX_SERVICE_NAME_LEN {
            bail!("service name must contain 1 to {MAX_SERVICE_NAME_LEN} bytes");
        }
        if !value.bytes().all(|byte| {
            byte.is_ascii_lowercase() || byte.is_ascii_digit() || matches!(byte, b'.' | b'_' | b'-')
        }) || !value
            .bytes()
            .next()
            .is_some_and(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit())
            || !value
                .bytes()
                .last()
                .is_some_and(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit())
        {
            bail!("service name is not canonical lowercase ASCII");
        }
        Ok(Self(value.to_owned()))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub enum ServiceRejection {
    UnknownService = 1,
    ClassDenied = 2,
    Capacity = 3,
    Unavailable = 4,
}

#[derive(Debug)]
pub enum ServiceSetupError {
    Rejected {
        rejection: ServiceRejection,
        reason: String,
    },
    PeerIncompatible,
    Timeout,
}

impl fmt::Display for ServiceSetupError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Rejected { rejection, reason } if reason.is_empty() => {
                write!(formatter, "peer rejected service: {rejection}")
            }
            Self::Rejected { rejection, reason } => {
                write!(formatter, "peer rejected service: {rejection}: {reason}")
            }
            Self::PeerIncompatible => {
                formatter.write_str("peer bond protocol does not support native services")
            }
            Self::Timeout => formatter.write_str("peer service negotiation timed out"),
        }
    }
}

impl std::error::Error for ServiceSetupError {}

impl ServiceRejection {
    fn from_wire(value: u8) -> Result<Self> {
        match value {
            1 => Ok(Self::UnknownService),
            2 => Ok(Self::ClassDenied),
            3 => Ok(Self::Capacity),
            4 => Ok(Self::Unavailable),
            _ => bail!("peer returned unknown service status {value}"),
        }
    }
}

impl fmt::Display for ServiceRejection {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Self::UnknownService => "unknown-service",
            Self::ClassDenied => "class-denied",
            Self::Capacity => "capacity",
            Self::Unavailable => "service-unavailable",
        };
        formatter.write_str(name)
    }
}

pub async fn request_service<T>(io: &mut T, service: &ServiceName) -> Result<()>
where
    T: AsyncRead + AsyncWrite + Unpin,
{
    let mut header = [0_u8; REQUEST_HEADER_LEN];
    header[..4].copy_from_slice(&REQUEST_MAGIC);
    header[4] = PROTOCOL_VERSION;
    header[5] = service.0.len() as u8;
    io.write_all(&header)
        .await
        .context("failed to write service request header")?;
    io.write_all(service.0.as_bytes())
        .await
        .context("failed to write service request name")?;
    io.flush()
        .await
        .context("failed to flush service request")?;

    let mut response = [0_u8; RESPONSE_HEADER_LEN];
    io.read_exact(&mut response)
        .await
        .context("failed to read service response header")?;
    if response[..4] != RESPONSE_MAGIC {
        bail!("peer returned an invalid service response magic");
    }
    if response[4] != PROTOCOL_VERSION {
        bail!(
            "peer returned unsupported service response version {}",
            response[4]
        );
    }
    if response[7] != 0 {
        bail!("peer returned nonzero reserved service response bytes");
    }
    let reason_len = usize::from(response[6]);
    if reason_len > MAX_REASON_LEN {
        bail!("peer service response reason exceeded its bound");
    }
    let mut reason = vec![0_u8; reason_len];
    io.read_exact(&mut reason)
        .await
        .context("failed to read service response reason")?;
    let reason = std::str::from_utf8(&reason).context("peer service reason was not UTF-8")?;
    match response[5] {
        0 if reason.is_empty() => Ok(()),
        0 => bail!("peer accepted a service with a nonempty reason"),
        status => Err(ServiceSetupError::Rejected {
            rejection: ServiceRejection::from_wire(status)?,
            reason: reason.to_owned(),
        }
        .into()),
    }
}

pub async fn read_service_request<T>(io: &mut T) -> Result<ServiceName>
where
    T: AsyncRead + Unpin,
{
    let mut header = [0_u8; REQUEST_HEADER_LEN];
    io.read_exact(&mut header)
        .await
        .context("failed to read service request header")?;
    if header[..4] != REQUEST_MAGIC {
        bail!("peer sent an invalid service request magic");
    }
    if header[4] != PROTOCOL_VERSION {
        bail!(
            "peer sent unsupported service request version {}",
            header[4]
        );
    }
    if header[6..] != [0, 0] {
        bail!("peer sent nonzero reserved service request bytes");
    }
    let name_len = usize::from(header[5]);
    if name_len == 0 || name_len > MAX_SERVICE_NAME_LEN {
        bail!("peer sent an invalid service name length");
    }
    let mut name = vec![0_u8; name_len];
    io.read_exact(&mut name)
        .await
        .context("failed to read service request name")?;
    ServiceName::parse(
        std::str::from_utf8(&name).context("peer service name was not canonical UTF-8")?,
    )
}

pub async fn accept_service<T>(io: &mut T) -> io::Result<()>
where
    T: AsyncWrite + Unpin,
{
    write_response(io, 0, "").await
}

pub async fn reject_service<T>(io: &mut T, rejection: ServiceRejection, reason: &str) -> Result<()>
where
    T: AsyncWrite + Unpin,
{
    if reason.len() > MAX_REASON_LEN || !reason.is_ascii() {
        bail!("service rejection reason is not bounded ASCII");
    }
    write_response(io, rejection as u8, reason)
        .await
        .context("failed to write service rejection")
}

async fn write_response<T>(io: &mut T, status: u8, reason: &str) -> io::Result<()>
where
    T: AsyncWrite + Unpin,
{
    let mut response = [0_u8; RESPONSE_HEADER_LEN];
    response[..4].copy_from_slice(&RESPONSE_MAGIC);
    response[4] = PROTOCOL_VERSION;
    response[5] = status;
    response[6] = reason.len() as u8;
    io.write_all(&response).await?;
    io.write_all(reason.as_bytes()).await?;
    io.flush().await
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn service_names_are_canonical_and_bounded() {
        for valid in ["ssh", "sync.bulk", "chat_realtime", "service-2"] {
            assert_eq!(ServiceName::parse(valid).unwrap().as_str(), valid);
        }
        for invalid in ["", ".ssh", "ssh.", "SSH", "ssh/path", "ssh service"] {
            assert!(ServiceName::parse(invalid).is_err(), "accepted {invalid:?}");
        }
        assert!(ServiceName::parse(&"a".repeat(MAX_SERVICE_NAME_LEN)).is_ok());
        assert!(ServiceName::parse(&"a".repeat(MAX_SERVICE_NAME_LEN + 1)).is_err());
    }

    #[tokio::test]
    async fn service_request_acceptance_is_exact_and_bounded() {
        let (mut client, mut server) = tokio::io::duplex(256);
        let client_task = tokio::spawn(async move {
            request_service(&mut client, &ServiceName::parse("sync.bulk").unwrap()).await
        });
        assert_eq!(
            read_service_request(&mut server).await.unwrap().as_str(),
            "sync.bulk"
        );
        accept_service(&mut server).await.unwrap();
        client_task.await.unwrap().unwrap();
    }

    #[tokio::test]
    async fn malformed_and_rejected_services_fail_closed() {
        let (mut client, mut server) = tokio::io::duplex(256);
        client
            .write_all(&[b'A', b'S', b'P', b'1', 1, 3, 0, 1, b's', b's', b'h'])
            .await
            .unwrap();
        assert!(read_service_request(&mut server).await.is_err());

        let (mut client, mut server) = tokio::io::duplex(256);
        let client_task = tokio::spawn(async move {
            request_service(&mut client, &ServiceName::parse("missing").unwrap()).await
        });
        let _ = read_service_request(&mut server).await.unwrap();
        reject_service(
            &mut server,
            ServiceRejection::UnknownService,
            "not configured",
        )
        .await
        .unwrap();
        let error = client_task.await.unwrap().unwrap_err();
        assert!(matches!(
            error.downcast_ref::<ServiceSetupError>(),
            Some(ServiceSetupError::Rejected {
                rejection: ServiceRejection::UnknownService,
                ..
            })
        ));
        let error = error.to_string();
        assert!(error.contains("unknown-service: not configured"));
    }
}
