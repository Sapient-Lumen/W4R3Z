use std::io;

use tokio::io::{AsyncRead, AsyncWrite};
use tokio::net::{TcpStream, ToSocketAddrs};

pub const RELAY_BUFFER_BYTES: usize = anonssh_bond::MAX_FRAME_PAYLOAD;

pub async fn connect<A>(address: A) -> io::Result<TcpStream>
where
    A: ToSocketAddrs,
{
    let stream = TcpStream::connect(address).await?;
    configure(&stream)?;
    Ok(stream)
}

pub fn configure(stream: &TcpStream) -> io::Result<()> {
    stream.set_nodelay(true)
}

pub async fn relay_bidirectional<A, B>(first: &mut A, second: &mut B) -> io::Result<(u64, u64)>
where
    A: AsyncRead + AsyncWrite + Unpin + ?Sized,
    B: AsyncRead + AsyncWrite + Unpin + ?Sized,
{
    tokio::io::copy_bidirectional_with_sizes(first, second, RELAY_BUFFER_BYTES, RELAY_BUFFER_BYTES)
        .await
}

#[cfg(test)]
mod tests {
    use tokio::net::TcpListener;

    use super::{configure, connect};

    #[tokio::test]
    async fn connected_and_accepted_data_streams_disable_nagle() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let address = listener.local_addr().unwrap();
        let (client, accepted) = tokio::join!(connect(address), listener.accept());
        let client = client.unwrap();
        let (server, _) = accepted.unwrap();
        configure(&server).unwrap();

        assert!(client.nodelay().unwrap());
        assert!(server.nodelay().unwrap());
    }
}
