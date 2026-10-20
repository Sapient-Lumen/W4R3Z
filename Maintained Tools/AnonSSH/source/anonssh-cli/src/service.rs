use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::net::SocketAddr;
use std::os::unix::fs::{DirBuilderExt, MetadataExt, OpenOptionsExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicU64, Ordering};

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};

use crate::bond_broker::{self, BrokerStatus};
use crate::product_config::{
    ExternalTorService, ResidentServicePolicy, ResourceProfile, TransportProfile,
};
use crate::runtime::chmod;

const MANIFEST_SCHEMA: &str = "anonssh.service-install.v1";
const STATUS_SCHEMA: &str = "anonssh.service-status.v1";
const REPORT_SCHEMA: &str = "anonssh.service-action.v1";
const MANIFEST_VERSION: u32 = 1;
const MAX_STATE_BYTES: u64 = 64 * 1024;
const MAX_PASSPHRASE_BYTES: u64 = 64 * 1024;
const BROKER_UNIT: &str = "anonssh-broker.service";
const SERVER_UNIT: &str = "anonssh-server.service";
const SYSTEMCTL_ENV: &str = "ANONSSH_SYSTEMCTL_BIN";
const SERVICE_EXECUTABLE_ENV: &str = "ANONSSH_SERVICE_EXECUTABLE";

static NEXT_TEMPORARY_FILE: AtomicU64 = AtomicU64::new(1);

#[derive(Clone, Debug)]
pub struct InstallOptions {
    pub executable: PathBuf,
    pub machine_id: String,
    pub server_transport: String,
    pub backend: SocketAddr,
    pub resource_profile: ResourceProfile,
    pub transport_profile: TransportProfile,
    pub external_tor_services: Vec<ExternalTorService>,
    pub resident_service: ResidentServicePolicy,
    pub credential_file: Option<PathBuf>,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
enum CredentialSource {
    RuntimeUnlock,
    File { path: PathBuf },
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
struct ServiceManifest {
    schema: String,
    version: u32,
    package_version: String,
    executable: PathBuf,
    machine_id: String,
    server_transport: String,
    backend: SocketAddr,
    resource_profile: ResourceProfile,
    transport_profile: TransportProfile,
    credential: CredentialSource,
}

#[derive(Serialize)]
struct FrozenProductConfig {
    version: u32,
    resource_profile: ResourceProfile,
    transport_profile: TransportProfile,
    external_tor_services: Vec<ExternalTorService>,
    resident_service: ResidentServicePolicy,
}

#[derive(Clone, Debug, Serialize)]
pub struct ActionReport {
    pub schema: &'static str,
    pub action: &'static str,
    pub changed: bool,
    pub credential_state: &'static str,
}

#[derive(Clone, Debug, Serialize)]
pub struct InstallReport {
    pub schema: &'static str,
    pub action: &'static str,
    pub changed: bool,
    pub manifest: PathBuf,
    pub units: [PathBuf; 2],
    pub credential_policy: &'static str,
    pub restart_required: bool,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct UnitStatus {
    pub load_state: String,
    pub unit_file_state: String,
    pub active_state: String,
    pub sub_state: String,
    pub main_pid: Option<u32>,
    pub exit_status: Option<i32>,
    pub error: Option<String>,
}

impl UnitStatus {
    fn unavailable(error: anyhow::Error) -> Self {
        Self {
            load_state: "unknown".to_owned(),
            unit_file_state: "unknown".to_owned(),
            active_state: "unknown".to_owned(),
            sub_state: "unknown".to_owned(),
            main_pid: None,
            exit_status: None,
            error: Some(format!("{error:#}")),
        }
    }
}

#[derive(Clone, Debug, Serialize)]
pub struct ServiceStatus {
    pub schema: &'static str,
    pub installed: bool,
    pub package_version: Option<String>,
    pub machine_id: Option<String>,
    pub server_transport: Option<String>,
    pub backend: Option<SocketAddr>,
    pub credential_policy: &'static str,
    pub credential_state: &'static str,
    pub credential_error: Option<String>,
    pub server: UnitStatus,
    pub broker: UnitStatus,
    pub broker_runtime: BrokerStatus,
    pub runtime_dependencies_ready: bool,
    pub topology_valid: bool,
}

#[derive(Clone, Debug)]
struct ServicePaths {
    service_directory: PathBuf,
    manifest: PathBuf,
    product_config: PathBuf,
    unit_directory: PathBuf,
    broker_unit: PathBuf,
    server_unit: PathBuf,
    runtime_directory: PathBuf,
    runtime_credential: PathBuf,
}

impl ServicePaths {
    fn for_user() -> Result<Self> {
        let config =
            dirs::config_dir().context("cannot resolve the user configuration directory")?;
        let runtime = dirs::runtime_dir()
            .or_else(|| dirs::cache_dir().map(|path| path.join("anonssh-runtime")))
            .context("cannot resolve a private runtime directory for AnonSSH services")?;
        Ok(Self::under(config, runtime))
    }

    fn under(config: PathBuf, runtime: PathBuf) -> Self {
        let service_directory = config.join("anonssh/service");
        let unit_directory = config.join("systemd/user");
        let runtime_directory = runtime.join("anonssh/service");
        Self {
            manifest: service_directory.join("install.json"),
            product_config: service_directory.join("config.json"),
            broker_unit: unit_directory.join(BROKER_UNIT),
            server_unit: unit_directory.join(SERVER_UNIT),
            runtime_credential: runtime_directory.join("identity-password"),
            service_directory,
            unit_directory,
            runtime_directory,
        }
    }
}

trait ServiceController {
    fn run(&self, arguments: &[&str]) -> Result<()>;
    fn inspect(&self, unit: &str) -> Result<UnitStatus>;
}

struct SystemdUserController {
    executable: PathBuf,
}

impl SystemdUserController {
    fn new() -> Self {
        Self {
            executable: std::env::var_os(SYSTEMCTL_ENV)
                .map(PathBuf::from)
                .unwrap_or_else(|| PathBuf::from("systemctl")),
        }
    }

    fn output(&self, arguments: &[&str]) -> Result<Output> {
        Command::new(&self.executable)
            .arg("--user")
            .args(arguments)
            .output()
            .with_context(|| {
                format!(
                    "failed to execute the user service manager {}",
                    self.executable.display()
                )
            })
    }
}

impl ServiceController for SystemdUserController {
    fn run(&self, arguments: &[&str]) -> Result<()> {
        let output = self.output(arguments)?;
        if output.status.success() {
            return Ok(());
        }
        let detail = bounded_command_error(&output);
        bail!(
            "user service manager command {:?} failed with {}: {detail}",
            arguments,
            output.status
        )
    }

    fn inspect(&self, unit: &str) -> Result<UnitStatus> {
        let output = self.output(&[
            "show",
            unit,
            "--property=LoadState",
            "--property=UnitFileState",
            "--property=ActiveState",
            "--property=SubState",
            "--property=MainPID",
            "--property=ExecMainStatus",
            "--no-pager",
        ])?;
        if !output.status.success() {
            let detail = bounded_command_error(&output);
            bail!("cannot inspect {unit}: {detail}")
        }
        parse_unit_status(&output.stdout)
    }
}

pub fn install(options: InstallOptions) -> Result<InstallReport> {
    install_at(
        &ServicePaths::for_user()?,
        &SystemdUserController::new(),
        options,
    )
}

pub fn current_launcher() -> Result<PathBuf> {
    if let Some(path) = std::env::var_os(SERVICE_EXECUTABLE_ENV) {
        return validate_executable(&PathBuf::from(path));
    }
    let executable = std::env::current_exe().context("failed to resolve anonssh executable")?;
    if executable
        .file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.starts_with(".anonssh-wrapped"))
    {
        if let Some(sibling) = executable.parent().map(|parent| parent.join("anonssh")) {
            if sibling.is_file() {
                return validate_executable(&sibling);
            }
        }
    }
    validate_executable(&executable)
}

pub fn installed_config_path() -> Result<Option<PathBuf>> {
    let paths = ServicePaths::for_user()?;
    match read_manifest(&paths)? {
        Some(_) => {
            validate_regular_bounded_file(
                &paths.product_config,
                MAX_STATE_BYTES,
                "service config",
            )?;
            Ok(Some(paths.product_config))
        }
        None => Ok(None),
    }
}

pub fn unlock(passphrase: &str) -> Result<ActionReport> {
    unlock_at(
        &ServicePaths::for_user()?,
        &SystemdUserController::new(),
        passphrase,
    )
}

pub fn start() -> Result<ActionReport> {
    start_at(&ServicePaths::for_user()?, &SystemdUserController::new())
}

pub fn stop() -> Result<ActionReport> {
    stop_at(&ServicePaths::for_user()?, &SystemdUserController::new())
}

pub fn uninstall() -> Result<ActionReport> {
    uninstall_at(&ServicePaths::for_user()?, &SystemdUserController::new())
}

pub async fn status(
    runtime_dependencies_ready: bool,
    topology_valid: bool,
) -> Result<ServiceStatus> {
    status_at(
        &ServicePaths::for_user()?,
        &SystemdUserController::new(),
        runtime_dependencies_ready,
        topology_valid,
    )
    .await
}

fn install_at<C: ServiceController>(
    paths: &ServicePaths,
    controller: &C,
    options: InstallOptions,
) -> Result<InstallReport> {
    validate_machine_id(&options.machine_id)?;
    validate_server_transport(&options.server_transport)?;
    if !options.backend.ip().is_loopback() || options.backend.port() == 0 {
        bail!("service SSH backend must be a non-zero loopback socket")
    }
    let executable = validate_executable(&options.executable)?;
    let credential = match options.credential_file {
        Some(path) => CredentialSource::File {
            path: validate_credential_file(&path)?,
        },
        None => CredentialSource::RuntimeUnlock,
    };
    let manifest = ServiceManifest {
        schema: MANIFEST_SCHEMA.to_owned(),
        version: MANIFEST_VERSION,
        package_version: env!("CARGO_PKG_VERSION").to_owned(),
        executable,
        machine_id: options.machine_id,
        server_transport: options.server_transport,
        backend: options.backend,
        resource_profile: options.resource_profile,
        transport_profile: options.transport_profile,
        credential,
    };

    ensure_owned_directory(&paths.service_directory, 0o700, true)?;
    ensure_owned_directory(&paths.unit_directory, 0o755, false)?;
    let frozen = FrozenProductConfig {
        version: 2,
        resource_profile: manifest.resource_profile,
        transport_profile: manifest.transport_profile,
        external_tor_services: options.external_tor_services,
        resident_service: options.resident_service,
    };
    let config = encoded_json(&frozen)?;
    let manifest_bytes = encoded_json(&manifest)?;
    let broker_unit = broker_unit(&manifest, paths)?;
    let server_unit = server_unit(&manifest, paths)?;

    for path in [
        &paths.product_config,
        &paths.broker_unit,
        &paths.server_unit,
        &paths.manifest,
    ] {
        ensure_regular_or_missing(path)?;
    }
    let mut changed = false;
    changed |= write_atomic_if_changed(&paths.product_config, &config, 0o600)?;
    changed |= write_atomic_if_changed(&paths.broker_unit, broker_unit.as_bytes(), 0o644)?;
    changed |= write_atomic_if_changed(&paths.server_unit, server_unit.as_bytes(), 0o644)?;
    changed |= write_atomic_if_changed(&paths.manifest, &manifest_bytes, 0o600)?;

    if changed {
        controller.run(&["daemon-reload"])?;
    }
    controller.run(&["enable", BROKER_UNIT, SERVER_UNIT])?;
    let restart_required = changed
        && [BROKER_UNIT, SERVER_UNIT].iter().any(|unit| {
            controller
                .inspect(unit)
                .is_ok_and(|status| status.active_state == "active")
        });
    Ok(InstallReport {
        schema: REPORT_SCHEMA,
        action: "install",
        changed,
        manifest: paths.manifest.clone(),
        units: [paths.broker_unit.clone(), paths.server_unit.clone()],
        credential_policy: credential_policy(&manifest.credential),
        restart_required,
    })
}

fn unlock_at<C: ServiceController>(
    paths: &ServicePaths,
    controller: &C,
    passphrase: &str,
) -> Result<ActionReport> {
    let manifest = read_manifest(paths)?.context("AnonSSH services are not installed")?;
    if !matches!(manifest.credential, CredentialSource::RuntimeUnlock) {
        bail!("this installation uses an explicit persistent credential file; run service start")
    }
    if passphrase.is_empty() {
        bail!("identity password must not be empty")
    }
    if passphrase.len() as u64 > MAX_PASSPHRASE_BYTES {
        bail!("identity password exceeds {MAX_PASSPHRASE_BYTES} bytes")
    }
    ensure_owned_directory(&paths.runtime_directory, 0o700, true)?;
    write_atomic_if_changed(&paths.runtime_credential, passphrase.as_bytes(), 0o600)?;
    if let Err(error) = start_services(paths, controller, &manifest) {
        let _ = remove_file_if_present(&paths.runtime_credential);
        return Err(error);
    }
    Ok(ActionReport {
        schema: REPORT_SCHEMA,
        action: "unlock",
        changed: true,
        credential_state: "ready-until-runtime-directory-is-cleared",
    })
}

fn start_at<C: ServiceController>(paths: &ServicePaths, controller: &C) -> Result<ActionReport> {
    let manifest = read_manifest(paths)?.context("AnonSSH services are not installed")?;
    let (_, credential_error) = credential_state(paths, &manifest);
    if let Some(error) = credential_error {
        bail!("AnonSSH service credential is not ready: {error}")
    }
    start_services(paths, controller, &manifest)?;
    Ok(ActionReport {
        schema: REPORT_SCHEMA,
        action: "start",
        changed: true,
        credential_state: "ready",
    })
}

fn start_services<C: ServiceController>(
    paths: &ServicePaths,
    controller: &C,
    manifest: &ServiceManifest,
) -> Result<()> {
    validate_installed_files(paths, manifest)?;
    controller.run(&["start", BROKER_UNIT, SERVER_UNIT])
}

fn stop_at<C: ServiceController>(paths: &ServicePaths, controller: &C) -> Result<ActionReport> {
    let installed =
        read_manifest(paths)?.is_some() || paths.broker_unit.exists() || paths.server_unit.exists();
    if installed {
        controller.run(&["stop", SERVER_UNIT, BROKER_UNIT])?;
    }
    let removed = remove_file_if_present(&paths.runtime_credential)?;
    remove_empty_directory(&paths.runtime_directory)?;
    Ok(ActionReport {
        schema: REPORT_SCHEMA,
        action: "stop",
        changed: installed || removed,
        credential_state: "locked",
    })
}

fn uninstall_at<C: ServiceController>(
    paths: &ServicePaths,
    controller: &C,
) -> Result<ActionReport> {
    let installed = paths.manifest.exists()
        || paths.product_config.exists()
        || paths.broker_unit.exists()
        || paths.server_unit.exists();
    if installed {
        controller.run(&["disable", "--now", SERVER_UNIT, BROKER_UNIT])?;
    }
    let mut changed = remove_file_if_present(&paths.runtime_credential)?;
    changed |= remove_file_if_present(&paths.manifest)?;
    changed |= remove_file_if_present(&paths.product_config)?;
    changed |= remove_file_if_present(&paths.broker_unit)?;
    changed |= remove_file_if_present(&paths.server_unit)?;
    remove_empty_directory(&paths.runtime_directory)?;
    remove_empty_directory(&paths.service_directory)?;
    if installed {
        controller.run(&["daemon-reload"])?;
    }
    Ok(ActionReport {
        schema: REPORT_SCHEMA,
        action: "uninstall",
        changed,
        credential_state: "not-installed",
    })
}

async fn status_at<C: ServiceController>(
    paths: &ServicePaths,
    controller: &C,
    runtime_dependencies_ready: bool,
    topology_valid: bool,
) -> Result<ServiceStatus> {
    let manifest = read_manifest(paths)?;
    let (credential_state, credential_error) = manifest
        .as_ref()
        .map(|manifest| credential_state(paths, manifest))
        .unwrap_or(("not-installed", None));
    let inspect = |unit| {
        if manifest.is_none() {
            UnitStatus {
                load_state: "not-found".to_owned(),
                unit_file_state: "disabled".to_owned(),
                active_state: "inactive".to_owned(),
                sub_state: "dead".to_owned(),
                main_pid: None,
                exit_status: None,
                error: None,
            }
        } else {
            controller
                .inspect(unit)
                .unwrap_or_else(UnitStatus::unavailable)
        }
    };
    let broker_runtime = bond_broker::status().await?;
    Ok(ServiceStatus {
        schema: STATUS_SCHEMA,
        installed: manifest.is_some(),
        package_version: manifest
            .as_ref()
            .map(|manifest| manifest.package_version.clone()),
        machine_id: manifest
            .as_ref()
            .map(|manifest| manifest.machine_id.clone()),
        server_transport: manifest
            .as_ref()
            .map(|manifest| manifest.server_transport.clone()),
        backend: manifest.as_ref().map(|manifest| manifest.backend),
        credential_policy: manifest
            .as_ref()
            .map(|manifest| credential_policy(&manifest.credential))
            .unwrap_or("not-installed"),
        credential_state,
        credential_error,
        server: inspect(SERVER_UNIT),
        broker: inspect(BROKER_UNIT),
        broker_runtime,
        runtime_dependencies_ready,
        topology_valid,
    })
}

fn broker_unit(manifest: &ServiceManifest, paths: &ServicePaths) -> Result<String> {
    let command = systemd_command(&[
        path_text(&manifest.executable)?,
        "--config",
        path_text(&paths.product_config)?,
        "bond-broker",
        "--resident",
    ])?;
    Ok(format!(
        "[Unit]\nDescription=AnonSSH resident transport broker\nAfter=network-online.target\nWants=network-online.target\nStartLimitIntervalSec=60s\nStartLimitBurst=5\n\n[Service]\nType=simple\nUnsetEnvironment=ANONSSH_CONFIG_FILE ANONSSH_RESOURCE_PROFILE ANONSSH_TRANSPORT_PROFILE ANONSSH_PASSPHRASE\nExecStart={command}\nRestart=on-failure\nRestartSec=2s\nTimeoutStopSec=45s\nKillMode=control-group\nUMask=0077\nNoNewPrivileges=yes\n\n[Install]\nWantedBy=default.target\n"
    ))
}

fn server_unit(manifest: &ServiceManifest, paths: &ServicePaths) -> Result<String> {
    let credential = credential_path(paths, manifest);
    let command = systemd_command(&[
        path_text(&manifest.executable)?,
        "--config",
        path_text(&paths.product_config)?,
        "server",
        "--machine-id",
        &manifest.machine_id,
        "--transport",
        &manifest.server_transport,
        "--backend",
        &manifest.backend.to_string(),
    ])?;
    let condition = systemd_path_value(path_text(&credential)?)?;
    let environment = systemd_word(&format!(
        "ANONSSH_PASSPHRASE_FILE={}",
        path_text(&credential)?
    ))?;
    Ok(format!(
        "[Unit]\nDescription=AnonSSH recovery server\nAfter=network-online.target\nWants=network-online.target\nConditionPathExists={condition}\nStartLimitIntervalSec=60s\nStartLimitBurst=5\n\n[Service]\nType=simple\nUnsetEnvironment=ANONSSH_CONFIG_FILE ANONSSH_RESOURCE_PROFILE ANONSSH_TRANSPORT_PROFILE ANONSSH_PASSPHRASE\nEnvironment={environment}\nExecStart={command}\nRestart=on-failure\nRestartSec=2s\nTimeoutStopSec=45s\nKillMode=control-group\nUMask=0077\nNoNewPrivileges=yes\n\n[Install]\nWantedBy=default.target\n"
    ))
}

fn systemd_command(arguments: &[&str]) -> Result<String> {
    arguments
        .iter()
        .map(|argument| systemd_word(argument))
        .collect::<Result<Vec<_>>>()
        .map(|arguments| arguments.join(" "))
}

fn systemd_word(value: &str) -> Result<String> {
    if value.bytes().any(|byte| matches!(byte, 0 | b'\n' | b'\r')) {
        bail!("service arguments cannot contain NUL or line endings")
    }
    let mut encoded = String::with_capacity(value.len() + 2);
    encoded.push('"');
    for character in value.chars() {
        match character {
            '\\' => encoded.push_str("\\\\"),
            '"' => encoded.push_str("\\\""),
            '%' => encoded.push_str("%%"),
            _ => encoded.push(character),
        }
    }
    encoded.push('"');
    Ok(encoded)
}

fn systemd_path_value(value: &str) -> Result<String> {
    if !value.starts_with('/') {
        bail!("systemd condition paths must be absolute")
    }
    if value.bytes().any(|byte| matches!(byte, 0 | b'\n' | b'\r')) {
        bail!("service paths cannot contain NUL or line endings")
    }
    let mut encoded = String::with_capacity(value.len());
    for byte in value.bytes() {
        match byte {
            b'%' => encoded.push_str("%%"),
            b'/' | b'.' | b'_' | b'-' | b'0'..=b'9' | b'a'..=b'z' | b'A'..=b'Z' => {
                encoded.push(char::from(byte));
            }
            _ => encoded.push_str(&format!("\\x{byte:02x}")),
        }
    }
    Ok(encoded)
}

fn validate_installed_files(paths: &ServicePaths, manifest: &ServiceManifest) -> Result<()> {
    validate_manifest(manifest)?;
    let executable = validate_executable(&manifest.executable)?;
    if executable != manifest.executable {
        bail!("installed service executable no longer resolves to its recorded path")
    }
    validate_regular_bounded_file(&paths.product_config, MAX_STATE_BYTES, "service config")?;
    validate_regular_bounded_file(&paths.broker_unit, MAX_STATE_BYTES, "broker unit")?;
    validate_regular_bounded_file(&paths.server_unit, MAX_STATE_BYTES, "server unit")?;
    let credential = credential_path(paths, manifest);
    validate_credential_file(&credential)?;
    Ok(())
}

fn credential_state(
    paths: &ServicePaths,
    manifest: &ServiceManifest,
) -> (&'static str, Option<String>) {
    match validate_credential_file(&credential_path(paths, manifest)) {
        Ok(_) => ("ready", None),
        Err(error) => ("locked", Some(format!("{error:#}"))),
    }
}

fn credential_policy(source: &CredentialSource) -> &'static str {
    match source {
        CredentialSource::RuntimeUnlock => "runtime-unlock",
        CredentialSource::File { .. } => "explicit-persistent-file",
    }
}

fn credential_path(paths: &ServicePaths, manifest: &ServiceManifest) -> PathBuf {
    match &manifest.credential {
        CredentialSource::RuntimeUnlock => paths.runtime_credential.clone(),
        CredentialSource::File { path } => path.clone(),
    }
}

fn validate_credential_file(path: &Path) -> Result<PathBuf> {
    let source_metadata = fs::symlink_metadata(path)
        .with_context(|| format!("cannot inspect credential file {}", path.display()))?;
    if !source_metadata.file_type().is_file() {
        bail!("credential source must be a regular file, not a symlink")
    }
    let canonical = fs::canonicalize(path)
        .with_context(|| format!("cannot resolve credential file {}", path.display()))?;
    let metadata = fs::symlink_metadata(&canonical)
        .with_context(|| format!("cannot inspect credential file {}", canonical.display()))?;
    if !metadata.file_type().is_file() {
        bail!("credential source must be a regular file")
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("credential source must be owned by the current user")
    }
    if metadata.mode() & 0o077 != 0 {
        bail!("credential source must not be accessible by group or other users")
    }
    if metadata.len() == 0 || metadata.len() > MAX_PASSPHRASE_BYTES {
        bail!("credential source must contain 1..={MAX_PASSPHRASE_BYTES} bytes")
    }
    Ok(canonical)
}

fn validate_executable(path: &Path) -> Result<PathBuf> {
    let canonical = fs::canonicalize(path)
        .with_context(|| format!("cannot resolve AnonSSH executable {}", path.display()))?;
    let metadata = fs::symlink_metadata(&canonical)?;
    if !metadata.is_file() || metadata.permissions().mode() & 0o111 == 0 {
        bail!("AnonSSH service executable must be an executable regular file")
    }
    if !matches!(metadata.uid(), 0) && metadata.uid() != unsafe { libc::geteuid() } {
        bail!("AnonSSH service executable must be owned by the current user or root")
    }
    if metadata.permissions().mode() & 0o022 != 0 {
        bail!("AnonSSH service executable must not be writable by group or other users")
    }
    Ok(canonical)
}

fn validate_manifest(manifest: &ServiceManifest) -> Result<()> {
    if manifest.schema != MANIFEST_SCHEMA || manifest.version != MANIFEST_VERSION {
        bail!("unsupported AnonSSH service installation manifest")
    }
    validate_machine_id(&manifest.machine_id)?;
    validate_server_transport(&manifest.server_transport)?;
    if !manifest.executable.is_absolute() {
        bail!("service executable path must be absolute")
    }
    if !manifest.backend.ip().is_loopback() || manifest.backend.port() == 0 {
        bail!("installed SSH backend must be a non-zero loopback socket")
    }
    if let CredentialSource::File { path } = &manifest.credential {
        if !path.is_absolute() {
            bail!("persistent credential path must be absolute")
        }
    }
    Ok(())
}

fn validate_machine_id(machine_id: &str) -> Result<()> {
    let valid = !machine_id.is_empty()
        && machine_id.len() <= 253
        && machine_id
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-' | b'_'))
        && machine_id
            .as_bytes()
            .first()
            .is_some_and(u8::is_ascii_alphanumeric);
    if !valid {
        bail!("invalid machine ID: use ASCII letters, digits, '.', '-', and '_'")
    }
    Ok(())
}

fn validate_server_transport(transport: &str) -> Result<()> {
    if matches!(
        transport,
        "bond" | "bond-tor" | "bond-i2p" | "i2p" | "tor" | "both"
    ) {
        Ok(())
    } else {
        bail!("invalid installed server transport")
    }
}

fn read_manifest(paths: &ServicePaths) -> Result<Option<ServiceManifest>> {
    let encoded = match read_bounded_file(&paths.manifest, MAX_STATE_BYTES, "service manifest") {
        Ok(encoded) => encoded,
        Err(error)
            if error
                .downcast_ref::<io::Error>()
                .is_some_and(|io| io.kind() == io::ErrorKind::NotFound) =>
        {
            return Ok(None)
        }
        Err(error) => return Err(error),
    };
    let manifest: ServiceManifest =
        serde_json::from_slice(&encoded).context("service manifest is malformed")?;
    validate_manifest(&manifest)?;
    Ok(Some(manifest))
}

fn read_bounded_file(path: &Path, maximum: u64, label: &str) -> Result<Vec<u8>> {
    let file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_CLOEXEC | libc::O_NOFOLLOW)
        .open(path)?;
    let metadata = file.metadata()?;
    validate_owned_regular_metadata(&metadata, label)?;
    if metadata.len() > maximum {
        bail!("{label} exceeds {maximum} bytes")
    }
    let mut bytes = Vec::with_capacity(metadata.len() as usize);
    file.take(maximum + 1).read_to_end(&mut bytes)?;
    if bytes.len() as u64 > maximum {
        bail!("{label} exceeds {maximum} bytes")
    }
    Ok(bytes)
}

fn validate_regular_bounded_file(path: &Path, maximum: u64, label: &str) -> Result<()> {
    read_bounded_file(path, maximum, label).map(|_| ())
}

fn encoded_json<T: Serialize>(value: &T) -> Result<Vec<u8>> {
    let mut encoded = serde_json::to_vec_pretty(value)?;
    encoded.push(b'\n');
    Ok(encoded)
}

fn write_atomic_if_changed(path: &Path, contents: &[u8], mode: u32) -> Result<bool> {
    match fs::symlink_metadata(path) {
        Ok(metadata) if !metadata.file_type().is_file() => {
            bail!(
                "refusing to replace non-regular service file {}",
                path.display()
            )
        }
        Ok(metadata) => {
            validate_owned_regular_metadata(&metadata, "installed service file")?;
            if read_bounded_file(path, MAX_STATE_BYTES, "installed service file")? == contents {
                chmod(path, mode)?;
                return Ok(false);
            }
        }
        Err(error) if error.kind() == io::ErrorKind::NotFound => {}
        Err(error) => return Err(error.into()),
    }
    let parent = path
        .parent()
        .context("service file has no parent directory")?;
    fs::create_dir_all(parent)?;
    let name = path
        .file_name()
        .and_then(|name| name.to_str())
        .context("service file name is not UTF-8")?;
    let temporary = parent.join(format!(
        ".{name}.{}.{}.tmp",
        std::process::id(),
        NEXT_TEMPORARY_FILE.fetch_add(1, Ordering::Relaxed)
    ));
    let operation = (|| -> Result<()> {
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .custom_flags(libc::O_CLOEXEC | libc::O_NOFOLLOW)
            .mode(mode)
            .open(&temporary)?;
        file.write_all(contents)?;
        file.sync_all()?;
        fs::rename(&temporary, path)?;
        chmod(path, mode)?;
        File::open(parent)?.sync_all()?;
        Ok(())
    })();
    if operation.is_err() {
        let _ = fs::remove_file(&temporary);
    }
    operation?;
    Ok(true)
}

fn ensure_regular_or_missing(path: &Path) -> Result<()> {
    match fs::symlink_metadata(path) {
        Ok(metadata) => validate_owned_regular_metadata(&metadata, "installed service file")
            .with_context(|| format!("refusing to replace {}", path.display())),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error.into()),
    }
}

fn ensure_owned_directory(path: &Path, mode: u32, private: bool) -> Result<()> {
    let mut builder = fs::DirBuilder::new();
    builder.recursive(true).mode(mode);
    match builder.create(path) {
        Ok(()) => {}
        Err(error) if error.kind() == io::ErrorKind::AlreadyExists => {}
        Err(error) => return Err(error.into()),
    }
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.file_type().is_dir() {
        bail!("service directory is not a real directory")
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("service directory is not owned by the current user")
    }
    let forbidden = if private { 0o077 } else { 0o022 };
    if metadata.permissions().mode() & forbidden != 0 {
        bail!("service directory has unsafe permissions")
    }
    Ok(())
}

fn validate_owned_regular_metadata(metadata: &fs::Metadata, label: &str) -> Result<()> {
    if !metadata.file_type().is_file() {
        bail!("{label} is not a regular file")
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("{label} is not owned by the current user")
    }
    if metadata.nlink() != 1 {
        bail!("{label} must not have multiple filesystem links")
    }
    Ok(())
}

fn remove_file_if_present(path: &Path) -> Result<bool> {
    match fs::remove_file(path) {
        Ok(()) => Ok(true),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(false),
        Err(error) => Err(error.into()),
    }
}

fn remove_empty_directory(path: &Path) -> Result<()> {
    match fs::remove_dir(path) {
        Ok(()) => Ok(()),
        Err(error)
            if matches!(
                error.kind(),
                io::ErrorKind::NotFound | io::ErrorKind::DirectoryNotEmpty
            ) =>
        {
            Ok(())
        }
        Err(error) => Err(error.into()),
    }
}

fn path_text(path: &Path) -> Result<&str> {
    path.to_str().context("service paths must be valid UTF-8")
}

fn bounded_command_error(output: &Output) -> String {
    let bytes = if output.stderr.is_empty() {
        &output.stdout
    } else {
        &output.stderr
    };
    String::from_utf8_lossy(&bytes[..bytes.len().min(4_096)])
        .trim()
        .to_owned()
}

fn parse_unit_status(encoded: &[u8]) -> Result<UnitStatus> {
    let text = std::str::from_utf8(encoded).context("systemctl status output is not UTF-8")?;
    let mut fields = std::collections::BTreeMap::new();
    for line in text.lines() {
        let (key, value) = line
            .split_once('=')
            .context("systemctl status output is malformed")?;
        fields.insert(key, value);
    }
    let field = |name: &str| {
        fields
            .get(name)
            .copied()
            .with_context(|| format!("systemctl omitted {name}"))
    };
    let main_pid = field("MainPID")?.parse::<u32>()?;
    let exit_status = field("ExecMainStatus")?.parse::<i32>()?;
    Ok(UnitStatus {
        load_state: field("LoadState")?.to_owned(),
        unit_file_state: field("UnitFileState")?.to_owned(),
        active_state: field("ActiveState")?.to_owned(),
        sub_state: field("SubState")?.to_owned(),
        main_pid: (main_pid != 0).then_some(main_pid),
        exit_status: (exit_status != 0).then_some(exit_status),
        error: None,
    })
}

#[cfg(test)]
mod tests {
    use std::cell::RefCell;
    use std::os::unix::fs::{symlink, PermissionsExt};
    use std::sync::atomic::{AtomicU64, Ordering};

    use super::*;

    static NEXT_TEST: AtomicU64 = AtomicU64::new(1);

    struct TestRoot(PathBuf);

    impl TestRoot {
        fn new(label: &str) -> Self {
            let path = std::env::temp_dir().join(format!(
                "anonssh-service-{label}-{}-{}",
                std::process::id(),
                NEXT_TEST.fetch_add(1, Ordering::Relaxed)
            ));
            fs::create_dir_all(&path).unwrap();
            Self(path)
        }
    }

    impl Drop for TestRoot {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[derive(Default)]
    struct FakeController {
        commands: RefCell<Vec<Vec<String>>>,
        active: RefCell<bool>,
    }

    impl ServiceController for FakeController {
        fn run(&self, arguments: &[&str]) -> Result<()> {
            self.commands
                .borrow_mut()
                .push(arguments.iter().map(|value| (*value).to_owned()).collect());
            if arguments
                .first()
                .is_some_and(|argument| *argument == "start")
            {
                *self.active.borrow_mut() = true;
            }
            if arguments
                .first()
                .is_some_and(|argument| matches!(*argument, "stop" | "disable"))
            {
                *self.active.borrow_mut() = false;
            }
            Ok(())
        }

        fn inspect(&self, _unit: &str) -> Result<UnitStatus> {
            let active = *self.active.borrow();
            Ok(UnitStatus {
                load_state: "loaded".to_owned(),
                unit_file_state: "enabled".to_owned(),
                active_state: if active { "active" } else { "inactive" }.to_owned(),
                sub_state: if active { "running" } else { "dead" }.to_owned(),
                main_pid: active.then_some(1234),
                exit_status: None,
                error: None,
            })
        }
    }

    fn executable(root: &Path) -> PathBuf {
        let path = root.join("anonssh executable");
        fs::write(&path, b"test").unwrap();
        fs::set_permissions(&path, fs::Permissions::from_mode(0o700)).unwrap();
        path
    }

    fn options(root: &Path, credential_file: Option<PathBuf>) -> InstallOptions {
        InstallOptions {
            executable: executable(root),
            machine_id: "home-machine".to_owned(),
            server_transport: "bond".to_owned(),
            backend: "127.0.0.1:2222".parse().unwrap(),
            resource_profile: ResourceProfile::Performance,
            transport_profile: TransportProfile::Auto,
            external_tor_services: Vec::new(),
            resident_service: ResourceProfile::Performance.resident_policy(),
            credential_file,
        }
    }

    fn paths(root: &Path) -> ServicePaths {
        ServicePaths::under(root.join("config"), root.join("runtime"))
    }

    #[test]
    fn runtime_unlock_lifecycle_is_private_idempotent_and_explicit() {
        let root = TestRoot::new("runtime");
        let paths = paths(&root.0);
        let controller = FakeController::default();

        let first = install_at(&paths, &controller, options(&root.0, None)).unwrap();
        assert!(first.changed);
        assert!(!first.restart_required);
        let second = install_at(&paths, &controller, options(&root.0, None)).unwrap();
        assert!(!second.changed);
        assert_eq!(
            fs::metadata(&paths.manifest).unwrap().permissions().mode() & 0o777,
            0o600
        );
        assert_eq!(
            fs::metadata(&paths.product_config)
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
        assert_eq!(
            fs::metadata(&paths.server_unit)
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o644
        );
        let server = fs::read_to_string(&paths.server_unit).unwrap();
        let broker = fs::read_to_string(&paths.broker_unit).unwrap();
        assert!(server.contains("ConditionPathExists="));
        assert!(server.contains("Restart=on-failure"));
        assert!(server.contains("UnsetEnvironment=ANONSSH_CONFIG_FILE"));
        assert!(broker.contains("\"bond-broker\" \"--resident\""));
        assert!(start_at(&paths, &controller).is_err());

        let unlocked = unlock_at(&paths, &controller, "correct horse battery staple").unwrap();
        assert_eq!(
            unlocked.credential_state,
            "ready-until-runtime-directory-is-cleared"
        );
        assert_eq!(
            fs::metadata(&paths.runtime_credential)
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
        assert_eq!(
            fs::read(&paths.runtime_credential).unwrap(),
            b"correct horse battery staple"
        );
        assert!(start_at(&paths, &controller).is_ok());
        assert!(stop_at(&paths, &controller).unwrap().changed);
        assert!(!paths.runtime_credential.exists());
        assert!(stop_at(&paths, &controller).unwrap().changed);

        assert!(uninstall_at(&paths, &controller).unwrap().changed);
        assert!(!uninstall_at(&paths, &controller).unwrap().changed);
        assert!(!paths.manifest.exists());
        assert!(!paths.server_unit.exists());
        assert!(!paths.broker_unit.exists());
    }

    #[test]
    fn persistent_credentials_require_owner_only_file_and_escape_unit_arguments() {
        let root = TestRoot::new("persistent-percent-%");
        let paths = paths(&root.0);
        let controller = FakeController::default();
        let credential = root.0.join("credential % with spaces");
        fs::write(&credential, b"secret").unwrap();
        fs::set_permissions(&credential, fs::Permissions::from_mode(0o600)).unwrap();

        let report = install_at(
            &paths,
            &controller,
            options(&root.0, Some(credential.clone())),
        )
        .unwrap();
        assert_eq!(report.credential_policy, "explicit-persistent-file");
        let unit = fs::read_to_string(&paths.server_unit).unwrap();
        assert!(unit.contains("credential %% with spaces"));
        assert!(!unit.contains("sh -c"));
        assert!(unlock_at(&paths, &controller, "secret").is_err());
        assert!(start_at(&paths, &controller).is_ok());

        fs::set_permissions(&credential, fs::Permissions::from_mode(0o644)).unwrap();
        assert!(start_at(&paths, &controller).is_err());
    }

    #[test]
    fn unit_status_parser_is_strict_and_bounded() {
        let status = parse_unit_status(
            b"LoadState=loaded\nUnitFileState=enabled\nActiveState=active\nSubState=running\nMainPID=42\nExecMainStatus=0\n",
        )
        .unwrap();
        assert_eq!(status.main_pid, Some(42));
        assert_eq!(status.exit_status, None);
        assert!(parse_unit_status(b"LoadState=loaded\n").is_err());
        assert!(systemd_word("line\nfeed").is_err());
        assert_eq!(
            systemd_path_value("/tmp/credential % file").unwrap(),
            "/tmp/credential\\x20%%\\x20file"
        );
        assert!(systemd_path_value("relative").is_err());
    }

    #[test]
    fn lifecycle_state_and_credentials_reject_symlinks() {
        let root = TestRoot::new("symlink");
        let paths = paths(&root.0);
        let controller = FakeController::default();
        fs::create_dir_all(&paths.unit_directory).unwrap();
        let target = root.0.join("unrelated");
        fs::write(&target, b"do not replace").unwrap();
        symlink(&target, &paths.server_unit).unwrap();
        assert!(install_at(&paths, &controller, options(&root.0, None)).is_err());
        assert_eq!(fs::read(&target).unwrap(), b"do not replace");

        let credential = root.0.join("credential");
        let credential_link = root.0.join("credential-link");
        fs::write(&credential, b"secret").unwrap();
        fs::set_permissions(&credential, fs::Permissions::from_mode(0o600)).unwrap();
        symlink(&credential, &credential_link).unwrap();
        assert!(validate_credential_file(&credential_link).is_err());
    }

    #[test]
    fn installation_rejects_writable_executables_and_unsafe_directories() {
        let writable_root = TestRoot::new("writable-executable");
        let writable_paths = paths(&writable_root.0);
        let controller = FakeController::default();
        let writable_options = options(&writable_root.0, None);
        fs::set_permissions(
            &writable_options.executable,
            fs::Permissions::from_mode(0o720),
        )
        .unwrap();
        assert!(install_at(&writable_paths, &controller, writable_options).is_err());
        assert!(!writable_paths.manifest.exists());

        let linked_root = TestRoot::new("linked-directory");
        let linked_paths = paths(&linked_root.0);
        let target = linked_root.0.join("unrelated-service-directory");
        fs::create_dir(&target).unwrap();
        fs::set_permissions(&target, fs::Permissions::from_mode(0o700)).unwrap();
        fs::create_dir_all(linked_paths.service_directory.parent().unwrap()).unwrap();
        symlink(&target, &linked_paths.service_directory).unwrap();
        assert!(install_at(&linked_paths, &controller, options(&linked_root.0, None),).is_err());
        assert!(fs::read_dir(target).unwrap().next().is_none());

        let shared_root = TestRoot::new("shared-unit-directory");
        let shared_paths = paths(&shared_root.0);
        fs::create_dir_all(&shared_paths.unit_directory).unwrap();
        fs::set_permissions(
            &shared_paths.unit_directory,
            fs::Permissions::from_mode(0o775),
        )
        .unwrap();
        assert!(install_at(&shared_paths, &controller, options(&shared_root.0, None),).is_err());
    }

    #[test]
    fn installed_state_rejects_hard_link_aliases() {
        let root = TestRoot::new("hard-link");
        let paths = paths(&root.0);
        let controller = FakeController::default();
        install_at(&paths, &controller, options(&root.0, None)).unwrap();
        fs::hard_link(&paths.manifest, root.0.join("manifest-alias")).unwrap();

        assert!(read_manifest(&paths).is_err());
    }
}
