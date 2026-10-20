use std::net::{IpAddr, SocketAddr};
use std::str::FromStr;

use anyhow::{bail, Context, Result};

const MAX_REMOTE_HOST_BYTES: usize = 253;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LocalTcpForward {
    listen: SocketAddr,
    remote_host: String,
    remote_port: u16,
}

impl LocalTcpForward {
    pub fn parse(listen: SocketAddr, remote: &str) -> Result<Self> {
        if !listen.ip().is_loopback() || listen.port() == 0 {
            bail!("forward listener must be a non-zero loopback TCP socket");
        }
        if remote.is_empty()
            || remote.len() > MAX_REMOTE_HOST_BYTES + 8
            || remote
                .bytes()
                .any(|byte| byte.is_ascii_control() || byte.is_ascii_whitespace())
            || remote.starts_with('-')
        {
            bail!("invalid remote forward destination");
        }

        let (host, port) = parse_remote(remote)?;
        validate_remote_host(host)?;
        Ok(Self {
            listen,
            remote_host: host.to_owned(),
            remote_port: port,
        })
    }

    pub fn ssh_options(&self) -> Vec<String> {
        vec![
            "-N".to_owned(),
            "-o".to_owned(),
            "ExitOnForwardFailure=yes".to_owned(),
            "-o".to_owned(),
            format!("LocalForward={}", self.openssh_spec()),
        ]
    }

    pub fn listen(&self) -> SocketAddr {
        self.listen
    }

    pub fn remote(&self) -> String {
        format_host_port(&self.remote_host, self.remote_port)
    }

    fn openssh_spec(&self) -> String {
        format!(
            "{} {}",
            format_host_port(&self.listen.ip().to_string(), self.listen.port()),
            format_host_port(&self.remote_host, self.remote_port)
        )
    }
}

fn parse_remote(remote: &str) -> Result<(&str, u16)> {
    let (host, port) = if let Some(rest) = remote.strip_prefix('[') {
        let (host, port) = rest
            .split_once("]:")
            .context("bracketed remote destination requires [IPv6]:PORT")?;
        if !matches!(IpAddr::from_str(host), Ok(IpAddr::V6(_))) {
            bail!("brackets are permitted only around an IPv6 remote host");
        }
        (host, port)
    } else {
        let (host, port) = remote
            .rsplit_once(':')
            .context("remote destination requires HOST:PORT")?;
        if host.contains(':') {
            bail!("IPv6 remote hosts must use [IPv6]:PORT syntax");
        }
        (host, port)
    };
    let port = port
        .parse::<u16>()
        .context("remote forward port is invalid")?;
    if port == 0 {
        bail!("remote forward port must be non-zero");
    }
    Ok((host, port))
}

fn validate_remote_host(host: &str) -> Result<()> {
    if host.is_empty() || host.len() > MAX_REMOTE_HOST_BYTES || host.starts_with('-') {
        bail!("invalid remote forward host");
    }
    if IpAddr::from_str(host).is_ok() {
        return Ok(());
    }
    if host.ends_with('.') {
        bail!("remote forward host must use a canonical name without a trailing dot");
    }
    for label in host.split('.') {
        let valid = !label.is_empty()
            && label.len() <= 63
            && label
                .as_bytes()
                .first()
                .is_some_and(u8::is_ascii_alphanumeric)
            && label
                .as_bytes()
                .last()
                .is_some_and(u8::is_ascii_alphanumeric)
            && label
                .bytes()
                .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-');
        if !valid {
            bail!("invalid remote forward host");
        }
    }
    Ok(())
}

fn format_host_port(host: &str, port: u16) -> String {
    if host.contains(':') {
        format!("[{host}]:{port}")
    } else {
        format!("{host}:{port}")
    }
}

#[cfg(test)]
mod tests {
    use std::net::SocketAddr;

    use super::LocalTcpForward;

    #[test]
    fn local_forward_is_loopback_named_and_canonical() {
        let forward = LocalTcpForward::parse(
            "127.0.0.1:8022".parse::<SocketAddr>().unwrap(),
            "service.internal:443",
        )
        .unwrap();
        assert_eq!(forward.listen().to_string(), "127.0.0.1:8022");
        assert_eq!(forward.remote(), "service.internal:443");
        assert_eq!(
            forward.ssh_options(),
            [
                "-N",
                "-o",
                "ExitOnForwardFailure=yes",
                "-o",
                "LocalForward=127.0.0.1:8022 service.internal:443",
            ]
        );

        let ipv6 = LocalTcpForward::parse(
            "[::1]:8022".parse::<SocketAddr>().unwrap(),
            "[2001:db8::5]:8443",
        )
        .unwrap();
        assert_eq!(ipv6.remote(), "[2001:db8::5]:8443");
        assert_eq!(
            ipv6.ssh_options().last().unwrap(),
            "LocalForward=[::1]:8022 [2001:db8::5]:8443"
        );
    }

    #[test]
    fn local_forward_rejects_unsafe_or_ambiguous_endpoints() {
        for listen in ["0.0.0.0:8000", "192.0.2.1:8000", "127.0.0.1:0"] {
            assert!(LocalTcpForward::parse(listen.parse().unwrap(), "localhost:22").is_err());
        }
        let listen = "127.0.0.1:8000".parse().unwrap();
        for remote in [
            "",
            "localhost",
            "localhost:0",
            "localhost:65536",
            "-oProxyCommand=evil:22",
            "bad host:22",
            "bad\nname:22",
            ".example:22",
            "example.:22",
            "2001:db8::5:22",
            "[example.com]:22",
            "[2001:db8::5]",
        ] {
            assert!(
                LocalTcpForward::parse(listen, remote).is_err(),
                "accepted {remote:?}"
            );
        }
    }
}
