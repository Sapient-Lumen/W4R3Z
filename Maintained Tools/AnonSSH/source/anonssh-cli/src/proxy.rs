use std::time::Duration;

use anyhow::{bail, Context, Result};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};
use tokio::time::timeout;
use tracing::warn;

use crate::data_stream;
use crate::sam::SamConnector;
use crate::tor_transport::TorConnector;

const MAX_SSH_IDENTIFICATION_BYTES: usize = 255;
const MAX_SSH_BANNER_BYTES: usize = 1_024;

pub async fn tor(destination: &str, endpoint: &str) -> Result<()> {
    let connector = TorConnector::new(endpoint.to_string());
    let mut last_error = None;
    for attempt in 1..=6 {
        match connector.connect(destination, 0).await {
            Ok(stream) => return relay(stream).await,
            Err(error) => last_error = Some(error),
        }
        if attempt < 6 {
            warn!("Tor connection attempt {attempt} failed; retrying");
            tokio::time::sleep(Duration::from_secs(5)).await;
        }
    }
    Err(last_error.unwrap_or_else(|| anyhow::anyhow!("Tor connection failed")))
}

pub async fn i2p(destination: &str, endpoint: &str) -> Result<()> {
    let mut stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let identification = read_ssh_identification(&mut stdin).await?;
    // Keep the SAM session alive across retries so a transient stream failure does
    // not discard and rebuild the client's I2P tunnels.
    let connector = SamConnector::new(endpoint.to_string(), None);
    let mut last_error = None;
    for attempt in 1..=3 {
        match connector
            .connect_with_initial_payload(destination, 0, &identification)
            .await
        {
            Ok(mut stream) => match read_ssh_banner(&mut stream).await {
                Ok(banner) => {
                    stdout.write_all(&banner).await?;
                    stdout.flush().await?;
                    return relay_with(stream, stdin, stdout).await;
                }
                Err(error) => last_error = Some(error),
            },
            Err(error) => last_error = Some(error),
        }
        if attempt < 3 {
            warn!("I2P connection attempt {attempt} failed; retrying");
            tokio::time::sleep(Duration::from_secs(2)).await;
        }
    }
    Err(last_error.unwrap_or_else(|| anyhow::anyhow!("I2P connection failed")))
}

async fn relay(stream: tokio::net::TcpStream) -> Result<()> {
    relay_with(stream, tokio::io::stdin(), tokio::io::stdout()).await
}

pub async fn bond(stream: anonssh_bond_tokio::BondedStream) -> Result<()> {
    relay_with(stream, tokio::io::stdin(), tokio::io::stdout()).await
}

async fn relay_with<S, I, O>(mut stream: S, input: I, output: O) -> Result<()>
where
    S: AsyncRead + AsyncWrite + Unpin,
    I: AsyncRead + Unpin,
    O: AsyncWrite + Unpin,
{
    let mut stdio = tokio::io::join(input, output);
    data_stream::relay_bidirectional(&mut stream, &mut stdio).await?;
    Ok(())
}

async fn read_ssh_identification<R: AsyncRead + Unpin>(reader: &mut R) -> Result<Vec<u8>> {
    let mut line = Vec::new();
    timeout(Duration::from_secs(10), async {
        let mut byte = [0_u8; 1];
        while line.len() < MAX_SSH_IDENTIFICATION_BYTES {
            if reader.read(&mut byte).await? == 0 {
                break;
            }
            line.push(byte[0]);
            if byte[0] == b'\n' {
                break;
            }
        }
        Ok::<(), std::io::Error>(())
    })
    .await
    .context("timed out waiting for OpenSSH identification")??;
    validate_ssh_identification(&line).context("invalid OpenSSH identification")?;
    Ok(line)
}

async fn read_ssh_banner<R: AsyncRead + Unpin>(reader: &mut R) -> Result<Vec<u8>> {
    timeout(Duration::from_secs(120), async {
        let mut collected = Vec::new();
        let mut line = Vec::new();
        let mut byte = [0_u8; 1];
        while collected.len() < MAX_SSH_BANNER_BYTES {
            if reader.read(&mut byte).await? == 0 {
                bail!("remote closed before its SSH banner")
            }
            line.push(byte[0]);
            collected.push(byte[0]);
            if line.len() > MAX_SSH_IDENTIFICATION_BYTES {
                bail!("remote SSH banner line exceeded 255 bytes")
            }
            if byte[0] == b'\n' {
                if line.starts_with(b"SSH-") {
                    validate_ssh_identification(&line)
                        .context("remote sent an invalid SSH identification")?;
                    return Ok(collected);
                }
                line.clear();
            }
        }
        bail!("remote SSH banner exceeded 1024 bytes")
    })
    .await
    .context("timed out waiting for remote SSH banner")?
}

fn validate_ssh_identification(line: &[u8]) -> Result<()> {
    if line.len() > MAX_SSH_IDENTIFICATION_BYTES
        || !line.starts_with(b"SSH-2.0-")
        || !line.ends_with(b"\r\n")
    {
        bail!("expected an SSH-2.0 identification terminated by CRLF")
    }
    let software_and_comments = &line[b"SSH-2.0-".len()..line.len() - 2];
    if software_and_comments.is_empty()
        || !software_and_comments
            .iter()
            .all(|byte| matches!(byte, 0x20..=0x7e))
    {
        bail!("SSH identification contains invalid software or comment bytes")
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{read_ssh_banner, read_ssh_identification};

    #[tokio::test]
    async fn reads_a_strict_client_identification() {
        let mut input = &b"SSH-2.0-OpenSSH_9.9 test\r\nignored"[..];
        assert_eq!(
            read_ssh_identification(&mut input).await.unwrap(),
            b"SSH-2.0-OpenSSH_9.9 test\r\n"
        );

        for invalid in [
            &b"SSH-2.0-client\n"[..],
            &b"SSH-1.99-client\r\n"[..],
            &b"SSH-2.0-\r\n"[..],
            &b"SSH-2.0-client\0bad\r\n"[..],
        ] {
            assert!(read_ssh_identification(&mut &*invalid).await.is_err());
        }
    }

    #[tokio::test]
    async fn preserves_a_bounded_server_pre_banner() {
        let expected = b"maintenance notice\r\nSSH-2.0-dropbear_2025.89\r\n";
        let mut input = &expected[..];
        assert_eq!(read_ssh_banner(&mut input).await.unwrap(), expected);

        let mut oversized = vec![b'a'; 256];
        oversized.push(b'\n');
        oversized.extend_from_slice(b"SSH-2.0-server\r\n");
        assert!(read_ssh_banner(&mut &oversized[..]).await.is_err());
    }
}
