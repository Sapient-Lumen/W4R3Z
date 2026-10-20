use std::ffi::{OsStr, OsString};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::net::{SocketAddr, TcpListener as StdTcpListener};
#[cfg(unix)]
use std::os::unix::fs::{DirBuilderExt, MetadataExt, OpenOptionsExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::process::{Command as StdCommand, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

use anyhow::{anyhow, bail, Context, Result};
use tokio::io::{AsyncReadExt, AsyncWriteExt, BufReader};
use tokio::net::TcpStream;
use tokio::process::{Child, Command};
use tokio::time::{sleep, timeout, Instant};
use zeroize::Zeroizing;

use crate::identity::{DerivedClientRecoveryIdentity, DerivedServerRecoveryIdentity, HostRecord};
use crate::runtime::{
    configure_owned_child, configure_owned_std_child, remove_identity_environment,
    remove_identity_environment_std, AppConfig,
};

static SESSION_COUNTER: AtomicU64 = AtomicU64::new(1);

#[derive(Clone, Copy)]
pub(crate) struct SshServerPrograms<'a> {
    pub dropbear: &'a Path,
    pub sftp_server: &'a Path,
    pub scp: &'a Path,
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct SshInvocation {
    options: Vec<OsString>,
    remote_command: Vec<OsString>,
}

impl SshInvocation {
    pub fn parse(arguments: &[OsString]) -> Result<Self> {
        Self::parse_with_internal_forwarding(arguments, false)
    }

    fn parse_with_internal_forwarding(
        arguments: &[OsString],
        allow_internal_forwarding: bool,
    ) -> Result<Self> {
        let mut options = Vec::new();
        let mut index = 0;
        while index < arguments.len() {
            let argument = &arguments[index];
            if argument == OsStr::new("--") {
                index += 1;
                break;
            }
            let Some(argument_text) = argument.to_str() else {
                bail!("SSH options must be valid UTF-8");
            };
            if argument_text == "-" || !argument_text.starts_with('-') {
                break;
            }
            let consumed = validate_ssh_option(arguments, index, allow_internal_forwarding)?;
            options.extend(arguments[index..index + consumed].iter().cloned());
            index += consumed;
        }
        Ok(Self {
            options,
            remote_command: arguments[index..].to_vec(),
        })
    }

    pub fn from_options(options: impl IntoIterator<Item = String>) -> Result<Self> {
        let arguments = options.into_iter().map(OsString::from).collect::<Vec<_>>();
        let invocation = Self::parse_with_internal_forwarding(&arguments, true)?;
        if !invocation.remote_command.is_empty() {
            bail!("SSH option list contains a remote command");
        }
        Ok(invocation)
    }

    pub fn options(&self) -> &[OsString] {
        &self.options
    }

    pub fn remote_command(&self) -> &[OsString] {
        &self.remote_command
    }

    pub fn is_quiet(&self) -> bool {
        self.options.iter().any(|option| option == OsStr::new("-q"))
    }
}

pub struct RecoverySshSession {
    _runtime: PrivateRuntimeDirectory,
    identity_file: PathBuf,
    known_hosts_file: PathBuf,
    host_key_alias: String,
}

impl RecoverySshSession {
    pub fn materialize(
        config: &AppConfig,
        machine_id: &str,
        client_private_key: &Zeroizing<String>,
        host_public_key: &str,
    ) -> Result<Self> {
        validate_component("machine ID", machine_id)?;
        let parent = config.cache_dir.join("ssh-client");
        let runtime = PrivateRuntimeDirectory::create(parent, config.cache_dir.clone())?;
        let identity_file = runtime.root.join("id_ed25519");
        let known_hosts_file = runtime.root.join("known_hosts");
        let session = Self {
            _runtime: runtime,
            identity_file,
            known_hosts_file,
            host_key_alias: machine_id.to_owned(),
        };
        private_file(&session.identity_file, client_private_key.as_bytes())?;
        private_file(
            &session.known_hosts_file,
            format!("{machine_id} {host_public_key}\n").as_bytes(),
        )?;
        Ok(session)
    }

    pub fn materialize_bond_key(&self, key: &[u8; 32]) -> Result<PathBuf> {
        let path = self._runtime.root.join("bond-session.key");
        private_file(&path, key)?;
        Ok(path)
    }
}

pub fn build_recovery_command(
    record: &HostRecord,
    proxy_command: &str,
    invocation: &SshInvocation,
    session: &RecoverySshSession,
    connect_timeout_secs: u64,
    ssh_binary: &Path,
) -> Result<StdCommand> {
    build_recovery_command_for_mode(
        record,
        RecoveryRoute::Proxy(proxy_command),
        invocation,
        session,
        connect_timeout_secs,
        ssh_binary,
        RecoverySshMode::Interactive,
    )
}

pub(crate) fn build_recovery_control_master_command(
    record: &HostRecord,
    proxy_command: &str,
    invocation: &SshInvocation,
    session: &RecoverySshSession,
    connect_timeout_secs: u64,
    ssh_binary: &Path,
    control_path: &Path,
) -> Result<StdCommand> {
    if !control_path.is_absolute() {
        bail!("SSH control path must be absolute");
    }
    if !invocation.remote_command().is_empty() {
        bail!("SSH control master cannot execute a remote command");
    }
    build_recovery_command_for_mode(
        record,
        RecoveryRoute::Proxy(proxy_command),
        invocation,
        session,
        connect_timeout_secs,
        ssh_binary,
        RecoverySshMode::ControlMaster(control_path),
    )
}

#[derive(Clone, Copy)]
enum RecoverySshMode<'a> {
    Interactive,
    ControlMaster(&'a Path),
}

#[derive(Clone, Copy)]
enum RecoveryRoute<'a> {
    Proxy(&'a str),
    Direct(SocketAddr),
}

fn build_recovery_command_for_mode(
    record: &HostRecord,
    route: RecoveryRoute<'_>,
    invocation: &SshInvocation,
    session: &RecoverySshSession,
    connect_timeout_secs: u64,
    ssh_binary: &Path,
    mode: RecoverySshMode<'_>,
) -> Result<StdCommand> {
    validate_component("machine ID", &record.name)?;
    validate_component("SSH user", &record.user)?;
    if !(10..=3_600).contains(&connect_timeout_secs) {
        bail!("SSH connect timeout must be between 10 and 3600 seconds");
    }
    if matches!(route, RecoveryRoute::Proxy(proxy) if proxy.contains(['\r', '\n'])) {
        bail!("ProxyCommand contains a newline");
    }

    let mut command = StdCommand::new(ssh_binary);
    command
        .arg("-F")
        .arg("/dev/null")
        .arg("-p")
        .arg(record.port.to_string());
    match route {
        RecoveryRoute::Proxy(proxy) => {
            command.arg("-o").arg(format!("ProxyCommand={proxy}"));
        }
        RecoveryRoute::Direct(endpoint) => {
            command.arg("-o").arg(format!("Hostname={}", endpoint.ip()));
        }
    }
    for option in [
        "BatchMode=yes".to_owned(),
        "StrictHostKeyChecking=yes".to_owned(),
        format!("HostKeyAlias={}", session.host_key_alias),
        format!("UserKnownHostsFile={}", session.known_hosts_file.display()),
        "GlobalKnownHostsFile=/dev/null".to_owned(),
        "HostKeyAlgorithms=ssh-ed25519".to_owned(),
        format!("IdentityFile={}", session.identity_file.display()),
        "IdentityAgent=none".to_owned(),
        "IdentitiesOnly=yes".to_owned(),
        "PreferredAuthentications=publickey".to_owned(),
        "PubkeyAuthentication=yes".to_owned(),
        "PasswordAuthentication=no".to_owned(),
        "KbdInteractiveAuthentication=no".to_owned(),
        "ChallengeResponseAuthentication=no".to_owned(),
        "NumberOfPasswordPrompts=0".to_owned(),
        "UpdateHostKeys=no".to_owned(),
        "VerifyHostKeyDNS=no".to_owned(),
        "CheckHostIP=no".to_owned(),
        "CanonicalizeHostname=no".to_owned(),
        "Compression=no".to_owned(),
        "LogLevel=INFO".to_owned(),
        format!("ConnectTimeout={connect_timeout_secs}"),
        "ServerAliveInterval=30".to_owned(),
        "ServerAliveCountMax=3".to_owned(),
    ] {
        command.arg("-o").arg(option);
    }
    match mode {
        RecoverySshMode::Interactive => {
            command
                .arg("-o")
                .arg("ControlMaster=no")
                .arg("-o")
                .arg("ControlPath=none");
        }
        RecoverySshMode::ControlMaster(control_path) => {
            command
                .arg("-N")
                .arg("-o")
                .arg("ControlMaster=yes")
                .arg("-o")
                .arg(format!("ControlPath={}", control_path.display()))
                .arg("-o")
                .arg("ControlPersist=no");
        }
    }
    command.args(invocation.options());
    command.arg(format!("{}@{}", record.user.as_str(), record.name.as_str()));
    command.args(invocation.remote_command());
    command.env_remove("SSH_AUTH_SOCK");
    remove_identity_environment_std(&mut command);
    configure_owned_std_child(&mut command);
    Ok(command)
}

pub(crate) async fn embedded_runtime_login(
    config: &AppConfig,
    machine_id: &str,
    username: &str,
    client_identity: &DerivedClientRecoveryIdentity,
    server_identity: &DerivedServerRecoveryIdentity,
    ssh_binary: &Path,
    server_programs: SshServerPrograms<'_>,
) -> Result<()> {
    validate_component("SSH user", username)?;
    let reservation = StdTcpListener::bind("127.0.0.1:0")?;
    let endpoint = reservation.local_addr()?;
    drop(reservation);

    let mut backend = SshBackend::start(
        config,
        machine_id,
        server_identity,
        server_programs,
        endpoint,
    )
    .await?;
    let session = RecoverySshSession::materialize(
        config,
        machine_id,
        &client_identity.ssh_client.private_key,
        &client_identity.ssh_host_public_key,
    )?;
    let record = HostRecord {
        name: Zeroizing::new(machine_id.to_owned()),
        user: Zeroizing::new(username.to_owned()),
        port: endpoint.port(),
    };
    let mut command = build_recovery_command_for_mode(
        &record,
        RecoveryRoute::Direct(endpoint),
        &SshInvocation::default(),
        &session,
        15,
        ssh_binary,
        RecoverySshMode::Interactive,
    )?;
    command
        .arg("printf 'anonssh-embedded-ssh-ok\\n'")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut command = Command::from(command);
    let operation = timeout(Duration::from_secs(20), command.output())
        .await
        .context("embedded SSH login timed out")?
        .context("failed to run embedded OpenSSH")
        .and_then(|output| {
            if !output.status.success() {
                bail!(
                    "embedded OpenSSH login failed with {}: {}",
                    output.status,
                    String::from_utf8_lossy(&output.stderr).trim()
                );
            }
            if output.stdout != b"anonssh-embedded-ssh-ok\n" {
                bail!("embedded OpenSSH login returned an unexpected response");
            }
            Ok(())
        });
    let operation = match operation {
        Ok(()) => {
            embedded_runtime_sftp(
                &record,
                &session,
                ssh_binary,
                server_programs.sftp_server,
                server_programs.scp,
            )
            .await
        }
        Err(error) => Err(error),
    };
    let shutdown = backend.shutdown().await;
    operation.and(shutdown)
}

async fn embedded_runtime_sftp(
    record: &HostRecord,
    session: &RecoverySshSession,
    ssh_binary: &Path,
    sftp_server_binary: &Path,
    scp_binary: &Path,
) -> Result<()> {
    let invocation = SshInvocation::parse(&[OsString::from("-s"), OsString::from("sftp")])?;
    let mut command = build_recovery_command_for_mode(
        record,
        RecoveryRoute::Direct(SocketAddr::from(([127, 0, 0, 1], record.port))),
        &invocation,
        session,
        15,
        ssh_binary,
        RecoverySshMode::Interactive,
    )?;
    command
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = Command::from(command)
        .spawn()
        .context("failed to run embedded SFTP subsystem")?;
    let mut stdin = child
        .stdin
        .take()
        .context("embedded SFTP stdin is unavailable")?;
    let mut stdout = child
        .stdout
        .take()
        .context("embedded SFTP stdout is unavailable")?;
    let mut stderr = child
        .stderr
        .take()
        .context("embedded SFTP stderr is unavailable")?;
    let stderr_reader = tokio::spawn(async move {
        let mut bytes = Vec::new();
        stderr.read_to_end(&mut bytes).await.map(|_| bytes)
    });
    stdin
        .write_all(&[0, 0, 0, 5, 1, 0, 0, 0, 3])
        .await
        .context("failed to send embedded SFTP initialization")?;
    stdin
        .flush()
        .await
        .context("failed to flush embedded SFTP initialization")?;
    let response = timeout(Duration::from_secs(20), async {
        let mut length = [0_u8; 4];
        stdout.read_exact(&mut length).await?;
        let length = usize::try_from(u32::from_be_bytes(length))?;
        if !(5..=64 * 1024).contains(&length) {
            bail!("embedded SFTP response length {length} is outside protocol bounds");
        }
        let mut payload = vec![0_u8; length];
        stdout.read_exact(&mut payload).await?;
        Ok::<_, anyhow::Error>(payload)
    })
    .await
    .context("embedded SFTP subsystem timed out");
    drop(stdin);
    if response.is_err() || response.as_ref().is_ok_and(Result::is_err) {
        let _ = child.start_kill();
    }
    let status = timeout(Duration::from_secs(5), child.wait())
        .await
        .context("embedded SFTP subsystem did not stop")??;
    let stderr = stderr_reader
        .await
        .context("embedded SFTP stderr reader failed")??;
    if !status.success() {
        bail!(
            "embedded SFTP subsystem failed with {}: {}",
            status,
            String::from_utf8_lossy(&stderr).trim()
        );
    }
    let response = response??;
    if response[0] != 2 || response[1..5] != [0, 0, 0, 3] {
        bail!(
            "embedded SFTP subsystem returned an invalid version packet ({} bytes, prefix {:02x?}): {}",
            response.len(),
            &response[..response.len().min(16)],
            String::from_utf8_lossy(&stderr).trim(),
        );
    }

    let invocation = SshInvocation::parse(&[OsString::from("scp"), OsString::from("-V")])?;
    let mut command = build_recovery_command_for_mode(
        record,
        RecoveryRoute::Direct(SocketAddr::from(([127, 0, 0, 1], record.port))),
        &invocation,
        session,
        15,
        ssh_binary,
        RecoverySshMode::Interactive,
    )?;
    command
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let output = timeout(Duration::from_secs(20), Command::from(command).output())
        .await
        .context("embedded legacy scp helper lookup timed out")??;
    let stderr = String::from_utf8_lossy(&output.stderr);
    let expected_prefix = format!("{}:", scp_binary.display());
    if output.status.success() || !output.stdout.is_empty() || !stderr.starts_with(&expected_prefix)
    {
        bail!(
            "embedded legacy scp helper was not selected (status {}, stdout {:?}): {}",
            output.status,
            String::from_utf8_lossy(&output.stdout).trim(),
            stderr.trim(),
        );
    }
    if !sftp_server_binary.is_absolute() || !scp_binary.is_absolute() {
        bail!("embedded SSH helpers must have absolute paths");
    }
    Ok(())
}

pub struct SshBackend {
    child: Child,
    _material: ServerMaterial,
    _runtime: PrivateRuntimeDirectory,
}

impl SshBackend {
    pub async fn start(
        config: &AppConfig,
        machine_id: &str,
        identity: &DerivedServerRecoveryIdentity,
        programs: SshServerPrograms<'_>,
        endpoint: SocketAddr,
    ) -> Result<Self> {
        validate_component("machine ID", machine_id)?;
        if !endpoint.ip().is_loopback() || endpoint.port() == 0 {
            bail!("SSH backend must be a non-zero loopback socket");
        }
        if timeout(Duration::from_millis(300), TcpStream::connect(endpoint))
            .await
            .is_ok_and(|result| result.is_ok())
        {
            bail!("SSH backend endpoint {endpoint} is already occupied");
        }
        if !programs.sftp_server.is_absolute() || !programs.scp.is_absolute() {
            bail!("SSH server helpers must use absolute paths");
        }
        let material = ServerMaterial::create(config, machine_id, identity)?;
        let runtime_parent = config.cache_dir.join("ssh-server");
        let runtime = PrivateRuntimeDirectory::create(runtime_parent, config.cache_dir.clone())?;
        let pid_file = runtime.root.join("dropbear.pid");

        let mut command = Command::new(programs.dropbear);
        command
            .arg("-F")
            .arg("-E")
            .arg("-s")
            .arg("-P")
            .arg(&pid_file)
            .arg("-p")
            .arg(endpoint.to_string())
            .arg("-r")
            .arg(&material.host_key)
            .arg("-D")
            .arg(&material.authorized_keys_argument)
            .env("ANONSSH_SFTP_SERVER", programs.sftp_server)
            .env("ANONSSH_SCP_SERVER", programs.scp)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::inherit());
        remove_identity_environment(&mut command);
        configure_owned_child(&mut command);
        let mut child = command.spawn().context("failed to start Dropbear")?;
        let deadline = Instant::now() + Duration::from_secs(15);
        loop {
            if let Some(status) = child.try_wait()? {
                bail!("Dropbear exited before becoming ready: {status}");
            }
            if ssh_banner_ready(endpoint).await {
                return Ok(Self {
                    child,
                    _material: material,
                    _runtime: runtime,
                });
            }
            if Instant::now() >= deadline {
                let _ = child.start_kill();
                let _ = child.wait().await;
                bail!("Dropbear did not become ready within 15 seconds");
            }
            sleep(Duration::from_millis(50)).await;
        }
    }

    pub async fn wait_for_exit(&mut self) -> Result<()> {
        let status = self.child.wait().await?;
        bail!("Dropbear exited unexpectedly: {status}")
    }

    pub async fn shutdown(&mut self) -> Result<()> {
        if self.child.try_wait()?.is_none() {
            self.child.start_kill()?;
            timeout(Duration::from_secs(5), self.child.wait())
                .await
                .context("Dropbear did not stop within five seconds")??;
        }
        Ok(())
    }
}

impl Drop for SshBackend {
    fn drop(&mut self) {
        let _ = self.child.start_kill();
    }
}

struct ServerMaterial {
    host_key: PathBuf,
    authorized_keys: PathBuf,
    authorized_keys_dir: PathBuf,
    authorized_keys_root: PathBuf,
    keys_dir: PathBuf,
    cache_dir: PathBuf,
    authorized_keys_argument: String,
}

impl ServerMaterial {
    fn create(
        config: &AppConfig,
        machine_id: &str,
        identity: &DerivedServerRecoveryIdentity,
    ) -> Result<Self> {
        if !config.keys_dir.is_absolute() {
            bail!("SSH recovery material directory must be absolute");
        }
        let authorized_keys_root = config.keys_dir.join("recovery-auth");
        let authorized_keys_dir = authorized_keys_root.join(machine_id);
        let host_key = config
            .keys_dir
            .join(format!("dropbear_ed25519_{machine_id}"));
        let authorized_keys = authorized_keys_dir.join("authorized_keys");
        let authorized_keys_argument = authorized_keys_dir
            .to_str()
            .context("SSH recovery material directory is not UTF-8")?
            .to_owned();
        let material = Self {
            host_key,
            authorized_keys,
            authorized_keys_dir,
            authorized_keys_root,
            keys_dir: config.keys_dir.clone(),
            cache_dir: config.cache_dir.clone(),
            authorized_keys_argument,
        };
        ensure_private_directory(&material.cache_dir, true)?;
        ensure_protected_parent_directory(&config.state_dir, true)?;
        ensure_private_directory(&material.keys_dir, false)?;
        ensure_private_directory(&material.authorized_keys_root, false)?;
        ensure_private_directory(&material.authorized_keys_dir, false)?;
        private_file(&material.host_key, &identity.ssh_host.dropbear_private_key)?;
        private_file(
            &material.authorized_keys,
            format!("{} anonssh-recovery\n", identity.ssh_client_public_key).as_bytes(),
        )?;
        Ok(material)
    }
}

impl Drop for ServerMaterial {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.host_key);
        let _ = fs::remove_file(&self.authorized_keys);
        let _ = fs::remove_dir(&self.authorized_keys_dir);
        let _ = fs::remove_dir(&self.authorized_keys_root);
        let _ = fs::remove_dir(&self.keys_dir);
        let _ = fs::remove_dir(&self.cache_dir);
    }
}

struct PrivateRuntimeDirectory {
    root: PathBuf,
    parent: PathBuf,
    cache_dir: PathBuf,
}

impl PrivateRuntimeDirectory {
    fn create(parent: PathBuf, cache_dir: PathBuf) -> Result<Self> {
        let root = (|| {
            ensure_private_directory(&cache_dir, true)?;
            ensure_private_directory(&parent, false)?;
            create_private_runtime_dir(&parent)
        })();
        let root = match root {
            Ok(root) => root,
            Err(error) => {
                let _ = fs::remove_dir(&parent);
                let _ = fs::remove_dir(&cache_dir);
                return Err(error);
            }
        };
        Ok(Self {
            root,
            parent,
            cache_dir,
        })
    }
}

impl Drop for PrivateRuntimeDirectory {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
        let _ = fs::remove_dir(&self.parent);
        let _ = fs::remove_dir(&self.cache_dir);
    }
}

async fn ssh_banner_ready(endpoint: SocketAddr) -> bool {
    let operation = async {
        let stream = TcpStream::connect(endpoint).await?;
        let mut reader = BufReader::new(stream);
        let mut collected = Vec::new();
        while collected.len() < 1_024 {
            let byte = reader.read_u8().await?;
            collected.push(byte);
            if byte == b'\n' && collected.starts_with(b"SSH-2.0-") {
                return Ok::<bool, std::io::Error>(true);
            }
        }
        Ok(false)
    };
    matches!(
        timeout(Duration::from_millis(500), operation).await,
        Ok(Ok(true))
    )
}

fn create_private_runtime_dir(parent: &Path) -> Result<PathBuf> {
    for _ in 0..32 {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let candidate = parent.join(format!("{}-{sequence}", std::process::id()));
        let mut builder = fs::DirBuilder::new();
        builder.mode(0o700);
        match builder.create(&candidate) {
            Ok(()) => {
                if let Err(error) = validate_private_directory(&candidate) {
                    let _ = fs::remove_dir(&candidate);
                    return Err(error);
                }
                return Ok(candidate);
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error.into()),
        }
    }
    Err(anyhow!("failed to allocate a private runtime directory"))
}

fn ensure_private_directory(path: &Path, recursive: bool) -> Result<()> {
    ensure_directory(path, recursive)?;
    validate_private_directory(path)
}

fn ensure_protected_parent_directory(path: &Path, recursive: bool) -> Result<()> {
    ensure_directory(path, recursive)?;
    let metadata = validate_owned_directory(path)?;
    if metadata.permissions().mode() & 0o022 != 0 {
        bail!("SSH state parent is writable by another user");
    }
    Ok(())
}

fn ensure_directory(path: &Path, recursive: bool) -> Result<()> {
    let mut builder = fs::DirBuilder::new();
    builder.mode(0o700).recursive(recursive);
    match builder.create(path) {
        Ok(()) => {}
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
        Err(error) => return Err(error.into()),
    }
    Ok(())
}

fn validate_private_directory(path: &Path) -> Result<()> {
    let metadata = validate_owned_directory(path)?;
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("SSH runtime directory is accessible by another user");
    }
    Ok(())
}

fn validate_owned_directory(path: &Path) -> Result<fs::Metadata> {
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.file_type().is_dir() {
        bail!("SSH runtime path is not a real directory");
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("SSH runtime directory is not owned by the current user");
    }
    Ok(metadata)
}

fn private_file(path: &Path, contents: &[u8]) -> Result<()> {
    let mut options = OpenOptions::new();
    options
        .create(true)
        .write(true)
        .custom_flags(libc::O_CLOEXEC | libc::O_NOFOLLOW);
    #[cfg(unix)]
    options.mode(0o600);
    let mut file = options.open(path)?;
    let metadata = file.metadata()?;
    if !metadata.file_type().is_file() {
        bail!("SSH private material path is not a regular file");
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("SSH private material is not owned by the current user");
    }
    if metadata.nlink() != 1 {
        bail!("SSH private material must not have multiple filesystem links");
    }
    file.set_permissions(fs::Permissions::from_mode(0o600))?;
    file.set_len(0)?;
    file.write_all(contents)?;
    file.sync_all()?;
    Ok(())
}

fn validate_component(label: &str, value: &str) -> Result<()> {
    let valid = !value.is_empty()
        && value.len() <= 253
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-' | b'_'))
        && value
            .as_bytes()
            .first()
            .is_some_and(u8::is_ascii_alphanumeric);
    if !valid {
        bail!("invalid {label}");
    }
    Ok(())
}

fn validate_ssh_option(
    options: &[OsString],
    index: usize,
    allow_internal_forwarding: bool,
) -> Result<usize> {
    const PROTECTED_FLAGS: &[&str] = &["-F", "-I", "-J", "-M", "-O", "-S", "-i", "-l", "-p"];
    const PROTECTED_OPTIONS: &[&str] = &[
        "batchmode",
        "canonicalizehostname",
        "certificatefile",
        "checkhostip",
        "clearallforwardings",
        "controlmaster",
        "controlpath",
        "controlpersist",
        "connecttimeout",
        "dynamicforward",
        "forkafterauthentication",
        "gatewayports",
        "globalknownhostsfile",
        "hostkeyalgorithms",
        "hostkeyalias",
        "hostname",
        "identitiesonly",
        "identityagent",
        "identityfile",
        "include",
        "kbdinteractiveauthentication",
        "knownhostscommand",
        "localcommand",
        "numberofpasswordprompts",
        "passwordauthentication",
        "port",
        "preferredauthentications",
        "proxycommand",
        "proxyjump",
        "proxyusefdpass",
        "permitlocalcommand",
        "pubkeyauthentication",
        "remotecommand",
        "remoteforward",
        "serveralivecountmax",
        "serveraliveinterval",
        "stricthostkeychecking",
        "streamlocalbindmask",
        "streamlocalbindunlink",
        "stdioforwarding",
        "tunnel",
        "tunneldevice",
        "updatehostkeys",
        "user",
        "userknownhostsfile",
        "verifyhostkeydns",
    ];
    const SAFE_OPTIONS: &[&str] = &[
        "compression",
        "escapechar",
        "exitonforwardfailure",
        "forwardagent",
        "forwardx11",
        "forwardx11trusted",
        "ipqos",
        "loglevel",
        "obscurekeystroketiming",
        "rekeylimit",
        "requesttty",
        "sendenv",
        "sessiontype",
        "stdinnull",
        "tcpkeepalive",
        "visualhostkey",
    ];
    let argument = options[index]
        .to_str()
        .context("SSH options must be valid UTF-8")?;
    if PROTECTED_FLAGS
        .iter()
        .any(|flag| argument == *flag || argument.starts_with(flag))
    {
        bail!("SSH option {argument} would override recovery policy");
    }
    let (option, consumed) = if argument == "-o" {
        let option = options
            .get(index + 1)
            .context("-o requires a value")?
            .to_str()
            .context("SSH options must be valid UTF-8")?;
        (Some(option), 2)
    } else if let Some(option) = argument.strip_prefix("-o") {
        if option.is_empty() {
            bail!("-o requires a value");
        }
        (Some(option), 1)
    } else if matches!(
        argument,
        "-2" | "-4"
            | "-6"
            | "-a"
            | "-N"
            | "-n"
            | "-q"
            | "-s"
            | "-T"
            | "-t"
            | "-tt"
            | "-v"
            | "-vv"
            | "-vvv"
            | "-x"
            | "-y"
    ) {
        (None, 1)
    } else {
        bail!("unsupported SSH option {argument}");
    };
    if let Some(option) = option {
        if option.contains(['\0', '\r', '\n']) {
            bail!("SSH option contains a forbidden control character");
        }
        let (keyword, value) = ssh_option_keyword_and_value(option);
        if PROTECTED_OPTIONS.contains(&keyword.as_str()) {
            if safe_tool_control_option(&keyword, value) {
                return Ok(consumed);
            }
            bail!("SSH option {keyword} is controlled by recovery policy");
        }
        if keyword == "localforward" && allow_internal_forwarding {
            return Ok(consumed);
        }
        if !SAFE_OPTIONS.contains(&keyword.as_str()) {
            bail!("unsupported SSH option {keyword}");
        }
    }
    Ok(consumed)
}

fn ssh_option_keyword_and_value(option: &str) -> (String, &str) {
    let split = option
        .find(|character: char| character == '=' || character.is_ascii_whitespace())
        .unwrap_or(option.len());
    let keyword = option[..split].to_ascii_lowercase();
    let value = option[split..]
        .trim_start_matches(|character: char| character == '=' || character.is_ascii_whitespace())
        .trim();
    (keyword, value)
}

fn safe_tool_control_option(keyword: &str, value: &str) -> bool {
    matches!(
        (keyword, value.to_ascii_lowercase().as_str()),
        ("batchmode", "yes")
            | ("clearallforwardings", "yes")
            | ("controlmaster", "no")
            | ("permitlocalcommand", "no")
            | ("remotecommand", "none")
    )
}

#[cfg(test)]
mod tests {
    use std::ffi::OsString;
    use std::fs;
    #[cfg(unix)]
    use std::os::unix::fs::PermissionsExt;
    use std::path::Path;
    use std::sync::atomic::Ordering;

    use zeroize::Zeroizing;

    use super::{
        build_recovery_command, build_recovery_control_master_command,
        ensure_protected_parent_directory, private_file, PrivateRuntimeDirectory,
        RecoverySshSession, ServerMaterial, SshInvocation, SESSION_COUNTER,
    };
    use crate::identity::{HostRecord, IdentityManager};
    use crate::runtime::AppConfig;

    #[test]
    fn recovery_route_and_identity_cannot_be_overridden() {
        let parse = |arguments: &[&str]| {
            SshInvocation::parse(&arguments.iter().map(OsString::from).collect::<Vec<_>>())
        };
        assert!(parse(&["-v"]).is_ok());
        assert!(parse(&["-i", "/tmp/key"]).is_err());
        assert!(parse(&["-oProxyCommand=evil"]).is_err());
        assert!(parse(&["-oPermitLocalCommand=yes"]).is_err());
        assert!(parse(&["-oLocalCommand=evil"]).is_err());
        assert!(parse(&["-oRemoteCommand=evil"]).is_err());
        assert!(parse(&["-oDynamicForward=1080"]).is_err());
        assert!(parse(&["-oLocalForward=127.0.0.1:8022 localhost:22"]).is_err());
        assert!(parse(&["-oUnreviewedFutureOption=yes"]).is_err());
        assert!(parse(&["-oRequestTTY=yes\nProxyCommand=evil"]).is_err());
        assert!(parse(&["-oRequestTTY=yes\rProxyCommand=evil"]).is_err());
        assert!(parse(&["-oRequestTTY=force"]).is_ok());
        for option in [
            "BatchMode=yes",
            "ClearAllForwardings=yes",
            "ControlMaster=no",
            "PermitLocalCommand=no",
            "RemoteCommand=none",
        ] {
            assert!(parse(&["-o", option]).is_ok(), "rejected {option}");
        }
        for option in [
            "BatchMode=no",
            "ClearAllForwardings=no",
            "ControlMaster=yes",
            "PermitLocalCommand=yes",
            "RemoteCommand=touch /tmp/owned",
        ] {
            assert!(parse(&["-o", option]).is_err(), "accepted {option}");
        }
        assert!(parse(&[
            "-oForwardX11 no",
            "-oPermitLocalCommand no",
            "-oClearAllForwardings yes",
            "-oControlMaster no",
            "-s",
            "sftp",
        ])
        .is_ok());
        assert!(parse(&[
            "-2",
            "-a",
            "-x",
            "-oPermitLocalCommand=no",
            "-oClearAllForwardings=yes",
            "-oRemoteCommand=none",
            "-oRequestTTY=no",
            "-oControlMaster=no",
            "-s",
            "sftp",
        ])
        .is_ok());
        assert!(parse(&["-o"]).is_err());
        let command = parse(&["remote-command", "--argument"]).unwrap();
        assert_eq!(
            command.remote_command(),
            [
                OsString::from("remote-command"),
                OsString::from("--argument")
            ]
        );
        assert!(SshInvocation::from_options([
            "-N".to_owned(),
            "-o".to_owned(),
            "ExitOnForwardFailure=yes".to_owned(),
            "-o".to_owned(),
            "LocalForward=127.0.0.1:8022 localhost:22".to_owned(),
        ])
        .is_ok());
    }

    #[test]
    fn private_material_rejects_symbolic_and_hard_links_without_clobbering() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-private-file-test-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir(&root).unwrap();
        let victim = root.join("victim");
        let symbolic = root.join("symbolic");
        let hard = root.join("hard");
        fs::write(&victim, b"do not replace").unwrap();
        std::os::unix::fs::symlink(&victim, &symbolic).unwrap();
        fs::hard_link(&victim, &hard).unwrap();

        assert!(private_file(&symbolic, b"secret").is_err());
        assert!(private_file(&hard, b"secret").is_err());
        assert_eq!(fs::read(&victim).unwrap(), b"do not replace");

        fs::remove_file(symbolic).unwrap();
        fs::remove_file(hard).unwrap();
        fs::remove_file(victim).unwrap();
        fs::remove_dir(root).unwrap();
    }

    #[test]
    fn private_runtime_rejects_a_symbolic_directory() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-runtime-link-test-{}-{sequence}",
            std::process::id()
        ));
        let cache = root.join("cache");
        let target = root.join("target");
        fs::create_dir(&root).unwrap();
        fs::create_dir(&cache).unwrap();
        fs::set_permissions(&cache, fs::Permissions::from_mode(0o700)).unwrap();
        fs::create_dir(&target).unwrap();
        fs::set_permissions(&target, fs::Permissions::from_mode(0o700)).unwrap();
        let parent = cache.join("ssh-client");
        std::os::unix::fs::symlink(&target, &parent).unwrap();

        assert!(PrivateRuntimeDirectory::create(parent.clone(), cache.clone()).is_err());

        fs::remove_file(parent).unwrap();
        fs::remove_dir(cache).unwrap();
        fs::remove_dir(target).unwrap();
        fs::remove_dir(root).unwrap();
    }

    #[test]
    fn protected_state_parent_accepts_readable_but_not_writable_access() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-state-parent-test-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir(&root).unwrap();
        fs::set_permissions(&root, fs::Permissions::from_mode(0o755)).unwrap();
        ensure_protected_parent_directory(&root, false).unwrap();
        fs::set_permissions(&root, fs::Permissions::from_mode(0o775)).unwrap();
        assert!(ensure_protected_parent_directory(&root, false).is_err());
        fs::remove_dir(root).unwrap();
    }

    #[test]
    fn server_authorization_material_stays_inside_configured_state() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-server-material-test-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir(&root).unwrap();
        let config = AppConfig::temporary(&root);
        let identity = IdentityManager::derive_server_recovery_identity(
            &Zeroizing::new("test-password".to_owned()),
            "home",
        )
        .unwrap();
        let material = ServerMaterial::create(&config, "home", &identity).unwrap();
        assert_eq!(
            material.authorized_keys_root,
            config.keys_dir.join("recovery-auth")
        );
        assert!(material.authorized_keys.starts_with(&config.state_dir));
        assert!(!material.authorized_keys.starts_with(&config.cache_dir));
        assert!(material.authorized_keys.starts_with(&root));
        assert_eq!(
            material.authorized_keys_argument,
            material.authorized_keys_dir.to_string_lossy()
        );
        assert_eq!(
            fs::metadata(&config.cache_dir)
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o700
        );
        drop(material);
        assert!(!config.keys_dir.exists());
        fs::remove_dir(&config.state_dir).unwrap();
        fs::remove_dir(&root).unwrap();
    }

    #[test]
    fn internal_control_master_preserves_recovery_policy() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-control-test-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir(&root).unwrap();
        let config = AppConfig::temporary(&root);
        let session = RecoverySshSession::materialize(
            &config,
            "home",
            &Zeroizing::new("private-key\n".to_owned()),
            "ssh-ed25519 public-key",
        )
        .unwrap();
        let record = HostRecord {
            name: Zeroizing::new("home".to_owned()),
            user: Zeroizing::new("alice".to_owned()),
            port: 22,
        };
        let socket = root.join("control.sock");
        let command = build_recovery_control_master_command(
            &record,
            "anonssh bond-proxy",
            &SshInvocation::default(),
            &session,
            120,
            Path::new("/usr/bin/ssh"),
            &socket,
        )
        .unwrap();
        for variable in [
            "ANONSSH_PASSPHRASE",
            "ANONSSH_PASSPHRASE_FILE",
            "SSH_AUTH_SOCK",
        ] {
            assert!(command
                .get_envs()
                .any(|(name, value)| name == variable && value.is_none()));
        }
        let arguments = command
            .get_args()
            .map(|argument| argument.to_string_lossy().into_owned())
            .collect::<Vec<_>>();

        assert!(arguments
            .windows(2)
            .any(|pair| pair == ["-o", "ControlMaster=yes"]));
        assert!(arguments
            .windows(2)
            .any(|pair| pair == ["-o", "ControlPersist=no"]));
        assert!(arguments.contains(&format!("ControlPath={}", socket.display())));
        assert!(arguments.contains(&"IdentitiesOnly=yes".to_owned()));
        assert!(arguments.contains(&"StrictHostKeyChecking=yes".to_owned()));
        assert!(!arguments.contains(&"ControlMaster=no".to_owned()));
        assert!(arguments.contains(&"-N".to_owned()));

        drop(session);
        fs::remove_dir(&root).unwrap();
    }

    #[test]
    fn public_builder_still_disables_multiplexing() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-interactive-test-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir(&root).unwrap();
        let config = AppConfig::temporary(&root);
        let session = RecoverySshSession::materialize(
            &config,
            "home",
            &Zeroizing::new("private-key\n".to_owned()),
            "ssh-ed25519 public-key",
        )
        .unwrap();
        let record = HostRecord {
            name: Zeroizing::new("home".to_owned()),
            user: Zeroizing::new("alice".to_owned()),
            port: 22,
        };
        let invocation = SshInvocation::parse(&[
            OsString::from("-T"),
            OsString::from("printf"),
            OsString::from("%s"),
            OsString::from("value with spaces"),
        ])
        .unwrap();
        let command = build_recovery_command(
            &record,
            "anonssh bond-proxy",
            &invocation,
            &session,
            120,
            Path::new("/usr/bin/ssh"),
        )
        .unwrap();
        let arguments = command
            .get_args()
            .map(|argument| argument.to_string_lossy().into_owned())
            .collect::<Vec<_>>();
        assert!(arguments.contains(&"ControlMaster=no".to_owned()));
        assert!(arguments.contains(&"ControlPath=none".to_owned()));
        let destination = arguments
            .iter()
            .position(|argument| argument == "alice@home")
            .unwrap();
        assert!(arguments[..destination].contains(&"-T".to_owned()));
        assert_eq!(
            &arguments[destination + 1..],
            ["printf", "%s", "value with spaces"]
        );

        drop(session);
        fs::remove_dir(&root).unwrap();
    }

    #[test]
    fn client_material_is_private_and_ephemeral() {
        let sequence = SESSION_COUNTER.fetch_add(1, Ordering::Relaxed);
        let root = std::env::temp_dir().join(format!(
            "anonssh-ssh-test-{}-{sequence}",
            std::process::id()
        ));
        fs::create_dir(&root).unwrap();
        let config = AppConfig::temporary(&root);
        let session = RecoverySshSession::materialize(
            &config,
            "home",
            &Zeroizing::new("private-key\n".to_owned()),
            "ssh-ed25519 public-key",
        )
        .unwrap();

        assert_eq!(fs::read(&session.identity_file).unwrap(), b"private-key\n");
        assert_eq!(
            fs::read(&session.known_hosts_file).unwrap(),
            b"home ssh-ed25519 public-key\n"
        );
        #[cfg(unix)]
        {
            assert_eq!(
                fs::metadata(&session.identity_file)
                    .unwrap()
                    .permissions()
                    .mode()
                    & 0o777,
                0o600
            );
            assert_eq!(
                fs::metadata(&session.known_hosts_file)
                    .unwrap()
                    .permissions()
                    .mode()
                    & 0o777,
                0o600
            );
        }

        drop(session);
        assert!(!config.cache_dir.exists());
        fs::remove_dir(&root).unwrap();
    }
}
