use std::net::SocketAddr;

use crate::data_stream;
use crate::sam::SamListener;
use anyhow::{Context, Result};
use tokio::net::TcpStream;
use tokio::sync::oneshot;
use tokio::task::JoinSet;

async fn serve_connection(mut anonymous_stream: TcpStream, backend: SocketAddr) -> Result<()> {
    data_stream::configure(&anonymous_stream)
        .context("failed to configure I2P ingress data stream")?;
    let mut ssh = data_stream::connect(backend)
        .await
        .with_context(|| format!("failed to connect and configure SSH backend at {backend}"))?;
    data_stream::relay_bidirectional(&mut anonymous_stream, &mut ssh)
        .await
        .context("failed to bridge I2P and SSH streams")?;
    Ok(())
}

pub async fn run(
    listener: SamListener,
    backend: SocketAddr,
    mut stop: oneshot::Receiver<()>,
) -> Result<()> {
    let mut connections = JoinSet::new();
    loop {
        tokio::select! {
            biased;
            _ = &mut stop => break,
            joined = connections.join_next(), if !connections.is_empty() => {
                if let Some(result) = joined {
                    result.context("I2P ingress task panicked")??;
                }
            }
            accepted = listener.accept() => {
                let stream = accepted.context("I2P SAM listener failed")?;
                connections.spawn(serve_connection(stream, backend));
            }
        }
    }

    connections.abort_all();
    while connections.join_next().await.is_some() {}
    Ok(())
}
