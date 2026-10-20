use std::fmt;
use std::future::Future;
use std::sync::{Arc, Weak};

use anyhow::{anyhow, Context, Result};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::sync::{oneshot, Mutex};
use tokio::time::{timeout, Duration};
use zeroize::Zeroizing;

use crate::data_stream;

const SAM_HELLO: &[u8] = b"HELLO VERSION MIN=3.0 MAX=3.3\n";
const DEFAULT_SETUP_TIMEOUT_SECS: u64 = 600;
const MAX_SETUP_TIMEOUT_SECS: u64 = 1_800;
const DEFAULT_TUNNEL_QUANTITY: u8 = 2;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct SamSessionQuantities {
    inbound: u8,
    outbound: u8,
}

impl SamSessionQuantities {
    pub const DEFAULT: Self = Self {
        inbound: DEFAULT_TUNNEL_QUANTITY,
        outbound: DEFAULT_TUNNEL_QUANTITY,
    };

    pub fn new(inbound: u8, outbound: u8) -> Result<Self> {
        if !(1..=16).contains(&inbound) || !(1..=16).contains(&outbound) {
            return Err(anyhow!("SAM tunnel quantities must be between 1 and 16"));
        }
        Ok(Self { inbound, outbound })
    }
}

impl Default for SamSessionQuantities {
    fn default() -> Self {
        Self::DEFAULT
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct SamVersion {
    major: u8,
    minor: u8,
}

impl SamVersion {
    fn parse(raw: &str) -> Option<Self> {
        match raw {
            "3" | "3.0" => Some(Self { major: 3, minor: 0 }),
            "3.1" => Some(Self { major: 3, minor: 1 }),
            "3.2" => Some(Self { major: 3, minor: 2 }),
            "3.3" => Some(Self { major: 3, minor: 3 }),
            _ => None,
        }
    }

    fn supports_ports(self) -> bool {
        self >= Self { major: 3, minor: 2 }
    }
}

impl fmt::Display for SamVersion {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}.{}", self.major, self.minor)
    }
}

#[derive(Clone)]
struct SessionLease {
    generation: u64,
    id: String,
    version: SamVersion,
}

struct ActiveSession {
    lease: SessionLease,
    shutdown: oneshot::Sender<()>,
}

struct SessionState {
    private_destination: Option<Zeroizing<String>>,
    active: Option<ActiveSession>,
    next_generation: u64,
}

struct Shared {
    sam_addr: String,
    state: Mutex<SessionState>,
}

#[derive(Clone)]
pub struct SamConnector {
    shared: Arc<Shared>,
}

impl fmt::Debug for SamConnector {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("SamConnector")
            .field("sam_addr", &self.shared.sam_addr)
            .finish_non_exhaustive()
    }
}

impl SamConnector {
    pub fn new(sam_addr: String, keys: Option<(String, String)>) -> Self {
        Self {
            shared: Arc::new(Shared {
                sam_addr,
                state: Mutex::new(SessionState {
                    private_destination: keys.map(|(_, private)| Zeroizing::new(private)),
                    active: None,
                    next_generation: 1,
                }),
            }),
        }
    }

    pub async fn handshake<S>(&self, stream: &mut S) -> Result<()>
    where
        S: AsyncRead + AsyncWrite + Unpin,
    {
        negotiate(stream).await.map(|_| ())
    }

    pub async fn connect_with_initial_payload(
        &self,
        destination: &str,
        port: u16,
        initial_payload: &[u8],
    ) -> Result<TcpStream> {
        self.connect_internal(destination, port, initial_payload)
            .await
    }

    async fn acquire_session(&self) -> Result<SessionLease> {
        let mut state = self.shared.state.lock().await;
        if let Some(active) = &state.active {
            return Ok(active.lease.clone());
        }

        let generation = state.next_generation;
        state.next_generation = state
            .next_generation
            .checked_add(1)
            .ok_or_else(|| anyhow!("SAM session generation exhausted"))?;
        let existing_destination = state.private_destination.clone();
        let (lease, control, private_destination) = bounded(
            "session creation",
            create_control_session(
                &self.shared.sam_addr,
                generation,
                existing_destination,
                session_quantities_from_env()?,
            ),
        )
        .await?;
        if state.private_destination.is_none() {
            state.private_destination = Some(private_destination);
        }

        let (shutdown, shutdown_rx) = oneshot::channel();
        state.active = Some(ActiveSession {
            lease: lease.clone(),
            shutdown,
        });
        tokio::spawn(monitor_control(
            Arc::downgrade(&self.shared),
            lease.generation,
            control,
            shutdown_rx,
        ));
        Ok(lease)
    }

    async fn invalidate(&self, generation: u64) {
        let mut state = self.shared.state.lock().await;
        if state
            .active
            .as_ref()
            .is_some_and(|active| active.lease.generation == generation)
        {
            if let Some(active) = state.active.take() {
                let _ = active.shutdown.send(());
            }
        }
    }

    async fn connect_internal(
        &self,
        destination: &str,
        port: u16,
        initial_payload: &[u8],
    ) -> Result<TcpStream> {
        let destination = normalize_destination(destination)?;
        let first = self.acquire_session().await?;
        match self
            .connect_once(&first, destination, port, initial_payload)
            .await
        {
            Ok(stream) => Ok(stream),
            Err(failure) if failure.stale_session => {
                self.invalidate(first.generation).await;
                let second = self.acquire_session().await?;
                self.connect_once(&second, destination, port, initial_payload)
                    .await
                    .map_err(|failure| failure.error)
            }
            Err(failure) => Err(failure.error),
        }
    }

    async fn connect_once(
        &self,
        session: &SessionLease,
        destination: &str,
        port: u16,
        initial_payload: &[u8],
    ) -> std::result::Result<TcpStream, ConnectFailure> {
        let operation = async {
            let mut stream = data_stream::connect(&self.shared.sam_addr)
                .await
                .with_context(|| {
                    format!(
                        "failed to connect and configure SAM at {}",
                        self.shared.sam_addr
                    )
                })?;
            let version = negotiate(&mut stream).await?;
            if version != session.version {
                return Err(anyhow!(
                    "SAM version changed from {} to {} within one session",
                    session.version,
                    version
                ));
            }
            if port > 0 && !version.supports_ports() {
                return Err(anyhow!("SAM {version} does not support stream ports"));
            }

            let command = if port == 0 {
                format!(
                    "STREAM CONNECT ID={} DESTINATION={}\n",
                    session.id, destination
                )
            } else {
                format!(
                    "STREAM CONNECT ID={} DESTINATION={} FROM_PORT={} TO_PORT={}\n",
                    session.id, destination, port, port
                )
            };
            stream.write_all(command.as_bytes()).await?;
            stream.write_all(initial_payload).await?;
            stream.flush().await?;
            let response = read_line(&mut stream).await?;
            if result_field(&response) != Some("OK") {
                let stale_session = result_field(&response) == Some("INVALID_ID");
                return Ok(Err(ConnectFailure {
                    error: anyhow!(
                        "SAM STREAM CONNECT failed: {}",
                        sanitize_response(&response)
                    ),
                    stale_session,
                }));
            }
            Ok(Ok(stream))
        };

        match bounded("stream connection", operation).await {
            Ok(result) => result,
            Err(error) => Err(ConnectFailure {
                error,
                stale_session: false,
            }),
        }
    }
}

struct ConnectFailure {
    error: anyhow::Error,
    stale_session: bool,
}

pub struct SamListener {
    sam_addr: String,
    session_id: String,
    _control: TcpStream,
}

impl SamListener {
    pub async fn bind_zeroizing(
        sam_addr: String,
        session_id: String,
        private_key: Zeroizing<String>,
    ) -> Result<Self> {
        Self::bind_inner(
            sam_addr,
            session_id,
            private_key,
            session_quantities_from_env()?,
        )
        .await
    }

    async fn bind_inner(
        sam_addr: String,
        session_id: String,
        private_key: Zeroizing<String>,
        quantities: SamSessionQuantities,
    ) -> Result<Self> {
        validate_session_id(&session_id)?;
        let operation = async {
            let mut control = TcpStream::connect(&sam_addr)
                .await
                .with_context(|| format!("failed to connect to SAM at {sam_addr}"))?;
            negotiate(&mut control).await?;
            let command = session_create_command(&session_id, &private_key, quantities);
            control.write_all(command.as_bytes()).await?;
            control.flush().await?;
            let response = Zeroizing::new(read_line(&mut control).await?);
            ensure_ok("SESSION CREATE", &response)?;
            let confirmed = field(&response, "DESTINATION")
                .ok_or_else(|| anyhow!("SAM SESSION STATUS omitted its destination"))?;
            if confirmed != private_key.as_str() {
                return Err(anyhow!(
                    "SAM SESSION STATUS did not confirm the requested destination"
                ));
            }
            Ok(Self {
                sam_addr,
                session_id,
                _control: control,
            })
        };
        bounded("listener publication", operation).await
    }

    pub async fn accept(&self) -> Result<TcpStream> {
        let mut stream = bounded("listener accept registration", async {
            let mut stream = data_stream::connect(&self.sam_addr).await?;
            negotiate(&mut stream).await?;
            let command = format!("STREAM ACCEPT ID={} SILENT=false\n", self.session_id);
            stream.write_all(command.as_bytes()).await?;
            stream.flush().await?;
            let status = read_line(&mut stream).await?;
            ensure_ok("STREAM ACCEPT", &status)?;
            Ok::<_, anyhow::Error>(stream)
        })
        .await?;

        // The peer line arrives only when a real inbound stream exists. It is
        // intentionally not covered by the setup deadline.
        let peer = read_line(&mut stream).await?;
        if peer.trim().is_empty() || peer.starts_with("STREAM STATUS RESULT=") {
            return Err(anyhow!(
                "SAM STREAM ACCEPT returned an invalid peer destination"
            ));
        }
        Ok(stream)
    }
}

async fn create_control_session(
    sam_addr: &str,
    generation: u64,
    private_destination: Option<Zeroizing<String>>,
    quantities: SamSessionQuantities,
) -> Result<(SessionLease, TcpStream, Zeroizing<String>)> {
    let mut control = TcpStream::connect(sam_addr)
        .await
        .with_context(|| format!("failed to connect to SAM at {sam_addr}"))?;
    let version = negotiate(&mut control).await?;
    let private_destination = match private_destination {
        Some(destination) => destination,
        None => generate_destination(&mut control).await?,
    };
    let id = format!("anonssh-{}-{generation}", std::process::id());
    let command = session_create_command(&id, &private_destination, quantities);
    control.write_all(command.as_bytes()).await?;
    control.flush().await?;
    let response = read_line(&mut control).await?;
    ensure_ok("SESSION CREATE", &response)?;
    Ok((
        SessionLease {
            generation,
            id,
            version,
        },
        control,
        private_destination,
    ))
}

async fn generate_destination(stream: &mut TcpStream) -> Result<Zeroizing<String>> {
    stream.write_all(b"DEST GENERATE\n").await?;
    stream.flush().await?;
    let response = Zeroizing::new(read_line(stream).await?);
    let private = field(&response, "PRIV")
        .ok_or_else(|| anyhow!("SAM DEST REPLY omitted PRIV"))?
        .to_owned();
    Ok(Zeroizing::new(private))
}

async fn monitor_control(
    shared: Weak<Shared>,
    generation: u64,
    mut control: TcpStream,
    mut shutdown: oneshot::Receiver<()>,
) {
    loop {
        let response = tokio::select! {
            _ = &mut shutdown => return,
            response = read_line(&mut control) => response,
        };
        let Ok(line) = response else {
            break;
        };
        let line = line.trim_end_matches(['\r', '\n']);
        if line == "PING" || line.starts_with("PING ") {
            let reply = format!("PONG{}\n", &line[4..]);
            if control.write_all(reply.as_bytes()).await.is_err() || control.flush().await.is_err()
            {
                break;
            }
        }
    }

    if let Some(shared) = shared.upgrade() {
        let mut state = shared.state.lock().await;
        if state
            .active
            .as_ref()
            .is_some_and(|active| active.lease.generation == generation)
        {
            state.active = None;
        }
    }
}

async fn negotiate<S>(stream: &mut S) -> Result<SamVersion>
where
    S: AsyncRead + AsyncWrite + Unpin,
{
    stream.write_all(SAM_HELLO).await?;
    stream.flush().await?;
    parse_hello(&read_line(stream).await?)
}

async fn read_line<R>(reader: &mut R) -> Result<String>
where
    R: AsyncRead + Unpin,
{
    let mut bytes = Vec::with_capacity(256);
    let mut byte = [0_u8; 1];
    while bytes.len() < 4_096 {
        if reader.read(&mut byte).await? == 0 {
            return Err(anyhow!("SAM connection closed unexpectedly"));
        }
        bytes.push(byte[0]);
        if byte[0] == b'\n' {
            return String::from_utf8(bytes).context("SAM response was not UTF-8");
        }
    }
    Err(anyhow!("SAM response line exceeded 4096 bytes"))
}

fn parse_hello(response: &str) -> Result<SamVersion> {
    let fields = split_fields(response)?;
    if fields.first().copied() != Some("HELLO")
        || fields.get(1).copied() != Some("REPLY")
        || result_field(response) != Some("OK")
    {
        return Err(anyhow!("SAM HELLO failed: {}", sanitize_response(response)));
    }
    let version = field(response, "VERSION")
        .and_then(SamVersion::parse)
        .ok_or_else(|| anyhow!("SAM HELLO returned an unsupported version"))?;
    Ok(version)
}

fn ensure_ok(command: &str, response: &str) -> Result<()> {
    if result_field(response) == Some("OK") {
        Ok(())
    } else {
        Err(anyhow!(
            "SAM {command} failed: {}",
            sanitize_response(response)
        ))
    }
}

fn session_create_command(
    session_id: &str,
    destination: &str,
    quantities: SamSessionQuantities,
) -> String {
    format!(
        "SESSION CREATE STYLE=STREAM ID={} DESTINATION={} inbound.quantity={} outbound.quantity={}\n",
        session_id, destination, quantities.inbound, quantities.outbound
    )
}

fn normalize_destination(destination: &str) -> Result<&str> {
    let destination = destination.strip_prefix("i2p://").unwrap_or(destination);
    if destination.is_empty() || destination.bytes().any(|byte| byte <= 0x20 || byte == 0x7f) {
        return Err(anyhow!("invalid I2P destination"));
    }
    Ok(destination)
}

fn validate_session_id(id: &str) -> Result<()> {
    if id.is_empty()
        || !id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_'))
    {
        return Err(anyhow!("invalid SAM session ID"));
    }
    Ok(())
}

fn split_fields(response: &str) -> Result<Vec<&str>> {
    let mut fields = Vec::new();
    let mut start = None;
    let mut quoted = false;
    let mut escaped = false;
    for (index, byte) in response.bytes().enumerate() {
        if start.is_none() {
            if byte.is_ascii_whitespace() {
                continue;
            }
            start = Some(index);
        }
        if quoted && escaped {
            escaped = false;
        } else if quoted && byte == b'\\' {
            escaped = true;
        } else if byte == b'"' {
            quoted = !quoted;
        } else if !quoted && byte.is_ascii_whitespace() {
            fields.push(&response[start.take().expect("field start")..index]);
        }
    }
    if quoted || escaped {
        return Err(anyhow!("SAM response contained an unterminated quote"));
    }
    if let Some(start) = start {
        fields.push(&response[start..]);
    }
    Ok(fields)
}

fn field<'a>(response: &'a str, name: &str) -> Option<&'a str> {
    let prefix = format!("{name}=");
    let mut values = split_fields(response)
        .ok()?
        .into_iter()
        .filter_map(|entry| entry.strip_prefix(&prefix));
    let value = values.next()?;
    values.next().is_none().then_some(value)
}

fn result_field(response: &str) -> Option<&str> {
    field(response, "RESULT")
}

fn sanitize_response(response: &str) -> String {
    let mut output = Vec::new();
    for item in response.split_ascii_whitespace() {
        if let Some((name, _)) = item.split_once('=') {
            if matches!(
                name.to_ascii_uppercase().as_str(),
                "DESTINATION" | "PUB" | "PRIV"
            ) {
                output.push(format!("{name}=<redacted>"));
                continue;
            }
        }
        output.push(item.chars().take(128).collect());
    }
    output.join(" ").chars().take(512).collect()
}

fn session_quantities_from_env() -> Result<SamSessionQuantities> {
    fn quantity(name: &str) -> Result<u8> {
        match std::env::var(name) {
            Ok(raw) => raw
                .trim()
                .parse::<u8>()
                .ok()
                .filter(|value| (1..=16).contains(value))
                .ok_or_else(|| anyhow!("{name} must be between 1 and 16")),
            Err(std::env::VarError::NotPresent) => Ok(DEFAULT_TUNNEL_QUANTITY),
            Err(error) => Err(error.into()),
        }
    }
    SamSessionQuantities::new(
        quantity("ANONSSH_SAM_INBOUND_QUANTITY")?,
        quantity("ANONSSH_SAM_OUTBOUND_QUANTITY")?,
    )
}

pub fn setup_timeout() -> Duration {
    let seconds = std::env::var("ANONSSH_SAM_SETUP_TIMEOUT_SECS")
        .ok()
        .and_then(|value| value.trim().parse::<u64>().ok())
        .unwrap_or(DEFAULT_SETUP_TIMEOUT_SECS)
        .clamp(1, MAX_SETUP_TIMEOUT_SECS);
    Duration::from_secs(seconds)
}

async fn bounded<T, F>(phase: &str, operation: F) -> Result<T>
where
    F: Future<Output = Result<T>>,
{
    timeout(setup_timeout(), operation)
        .await
        .map_err(|_| anyhow!("SAM {phase} timed out"))?
}

#[cfg(test)]
mod tests {
    use super::{
        normalize_destination, parse_hello, sanitize_response, session_create_command,
        validate_session_id, SamSessionQuantities, SamVersion,
    };

    #[test]
    fn parses_supported_hello() {
        assert_eq!(
            parse_hello("HELLO REPLY RESULT=OK VERSION=3.3\n").unwrap(),
            SamVersion { major: 3, minor: 3 }
        );
        assert!(parse_hello("HELLO REPLY RESULT=NOVERSION VERSION=3.3\n").is_err());
        assert!(parse_hello("HELLO REPLY RESULT=OK VERSION=4.0\n").is_err());
    }

    #[test]
    fn rejects_command_injection() {
        assert_eq!(
            normalize_destination("i2p://example.b32.i2p").unwrap(),
            "example.b32.i2p"
        );
        assert!(normalize_destination("example.b32.i2p\nSTREAM ACCEPT").is_err());
        assert!(validate_session_id("anonssh-server").is_ok());
        assert!(validate_session_id("server\nSTREAM ACCEPT").is_err());
    }

    #[test]
    fn builds_bounded_tunnel_command() {
        let quantities = SamSessionQuantities::new(2, 3).unwrap();
        assert_eq!(
            session_create_command("session-1", "private-key", quantities),
            "SESSION CREATE STYLE=STREAM ID=session-1 DESTINATION=private-key inbound.quantity=2 outbound.quantity=3\n"
        );
        assert!(SamSessionQuantities::new(0, 2).is_err());
        assert!(SamSessionQuantities::new(2, 17).is_err());
    }

    #[test]
    fn redacts_destination_material() {
        let response = sanitize_response(
            "SESSION STATUS RESULT=I2P_ERROR DESTINATION=private PUB=public PRIV=private",
        );
        assert!(!response.contains("private"));
        assert!(!response.contains("public"));
        assert!(response.contains("DESTINATION=<redacted>"));
    }
}
