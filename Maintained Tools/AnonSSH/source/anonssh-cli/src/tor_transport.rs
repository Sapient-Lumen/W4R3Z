use std::net::SocketAddr;
use std::time::Duration;

use anyhow::{anyhow, bail, Context, Result};
use data_encoding::{BASE32_NOPAD, BASE64};
use ed25519_dalek::{hazmat::ExpandedSecretKey, VerifyingKey};
use sha3::{Digest, Sha3_256};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use zeroize::Zeroizing;

use crate::data_stream;

const DEFAULT_TOR_PORT: u16 = 22;
const MAX_CONTROL_REPLY_BYTES: usize = 64 * 1024;

pub struct TorConnector {
    proxy_addr: String,
}

impl TorConnector {
    pub fn new(proxy_addr: String) -> Self {
        Self { proxy_addr }
    }

    pub async fn connect(&self, destination: &str, port: u16) -> Result<TcpStream> {
        self.connect_isolated(destination, port, None).await
    }

    pub async fn connect_isolated(
        &self,
        destination: &str,
        port: u16,
        isolation_token: Option<&str>,
    ) -> Result<TcpStream> {
        let (host, port) = parse_destination(destination, port)?;
        let authentication = isolation_token
            .map(|token| {
                if token.is_empty() || token.len() > u8::MAX as usize {
                    bail!("Tor isolation token must contain 1 to 255 bytes");
                }
                Ok(async_socks5::Auth::new("anonssh", token))
            })
            .transpose()?;
        let duration =
            Duration::from_secs(timeout_from_env("ANONSSH_TOR_CONNECT_TIMEOUT_SECS", 120));
        let mut stream = tokio::time::timeout(duration, data_stream::connect(&self.proxy_addr))
            .await
            .context("timed out connecting to Tor SOCKS")?
            .with_context(|| {
                format!(
                    "failed to connect and configure Tor SOCKS at {}",
                    self.proxy_addr
                )
            })?;
        tokio::time::timeout(
            duration,
            async_socks5::connect(&mut stream, (host.as_str(), port), authentication),
        )
        .await
        .context("timed out establishing a Tor stream")?
        .map_err(|error| anyhow!("Tor SOCKS connection failed: {error}"))?;
        Ok(stream)
    }
}

pub struct TorListener {
    control: TorControlEndpoint,
}

#[derive(Clone)]
pub struct TorControlEndpoint {
    address: String,
    authentication: Zeroizing<String>,
}

impl TorControlEndpoint {
    pub fn from_cookie(address: String, authentication: Zeroizing<String>) -> Result<Self> {
        if authentication.len() != 64
            || !authentication.bytes().all(|byte| byte.is_ascii_hexdigit())
        {
            bail!("invalid Tor control cookie");
        }
        Ok(Self {
            address,
            authentication,
        })
    }
}

pub struct PublishedTorService {
    control_stream: TcpStream,
}

impl PublishedTorService {
    pub async fn wait_closed(&mut self) -> Result<()> {
        let mut byte = [0_u8; 1];
        match self.control_stream.read(&mut byte).await {
            Ok(0) => bail!("Tor control connection closed; onion service is unpublished"),
            Ok(_) => bail!("Tor control connection produced unexpected asynchronous data"),
            Err(error) => Err(anyhow!("Tor control connection failed: {error}")),
        }
    }
}

impl TorListener {
    pub fn new(control: TorControlEndpoint) -> Self {
        Self { control }
    }

    pub async fn listen_with_key(
        &self,
        virtual_port: u16,
        local_target: &str,
        expected_destination: &str,
        control_private_key: &str,
    ) -> Result<PublishedTorService> {
        let target = validate_loopback_target(local_target)?;
        self.listen_with_key_routes(
            &[(virtual_port, target)],
            expected_destination,
            control_private_key,
        )
        .await
    }

    pub async fn listen_with_key_routes(
        &self,
        routes: &[(u16, SocketAddr)],
        expected_destination: &str,
        control_private_key: &str,
    ) -> Result<PublishedTorService> {
        if routes.is_empty() {
            bail!("Tor onion service requires at least one port mapping");
        }
        for (virtual_port, target) in routes {
            if *virtual_port == 0 {
                bail!("Tor virtual port must be non-zero");
            }
            if !target.ip().is_loopback() || target.port() == 0 {
                bail!("Tor backend must be a non-zero loopback socket");
            }
        }
        let expected_service_id = parse_v3_service_id(expected_destination)?;
        if tor_v3_service_id_from_control_private_key(control_private_key)? != expected_service_id {
            bail!("Tor control key does not match the expected destination");
        }

        let (mut stream, duration) = self.authenticated_control_stream().await?;
        let mut command = Zeroizing::new(format!("ADD_ONION ED25519-V3:{control_private_key}"));
        for (virtual_port, target) in routes {
            command.push_str(&format!(" Port={virtual_port},{target}"));
        }
        let reply = write_control_command(&mut stream, &command, "ADD_ONION", duration).await?;
        let returned = parse_service_id(&reply)?;
        if returned.strip_suffix(".onion").unwrap_or(&returned) != expected_service_id {
            bail!("Tor ADD_ONION returned an unexpected service ID");
        }
        Ok(PublishedTorService {
            control_stream: stream,
        })
    }

    async fn authenticated_control_stream(&self) -> Result<(TcpStream, Duration)> {
        let duration =
            Duration::from_secs(timeout_from_env("ANONSSH_TOR_CONTROL_TIMEOUT_SECS", 10));
        let mut stream = tokio::time::timeout(duration, TcpStream::connect(&self.control.address))
            .await
            .context("timed out connecting to Tor control")?
            .with_context(|| {
                format!(
                    "failed to connect to Tor control at {}",
                    self.control.address
                )
            })?;
        let command = Zeroizing::new(format!(
            "AUTHENTICATE {}",
            self.control.authentication.as_str()
        ));
        write_control_command(&mut stream, &command, "AUTHENTICATE", duration).await?;
        Ok((stream, duration))
    }
}

pub fn tor_v3_service_id_from_control_private_key(key: &str) -> Result<String> {
    let decoded = Zeroizing::new(
        BASE64
            .decode(key.as_bytes())
            .map_err(|_| anyhow!("invalid Tor ED25519-V3 control key"))?,
    );
    if decoded.len() != 64 || BASE64.encode(&decoded) != key {
        bail!("invalid Tor ED25519-V3 control key");
    }
    let mut expanded = Zeroizing::new([0_u8; 64]);
    expanded.copy_from_slice(&decoded);
    let public_key = VerifyingKey::from(&ExpandedSecretKey::from_bytes(&expanded)).to_bytes();
    let version = [3_u8];
    let mut checksum = Sha3_256::new();
    checksum.update(b".onion checksum");
    checksum.update(public_key);
    checksum.update(version);
    let checksum = checksum.finalize();
    let mut address = [0_u8; 35];
    address[..32].copy_from_slice(&public_key);
    address[32..34].copy_from_slice(&checksum[..2]);
    address[34] = version[0];
    Ok(BASE32_NOPAD.encode(&address).to_ascii_lowercase())
}

fn parse_v3_service_id(destination: &str) -> Result<&str> {
    let value = destination.strip_prefix("tor://").unwrap_or(destination);
    let value = value.strip_suffix(".onion").unwrap_or(value);
    if value.len() != 56
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_lowercase() || matches!(byte, b'2'..=b'7'))
    {
        bail!("invalid Tor v3 onion destination");
    }
    Ok(value)
}

fn parse_destination(destination: &str, default_port: u16) -> Result<(String, u16)> {
    let raw = destination.strip_prefix("tor://").unwrap_or(destination);
    if raw.is_empty() || raw.contains('/') || raw.chars().any(char::is_whitespace) {
        bail!("invalid Tor destination");
    }
    let (host, port) = match raw.rsplit_once(':') {
        Some((host, port)) if !host.contains(':') => (host, parse_port(port)?),
        _ => (
            raw,
            if default_port == 0 {
                DEFAULT_TOR_PORT
            } else {
                default_port
            },
        ),
    };
    if host.is_empty() {
        bail!("Tor destination is missing its host");
    }
    Ok((host.to_owned(), port))
}

fn parse_port(value: &str) -> Result<u16> {
    value
        .parse::<u16>()
        .ok()
        .filter(|port| *port != 0)
        .ok_or_else(|| anyhow!("invalid Tor destination port"))
}

fn validate_loopback_target(target: &str) -> Result<SocketAddr> {
    let address: SocketAddr = target.parse().context("invalid Tor backend socket")?;
    if !address.ip().is_loopback() || address.port() == 0 {
        bail!("Tor backend must be a non-zero loopback socket");
    }
    Ok(address)
}

async fn write_control_command(
    stream: &mut TcpStream,
    command: &str,
    label: &str,
    duration: Duration,
) -> Result<Vec<String>> {
    let wire = Zeroizing::new(format!("{command}\r\n"));
    tokio::time::timeout(duration, async {
        stream.write_all(wire.as_bytes()).await?;
        stream.flush().await
    })
    .await
    .with_context(|| format!("timed out writing Tor {label}"))??;
    read_control_reply(stream, label, duration).await
}

async fn read_control_reply(
    stream: &mut TcpStream,
    label: &str,
    duration: Duration,
) -> Result<Vec<String>> {
    let operation = async {
        let mut bytes = Vec::with_capacity(2_048);
        loop {
            if bytes.len() > MAX_CONTROL_REPLY_BYTES {
                bail!("Tor control reply exceeded 64 KiB");
            }
            if let Some(code) = terminal_status(&bytes) {
                if code != 250 {
                    bail!("Tor control command {label} failed with status {code}");
                }
                return Ok(reply_lines(&bytes));
            }
            let mut buffer = [0_u8; 1_024];
            let count = stream.read(&mut buffer).await?;
            if count == 0 {
                bail!("Tor control socket closed unexpectedly");
            }
            bytes.extend_from_slice(&buffer[..count]);
        }
    };
    tokio::time::timeout(duration, operation)
        .await
        .context("timed out waiting for Tor control reply")?
}

fn terminal_status(reply: &[u8]) -> Option<u16> {
    String::from_utf8_lossy(reply)
        .split("\r\n")
        .filter(|line| line.len() >= 4 && line.as_bytes()[3] == b' ')
        .last()
        .and_then(|line| line[..3].parse().ok())
}

fn reply_lines(reply: &[u8]) -> Vec<String> {
    String::from_utf8_lossy(reply)
        .split("\r\n")
        .filter(|line| !line.is_empty())
        .map(str::to_owned)
        .collect()
}

fn parse_service_id(lines: &[String]) -> Result<String> {
    lines
        .iter()
        .find_map(|line| {
            line.strip_prefix("250-ServiceID=")
                .or_else(|| line.strip_prefix("250-OnionAddress="))
        })
        .filter(|value| !value.is_empty())
        .map(str::to_owned)
        .ok_or_else(|| anyhow!("Tor ADD_ONION reply omitted its service ID"))
}

fn timeout_from_env(variable: &str, default: u64) -> u64 {
    std::env::var(variable)
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(default)
        .clamp(1, 300)
}

#[cfg(test)]
mod tests {
    use zeroize::Zeroizing;

    use super::{parse_destination, parse_service_id, terminal_status, TorControlEndpoint};

    #[test]
    fn destination_defaults_to_ssh() {
        assert_eq!(
            parse_destination("tor://example.onion", 0).unwrap(),
            ("example.onion".to_owned(), 22)
        );
        assert_eq!(
            parse_destination("example.onion:2222", 0).unwrap(),
            ("example.onion".to_owned(), 2222)
        );
        assert!(parse_destination("example.onion:0", 0).is_err());
    }

    #[test]
    fn parses_control_replies_without_echoing_keys() {
        assert_eq!(terminal_status(b"250-first\r\n250 OK\r\n"), Some(250));
        assert_eq!(
            parse_service_id(&["250-ServiceID=example".to_owned()]).unwrap(),
            "example"
        );
        let error = parse_service_id(&["250-PrivateKey=secret".to_owned()])
            .unwrap_err()
            .to_string();
        assert!(!error.contains("secret"));
    }

    #[test]
    fn control_cookie_is_exact_hex() {
        assert!(TorControlEndpoint::from_cookie(
            "127.0.0.1:19150".to_owned(),
            Zeroizing::new("ab".repeat(32)),
        )
        .is_ok());
        assert!(TorControlEndpoint::from_cookie(
            "127.0.0.1:19150".to_owned(),
            Zeroizing::new("not-a-cookie".to_owned()),
        )
        .is_err());
    }
}
