use std::collections::{BTreeMap, BTreeSet};
use std::fmt;
use std::io;
use std::net::SocketAddr;

use anonssh_bond::EndpointProvider;
use anonssh_bond_tokio::{
    BoxLaneIo, LaneAcceptor, LaneDialProvider, LaneListenProvider, ProviderFuture,
};
use anyhow::{anyhow, bail, Result};
use tokio::net::TcpListener;
use zeroize::Zeroizing;

use crate::data_stream;
use crate::sam::{SamConnector, SamListener};
use crate::tor_transport::{
    tor_v3_service_id_from_control_private_key, PublishedTorService, TorConnector,
    TorControlEndpoint, TorListener,
};

/// Dials exact `tor://` endpoints through one caller-owned Tor SOCKS listener.
pub struct TorSocksDialProvider {
    connector: TorConnector,
    port: u16,
}

impl TorSocksDialProvider {
    pub fn new(proxy_addr: impl Into<String>, port: u16) -> Result<Self> {
        let proxy_addr = checked_loopback_endpoint(proxy_addr.into(), "Tor SOCKS")?;
        if port == 0 {
            bail!("Tor provider port must be non-zero");
        }
        Ok(Self {
            connector: TorConnector::new(proxy_addr),
            port,
        })
    }
}

impl LaneDialProvider for TorSocksDialProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::Tor
    }

    fn dial<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let stream = self
                .connector
                .connect(endpoint, self.port)
                .await
                .map_err(provider_error)?;
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

/// Dials exact `i2p://` endpoints through one caller-owned SAM session.
pub struct I2pSamDialProvider {
    connector: SamConnector,
    port: u16,
}

impl I2pSamDialProvider {
    pub fn new(
        sam_addr: impl Into<String>,
        keys: Option<(String, String)>,
        port: u16,
    ) -> Result<Self> {
        let sam_addr = checked_loopback_endpoint(sam_addr.into(), "I2P SAM")?;
        Ok(Self {
            connector: SamConnector::new(sam_addr, keys),
            port,
        })
    }
}

impl LaneDialProvider for I2pSamDialProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::I2p
    }

    fn dial<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, BoxLaneIo> {
        self.dial_with_initial_payload(endpoint, &[])
    }

    fn dial_with_initial_payload<'a>(
        &'a self,
        endpoint: &'a str,
        initial_payload: &'a [u8],
    ) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let stream = self
                .connector
                .connect_with_initial_payload(endpoint, self.port, initial_payload)
                .await
                .map_err(provider_error)?;
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

#[derive(Clone)]
pub struct TorOnionBinding {
    endpoint: String,
    service_destination: String,
    virtual_port: u16,
    control_private_key: Zeroizing<String>,
}

impl TorOnionBinding {
    pub fn new(
        endpoint: impl Into<String>,
        virtual_port: u16,
        control_private_key: Zeroizing<String>,
    ) -> Result<Self> {
        if virtual_port == 0 {
            bail!("Tor virtual port must be non-zero");
        }
        let endpoint = endpoint.into();
        let (service_id, endpoint_port) = split_onion_endpoint(&endpoint, virtual_port)?;
        let derived = tor_v3_service_id_from_control_private_key(&control_private_key)?;
        if service_id != derived || endpoint_port != virtual_port {
            bail!("Tor private key does not match the exact onion endpoint");
        }
        Ok(Self {
            endpoint,
            service_destination: format!("tor://{derived}.onion"),
            virtual_port,
            control_private_key,
        })
    }

    pub fn endpoint(&self) -> &str {
        &self.endpoint
    }
}

impl fmt::Debug for TorOnionBinding {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("TorOnionBinding")
            .field("endpoint", &self.endpoint)
            .field("virtual_port", &self.virtual_port)
            .field("control_private_key", &"[REDACTED]")
            .finish()
    }
}

/// Publishes exact caller-authorized onion destinations and accepts their streams.
pub struct TorOnionListenProvider {
    control: TorControlEndpoint,
    bindings: BTreeMap<String, TorOnionBinding>,
}

impl TorOnionListenProvider {
    pub fn new(
        control: TorControlEndpoint,
        bindings: impl IntoIterator<Item = TorOnionBinding>,
    ) -> Result<Self> {
        let mut exact = BTreeMap::new();
        for binding in bindings {
            if exact.insert(binding.endpoint.clone(), binding).is_some() {
                bail!("duplicate Tor onion endpoint");
            }
        }
        if exact.is_empty() {
            bail!("Tor listener provider requires at least one endpoint");
        }
        Ok(Self {
            control,
            bindings: exact,
        })
    }
}

impl LaneListenProvider for TorOnionListenProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::Tor
    }

    fn bind<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, Box<dyn LaneAcceptor>> {
        Box::pin(async move {
            let binding = self.bindings.get(endpoint).ok_or_else(|| {
                io::Error::new(
                    io::ErrorKind::PermissionDenied,
                    "Tor endpoint is not configured",
                )
            })?;
            let listener = TcpListener::bind("127.0.0.1:0").await?;
            let local = listener.local_addr()?;
            let service = TorListener::new(self.control.clone())
                .listen_with_key(
                    binding.virtual_port,
                    &local.to_string(),
                    &binding.service_destination,
                    &binding.control_private_key,
                )
                .await
                .map_err(provider_error)?;
            Ok(Box::new(TorOnionAcceptor {
                endpoint: binding.endpoint.clone(),
                listener,
                _service: service,
            }) as Box<dyn LaneAcceptor>)
        })
    }
}

struct TorOnionAcceptor {
    endpoint: String,
    listener: TcpListener,
    _service: PublishedTorService,
}

impl LaneAcceptor for TorOnionAcceptor {
    fn local_endpoint(&self) -> &str {
        &self.endpoint
    }

    fn accept<'a>(&'a mut self) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let (stream, _) = self.listener.accept().await?;
            data_stream::configure(&stream)?;
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

#[derive(Clone)]
pub struct I2pDestinationBinding {
    endpoint: String,
    session_id: String,
    private_key: Zeroizing<String>,
}

impl I2pDestinationBinding {
    pub fn new(
        endpoint: impl Into<String>,
        session_id: impl Into<String>,
        private_key: Zeroizing<String>,
    ) -> Result<Self> {
        let endpoint = endpoint.into();
        validate_i2p_endpoint(&endpoint)?;
        let session_id = session_id.into();
        validate_sam_session_id(&session_id)?;
        if private_key.is_empty()
            || private_key
                .bytes()
                .any(|byte| byte.is_ascii_control() || byte.is_ascii_whitespace())
        {
            bail!("invalid I2P private destination");
        }
        Ok(Self {
            endpoint,
            session_id,
            private_key,
        })
    }

    pub fn endpoint(&self) -> &str {
        &self.endpoint
    }
}

impl fmt::Debug for I2pDestinationBinding {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("I2pDestinationBinding")
            .field("endpoint", &self.endpoint)
            .field("session_id", &self.session_id)
            .field("private_key", &"[REDACTED]")
            .finish()
    }
}

/// Publishes exact caller-authorized I2P destinations and accepts their SAM streams.
pub struct I2pSamListenProvider {
    sam_addr: String,
    bindings: BTreeMap<String, I2pDestinationBinding>,
}

impl I2pSamListenProvider {
    pub fn new(
        sam_addr: impl Into<String>,
        bindings: impl IntoIterator<Item = I2pDestinationBinding>,
    ) -> Result<Self> {
        let sam_addr = checked_loopback_endpoint(sam_addr.into(), "I2P SAM")?;
        let mut exact = BTreeMap::new();
        let mut session_ids = BTreeSet::new();
        for binding in bindings {
            if !session_ids.insert(binding.session_id.clone()) {
                bail!("duplicate I2P SAM session ID");
            }
            if exact.insert(binding.endpoint.clone(), binding).is_some() {
                bail!("duplicate I2P destination endpoint");
            }
        }
        if exact.is_empty() {
            bail!("I2P listener provider requires at least one endpoint");
        }
        Ok(Self {
            sam_addr,
            bindings: exact,
        })
    }
}

impl LaneListenProvider for I2pSamListenProvider {
    fn provider(&self) -> EndpointProvider {
        EndpointProvider::I2p
    }

    fn bind<'a>(&'a self, endpoint: &'a str) -> ProviderFuture<'a, Box<dyn LaneAcceptor>> {
        Box::pin(async move {
            let binding = self.bindings.get(endpoint).ok_or_else(|| {
                io::Error::new(
                    io::ErrorKind::PermissionDenied,
                    "I2P endpoint is not configured",
                )
            })?;
            let listener = SamListener::bind_zeroizing(
                self.sam_addr.clone(),
                binding.session_id.clone(),
                binding.private_key.clone(),
            )
            .await
            .map_err(provider_error)?;
            Ok(Box::new(I2pSamAcceptor {
                endpoint: binding.endpoint.clone(),
                listener,
            }) as Box<dyn LaneAcceptor>)
        })
    }
}

struct I2pSamAcceptor {
    endpoint: String,
    listener: SamListener,
}

impl LaneAcceptor for I2pSamAcceptor {
    fn local_endpoint(&self) -> &str {
        &self.endpoint
    }

    fn accept<'a>(&'a mut self) -> ProviderFuture<'a, BoxLaneIo> {
        Box::pin(async move {
            let stream = self.listener.accept().await.map_err(provider_error)?;
            Ok(Box::new(stream) as BoxLaneIo)
        })
    }
}

fn checked_loopback_endpoint(raw: String, label: &str) -> Result<String> {
    let endpoint: SocketAddr = raw
        .parse()
        .map_err(|_| anyhow!("{label} endpoint must be a numeric loopback socket"))?;
    if !endpoint.ip().is_loopback() || endpoint.port() == 0 {
        bail!("{label} endpoint must be a non-zero loopback socket");
    }
    Ok(endpoint.to_string())
}

fn split_onion_endpoint(endpoint: &str, default_port: u16) -> Result<(String, u16)> {
    let raw = endpoint
        .strip_prefix("tor://")
        .ok_or_else(|| anyhow!("Tor endpoint must use tor://"))?;
    if raw.contains('/') || raw.bytes().any(|byte| byte.is_ascii_whitespace()) {
        bail!("invalid Tor onion endpoint");
    }
    let (host, port) = match raw.rsplit_once(':') {
        Some((host, raw_port)) => {
            let port = raw_port
                .parse::<u16>()
                .ok()
                .filter(|value| *value != 0)
                .ok_or_else(|| anyhow!("invalid Tor onion endpoint port"))?;
            (host, port)
        }
        None => (raw, default_port),
    };
    let service_id = host
        .strip_suffix(".onion")
        .ok_or_else(|| anyhow!("Tor endpoint must end in .onion"))?;
    if service_id.len() != 56
        || !service_id
            .bytes()
            .all(|byte| byte.is_ascii_lowercase() || matches!(byte, b'2'..=b'7'))
    {
        bail!("invalid Tor v3 onion endpoint");
    }
    Ok((service_id.to_owned(), port))
}

fn validate_i2p_endpoint(endpoint: &str) -> Result<()> {
    let destination = endpoint
        .strip_prefix("i2p://")
        .ok_or_else(|| anyhow!("I2P endpoint must use i2p://"))?;
    if destination.is_empty()
        || destination
            .bytes()
            .any(|byte| byte.is_ascii_control() || byte.is_ascii_whitespace())
    {
        bail!("invalid I2P destination endpoint");
    }
    Ok(())
}

fn validate_sam_session_id(session_id: &str) -> Result<()> {
    if session_id.is_empty()
        || !session_id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_'))
    {
        bail!("invalid I2P SAM session ID");
    }
    Ok(())
}

fn provider_error(error: anyhow::Error) -> io::Error {
    io::Error::other(error.to_string())
}

#[cfg(test)]
mod tests {
    use anonssh_bond::EndpointProvider;
    use anonssh_bond_tokio::{LaneDialProvider, LaneListenProvider};
    use zeroize::Zeroizing;

    use super::{
        I2pDestinationBinding, I2pSamDialProvider, I2pSamListenProvider, TorOnionBinding,
        TorSocksDialProvider,
    };

    #[test]
    fn dial_providers_require_numeric_loopback_router_endpoints() {
        assert_eq!(
            TorSocksDialProvider::new("127.0.0.1:9050", 22)
                .unwrap()
                .provider(),
            EndpointProvider::Tor
        );
        assert_eq!(
            I2pSamDialProvider::new("[::1]:7656", None, 0)
                .unwrap()
                .provider(),
            EndpointProvider::I2p
        );
        assert!(TorSocksDialProvider::new("0.0.0.0:9050", 22).is_err());
        assert!(I2pSamDialProvider::new("router.example:7656", None, 0).is_err());
    }

    #[test]
    fn listener_bindings_are_exact_and_redact_private_material() {
        let i2p = I2pDestinationBinding::new(
            "i2p://public-destination",
            "lane_1",
            Zeroizing::new("private-destination".to_owned()),
        )
        .unwrap();
        assert_eq!(i2p.endpoint(), "i2p://public-destination");
        assert!(!format!("{i2p:?}").contains("private-destination"));
        let provider = I2pSamListenProvider::new("127.0.0.1:7656", [i2p]).unwrap();
        assert_eq!(provider.provider(), EndpointProvider::I2p);

        assert!(I2pDestinationBinding::new(
            "tcp://wrong-provider",
            "lane_1",
            Zeroizing::new("private-destination".to_owned()),
        )
        .is_err());
        assert!(I2pDestinationBinding::new(
            "i2p://public-destination",
            "invalid session",
            Zeroizing::new("private-destination".to_owned()),
        )
        .is_err());

        let invalid_tor_key = Zeroizing::new("not-a-control-key".to_owned());
        assert!(TorOnionBinding::new(
            "tor://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.onion",
            22,
            invalid_tor_key,
        )
        .is_err());
    }
}
