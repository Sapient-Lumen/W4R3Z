use std::fs::{self, OpenOptions};
use std::io::Read;
use std::net::{IpAddr, SocketAddr, TcpListener as StdTcpListener};
#[cfg(unix)]
use std::os::unix::fs::{MetadataExt, OpenOptionsExt, PermissionsExt};
#[cfg(target_os = "linux")]
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::sync::atomic::{AtomicU64, Ordering};
#[cfg(target_os = "linux")]
use std::sync::OnceLock;
use std::sync::{Arc, Mutex as StdMutex};
use std::time::Duration;

use anyhow::{anyhow, bail, Context, Result};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::process::{Child, Command};
use tokio::sync::Mutex;
use tokio::task::JoinHandle;
use tokio::time::{sleep, timeout, Instant};
use zeroize::Zeroizing;

use crate::i2p_bootstrap;
use crate::sam::SamConnector;
use crate::tor_transport::TorControlEndpoint;

#[derive(Clone, Debug)]
pub struct AppConfig {
    pub cache_dir: PathBuf,
    pub state_dir: PathBuf,
    pub keys_dir: PathBuf,
    pub i2pd_dir: PathBuf,
    pub tor_dir: PathBuf,
}

impl AppConfig {
    pub fn new() -> Result<Self> {
        let cache_dir = dirs::cache_dir()
            .context("cannot resolve the user cache directory")?
            .join("anonssh");
        let state_dir = dirs::data_local_dir()
            .context("cannot resolve the user data directory")?
            .join("anonssh");
        let keys_dir = dirs::state_dir()
            .context("cannot resolve the user state directory")?
            .join("anonssh/keys");
        Ok(Self {
            keys_dir,
            i2pd_dir: state_dir.join("i2pd"),
            tor_dir: state_dir.join("tor"),
            cache_dir,
            state_dir,
        })
    }

    pub fn temporary(root: &Path) -> Self {
        let cache_dir = root.join("cache");
        let state_dir = root.join("state");
        Self {
            keys_dir: state_dir.join("keys"),
            i2pd_dir: state_dir.join("i2pd"),
            tor_dir: state_dir.join("tor"),
            cache_dir,
            state_dir,
        }
    }
}

pub fn resolve_i2pd_certificates(i2pd: &Path) -> Result<PathBuf> {
    let prefix = i2pd.parent().and_then(Path::parent);
    let mut candidates = Vec::new();
    if let Some(path) = std::env::var_os("ANONSSH_I2PD_CERTS_DIR") {
        candidates.push(PathBuf::from(path));
    }
    if let Some(prefix) = prefix {
        candidates.push(prefix.join("share/i2pd/certificates"));
        candidates.push(prefix.join("share/i2p/certificates"));
        candidates.push(prefix.join("certificates"));
    }
    candidates.push(PathBuf::from("/usr/share/i2pd/certificates"));
    candidates.push(PathBuf::from("/usr/share/i2p/certificates"));
    candidates
        .into_iter()
        .find_map(|candidate| {
            validate_certificate_directory(&candidate)
                .ok()
                .and_then(|()| fs::canonicalize(candidate).ok())
        })
        .context("cannot find i2pd reseed certificates; set ANONSSH_I2PD_CERTS_DIR")
}

fn validate_certificate_directory(path: &Path) -> Result<()> {
    if !path.is_absolute() || !path.join("reseed").is_dir() || !path.join("family").is_dir() {
        bail!("{} is not an i2pd certificate directory", path.display());
    }
    Ok(())
}

pub fn resolve_executable(variable: &str, name: &str) -> Result<PathBuf> {
    if let Some(path) = std::env::var_os(variable).map(PathBuf::from) {
        return invocation_executable(&path)
            .with_context(|| format!("{variable} does not name an executable"));
    }
    if let Some(path) = crate::embedded_runtime::materialize(name)? {
        return invocation_executable(&path)
            .with_context(|| format!("embedded executable '{name}' is invalid"));
    }
    let path = std::env::var_os("PATH")
        .and_then(|path| {
            std::env::split_paths(&path)
                .map(|directory| directory.join(name))
                .find(|candidate| validate_executable(candidate).is_ok())
        })
        .ok_or_else(|| anyhow!("required executable '{name}' is not on PATH"))?;
    invocation_executable(&path)
}

fn invocation_executable(path: &Path) -> Result<PathBuf> {
    validate_executable(path)?;
    let name = path
        .file_name()
        .context("executable path has no invocation name")?;
    let parent = path
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
        .unwrap_or_else(|| Path::new("."));
    let resolved = fs::canonicalize(parent)?.join(name);
    validate_executable(&resolved)?;
    Ok(resolved)
}

fn validate_executable(path: &Path) -> Result<()> {
    let metadata = fs::metadata(path)?;
    if !metadata.is_file() {
        bail!("{} is not a file", path.display());
    }
    #[cfg(unix)]
    if metadata.permissions().mode() & 0o111 == 0 {
        bail!("{} is not executable", path.display());
    }
    Ok(())
}

pub struct ReservedLoopbackEndpoint {
    listener: StdTcpListener,
}

impl ReservedLoopbackEndpoint {
    pub fn allocate() -> Result<Self> {
        Self::bind("127.0.0.1:0".parse().expect("valid loopback endpoint"))
    }

    fn bind(address: SocketAddr) -> Result<Self> {
        if !address.ip().is_loopback() {
            bail!("reserved endpoint must be loopback");
        }
        let listener =
            StdTcpListener::bind(address).context("failed to reserve managed loopback endpoint")?;
        Ok(Self { listener })
    }

    pub fn address(&self) -> Result<SocketAddr> {
        self.listener
            .local_addr()
            .context("failed to read reserved endpoint")
    }

    fn reclaim(address: SocketAddr) -> Result<Self> {
        Self::bind(address)
    }
}

fn reserve_managed_endpoint_if_available(
    address: SocketAddr,
) -> Result<Option<ReservedLoopbackEndpoint>> {
    match StdTcpListener::bind(address) {
        Ok(listener) => Ok(Some(ReservedLoopbackEndpoint { listener })),
        Err(error) if error.kind() == std::io::ErrorKind::AddrInUse => Ok(None),
        Err(error) => Err(error).context("failed to reserve configured managed endpoint"),
    }
}

async fn reclaim_managed_endpoint(address: SocketAddr) -> Result<ReservedLoopbackEndpoint> {
    let deadline = Instant::now() + MANAGED_ENDPOINT_RECLAIM_TIMEOUT;
    loop {
        match ReservedLoopbackEndpoint::reclaim(address) {
            Ok(reservation) => return Ok(reservation),
            Err(error) if Instant::now() >= deadline => return Err(error),
            Err(_) => sleep(Duration::from_millis(25)).await,
        }
    }
}

enum I2pRuntime {
    Idle,
    Reserved(ReservedLoopbackEndpoint),
    External,
    Owned(ManagedChild),
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum I2pEndpointPolicy {
    Owned,
    ExternalOnly,
    Unreserved,
}

const MANAGED_OUTPUT_TAIL_BYTES: usize = 16 * 1024;
const MANAGED_OUTPUT_SUMMARY_CHARS: usize = 512;
const MANAGED_ENDPOINT_RECLAIM_TIMEOUT: Duration = Duration::from_secs(2);
const IDENTITY_ENVIRONMENT: [&str; 2] = ["ANONSSH_PASSPHRASE", "ANONSSH_PASSPHRASE_FILE"];

struct ManagedChild {
    child: Child,
    output: Arc<StdMutex<BoundedOutput>>,
    readers: Vec<JoinHandle<std::io::Result<()>>>,
}

#[derive(Default)]
struct BoundedOutput {
    bytes: Vec<u8>,
}

impl BoundedOutput {
    fn push(&mut self, bytes: &[u8]) {
        if bytes.len() >= MANAGED_OUTPUT_TAIL_BYTES {
            self.bytes.clear();
            self.bytes
                .extend_from_slice(&bytes[bytes.len() - MANAGED_OUTPUT_TAIL_BYTES..]);
            return;
        }
        let overflow = self
            .bytes
            .len()
            .saturating_add(bytes.len())
            .saturating_sub(MANAGED_OUTPUT_TAIL_BYTES);
        if overflow != 0 {
            self.bytes.drain(..overflow);
        }
        self.bytes.extend_from_slice(bytes);
    }
}

impl ManagedChild {
    fn spawn(command: &mut Command, label: &str) -> Result<Self> {
        remove_identity_environment(command);
        configure_owned_child(command);
        command.stdout(Stdio::piped()).stderr(Stdio::piped());
        let mut child = command
            .spawn()
            .with_context(|| format!("failed to start {label}"))?;
        let stdout = child
            .stdout
            .take()
            .with_context(|| format!("{label} stdout pipe is absent"))?;
        let stderr = child
            .stderr
            .take()
            .with_context(|| format!("{label} stderr pipe is absent"))?;
        let output = Arc::new(StdMutex::new(BoundedOutput::default()));
        let readers = vec![
            tokio::spawn(capture_managed_output(stdout, output.clone())),
            tokio::spawn(capture_managed_output(stderr, output.clone())),
        ];
        Ok(Self {
            child,
            output,
            readers,
        })
    }

    async fn stop(&mut self) -> Result<()> {
        let result = stop_child(&mut self.child).await;
        self.finish_readers().await;
        result
    }

    async fn finish_readers(&mut self) {
        for mut reader in self.readers.drain(..) {
            if timeout(Duration::from_secs(1), &mut reader).await.is_err() {
                reader.abort();
                let _ = reader.await;
            }
        }
    }

    fn output_summary(&self) -> String {
        let output = match self.output.lock() {
            Ok(output) => output,
            Err(poisoned) => poisoned.into_inner(),
        };
        sanitize_managed_output(&output.bytes)
    }
}

pub(crate) fn remove_identity_environment(command: &mut Command) {
    for variable in IDENTITY_ENVIRONMENT {
        command.env_remove(variable);
    }
}

pub(crate) fn remove_identity_environment_std(command: &mut std::process::Command) {
    for variable in IDENTITY_ENVIRONMENT {
        command.env_remove(variable);
    }
}

/// Makes a subprocess share the lifetime of the AnonSSH process that owns it.
///
/// `kill_on_drop` handles every normal and unwinding path. Linux parent-death
/// signaling also covers SIGKILL, power loss of a container, and other paths
/// that cannot run Rust destructors.
pub(crate) fn configure_owned_child(command: &mut Command) {
    command.kill_on_drop(true);
    #[cfg(target_os = "linux")]
    {
        // Capture before fork. The post-prctl parent check closes the race where
        // the owner exits between fork and PR_SET_PDEATHSIG in the child.
        let expected_parent = unsafe { libc::getpid() };
        // SAFETY: pre_exec performs only async-signal-safe libc operations. It
        // neither allocates nor touches shared Rust state in the forked child.
        unsafe {
            command.as_std_mut().pre_exec(move || {
                if libc::prctl(libc::PR_SET_PDEATHSIG, libc::SIGKILL) != 0 {
                    return Err(std::io::Error::last_os_error());
                }
                if libc::getppid() != expected_parent {
                    libc::kill(libc::getpid(), libc::SIGKILL);
                    libc::_exit(127);
                }
                Ok(())
            });
        }
    }
}

/// Gives a blocking std-process child the same Linux owner lifetime as managed routers.
pub(crate) fn configure_owned_std_child(command: &mut std::process::Command) {
    #[cfg(not(target_os = "linux"))]
    let _ = command;
    #[cfg(target_os = "linux")]
    {
        use std::os::unix::process::CommandExt;

        let expected_parent = unsafe { libc::getpid() };
        // SAFETY: pre_exec performs only async-signal-safe libc operations.
        unsafe {
            command.pre_exec(move || {
                if libc::prctl(libc::PR_SET_PDEATHSIG, libc::SIGKILL) != 0 {
                    return Err(std::io::Error::last_os_error());
                }
                if libc::getppid() != expected_parent {
                    libc::kill(libc::getpid(), libc::SIGKILL);
                    libc::_exit(127);
                }
                Ok(())
            });
        }
    }
}

impl Drop for ManagedChild {
    fn drop(&mut self) {
        let _ = self.child.start_kill();
        for reader in &self.readers {
            reader.abort();
        }
    }
}

pub struct I2pdManager {
    data_dir: PathBuf,
    binary: PathBuf,
    sam_addr: SocketAddr,
    endpoint_policy: I2pEndpointPolicy,
    runtime: Mutex<I2pRuntime>,
    startup_millis: AtomicU64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ManagedProcessUsage {
    pub cpu_time: Duration,
    pub resident_bytes: u64,
}

impl I2pdManager {
    pub fn new(data_dir: PathBuf, binary: PathBuf, sam_addr: SocketAddr) -> Result<Self> {
        if !sam_addr.ip().is_loopback() || sam_addr.port() == 0 {
            bail!("the managed SAM endpoint must be a non-zero loopback socket");
        }
        match reserve_managed_endpoint_if_available(sam_addr)? {
            Some(reservation) => Self::new_with_runtime(
                data_dir,
                binary,
                sam_addr,
                I2pEndpointPolicy::Owned,
                I2pRuntime::Reserved(reservation),
            ),
            None => Self::new_with_runtime(
                data_dir,
                binary,
                sam_addr,
                I2pEndpointPolicy::ExternalOnly,
                I2pRuntime::Idle,
            ),
        }
    }

    pub fn new_reserved(
        data_dir: PathBuf,
        binary: PathBuf,
        reservation: ReservedLoopbackEndpoint,
    ) -> Result<Self> {
        let sam_addr = reservation.address()?;
        Self::new_with_runtime(
            data_dir,
            binary,
            sam_addr,
            I2pEndpointPolicy::Owned,
            I2pRuntime::Reserved(reservation),
        )
    }

    pub(crate) fn new_unreserved(
        data_dir: PathBuf,
        binary: PathBuf,
        sam_addr: SocketAddr,
    ) -> Result<Self> {
        Self::new_with_runtime(
            data_dir,
            binary,
            sam_addr,
            I2pEndpointPolicy::Unreserved,
            I2pRuntime::Idle,
        )
    }

    fn new_with_runtime(
        data_dir: PathBuf,
        binary: PathBuf,
        sam_addr: SocketAddr,
        endpoint_policy: I2pEndpointPolicy,
        runtime: I2pRuntime,
    ) -> Result<Self> {
        if !sam_addr.ip().is_loopback() || sam_addr.port() == 0 {
            bail!("the managed SAM endpoint must be a non-zero loopback socket");
        }
        Ok(Self {
            data_dir,
            binary,
            sam_addr,
            endpoint_policy,
            runtime: Mutex::new(runtime),
            startup_millis: AtomicU64::new(0),
        })
    }

    pub async fn ensure_running(&self) -> Result<()> {
        let mut runtime = self.runtime.lock().await;
        let should_probe = match &mut *runtime {
            I2pRuntime::Owned(node) => node.child.try_wait()?.is_none(),
            I2pRuntime::External => true,
            I2pRuntime::Idle | I2pRuntime::Reserved(_) => false,
        };
        if should_probe && sam_healthy(self.sam_addr, Duration::from_secs(2)).await {
            return Ok(());
        }

        if let I2pRuntime::Owned(node) = &mut *runtime {
            node.stop().await?;
        }
        let previous = std::mem::replace(&mut *runtime, I2pRuntime::Idle);
        if self.endpoint_policy == I2pEndpointPolicy::ExternalOnly {
            let healthy = !should_probe && sam_healthy(self.sam_addr, Duration::from_secs(2)).await;
            drop(previous);
            if healthy {
                *runtime = I2pRuntime::External;
                return Ok(());
            }
            bail!("occupied SAM endpoint is not a healthy external router");
        }
        let reservation = match previous {
            I2pRuntime::Reserved(reservation) => Some(reservation),
            previous => {
                drop(previous);
                if self.endpoint_policy == I2pEndpointPolicy::Owned {
                    Some(reclaim_managed_endpoint(self.sam_addr).await?)
                } else {
                    None
                }
            }
        };

        match self.start_owned(reservation).await {
            Ok(node) => {
                *runtime = I2pRuntime::Owned(node);
                Ok(())
            }
            Err(error) => {
                if self.endpoint_policy == I2pEndpointPolicy::Owned {
                    match reclaim_managed_endpoint(self.sam_addr).await {
                        Ok(reservation) => {
                            *runtime = I2pRuntime::Reserved(reservation);
                        }
                        Err(reservation_error) => {
                            return Err(error.context(format!(
                                "failed to reclaim managed SAM endpoint: {reservation_error:#}"
                            )));
                        }
                    }
                }
                Err(error)
            }
        }
    }

    async fn start_owned(
        &self,
        reservation: Option<ReservedLoopbackEndpoint>,
    ) -> Result<ManagedChild> {
        fs::create_dir_all(&self.data_dir)?;
        chmod(&self.data_dir, 0o700)?;
        i2p_bootstrap::import_configured(&self.data_dir)
            .context("failed to import the packaged I2P bootstrap corpus")?;
        let config_path = self.data_dir.join("i2pd.conf");
        let certificates = resolve_i2pd_certificates(&self.binary)?;
        let config = i2pd_config(&self.data_dir, &certificates, self.sam_addr)?;
        fs::write(&config_path, config)?;
        chmod(&config_path, 0o600)?;
        remove_legacy_logs(&self.data_dir, &["i2pd.log", "i2pd.stderr.log"])?;
        let mut command = Command::new(&self.binary);
        command
            .arg(format!("--datadir={}", self.data_dir.display()))
            .arg(format!("--conf={}", config_path.display()))
            .stdin(Stdio::null());
        let startup_started = Instant::now();
        drop(reservation);
        let mut node = ManagedChild::spawn(&mut command, "i2pd")?;
        let deadline = Instant::now() + i2p_start_timeout();
        loop {
            if let Some(status) = node.child.try_wait()? {
                node.finish_readers().await;
                bail!(managed_startup_diagnostic(
                    "i2pd",
                    &format!("exited before SAM was ready: {status}"),
                    &node.output_summary(),
                ));
            }
            if sam_healthy(self.sam_addr, Duration::from_secs(2)).await {
                self.record_startup(startup_started.elapsed());
                return Ok(node);
            }
            if Instant::now() >= deadline {
                let stop_error = node.stop().await.err();
                let output = node.output_summary();
                if let Some(stop_error) = stop_error {
                    bail!(managed_startup_diagnostic(
                        "i2pd",
                        &format!(
                            "did not expose SAM before its startup deadline; stop failed: {stop_error}"
                        ),
                        &output,
                    ));
                }
                bail!(managed_startup_diagnostic(
                    "i2pd",
                    "did not expose SAM before its startup deadline",
                    &output,
                ));
            }
            sleep(Duration::from_millis(500)).await;
        }
    }

    pub async fn stop(&self) -> Result<()> {
        let mut runtime = self.runtime.lock().await;
        if self.endpoint_policy == I2pEndpointPolicy::Owned
            && matches!(&*runtime, I2pRuntime::Reserved(_))
        {
            return Ok(());
        }
        if let I2pRuntime::Owned(node) = &mut *runtime {
            node.stop().await?;
        }
        let previous = std::mem::replace(&mut *runtime, I2pRuntime::Idle);
        drop(previous);
        *runtime = if self.endpoint_policy == I2pEndpointPolicy::Owned {
            I2pRuntime::Reserved(reclaim_managed_endpoint(self.sam_addr).await?)
        } else {
            I2pRuntime::Idle
        };
        Ok(())
    }

    pub fn state_root(&self) -> &Path {
        &self.data_dir
    }

    pub fn try_process_usage(&self) -> Result<Option<ManagedProcessUsage>> {
        let runtime = match self.runtime.try_lock() {
            Ok(runtime) => runtime,
            Err(_) => return Ok(None),
        };
        match &*runtime {
            I2pRuntime::Owned(node) => managed_process_usage(&node.child),
            I2pRuntime::External | I2pRuntime::Idle | I2pRuntime::Reserved(_) => Ok(None),
        }
    }

    pub fn startup_latency(&self) -> Option<Duration> {
        let millis = self.startup_millis.load(Ordering::Relaxed);
        (millis != 0).then(|| Duration::from_millis(millis))
    }

    fn record_startup(&self, elapsed: Duration) {
        self.startup_millis.store(
            u64::try_from(elapsed.as_millis())
                .unwrap_or(u64::MAX)
                .max(1),
            Ordering::Relaxed,
        );
    }
}

impl Drop for I2pdManager {
    fn drop(&mut self) {
        if let I2pRuntime::Owned(node) = self.runtime.get_mut() {
            let _ = node.child.start_kill();
        }
    }
}

async fn capture_managed_output<R>(
    mut reader: R,
    output: Arc<StdMutex<BoundedOutput>>,
) -> std::io::Result<()>
where
    R: AsyncRead + Unpin,
{
    let mut buffer = [0_u8; 4096];
    loop {
        let read = reader.read(&mut buffer).await?;
        if read == 0 {
            return Ok(());
        }
        let mut output = match output.lock() {
            Ok(output) => output,
            Err(poisoned) => poisoned.into_inner(),
        };
        output.push(&buffer[..read]);
    }
}

fn sanitize_managed_output(bytes: &[u8]) -> String {
    let cleaned = strip_terminal_sequences(bytes);
    let text = String::from_utf8_lossy(&cleaned);
    let mut lines = text
        .lines()
        .filter(|line| !line.trim().is_empty())
        .rev()
        .take(4)
        .collect::<Vec<_>>();
    lines.reverse();
    if lines.is_empty() {
        return String::from("no output captured");
    }
    let mut sanitized = String::new();
    for token in lines.join(" | ").split_whitespace() {
        if !sanitized.is_empty() {
            sanitized.push(' ');
        }
        if managed_token_contains_endpoint(token) {
            sanitized.push_str("<endpoint>");
        } else if managed_token_contains_identity(token) {
            sanitized.push_str("<redacted>");
        } else {
            sanitized.push_str(token);
        }
    }
    let mut characters = sanitized.chars();
    let summary = characters
        .by_ref()
        .take(MANAGED_OUTPUT_SUMMARY_CHARS)
        .collect::<String>();
    if characters.next().is_some() {
        format!("{summary}...")
    } else {
        summary
    }
}

fn managed_token_contains_endpoint(token: &str) -> bool {
    let candidate = trim_managed_token(token);
    if candidate.parse::<SocketAddr>().is_ok() || candidate.parse::<IpAddr>().is_ok() {
        return true;
    }
    if candidate
        .strip_prefix('[')
        .and_then(|value| value.strip_suffix(']'))
        .is_some_and(|value| value.parse::<SocketAddr>().is_ok() || value.parse::<IpAddr>().is_ok())
    {
        return true;
    }
    candidate
        .rsplit_once('=')
        .map(|(_, value)| value)
        .or_else(|| candidate.rsplit_once("://").map(|(_, value)| value))
        .is_some_and(managed_token_contains_endpoint)
}

fn managed_token_contains_identity(token: &str) -> bool {
    let candidate = trim_managed_token(token);
    managed_identity_value(candidate)
        || candidate
            .split_once(['=', ':'])
            .is_some_and(|(_, value)| managed_identity_value(trim_managed_token(value)))
}

fn managed_identity_value(value: &str) -> bool {
    value.len() >= 43
        && value.chars().all(|character| {
            character.is_ascii_alphanumeric()
                || matches!(character, '+' | '/' | '-' | '_' | '=' | '~' | '.')
        })
}

fn trim_managed_token(token: &str) -> &str {
    token.trim_matches(|character: char| {
        matches!(
            character,
            '(' | ')' | '{' | '}' | '<' | '>' | ',' | ';' | '\'' | '"'
        )
    })
}

fn managed_startup_diagnostic(label: &str, failure: &str, output: &str) -> String {
    format!("{label} {failure}; recent output: {output}")
}

fn strip_terminal_sequences(bytes: &[u8]) -> Vec<u8> {
    let mut cleaned = Vec::with_capacity(bytes.len());
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] == 0x1b && bytes.get(index + 1) == Some(&b'[') {
            index += 2;
            while index < bytes.len() {
                let byte = bytes[index];
                index += 1;
                if (0x40..=0x7e).contains(&byte) {
                    break;
                }
            }
            continue;
        }
        let byte = bytes[index];
        index += 1;
        if byte >= b' ' || matches!(byte, b'\n' | b'\t') {
            cleaned.push(byte);
        }
    }
    cleaned
}

struct TorNode {
    process: Option<ManagedChild>,
    socks: SocketAddr,
    control: SocketAddr,
    authentication: Zeroizing<String>,
}

enum TorEndpointPolicy {
    Owned,
    Unreserved,
    External(PathBuf),
}

struct TorEndpointReservations {
    socks: ReservedLoopbackEndpoint,
    control: ReservedLoopbackEndpoint,
}

impl TorEndpointReservations {
    fn release(self) {
        drop(self.socks);
        drop(self.control);
    }
}

async fn reclaim_tor_endpoints(
    socks: SocketAddr,
    control: SocketAddr,
) -> Result<TorEndpointReservations> {
    Ok(TorEndpointReservations {
        socks: reclaim_managed_endpoint(socks).await?,
        control: reclaim_managed_endpoint(control).await?,
    })
}

struct TorRuntime {
    node: Option<TorNode>,
    reservations: Option<TorEndpointReservations>,
}

pub struct TorManager {
    data_dir: PathBuf,
    binary: PathBuf,
    socks: SocketAddr,
    control: SocketAddr,
    endpoint_policy: TorEndpointPolicy,
    runtime: Mutex<TorRuntime>,
    startup_millis: AtomicU64,
}

impl TorManager {
    pub fn new_at(
        data_dir: PathBuf,
        binary: PathBuf,
        socks: SocketAddr,
        control: SocketAddr,
    ) -> Result<Self> {
        if !socks.ip().is_loopback()
            || socks.port() == 0
            || !control.ip().is_loopback()
            || control.port() == 0
        {
            bail!("managed Tor endpoints must be non-zero loopback sockets");
        }
        if socks == control {
            bail!("Tor SOCKS and control endpoints must differ");
        }
        let reservations = match (
            reserve_managed_endpoint_if_available(socks)?,
            reserve_managed_endpoint_if_available(control)?,
        ) {
            (Some(socks), Some(control)) => TorEndpointReservations { socks, control },
            _ => bail!("managed Tor endpoint is already occupied"),
        };
        Self::new_with_runtime(
            data_dir,
            binary,
            socks,
            control,
            TorEndpointPolicy::Owned,
            Some(reservations),
        )
    }

    pub fn new_external_at(
        data_dir: PathBuf,
        binary: PathBuf,
        socks: SocketAddr,
        control: SocketAddr,
        cookie: PathBuf,
    ) -> Result<Self> {
        let cookie = canonical_external_tor_cookie(&cookie)?;
        Self::new_with_runtime(
            data_dir,
            binary,
            socks,
            control,
            TorEndpointPolicy::External(cookie),
            None,
        )
    }

    pub fn new_reserved(
        data_dir: PathBuf,
        binary: PathBuf,
        socks: ReservedLoopbackEndpoint,
        control: ReservedLoopbackEndpoint,
    ) -> Result<Self> {
        let socks_addr = socks.address()?;
        let control_addr = control.address()?;
        Self::new_with_runtime(
            data_dir,
            binary,
            socks_addr,
            control_addr,
            TorEndpointPolicy::Owned,
            Some(TorEndpointReservations { socks, control }),
        )
    }

    pub(crate) fn new_at_unreserved(
        data_dir: PathBuf,
        binary: PathBuf,
        socks: SocketAddr,
        control: SocketAddr,
    ) -> Result<Self> {
        Self::new_with_runtime(
            data_dir,
            binary,
            socks,
            control,
            TorEndpointPolicy::Unreserved,
            None,
        )
    }

    fn new_with_runtime(
        data_dir: PathBuf,
        binary: PathBuf,
        socks: SocketAddr,
        control: SocketAddr,
        endpoint_policy: TorEndpointPolicy,
        reservations: Option<TorEndpointReservations>,
    ) -> Result<Self> {
        if !socks.ip().is_loopback()
            || socks.port() == 0
            || !control.ip().is_loopback()
            || control.port() == 0
        {
            bail!("managed Tor endpoints must be non-zero loopback sockets");
        }
        if socks == control {
            bail!("Tor SOCKS and control endpoints must differ");
        }
        Ok(Self {
            data_dir,
            binary,
            socks,
            control,
            endpoint_policy,
            runtime: Mutex::new(TorRuntime {
                node: None,
                reservations,
            }),
            startup_millis: AtomicU64::new(0),
        })
    }

    pub async fn ensure_running(&self) -> Result<String> {
        let mut runtime = self.runtime.lock().await;
        if let Some(current) = runtime.node.as_mut() {
            let process_running = match current.process.as_mut() {
                Some(process) => process.child.try_wait()?.is_none(),
                None => true,
            };
            if process_running
                && tor_ready(current.control, &current.authentication).await
                && port_open(current.socks).await
            {
                return Ok(current.socks.to_string());
            }
            if let Some(process) = current.process.as_mut() {
                process.stop().await?;
            }
            runtime.node = None;
        }

        if let TorEndpointPolicy::External(cookie) = &self.endpoint_policy {
            let authentication = read_external_control_cookie(cookie)?;
            if !port_open(self.socks).await || !tor_ready(self.control, &authentication).await {
                bail!("declared external Tor service is not authenticated and ready");
            }
            runtime.node = Some(TorNode {
                process: None,
                socks: self.socks,
                control: self.control,
                authentication,
            });
            return Ok(self.socks.to_string());
        }

        if matches!(&self.endpoint_policy, TorEndpointPolicy::Unreserved)
            && (port_open(self.socks).await || port_open(self.control).await)
        {
            bail!("managed Tor endpoint is already occupied");
        }
        let reservations = match runtime.reservations.take() {
            Some(reservations) => Some(reservations),
            None if matches!(&self.endpoint_policy, TorEndpointPolicy::Owned) => {
                Some(reclaim_tor_endpoints(self.socks, self.control).await?)
            }
            None => None,
        };

        match self.start_owned(reservations).await {
            Ok(node) => {
                runtime.node = Some(node);
                Ok(self.socks.to_string())
            }
            Err(error) => {
                if matches!(&self.endpoint_policy, TorEndpointPolicy::Owned) {
                    match reclaim_tor_endpoints(self.socks, self.control).await {
                        Ok(reservations) => runtime.reservations = Some(reservations),
                        Err(reservation_error) => {
                            return Err(error.context(format!(
                                "failed to reclaim managed Tor endpoints: {reservation_error:#}"
                            )));
                        }
                    }
                }
                Err(error)
            }
        }
    }

    async fn start_owned(&self, reservations: Option<TorEndpointReservations>) -> Result<TorNode> {
        fs::create_dir_all(&self.data_dir)?;
        chmod(&self.data_dir, 0o700)?;
        let torrc = self.data_dir.join("torrc");
        fs::write(&torrc, tor_config(&self.data_dir, self.socks, self.control))?;
        chmod(&torrc, 0o600)?;
        remove_legacy_logs(&self.data_dir, &["tor.stderr.log"])?;
        let cookie_path = self.data_dir.join("control_auth_cookie");
        let mut command = Command::new(&self.binary);
        command.arg("-f").arg(&torrc).stdin(Stdio::null());
        let startup_started = Instant::now();
        drop(reservations);
        let mut process = ManagedChild::spawn(&mut command, "Tor")?;
        let deadline = Instant::now() + tor_start_timeout();
        loop {
            if let Some(status) = process.child.try_wait()? {
                process.finish_readers().await;
                bail!(managed_startup_diagnostic(
                    "Tor",
                    &format!("exited before bootstrap completed: {status}"),
                    &process.output_summary(),
                ));
            }
            if let Some(authentication) = read_control_cookie(&cookie_path) {
                if tor_ready(self.control, &authentication).await {
                    self.record_startup(startup_started.elapsed());
                    return Ok(TorNode {
                        process: Some(process),
                        socks: self.socks,
                        control: self.control,
                        authentication,
                    });
                }
            }
            if Instant::now() >= deadline {
                let stop_error = process.stop().await.err();
                let output = process.output_summary();
                if let Some(stop_error) = stop_error {
                    bail!(managed_startup_diagnostic(
                        "Tor",
                        &format!(
                            "did not bootstrap before its startup deadline; stop failed: {stop_error}"
                        ),
                        &output,
                    ));
                }
                bail!(managed_startup_diagnostic(
                    "Tor",
                    "did not bootstrap before its startup deadline",
                    &output,
                ));
            }
            sleep(Duration::from_millis(500)).await;
        }
    }

    pub async fn control_endpoint(&self) -> Result<TorControlEndpoint> {
        let runtime = self.runtime.lock().await;
        runtime
            .node
            .as_ref()
            .map(|node| {
                TorControlEndpoint::from_cookie(
                    node.control.to_string(),
                    node.authentication.clone(),
                )
            })
            .transpose()?
            .context("Tor is not running")
    }

    pub async fn stop(&self) -> Result<()> {
        let mut runtime = self.runtime.lock().await;
        if matches!(&self.endpoint_policy, TorEndpointPolicy::Owned)
            && runtime.node.is_none()
            && runtime.reservations.is_some()
        {
            return Ok(());
        }
        if let Some(current) = runtime.node.as_mut() {
            if let Some(process) = current.process.as_mut() {
                process.stop().await?;
            }
        }
        runtime.node = None;
        if let Some(reservations) = runtime.reservations.take() {
            reservations.release();
        }
        if matches!(&self.endpoint_policy, TorEndpointPolicy::Owned) {
            runtime.reservations = Some(reclaim_tor_endpoints(self.socks, self.control).await?);
        }
        Ok(())
    }

    pub fn state_root(&self) -> &Path {
        &self.data_dir
    }

    pub fn try_process_usage(&self) -> Result<Option<ManagedProcessUsage>> {
        let runtime = match self.runtime.try_lock() {
            Ok(runtime) => runtime,
            Err(_) => return Ok(None),
        };
        match runtime.node.as_ref() {
            Some(node) => match node.process.as_ref() {
                Some(process) => managed_process_usage(&process.child),
                None => Ok(None),
            },
            None => Ok(None),
        }
    }

    pub fn startup_latency(&self) -> Option<Duration> {
        let millis = self.startup_millis.load(Ordering::Relaxed);
        (millis != 0).then(|| Duration::from_millis(millis))
    }

    fn record_startup(&self, elapsed: Duration) {
        self.startup_millis.store(
            u64::try_from(elapsed.as_millis())
                .unwrap_or(u64::MAX)
                .max(1),
            Ordering::Relaxed,
        );
    }
}

impl Drop for TorManager {
    fn drop(&mut self) {
        if let Some(node) = self.runtime.get_mut().node.as_mut() {
            if let Some(process) = node.process.as_mut() {
                let _ = process.child.start_kill();
            }
        }
    }
}

#[cfg(target_os = "linux")]
fn managed_process_usage(child: &Child) -> Result<Option<ManagedProcessUsage>> {
    let Some(process_id) = child.id() else {
        return Ok(None);
    };
    let stat_path = format!("/proc/{process_id}/stat");
    let statm_path = format!("/proc/{process_id}/statm");
    let stat = match fs::read_to_string(&stat_path) {
        Ok(stat) => stat,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(error).with_context(|| format!("failed to read {stat_path}")),
    };
    let statm = match fs::read_to_string(&statm_path) {
        Ok(statm) => statm,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(error).with_context(|| format!("failed to read {statm_path}")),
    };
    let cpu_ticks = parse_process_stat_cpu_ticks(&stat)?;
    let resident_pages = parse_process_statm_resident_pages(&statm)?;
    let clock_ticks = *CLOCK_TICKS_PER_SECOND.get_or_init(|| {
        // SAFETY: sysconf reads a process-global constant and does not dereference pointers.
        let value = unsafe { libc::sysconf(libc::_SC_CLK_TCK) };
        u64::try_from(value).unwrap_or(100).max(1)
    });
    let page_size = *PAGE_SIZE.get_or_init(|| {
        // SAFETY: sysconf reads a process-global constant and does not dereference pointers.
        let value = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
        u64::try_from(value).unwrap_or(4_096).max(1)
    });
    let cpu_nanos = u128::from(cpu_ticks)
        .saturating_mul(1_000_000_000)
        .checked_div(u128::from(clock_ticks))
        .unwrap_or(u128::MAX)
        .min(u64::MAX.into()) as u64;
    Ok(Some(ManagedProcessUsage {
        cpu_time: Duration::from_nanos(cpu_nanos),
        resident_bytes: resident_pages.saturating_mul(page_size),
    }))
}

#[cfg(target_os = "linux")]
static CLOCK_TICKS_PER_SECOND: OnceLock<u64> = OnceLock::new();
#[cfg(target_os = "linux")]
static PAGE_SIZE: OnceLock<u64> = OnceLock::new();

#[cfg(target_os = "linux")]
fn parse_process_stat_cpu_ticks(contents: &str) -> Result<u64> {
    let (_, fields) = contents
        .rsplit_once(") ")
        .context("managed process stat omitted command terminator")?;
    let mut fields = fields.split_whitespace();
    let user = fields
        .nth(11)
        .context("managed process stat omitted user CPU time")?
        .parse::<u64>()?;
    let system = fields
        .next()
        .context("managed process stat omitted system CPU time")?
        .parse::<u64>()?;
    user.checked_add(system)
        .context("managed CPU time overflow")
}

#[cfg(target_os = "linux")]
fn parse_process_statm_resident_pages(contents: &str) -> Result<u64> {
    contents
        .split_whitespace()
        .nth(1)
        .context("managed process statm omitted resident pages")?
        .parse::<u64>()
        .context("managed process statm has invalid resident pages")
}

#[cfg(not(target_os = "linux"))]
fn managed_process_usage(_child: &Child) -> Result<Option<ManagedProcessUsage>> {
    Ok(None)
}

async fn sam_healthy(address: SocketAddr, deadline: Duration) -> bool {
    let connector = SamConnector::new(address.to_string(), None);
    matches!(
        timeout(deadline, async {
            let mut stream = TcpStream::connect(address).await?;
            connector.handshake(&mut stream).await
        })
        .await,
        Ok(Ok(()))
    )
}

async fn tor_ready(control: SocketAddr, authentication: &str) -> bool {
    let check = async {
        let mut stream = TcpStream::connect(control).await?;
        let command = Zeroizing::new(format!("AUTHENTICATE {authentication}\r\n"));
        stream.write_all(command.as_bytes()).await?;
        let authenticated = read_tor_reply(&mut stream).await?;
        if !authenticated.lines().any(|line| line == "250 OK") {
            bail!("Tor control authentication failed");
        }
        stream
            .write_all(b"GETINFO status/bootstrap-phase\r\n")
            .await?;
        let status = read_tor_reply(&mut stream).await?;
        Ok::<bool, anyhow::Error>(status.contains("PROGRESS=100"))
    };
    matches!(timeout(Duration::from_secs(2), check).await, Ok(Ok(true)))
}

async fn read_tor_reply(stream: &mut TcpStream) -> Result<String> {
    let mut bytes = Vec::with_capacity(1024);
    loop {
        if bytes.len() > 64 * 1024 {
            bail!("Tor control reply exceeded 64 KiB");
        }
        let text = String::from_utf8_lossy(&bytes);
        if text
            .split("\r\n")
            .any(|line| line.len() >= 4 && &line[3..4] == " ")
        {
            return Ok(text.into_owned());
        }
        let mut buffer = [0_u8; 1024];
        let count = stream.read(&mut buffer).await?;
        if count == 0 {
            bail!("Tor control socket closed unexpectedly");
        }
        bytes.extend_from_slice(&buffer[..count]);
    }
}

async fn port_open(address: SocketAddr) -> bool {
    matches!(
        timeout(Duration::from_millis(300), TcpStream::connect(address)).await,
        Ok(Ok(_))
    )
}

pub(crate) async fn stop_child(child: &mut Child) -> Result<()> {
    if child.try_wait()?.is_some() {
        return Ok(());
    }
    if request_graceful_stop(child).is_ok()
        && matches!(
            timeout(Duration::from_secs(5), child.wait()).await,
            Ok(Ok(_))
        )
    {
        return Ok(());
    }
    if child.try_wait()?.is_some() {
        return Ok(());
    }
    child.start_kill()?;
    timeout(Duration::from_secs(5), child.wait())
        .await
        .context("process did not stop after forced termination")??;
    Ok(())
}

#[cfg(unix)]
fn request_graceful_stop(child: &mut Child) -> Result<()> {
    let process_id = child.id().context("managed process has no process ID")?;
    let process_id = i32::try_from(process_id).context("managed process ID is out of range")?;
    // SAFETY: kill only reads the integer PID and sends SIGTERM to that exact process.
    if unsafe { libc::kill(process_id, libc::SIGTERM) } == 0 {
        Ok(())
    } else {
        Err(std::io::Error::last_os_error().into())
    }
}

#[cfg(not(unix))]
fn request_graceful_stop(child: &mut Child) -> Result<()> {
    child.start_kill()?;
    Ok(())
}

fn i2pd_config(data_dir: &Path, certificates: &Path, sam_addr: SocketAddr) -> Result<String> {
    let reseed = if std::env::var_os("ANONSSH_INTERNAL_TEST_DISABLE_I2P_RESEED").is_some() {
        "verify = true\nthreshold = 0\n"
    } else {
        "verify = true\n"
    };
    Ok(format!(
        "daemon = false\nlog = stdout\nloglevel = warn\nnotransit = true\nfloodfill = false\nipv4 = true\nipv6 = true\nshare = 100\npidfile = {}\ncertsdir = {}\n\n[http]\nenabled = false\n\n[httpproxy]\nenabled = false\n\n[sam]\nenabled = true\naddress = {}\nport = {}\nportudp = 0\n\n[socksproxy]\nenabled = false\n\n[addressbook]\nenabled = true\n\n[persist]\nprofiles = true\naddressbook = true\n\n[reseed]\n{reseed}",
        config_value(&data_dir.join("i2pd.pid"))?,
        config_value(certificates)?,
        sam_addr.ip(),
        sam_addr.port(),
    ))
}

fn tor_config(data_dir: &Path, socks: SocketAddr, control: SocketAddr) -> String {
    format!(
        "DataDirectory {}\nSocksPort {} IsolateSOCKSAuth\nControlPort {}\nCookieAuthentication 1\nCookieAuthFileGroupReadable 0\nClientOnly 1\nORPort 0\nExitRelay 0\nAvoidDiskWrites 1\nSafeLogging 1\nLog warn stderr\n",
        tor_value(data_dir),
        socks,
        control,
    )
}

fn read_control_cookie(path: &Path) -> Option<Zeroizing<String>> {
    let bytes = Zeroizing::new(fs::read(path).ok()?);
    if bytes.len() != 32 {
        return None;
    }
    let mut encoded = Zeroizing::new(String::with_capacity(64));
    for byte in bytes.iter() {
        use std::fmt::Write as _;
        write!(encoded, "{byte:02x}").ok()?;
    }
    Some(encoded)
}

pub(crate) fn canonical_external_tor_cookie(path: &Path) -> Result<PathBuf> {
    read_external_control_cookie(path)?;
    fs::canonicalize(path).context("cannot canonicalize external Tor cookie")
}

fn read_external_control_cookie(path: &Path) -> Result<Zeroizing<String>> {
    if !path.is_absolute() {
        bail!("external Tor control cookie path must be absolute");
    }
    let file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_CLOEXEC | libc::O_NOFOLLOW)
        .open(path)
        .with_context(|| format!("cannot open external Tor control cookie {}", path.display()))?;
    let metadata = file.metadata()?;
    if !metadata.is_file() {
        bail!("external Tor control cookie must be a regular file");
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("external Tor control cookie must be owned by the current user");
    }
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("external Tor control cookie must not be accessible by group or other users");
    }
    if metadata.len() != 32 {
        bail!("external Tor control cookie must contain exactly 32 bytes");
    }
    let mut bytes = Zeroizing::new(Vec::with_capacity(33));
    file.take(33).read_to_end(&mut bytes)?;
    if bytes.len() != 32 {
        bail!("external Tor control cookie changed while being read");
    }
    let mut encoded = Zeroizing::new(String::with_capacity(64));
    for byte in bytes.iter() {
        use std::fmt::Write as _;
        write!(encoded, "{byte:02x}")?;
    }
    Ok(encoded)
}

fn remove_legacy_logs(data_dir: &Path, names: &[&str]) -> Result<()> {
    for name in names {
        match fs::remove_file(data_dir.join(name)) {
            Ok(()) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => return Err(error.into()),
        }
    }
    Ok(())
}

fn config_value(path: &Path) -> Result<String> {
    let value = path.to_string_lossy();
    if value.contains(['\n', '\r']) {
        bail!("runtime path contains a newline");
    }
    Ok(value.into_owned())
}

fn tor_value(path: &Path) -> String {
    format!(
        "\"{}\"",
        path.to_string_lossy()
            .replace('\\', "\\\\")
            .replace('"', "\\\"")
    )
}

fn loopback_endpoint(variable: &str, default_port: u16) -> Result<SocketAddr> {
    let value = std::env::var(variable).unwrap_or_else(|_| format!("127.0.0.1:{default_port}"));
    let address: SocketAddr = value
        .parse()
        .with_context(|| format!("invalid {variable}"))?;
    if !address.ip().is_loopback() || address.port() == 0 {
        bail!("{variable} must be a non-zero loopback socket");
    }
    Ok(address)
}

pub fn sam_endpoint() -> Result<SocketAddr> {
    loopback_endpoint("ANONSSH_SAM_ADDR", 7_656)
}

pub fn tor_socks_endpoint() -> Result<SocketAddr> {
    loopback_endpoint("ANONSSH_TOR_SOCKS_ADDR", 19_050)
}

pub fn tor_control_endpoint() -> Result<SocketAddr> {
    loopback_endpoint("ANONSSH_TOR_CONTROL_ADDR", 19_150)
}

pub(crate) fn i2p_start_timeout() -> Duration {
    environment_timeout("ANONSSH_I2PD_START_TIMEOUT_SECS", 300, 30, 1_800)
}

pub(crate) fn tor_start_timeout() -> Duration {
    environment_timeout("ANONSSH_TOR_START_TIMEOUT_SECS", 180, 10, 600)
}

fn environment_timeout(variable: &str, default: u64, minimum: u64, maximum: u64) -> Duration {
    Duration::from_secs(
        std::env::var(variable)
            .ok()
            .and_then(|value| value.parse().ok())
            .unwrap_or(default)
            .clamp(minimum, maximum),
    )
}

pub fn chmod(path: &Path, mode: u32) -> Result<()> {
    #[cfg(unix)]
    fs::set_permissions(path, fs::Permissions::from_mode(mode))?;
    let _ = mode;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{
        canonical_external_tor_cookie, capture_managed_output, chmod, i2pd_config,
        invocation_executable, loopback_endpoint, managed_startup_diagnostic,
        read_external_control_cookie, remove_identity_environment, remove_identity_environment_std,
        sanitize_managed_output, tor_config, tor_value, BoundedOutput, I2pRuntime, I2pdManager,
        ReservedLoopbackEndpoint, TorManager, IDENTITY_ENVIRONMENT, MANAGED_OUTPUT_TAIL_BYTES,
    };
    #[cfg(target_os = "linux")]
    use super::{
        configure_owned_child, parse_process_stat_cpu_ticks, parse_process_statm_resident_pages,
    };
    use std::fs;
    use std::net::{SocketAddr, TcpListener};
    use std::path::Path;
    use std::sync::{Arc, Mutex};
    use std::time::{Duration, Instant};
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::TcpListener as TokioTcpListener;

    #[test]
    fn third_party_children_do_not_inherit_identity_environment() {
        let mut asynchronous = tokio::process::Command::new("/bin/true");
        let mut blocking = std::process::Command::new("/bin/true");
        for variable in IDENTITY_ENVIRONMENT {
            asynchronous.env(variable, "secret");
            blocking.env(variable, "secret");
        }
        remove_identity_environment(&mut asynchronous);
        remove_identity_environment_std(&mut blocking);

        for command in [asynchronous.as_std(), &blocking] {
            for variable in IDENTITY_ENVIRONMENT {
                assert!(command
                    .get_envs()
                    .any(|(name, value)| name == variable && value.is_none()));
            }
        }
    }

    fn reclaim_released_endpoint(address: SocketAddr) -> ReservedLoopbackEndpoint {
        let deadline = Instant::now() + Duration::from_secs(5);
        loop {
            match ReservedLoopbackEndpoint::reclaim(address) {
                Ok(reservation) => return reservation,
                Err(error) if Instant::now() >= deadline => {
                    panic!("released endpoint {address} could not be reclaimed: {error:#}")
                }
                Err(_) => std::thread::sleep(Duration::from_millis(10)),
            }
        }
    }

    #[test]
    fn tor_paths_are_quoted() {
        assert_eq!(tor_value(Path::new("/tmp/a b")), "\"/tmp/a b\"");
    }

    #[cfg(unix)]
    #[test]
    fn executable_resolution_preserves_symlink_dispatch_name() {
        use std::os::unix::fs::{symlink, PermissionsExt};

        let root = std::env::temp_dir().join(format!(
            "anonssh-executable-resolution-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let target = root.join("multicall");
        let alias = root.join("git-receive-pack");
        fs::write(&target, b"#!/bin/sh\nexit 0\n").unwrap();
        fs::set_permissions(&target, fs::Permissions::from_mode(0o700)).unwrap();
        symlink("multicall", &alias).unwrap();

        let resolved = invocation_executable(&alias).unwrap();
        assert_eq!(resolved.file_name().unwrap(), "git-receive-pack");
        assert_ne!(resolved, fs::canonicalize(&alias).unwrap());

        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn managed_endpoints_are_loopback_only() {
        std::env::set_var("ANONSSH_TEST_ENDPOINT", "8.8.8.8:7656");
        assert!(loopback_endpoint("ANONSSH_TEST_ENDPOINT", 7656).is_err());
        std::env::remove_var("ANONSSH_TEST_ENDPOINT");
    }

    #[test]
    fn managed_router_configs_persist_network_state_without_disk_logs() {
        let i2p = i2pd_config(
            Path::new("/tmp/anonssh-state/i2pd"),
            Path::new("/nix/store/certificates"),
            "127.0.0.1:7656".parse::<SocketAddr>().unwrap(),
        )
        .unwrap();
        assert!(i2p.contains("profiles = true"));
        assert!(i2p.contains("addressbook = true"));
        assert!(i2p.contains("log = stdout"));
        assert!(!i2p.contains("logfile"));

        let tor = tor_config(
            Path::new("/tmp/anonssh-state/tor"),
            "127.0.0.1:19050".parse().unwrap(),
            "127.0.0.1:19150".parse().unwrap(),
        );
        assert!(tor.contains("AvoidDiskWrites 1"));
        assert!(tor.contains("CookieAuthentication 1"));
        assert!(tor.contains("SocksPort 127.0.0.1:19050 IsolateSOCKSAuth"));
        assert!(tor.contains("Log warn stderr"));
        assert!(!tor.contains("tor.stderr.log"));
    }

    #[tokio::test]
    async fn process_samples_do_not_wait_for_router_runtime_locks() {
        let i2p = I2pdManager::new(
            "/tmp/anonssh-i2p-sample-test".into(),
            "/not/executed/i2pd".into(),
            "127.0.0.1:17656".parse().unwrap(),
        )
        .unwrap();
        let i2p_runtime = i2p.runtime.lock().await;
        assert_eq!(i2p.try_process_usage().unwrap(), None);
        drop(i2p_runtime);

        let tor = TorManager::new_at(
            "/tmp/anonssh-tor-sample-test".into(),
            "/not/executed/tor".into(),
            "127.0.0.1:19090".parse().unwrap(),
            "127.0.0.1:19190".parse().unwrap(),
        )
        .unwrap();
        let tor_runtime = tor.runtime.lock().await;
        assert_eq!(tor.try_process_usage().unwrap(), None);
        drop(tor_runtime);
    }

    #[tokio::test]
    async fn managed_router_reservations_survive_failed_start_and_stop() {
        let i2p_root =
            std::env::temp_dir().join(format!("anonssh-i2p-reservation-{}", std::process::id()));
        let tor_root =
            std::env::temp_dir().join(format!("anonssh-tor-reservation-{}", std::process::id()));
        let _ = fs::remove_dir_all(&i2p_root);
        let _ = fs::remove_dir_all(&tor_root);
        let i2p_reservation = ReservedLoopbackEndpoint::allocate().unwrap();
        let i2p_address = i2p_reservation.address().unwrap();
        let i2p = I2pdManager::new_reserved(
            i2p_root.clone(),
            "/not/executed/i2pd".into(),
            i2p_reservation,
        )
        .unwrap();
        assert!(TcpListener::bind(i2p_address).is_err());
        assert!(i2p.ensure_running().await.is_err());
        assert!(TcpListener::bind(i2p_address).is_err());
        assert!(i2p.ensure_running().await.is_err());
        assert!(TcpListener::bind(i2p_address).is_err());
        i2p.stop().await.unwrap();
        assert!(TcpListener::bind(i2p_address).is_err());

        let socks_reservation = ReservedLoopbackEndpoint::allocate().unwrap();
        let control_reservation = ReservedLoopbackEndpoint::allocate().unwrap();
        let socks = socks_reservation.address().unwrap();
        let control = control_reservation.address().unwrap();
        let tor = TorManager::new_reserved(
            tor_root.clone(),
            "/not/executed/tor".into(),
            socks_reservation,
            control_reservation,
        )
        .unwrap();
        assert!(TcpListener::bind(socks).is_err());
        assert!(TcpListener::bind(control).is_err());
        assert!(tor.ensure_running().await.is_err());
        assert!(TcpListener::bind(socks).is_err());
        assert!(TcpListener::bind(control).is_err());
        assert!(tor.ensure_running().await.is_err());
        assert!(TcpListener::bind(socks).is_err());
        assert!(TcpListener::bind(control).is_err());
        tor.stop().await.unwrap();
        assert!(TcpListener::bind(socks).is_err());
        assert!(TcpListener::bind(control).is_err());
        drop(i2p);
        drop(tor);
        let _ = fs::remove_dir_all(i2p_root);
        let _ = fs::remove_dir_all(tor_root);
    }

    #[tokio::test]
    async fn occupied_i2p_endpoint_requires_a_healthy_external_router() {
        for (reply, expected_ok) in [
            (b"HELLO REPLY RESULT=OK VERSION=3.3\n".as_slice(), true),
            (
                b"HELLO REPLY RESULT=I2P_ERROR VERSION=3.3\n".as_slice(),
                false,
            ),
        ] {
            let listener = Arc::new(TokioTcpListener::bind("127.0.0.1:0").await.unwrap());
            let address = listener.local_addr().unwrap();
            let server_listener = listener.clone();
            let server = tokio::spawn(async move {
                let (mut stream, _) = server_listener.accept().await.unwrap();
                let mut request = [0_u8; 128];
                let count = stream.read(&mut request).await.unwrap();
                assert!(request[..count].starts_with(b"HELLO VERSION"));
                stream.write_all(reply).await.unwrap();
            });
            let manager = I2pdManager::new(
                std::env::temp_dir().join(format!(
                    "anonssh-external-i2p-{}-{}",
                    std::process::id(),
                    address.port()
                )),
                "/not/executed/i2pd".into(),
                address,
            )
            .unwrap();

            let result = manager.ensure_running().await;
            server.await.unwrap();
            if expected_ok {
                result.unwrap();
                assert!(matches!(
                    *manager.runtime.lock().await,
                    I2pRuntime::External
                ));
            } else {
                assert!(result
                    .unwrap_err()
                    .to_string()
                    .contains("occupied SAM endpoint is not a healthy external router"));
            }
            manager.stop().await.unwrap();
            assert!(TcpListener::bind(address).is_err());
            drop(manager);
            drop(listener);
        }
    }

    #[test]
    fn occupied_tor_endpoint_fails_closed_without_leaking_other_reservations() {
        let occupied = ReservedLoopbackEndpoint::allocate().unwrap();
        let socks = occupied.address().unwrap();
        let available = ReservedLoopbackEndpoint::allocate().unwrap();
        let control = available.address().unwrap();
        drop(available);

        let error = TorManager::new_at(
            Path::new("/tmp/anonssh-occupied-tor-endpoint").to_path_buf(),
            "/not/executed/tor".into(),
            socks,
            control,
        )
        .err()
        .unwrap();
        assert!(error
            .to_string()
            .contains("managed Tor endpoint is already occupied"));
        assert!(TcpListener::bind(socks).is_err());
        let _control = reclaim_released_endpoint(control);
    }

    #[tokio::test]
    async fn declared_external_tor_is_authenticated_borrowed_and_never_stopped() {
        let root =
            std::env::temp_dir().join(format!("anonssh-external-tor-{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let cookie = root.join("control-cookie");
        fs::write(&cookie, [0x5a_u8; 32]).unwrap();
        chmod(&cookie, 0o600).unwrap();

        let socks_listener = Arc::new(TokioTcpListener::bind("127.0.0.1:0").await.unwrap());
        let control_listener = Arc::new(TokioTcpListener::bind("127.0.0.1:0").await.unwrap());
        let socks = socks_listener.local_addr().unwrap();
        let control = control_listener.local_addr().unwrap();
        let socks_server = {
            let listener = socks_listener.clone();
            tokio::spawn(async move {
                loop {
                    let _ = listener.accept().await.unwrap();
                }
            })
        };
        let control_server = {
            let listener = control_listener.clone();
            tokio::spawn(async move {
                loop {
                    let (mut stream, _) = listener.accept().await.unwrap();
                    let mut request = [0_u8; 256];
                    let count = stream.read(&mut request).await.unwrap();
                    assert!(request[..count].starts_with(b"AUTHENTICATE "));
                    stream.write_all(b"250 OK\r\n").await.unwrap();
                    let count = stream.read(&mut request).await.unwrap();
                    assert_eq!(&request[..count], b"GETINFO status/bootstrap-phase\r\n");
                    stream
                        .write_all(
                            b"250-status/bootstrap-phase=NOTICE BOOTSTRAP PROGRESS=100\r\n250 OK\r\n",
                        )
                        .await
                        .unwrap();
                }
            })
        };

        let manager = TorManager::new_external_at(
            root.join("unused-state"),
            "/not/executed/tor".into(),
            socks,
            control,
            cookie,
        )
        .unwrap();
        assert_eq!(manager.ensure_running().await.unwrap(), socks.to_string());
        assert_eq!(manager.try_process_usage().unwrap(), None);
        manager.stop().await.unwrap();
        assert!(TcpListener::bind(socks).is_err());
        assert!(TcpListener::bind(control).is_err());
        assert_eq!(manager.ensure_running().await.unwrap(), socks.to_string());

        socks_server.abort();
        control_server.abort();
        drop(socks_listener);
        drop(control_listener);
        socks_server.await.unwrap_err();
        control_server.await.unwrap_err();
        assert!(manager.ensure_running().await.is_err());
        drop(manager);
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn external_tor_cookie_is_owner_only_regular_and_exact() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-external-tor-cookie-{}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let cookie = root.join("cookie");
        fs::write(&cookie, [0x3c_u8; 32]).unwrap();
        chmod(&cookie, 0o600).unwrap();
        assert_eq!(read_external_control_cookie(&cookie).unwrap().len(), 64);
        assert_eq!(canonical_external_tor_cookie(&cookie).unwrap(), cookie);

        chmod(&cookie, 0o640).unwrap();
        assert!(read_external_control_cookie(&cookie).is_err());
        chmod(&cookie, 0o600).unwrap();
        fs::write(&cookie, [0_u8; 31]).unwrap();
        assert!(read_external_control_cookie(&cookie).is_err());
        fs::remove_file(&cookie).unwrap();
        std::os::unix::fs::symlink("missing", &cookie).unwrap();
        assert!(read_external_control_cookie(&cookie).is_err());
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn configured_managed_endpoints_are_reserved_during_deferred_startup() {
        let i2p_available = ReservedLoopbackEndpoint::allocate().unwrap();
        let i2p_address = i2p_available.address().unwrap();
        drop(i2p_available);
        let i2p = I2pdManager::new(
            Path::new("/tmp/anonssh-configured-i2p-reservation").to_path_buf(),
            "/not/executed/i2pd".into(),
            i2p_address,
        )
        .unwrap();
        assert!(TcpListener::bind(i2p_address).is_err());

        let socks_available = ReservedLoopbackEndpoint::allocate().unwrap();
        let control_available = ReservedLoopbackEndpoint::allocate().unwrap();
        let socks = socks_available.address().unwrap();
        let control = control_available.address().unwrap();
        drop(socks_available);
        drop(control_available);
        let tor = TorManager::new_at(
            Path::new("/tmp/anonssh-configured-tor-reservation").to_path_buf(),
            "/not/executed/tor".into(),
            socks,
            control,
        )
        .unwrap();
        assert!(TcpListener::bind(socks).is_err());
        assert!(TcpListener::bind(control).is_err());

        drop(i2p);
        drop(tor);
        let i2p_reservation = reclaim_released_endpoint(i2p_address);
        let socks_reservation = reclaim_released_endpoint(socks);
        let control_reservation = reclaim_released_endpoint(control);
        assert_eq!(i2p_reservation.address().unwrap(), i2p_address);
        assert_eq!(socks_reservation.address().unwrap(), socks);
        assert_eq!(control_reservation.address().unwrap(), control);
    }

    #[tokio::test]
    async fn managed_router_output_capture_retains_only_its_tail() {
        let output = Arc::new(Mutex::new(BoundedOutput::default()));
        let (mut writer, reader) = tokio::io::duplex(MANAGED_OUTPUT_TAIL_BYTES * 2);
        let capture = tokio::spawn(capture_managed_output(reader, output.clone()));
        let mut bytes = vec![b'x'; MANAGED_OUTPUT_TAIL_BYTES + 1024];
        bytes.extend_from_slice(b"useful terminal failure\n");
        writer.write_all(&bytes).await.unwrap();
        drop(writer);
        capture.await.unwrap().unwrap();

        let output = output.lock().unwrap();
        assert_eq!(output.bytes.len(), MANAGED_OUTPUT_TAIL_BYTES);
        assert!(output.bytes.ends_with(b"useful terminal failure\n"));
    }

    #[test]
    fn managed_router_output_summary_redacts_endpoints_and_identity_material() {
        let identity = "A".repeat(80);
        let i2p_hash = "v6wVmckXaRg5CAkiedF72eCyDGJODnGWh0BJcGs3CqU=";
        let output = format!(
            "ordinary startup line\n\x1b[1;33mwarn\x1b[0m failed to bind sam=127.0.0.1:7656 listener=[127.0.0.1:9050] control=[::1]:9051 route=tcp://127.0.0.1:7657 identity={identity} peer=<{i2p_hash}>\n"
        );
        let summary = sanitize_managed_output(output.as_bytes());
        assert!(summary.contains("ordinary startup line"));
        assert!(summary.contains("warn failed to bind"));
        assert_eq!(summary.matches("<endpoint>").count(), 4);
        assert!(summary.contains("<redacted>"));
        assert!(!summary.contains("127.0.0.1"));
        assert!(!summary.contains("::1"));
        assert!(!summary.contains(&identity));
        assert!(!summary.contains(i2p_hash));
        assert!(!summary.contains('\x1b'));

        for (label, failure) in [
            ("i2pd", "exited before SAM was ready: exit status: 17"),
            ("Tor", "did not bootstrap before its startup deadline"),
        ] {
            let diagnostic = managed_startup_diagnostic(label, failure, &summary);
            assert!(diagnostic.starts_with(&format!("{label} {failure}")));
            assert!(diagnostic.contains("recent output: ordinary startup line"));
            assert!(!diagnostic.contains("127.0.0.1"));
            assert!(!diagnostic.contains(i2p_hash));
        }
    }

    #[cfg(target_os = "linux")]
    #[test]
    fn linux_process_metrics_parse_commands_with_spaces() {
        let stat = "123 (managed router worker) S 1 2 3 4 5 6 7 8 9 10 111 222 13 14";
        assert_eq!(parse_process_stat_cpu_ticks(stat).unwrap(), 333);
        assert_eq!(
            parse_process_statm_resident_pages("1000 321 20").unwrap(),
            321
        );
        assert!(parse_process_stat_cpu_ticks("truncated").is_err());
        assert!(parse_process_statm_resident_pages("1000").is_err());
    }

    #[cfg(target_os = "linux")]
    #[test]
    fn owned_child_probe() {
        const ROLE: &str = "ANONSSH_INTERNAL_OWNED_CHILD_PROBE";
        const PID_FILE: &str = "ANONSSH_INTERNAL_OWNED_CHILD_PID_FILE";
        match std::env::var(ROLE).as_deref() {
            Ok("child") => loop {
                std::thread::sleep(Duration::from_secs(60));
            },
            Ok("parent") => {
                let runtime = tokio::runtime::Builder::new_current_thread()
                    .enable_all()
                    .build()
                    .unwrap();
                runtime.block_on(async {
                    let executable = std::env::current_exe().unwrap();
                    let mut command = tokio::process::Command::new(executable);
                    command
                        .arg("--exact")
                        .arg("runtime::tests::owned_child_probe")
                        .arg("--nocapture")
                        .env(ROLE, "child")
                        .stdin(std::process::Stdio::null())
                        .stdout(std::process::Stdio::null())
                        .stderr(std::process::Stdio::null());
                    configure_owned_child(&mut command);
                    let child = command.spawn().unwrap();
                    fs::write(
                        std::env::var_os(PID_FILE).unwrap(),
                        child.id().unwrap().to_string(),
                    )
                    .unwrap();
                    std::future::pending::<()>().await;
                });
            }
            _ => {}
        }
    }

    #[cfg(target_os = "linux")]
    #[test]
    fn owned_child_dies_when_its_parent_is_sigkilled() {
        const ROLE: &str = "ANONSSH_INTERNAL_OWNED_CHILD_PROBE";
        const PID_FILE: &str = "ANONSSH_INTERNAL_OWNED_CHILD_PID_FILE";
        let root = std::env::temp_dir().join(format!("anonssh-owned-child-{}", std::process::id()));
        let _ = fs::remove_dir_all(&root);
        fs::create_dir_all(&root).unwrap();
        let pid_file = root.join("child.pid");
        let executable = std::env::current_exe().unwrap();
        let mut parent = std::process::Command::new(executable)
            .arg("--exact")
            .arg("runtime::tests::owned_child_probe")
            .arg("--nocapture")
            .env(ROLE, "parent")
            .env(PID_FILE, &pid_file)
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .spawn()
            .unwrap();

        let deadline = Instant::now() + Duration::from_secs(5);
        let child_pid = loop {
            if let Ok(value) = fs::read_to_string(&pid_file) {
                break value.parse::<i32>().unwrap();
            }
            if Instant::now() >= deadline {
                let _ = parent.kill();
                let _ = parent.wait();
                panic!("owned-child probe did not publish its PID");
            }
            std::thread::sleep(Duration::from_millis(10));
        };
        assert!(linux_process_is_live(child_pid));

        // SAFETY: the PID came directly from the live Child handle above.
        assert_eq!(unsafe { libc::kill(parent.id() as i32, libc::SIGKILL) }, 0);
        let _ = parent.wait().unwrap();
        let deadline = Instant::now() + Duration::from_secs(5);
        while linux_process_is_live(child_pid) && Instant::now() < deadline {
            std::thread::sleep(Duration::from_millis(10));
        }
        assert!(!linux_process_is_live(child_pid));
        fs::remove_dir_all(root).unwrap();
    }

    #[cfg(target_os = "linux")]
    fn linux_process_is_live(process_id: i32) -> bool {
        let Ok(stat) = fs::read_to_string(format!("/proc/{process_id}/stat")) else {
            return false;
        };
        stat.rsplit_once(") ")
            .and_then(|(_, fields)| fields.as_bytes().first())
            .is_some_and(|state| *state != b'Z')
    }
}
