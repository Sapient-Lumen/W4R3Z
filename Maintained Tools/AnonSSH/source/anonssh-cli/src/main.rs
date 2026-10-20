use std::collections::BTreeSet;
use std::ffi::{OsStr, OsString};
use std::io::Write;
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;

use anonssh_bond::{CapabilityFeatures, ScalingAction, ScalingReason};
use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand, ValueEnum};
use sha2::{Digest, Sha256};
use tokio::io::AsyncWriteExt;
use tokio::sync::oneshot;
use tokio::task::JoinSet;
use tracing::warn;
use zeroize::Zeroizing;

mod application_service;
mod bond_broker;
mod bond_e2e;
mod bond_transport;
mod diagnostics;
mod e2e;
mod embedded_runtime;
mod forwarding;
mod i2p_bootstrap;
mod identity;
mod local_transport;
mod native_service;
mod product_config;
mod proxy;
mod recovery_server_ingress;
mod router_pool;
mod runtime;
mod service;
mod ssh;

pub(crate) use anonssh::{data_stream, sam, tor_transport};

use crate::forwarding::LocalTcpForward;
use crate::identity::{DerivedClientRecoveryIdentity, HostRecord, IdentityManager};
use crate::product_config::{ExternalTorService, ProductConfig, TransportProfile, CONFIG_PATH_ENV};
use crate::runtime::{
    resolve_executable, sam_endpoint, tor_control_endpoint, tor_socks_endpoint, AppConfig,
    I2pdManager, TorManager,
};
use crate::sam::SamListener;
use crate::ssh::{
    build_recovery_command, build_recovery_control_master_command, RecoverySshSession, SshBackend,
    SshInvocation, SshServerPrograms,
};
use crate::tor_transport::{PublishedTorService, TorControlEndpoint, TorListener};

const I2P_SSH_TIMEOUT_SECS: u64 = 840;
const TOR_SSH_TIMEOUT_SECS: u64 = 360;
const MAX_SSH_STREAMS_PER_BOND_SESSION: usize = 64;
const SSH_STREAM_REJECTED: u32 = 2;

#[derive(Parser)]
#[command(
    name = "anonssh",
    version,
    about = "Password-recoverable SSH over I2P and Tor",
    override_usage = "anonssh [OPTIONS] <COMMAND>\n       anonssh [SAFE-SSH-OPTIONS] <USER@MACHINE-ID> [COMMAND ...]\n       anonssh -l <USER> [SAFE-SSH-OPTIONS] <MACHINE-ID> [COMMAND ...]",
    after_help = "Quick connect: anonssh user@machine-id"
)]
struct Cli {
    /// Read product policy from this versioned JSON file.
    #[arg(long, global = true, value_name = "PATH")]
    config: Option<PathBuf>,
    /// Show per-slot startup details and machine-readable route diagnostics.
    #[arg(short, long, global = true)]
    verbose: bool,
    #[command(subcommand)]
    command: Command,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, ValueEnum)]
enum ClientTransport {
    /// Prefer the bonded path, then bounded direct recovery fallbacks.
    Auto,
    /// Use an adaptive Tor-only bond with a four-lane minimum.
    BondTor,
    /// Use an adaptive I2P-only bond with a four-lane minimum.
    BondI2p,
    Bond,
    I2p,
    Tor,
}

impl ClientTransport {
    fn is_bond(self) -> bool {
        matches!(self, Self::Bond | Self::BondTor | Self::BondI2p)
    }

    fn uses_i2p(self) -> bool {
        matches!(self, Self::Bond | Self::BondI2p | Self::I2p)
    }

    fn uses_tor(self) -> bool {
        matches!(self, Self::Bond | Self::BondTor | Self::Tor)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, ValueEnum)]
enum ServerTransport {
    Bond,
    BondTor,
    BondI2p,
    I2p,
    Tor,
    Both,
}

impl ServerTransport {
    fn is_bond(self) -> bool {
        matches!(self, Self::Bond | Self::BondTor | Self::BondI2p)
    }

    fn uses_i2p(self) -> bool {
        matches!(self, Self::Bond | Self::BondI2p | Self::I2p | Self::Both)
    }

    fn uses_tor(self) -> bool {
        matches!(self, Self::Bond | Self::BondTor | Self::Tor | Self::Both)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, ValueEnum)]
enum ProxyTransport {
    I2p,
    Tor,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, ValueEnum)]
enum LiveTransport {
    AutoFallback,
    AutoTopology,
    Bond,
    BondEndurance,
    BondForward,
    BondNative,
    BondScale,
    BondSsh,
    BondTools,
    BondTorSsh,
    BondI2pSsh,
    ConcurrentBondSsh,
    I2p,
    I2pFresh,
    I2pPool,
    PoolRecovery,
    ProcessRestart,
    Tor,
}

#[derive(Subcommand)]
enum BrokerCommand {
    /// Start a resident per-user transport broker.
    Start,
    /// Report whether the per-user transport broker is running.
    Status {
        /// Emit the broker report as JSON.
        #[arg(long)]
        json: bool,
    },
    /// Stop the per-user transport broker and its managed routers.
    Stop,
}

#[derive(Subcommand)]
enum ServiceCommand {
    /// Install or atomically update the user broker and recovery-server services.
    Install {
        #[arg(long)]
        machine_id: String,
        #[arg(long, value_enum)]
        transport: Option<ServerTransport>,
        #[arg(long, default_value = "127.0.0.1:2222")]
        backend: SocketAddr,
        /// Owner-only password file for unattended restart; omit for runtime unlock.
        #[arg(long, value_name = "PATH")]
        credential_file: Option<PathBuf>,
    },
    /// Prompt for the identity password, retain it only in the runtime directory, and start.
    Unlock,
    /// Start an installed service whose configured credential is already ready.
    Start,
    /// Report installation, credential, unit, broker, and topology state.
    Status {
        #[arg(long)]
        json: bool,
    },
    /// Stop the server and broker and remove any runtime unlock credential.
    Stop,
    /// Stop and remove the user service installation.
    Uninstall,
}

#[derive(Subcommand)]
enum Command {
    /// Connect using only user@machine-id and the shared identity password.
    Connect {
        target: String,
        #[arg(long, value_enum)]
        transport: Option<ClientTransport>,
        /// Safe OpenSSH options followed by an optional remote command.
        #[arg(last = true)]
        ssh_args: Vec<OsString>,
    },
    /// Forward one loopback TCP listener to a named service through AnonSSH.
    Forward {
        target: String,
        /// Non-zero loopback address to expose on this machine.
        #[arg(long, value_name = "LOOPBACK:PORT")]
        listen: SocketAddr,
        /// TCP destination as seen by the remote SSH server.
        #[arg(long, value_name = "HOST:PORT")]
        remote: String,
        #[arg(long, value_enum)]
        transport: Option<ClientTransport>,
    },
    /// Authorize one target for native ALP service connections in this broker generation.
    Authorize { target: String },
    /// Connect stdin/stdout to a named peer service through the public ALP socket.
    Dial {
        target: String,
        service: String,
        #[arg(long, value_enum, default_value = "bulk")]
        class: local_transport::AlpTrafficClass,
        #[arg(long, value_enum, default_value = "auto")]
        transport: local_transport::AlpTransport,
        #[arg(long, default_value_t = 900)]
        deadline_seconds: u64,
    },
    /// Publish this machine's derived SSH identity over I2P, Tor, or both.
    Server {
        #[arg(long)]
        machine_id: String,
        #[arg(long, value_enum)]
        transport: Option<ServerTransport>,
        #[arg(long, default_value = "127.0.0.1:2222")]
        backend: SocketAddr,
        /// Override the Dropbear executable used for the local recovery backend.
        #[arg(long = "dropbear", alias = "ssh-server", value_name = "PATH")]
        dropbear: Option<PathBuf>,
        /// Publish NAME through one owner-private local Unix socket (repeatable).
        #[arg(long = "native-service", value_name = "NAME=/ABSOLUTE/SOCKET")]
        native_services: Vec<String>,
    },
    /// Inspect runtime dependencies and live transport availability.
    Doctor {
        #[arg(long)]
        json: bool,
    },
    /// Run the test facility embedded in the shipped binary.
    Test {
        /// Run a real local-server-to-local-client transport and SSH login.
        #[arg(long, value_enum, conflicts_with = "fuzz")]
        live: Option<LiveTransport>,
        /// Run deterministic mutation campaigns against embedded parsers.
        #[arg(long)]
        fuzz: bool,
        /// Emit the selected deterministic test report as JSON.
        #[arg(long)]
        json: bool,
    },
    /// Record one corroborated daily observation from mature local routers.
    ObserveI2pBootstrap {
        /// Mature i2pd state root containing netDb and peerProfiles (repeatable).
        #[arg(long = "source", required = true, num_args = 2..)]
        sources: Vec<PathBuf>,
        /// Versioned public-identity observation ledger to update atomically.
        #[arg(long)]
        ledger: PathBuf,
    },
    /// Report longitudinal I2P evidence without scanning or changing router state.
    StatusI2pBootstrap {
        /// Versioned public-identity observation ledger.
        #[arg(long)]
        ledger: PathBuf,
        /// Required distinct UTC observation days.
        #[arg(long, default_value_t = i2p_bootstrap::DEFAULT_MINIMUM_OBSERVATION_DAYS)]
        minimum_observation_days: u64,
        /// Required span between first and latest observations.
        #[arg(long, default_value_t = i2p_bootstrap::DEFAULT_MINIMUM_OBSERVATION_SPAN_DAYS)]
        minimum_observation_span_days: u64,
    },
    /// Inspect current I2P source-root contribution without recording an observation.
    StatusI2pSources {
        /// Mature i2pd state root containing netDb and peerProfiles (repeatable).
        #[arg(long = "source", required = true, num_args = 2..)]
        sources: Vec<PathBuf>,
    },
    /// Build a public I2P bootstrap corpus from long-lived router evidence.
    CurateI2pBootstrap {
        /// Mature i2pd state root containing netDb and peerProfiles (repeatable).
        #[arg(long = "source", required = true, num_args = 2..)]
        sources: Vec<PathBuf>,
        /// Versioned public-identity observation ledger.
        #[arg(long)]
        ledger: PathBuf,
        /// New directory in which to write every qualifying public RouterInfo.
        #[arg(long)]
        output: PathBuf,
        /// Required distinct UTC observation days.
        #[arg(long, default_value_t = i2p_bootstrap::DEFAULT_MINIMUM_OBSERVATION_DAYS)]
        minimum_observation_days: u64,
        /// Required span between first and latest observations.
        #[arg(long, default_value_t = i2p_bootstrap::DEFAULT_MINIMUM_OBSERVATION_SPAN_DAYS)]
        minimum_observation_span_days: u64,
    },
    /// Validate and report longevity and current usefulness of an I2P corpus.
    CheckI2pBootstrap {
        /// Corpus directory containing manifest.json and netDb.
        #[arg(long)]
        corpus: PathBuf,
    },
    /// Inspect or stop the resident per-user transport broker.
    Broker {
        #[command(subcommand)]
        command: BrokerCommand,
    },
    /// Manage user-scoped broker and recovery-server services.
    Service {
        #[command(subcommand)]
        command: ServiceCommand,
    },
    /// Internal OpenSSH ProxyCommand entrypoint.
    #[command(hide = true)]
    Proxy {
        #[arg(long, value_enum)]
        transport: ProxyTransport,
        #[arg(long)]
        destination: String,
        #[arg(long)]
        endpoint: String,
    },
    /// Internal bonded OpenSSH ProxyCommand entrypoint.
    #[command(hide = true)]
    BondProxy {
        #[arg(long = "tor-destination", num_args = 1..)]
        tor_destinations: Vec<String>,
        #[arg(long = "i2p-destination", num_args = 1..)]
        i2p_destinations: Vec<String>,
        #[arg(long)]
        key_file: PathBuf,
    },
    /// Internal automatic OpenSSH ProxyCommand entrypoint.
    #[command(hide = true)]
    AutoProxy {
        #[arg(long = "tor-destination", num_args = 1..)]
        tor_destinations: Vec<String>,
        #[arg(long = "i2p-destination", num_args = 1..)]
        i2p_destinations: Vec<String>,
        #[arg(long)]
        direct_tor_destination: String,
        #[arg(long)]
        direct_i2p_destination: String,
        #[arg(long)]
        key_file: PathBuf,
    },
    /// Internal direct-route proxy through the resident router broker.
    #[command(hide = true)]
    BrokerProxy {
        #[arg(long, value_enum)]
        transport: ProxyTransport,
        #[arg(long)]
        destination: String,
    },
    /// Internal resident per-user bond broker.
    #[command(hide = true)]
    BondBroker {
        /// Remain available without active local clients.
        #[arg(long)]
        resident: bool,
    },
}

#[derive(Debug)]
struct RecoveryTarget {
    user: String,
    machine_id: String,
}

#[derive(Debug)]
struct SshExitStatus(std::process::ExitStatus);

impl std::fmt::Display for SshExitStatus {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "OpenSSH exited with {}", self.0)
    }
}

impl std::error::Error for SshExitStatus {}

impl SshExitStatus {
    fn process_code(&self) -> i32 {
        if let Some(code) = self.0.code() {
            return code;
        }
        #[cfg(unix)]
        {
            use std::os::unix::process::ExitStatusExt;
            if let Some(signal) = self.0.signal() {
                return 128 + signal;
            }
        }
        255
    }
}

#[tokio::main]
async fn main() {
    if let Err(error) = run().await {
        if let Some(status) = error.downcast_ref::<SshExitStatus>() {
            std::process::exit(status.process_code());
        }
        eprintln!("Error: {error:#}");
        std::process::exit(1);
    }
}

async fn run() -> Result<()> {
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_env_filter(
            tracing_subscriber::EnvFilter::builder()
                .with_default_directive(tracing::Level::WARN.into())
                .from_env_lossy(),
        )
        .init();

    let cli = Cli::parse_from(normalize_cli_args(std::env::args_os()));
    if cli.verbose {
        std::env::set_var("ANONSSH_VERBOSE_OUTPUT", "1");
    }
    let product_config = ProductConfig::load(cli.config.as_deref())?;
    if let Some(source) = product_config.source() {
        std::env::set_var(CONFIG_PATH_ENV, source);
    }

    match cli.command {
        Command::Connect {
            target,
            transport,
            ssh_args,
        } => {
            let invocation = SshInvocation::parse(&ssh_args)?;
            connect(
                &target,
                transport.unwrap_or_else(|| {
                    configured_client_transport(product_config.transport_profile())
                }),
                &invocation,
                &product_config,
            )
            .await
        }
        Command::Forward {
            target,
            listen,
            remote,
            transport,
        } => {
            let forward = LocalTcpForward::parse(listen, &remote)?;
            let invocation = SshInvocation::from_options(forward.ssh_options())?;
            eprintln!(
                "anonssh: forwarding {} to {} through {}",
                forward.listen(),
                forward.remote(),
                target
            );
            connect(
                &target,
                transport.unwrap_or_else(|| {
                    configured_client_transport(product_config.transport_profile())
                }),
                &invocation,
                &product_config,
            )
            .await
        }
        Command::Authorize { target } => {
            let target = parse_recovery_target(&target)?;
            let canonical = format!("{}@{}", target.user, target.machine_id);
            let password =
                identity_password(&format!("Identity password for {}: ", target.machine_id))?;
            let identity =
                IdentityManager::derive_client_recovery_identity(&password, &target.machine_id)
                    .context("failed to derive recovery identity")?;
            drop(password);
            bond_broker::authorize_target(&canonical, &identity, product_config.resource_profile())
                .await?;
            println!("authorized {canonical} for native services");
            Ok(())
        }
        Command::Dial {
            target,
            service,
            class,
            transport,
            deadline_seconds,
        } => {
            let target = parse_recovery_target(&target)?;
            let request = local_transport::AlpDialRequest::new(
                format!("cli-{}", std::process::id()),
                format!("{}@{}", target.user, target.machine_id),
                service,
                class,
                transport,
                Duration::from_secs(deadline_seconds),
            )?;
            bond_broker::dial_service(request).await
        }
        Command::Server {
            machine_id,
            transport,
            backend,
            dropbear,
            native_services,
        } => {
            server(
                &machine_id,
                transport.unwrap_or_else(|| {
                    configured_server_transport(product_config.transport_profile())
                }),
                backend,
                dropbear,
                native_services,
                &product_config,
            )
            .await
        }
        Command::Doctor { json } => {
            let diagnosis = diagnostics::doctor(&product_config).await;
            if json {
                println!("{}", serde_json::to_string_pretty(&diagnosis)?);
            } else {
                print_doctor(&diagnosis);
            }
            if diagnosis.system_ok {
                Ok(())
            } else {
                bail!("runtime dependencies are incomplete")
            }
        }
        Command::Test { live, fuzz, json } => match live {
            Some(_) if json => bail!("--json is not supported by live tests"),
            Some(transport) => e2e::run(transport).await,
            None if fuzz => diagnostics::embedded_fuzz_test(json).await,
            None => diagnostics::embedded_test(json).await,
        },
        Command::ObserveI2pBootstrap { sources, ledger } => {
            let report = i2p_bootstrap::observe(&sources, &ledger)?;
            println!("{}", serde_json::to_string_pretty(&report)?);
            Ok(())
        }
        Command::StatusI2pBootstrap {
            ledger,
            minimum_observation_days,
            minimum_observation_span_days,
        } => {
            let report = i2p_bootstrap::observation_status(
                &ledger,
                minimum_observation_days,
                minimum_observation_span_days,
            )?;
            println!("{}", serde_json::to_string_pretty(&report)?);
            Ok(())
        }
        Command::StatusI2pSources { sources } => {
            let report = i2p_bootstrap::source_status(&sources)?;
            println!("{}", serde_json::to_string_pretty(&report)?);
            if report.policy_ready {
                Ok(())
            } else {
                bail!("configured I2P roots cannot currently corroborate any candidate")
            }
        }
        Command::CurateI2pBootstrap {
            sources,
            ledger,
            output,
            minimum_observation_days,
            minimum_observation_span_days,
        } => {
            let report = i2p_bootstrap::curate(
                &sources,
                &ledger,
                &output,
                minimum_observation_days,
                minimum_observation_span_days,
            )?;
            println!("{}", serde_json::to_string_pretty(&report)?);
            if report.ready {
                Ok(())
            } else {
                bail!(
                    "no currently corroborated router has earned the configured longevity evidence"
                )
            }
        }
        Command::CheckI2pBootstrap { corpus } => {
            let report = i2p_bootstrap::validation(&corpus)?;
            println!("{}", serde_json::to_string_pretty(&report)?);
            Ok(())
        }
        Command::Broker { command } => match command {
            BrokerCommand::Start => {
                let started = bond_broker::start(true).await?;
                println!(
                    "broker {}",
                    if started {
                        "started"
                    } else {
                        "already running"
                    }
                );
                Ok(())
            }
            BrokerCommand::Status { json } => {
                let status = bond_broker::status().await?;
                if json {
                    println!("{}", serde_json::to_string_pretty(&status)?);
                } else if status.running {
                    println!(
                        "broker running: pid={}, sessions={}, recent_streams={}, resource_profile={:?}",
                        status.process_id.unwrap_or_default(),
                        status.bond_sessions,
                        status.recent_bond_stream_ids.len(),
                        status.resource_profile,
                    );
                    if let Some(progress) =
                        bond_broker::router_progress_line(&status.router_progress)
                    {
                        println!("{progress}");
                    }
                } else {
                    println!("broker stopped");
                }
                Ok(())
            }
            BrokerCommand::Stop => {
                if bond_broker::stop().await? {
                    println!("broker stopping");
                } else {
                    println!("broker already stopped");
                }
                Ok(())
            }
        },
        Command::Service { command } => match command {
            ServiceCommand::Install {
                machine_id,
                transport,
                backend,
                credential_file,
            } => {
                validate_component("machine ID", &machine_id, 253)?;
                if !backend.ip().is_loopback() || backend.port() == 0 {
                    bail!("SSH backend must be a non-zero loopback socket")
                }
                let transport = transport.unwrap_or_else(|| {
                    configured_server_transport(product_config.transport_profile())
                });
                let report = service::install(service::InstallOptions {
                    executable: service::current_launcher()?,
                    machine_id,
                    server_transport: server_transport_name(transport).to_owned(),
                    backend,
                    resource_profile: product_config.resource_profile(),
                    transport_profile: transport_profile_for_server(transport),
                    external_tor_services: product_config.external_tor_services().to_vec(),
                    resident_service: product_config.resident_service_policy(),
                    credential_file,
                })?;
                println!("{}", serde_json::to_string_pretty(&report)?);
                Ok(())
            }
            ServiceCommand::Unlock => {
                let password = identity_password("Identity password for installed service: ")?;
                let report = service::unlock(&password)?;
                drop(password);
                println!("{}", serde_json::to_string_pretty(&report)?);
                Ok(())
            }
            ServiceCommand::Start => {
                let report = service::start()?;
                println!("{}", serde_json::to_string_pretty(&report)?);
                Ok(())
            }
            ServiceCommand::Status { json } => {
                let installed_config = service::installed_config_path()?;
                let status_config = match installed_config.as_deref() {
                    Some(path) => ProductConfig::load_snapshot(path)?,
                    None => product_config.clone(),
                };
                let diagnosis = diagnostics::doctor(&status_config).await;
                let dependencies_ready = diagnosis
                    .dependencies
                    .iter()
                    .all(|dependency| !dependency.required || dependency.available);
                let status =
                    service::status(dependencies_ready, diagnosis.bond_topology.valid).await?;
                if json {
                    println!("{}", serde_json::to_string_pretty(&status)?);
                } else {
                    print_service_status(&status);
                }
                Ok(())
            }
            ServiceCommand::Stop => {
                let report = service::stop()?;
                println!("{}", serde_json::to_string_pretty(&report)?);
                Ok(())
            }
            ServiceCommand::Uninstall => {
                let report = service::uninstall()?;
                println!("{}", serde_json::to_string_pretty(&report)?);
                Ok(())
            }
        },
        Command::Proxy {
            transport,
            destination,
            endpoint,
        } => proxy(transport, &destination, &endpoint).await,
        Command::BondProxy {
            tor_destinations,
            i2p_destinations,
            key_file,
        } => {
            bond_proxy(
                &tor_destinations,
                &i2p_destinations,
                &key_file,
                product_config.resource_profile(),
                product_config.external_tor_services(),
            )
            .await
        }
        Command::AutoProxy {
            tor_destinations,
            i2p_destinations,
            direct_tor_destination,
            direct_i2p_destination,
            key_file,
        } => {
            bond_broker::auto_proxy(
                &tor_destinations,
                &i2p_destinations,
                &direct_tor_destination,
                &direct_i2p_destination,
                &key_file,
                product_config.resource_profile(),
            )
            .await
        }
        Command::BrokerProxy {
            transport,
            destination,
        } => {
            let provider = match transport {
                ProxyTransport::Tor => bond_broker::DirectProvider::Tor,
                ProxyTransport::I2p => bond_broker::DirectProvider::I2p,
            };
            bond_broker::direct_proxy(provider, &destination).await
        }
        Command::BondBroker { resident } => bond_broker::serve(product_config, resident).await,
    }
}

fn normalize_cli_args(args: impl IntoIterator<Item = OsString>) -> Vec<OsString> {
    const COMMANDS: &[&str] = &[
        "connect",
        "forward",
        "authorize",
        "dial",
        "server",
        "doctor",
        "test",
        "observe-i2p-bootstrap",
        "status-i2p-bootstrap",
        "status-i2p-sources",
        "curate-i2p-bootstrap",
        "check-i2p-bootstrap",
        "broker",
        "service",
        "proxy",
        "bond-proxy",
        "auto-proxy",
        "broker-proxy",
        "bond-broker",
    ];
    let original = args.into_iter().collect::<Vec<_>>();
    if original.len() <= 1 {
        return original;
    }

    let mut global = vec![original[0].clone()];
    let mut product = Vec::new();
    let mut ssh_options = Vec::new();
    let mut login_user: Option<OsString> = None;
    let mut index = 1;
    let mut options_ended = false;
    while index < original.len() {
        let argument = &original[index];
        let text = argument.to_str();
        if !options_ended && matches!(text, Some("--help" | "-h" | "--version" | "-V")) {
            return original;
        }
        if !options_ended && matches!(text, Some("--verbose" | "-v")) {
            global.push(argument.clone());
            index += 1;
            continue;
        }
        if !options_ended && text == Some("--config") {
            global.push(argument.clone());
            if let Some(value) = original.get(index + 1) {
                global.push(value.clone());
                index += 2;
                continue;
            }
            return original;
        }
        if !options_ended && text.is_some_and(|value| value.starts_with("--config=")) {
            global.push(argument.clone());
            index += 1;
            continue;
        }
        if !options_ended && text == Some("--transport") {
            product.push(argument.clone());
            if let Some(value) = original.get(index + 1) {
                product.push(value.clone());
                index += 2;
                continue;
            }
            return original;
        }
        if !options_ended && text.is_some_and(|value| value.starts_with("--transport=")) {
            product.push(argument.clone());
            index += 1;
            continue;
        }
        if !options_ended && text == Some("--") {
            options_ended = true;
            index += 1;
            continue;
        }
        if !options_ended && text == Some("-l") {
            let Some(value) = original.get(index + 1) else {
                return original;
            };
            login_user = Some(value.clone());
            index += 2;
            continue;
        }
        if !options_ended {
            if let Some(value) = text.and_then(|value| value.strip_prefix("-l")) {
                if !value.is_empty() {
                    login_user = Some(OsString::from(value));
                    index += 1;
                    continue;
                }
            }
        }
        if !options_ended && text.is_some_and(|value| value.starts_with('-')) {
            ssh_options.push(argument.clone());
            if text.is_some_and(ssh_option_takes_separate_value) {
                if let Some(value) = original.get(index + 1) {
                    ssh_options.push(value.clone());
                    index += 2;
                    continue;
                }
            }
            index += 1;
            continue;
        }

        if text.is_some_and(|value| COMMANDS.contains(&value))
            && global.len() + product.len() + ssh_options.len() == 1
            && login_user.is_none()
        {
            return original;
        }
        let Some(destination) = text else {
            return original;
        };
        let target = match (destination.split_once('@'), login_user.as_deref()) {
            (Some((user, machine)), Some(login)) if OsStr::new(user) == login => {
                OsString::from(format!("{user}@{machine}"))
            }
            (Some((_, machine)), Some(login)) => {
                let mut target = login.to_os_string();
                target.push("@");
                target.push(destination);
                if machine.is_empty() {
                    return original;
                }
                target
            }
            (Some(_), None) => argument.clone(),
            (None, Some(user)) => {
                let mut target = user.to_os_string();
                target.push("@");
                target.push(argument);
                target
            }
            (None, None) => return original,
        };
        let mut normalized = global;
        normalized.push(OsString::from("connect"));
        normalized.push(target);
        normalized.extend(product);
        normalized.push(OsString::from("--"));
        normalized.extend(ssh_options);
        normalized.extend(original[index + 1..].iter().cloned());
        return normalized;
    }
    original
}

fn ssh_option_takes_separate_value(argument: &str) -> bool {
    const VALUE_OPTIONS: &[&str] = &[
        "-B", "-b", "-c", "-D", "-E", "-e", "-F", "-I", "-i", "-J", "-L", "-m", "-O", "-o", "-P",
        "-p", "-Q", "-R", "-S", "-W", "-w",
    ];
    VALUE_OPTIONS.contains(&argument)
}

fn configured_client_transport(profile: TransportProfile) -> ClientTransport {
    match profile {
        TransportProfile::Auto => ClientTransport::Auto,
        TransportProfile::Mixed => ClientTransport::Bond,
        TransportProfile::TorOnly => ClientTransport::BondTor,
        TransportProfile::I2pOnly => ClientTransport::BondI2p,
    }
}

fn configured_server_transport(profile: TransportProfile) -> ServerTransport {
    match profile {
        TransportProfile::Auto | TransportProfile::Mixed => ServerTransport::Bond,
        TransportProfile::TorOnly => ServerTransport::BondTor,
        TransportProfile::I2pOnly => ServerTransport::BondI2p,
    }
}

const fn server_transport_name(transport: ServerTransport) -> &'static str {
    match transport {
        ServerTransport::Bond => "bond",
        ServerTransport::BondTor => "bond-tor",
        ServerTransport::BondI2p => "bond-i2p",
        ServerTransport::I2p => "i2p",
        ServerTransport::Tor => "tor",
        ServerTransport::Both => "both",
    }
}

const fn transport_profile_for_server(transport: ServerTransport) -> TransportProfile {
    match transport {
        ServerTransport::Bond | ServerTransport::Both => TransportProfile::Mixed,
        ServerTransport::BondTor | ServerTransport::Tor => TransportProfile::TorOnly,
        ServerTransport::BondI2p | ServerTransport::I2p => TransportProfile::I2pOnly,
    }
}

enum ClientRouter {
    I2p(I2pdManager),
    Tor(TorManager),
}

impl ClientRouter {
    async fn stop(&self) -> Result<()> {
        match self {
            Self::I2p(router) => router.stop().await,
            Self::Tor(router) => router.stop().await,
        }
    }
}

struct ActiveClientRoute {
    transport: ClientTransport,
    destination: String,
    endpoint: String,
    router: ClientRouter,
}

struct ClientDependencies {
    ssh: PathBuf,
    i2pd: Option<PathBuf>,
    tor: Option<PathBuf>,
}

fn resolve_client_dependencies(transport: ClientTransport) -> Result<ClientDependencies> {
    let ssh = resolve_executable("ANONSSH_SSH_BIN", "ssh").context("OpenSSH is unavailable")?;
    if transport == ClientTransport::Auto {
        bail!("automatic route must be resolved before dependencies");
    }
    let i2pd = transport
        .uses_i2p()
        .then(|| resolve_executable("ANONSSH_I2PD_BIN", "i2pd"))
        .transpose()
        .context("i2pd is unavailable")?;
    let tor = transport
        .uses_tor()
        .then(|| resolve_executable("ANONSSH_TOR_BIN", "tor"))
        .transpose()
        .context("Tor is unavailable")?;
    Ok(ClientDependencies { ssh, i2pd, tor })
}

async fn activate_client_route(
    config: &AppConfig,
    identity: &DerivedClientRecoveryIdentity,
    transport: ClientTransport,
    router_binary: PathBuf,
    external_tor_services: &[ExternalTorService],
) -> Result<ActiveClientRoute> {
    match transport {
        ClientTransport::I2p => {
            let router = I2pdManager::new(config.i2pd_dir.clone(), router_binary, sam_endpoint()?)?;
            router
                .ensure_running()
                .await
                .context("failed to start I2P")?;
            Ok(ActiveClientRoute {
                transport,
                destination: identity.i2p.destination.clone(),
                endpoint: sam_endpoint()?.to_string(),
                router: ClientRouter::I2p(router),
            })
        }
        ClientTransport::Tor => {
            let router = configured_direct_tor_manager(
                config.tor_dir.clone(),
                router_binary,
                external_tor_services,
            )?;
            let endpoint = router
                .ensure_running()
                .await
                .context("failed to start Tor")?;
            Ok(ActiveClientRoute {
                transport,
                destination: identity.tor_destination.clone(),
                endpoint,
                router: ClientRouter::Tor(router),
            })
        }
        ClientTransport::Auto
        | ClientTransport::Bond
        | ClientTransport::BondTor
        | ClientTransport::BondI2p => {
            bail!("selected route is not a direct transport")
        }
    }
}

fn configured_direct_tor_manager(
    data_dir: PathBuf,
    binary: PathBuf,
    external_tor_services: &[ExternalTorService],
) -> Result<TorManager> {
    let socks = tor_socks_endpoint()?;
    let control = tor_control_endpoint()?;
    match external_tor_services
        .iter()
        .find(|service| service.socks == socks && service.control == control)
    {
        Some(service) => TorManager::new_external_at(
            data_dir,
            binary,
            socks,
            control,
            service.cookie_file.clone(),
        ),
        None => TorManager::new_at(data_dir, binary, socks, control),
    }
}

async fn connect(
    target: &str,
    requested: ClientTransport,
    invocation: &SshInvocation,
    product_config: &ProductConfig,
) -> Result<()> {
    if invocation.is_quiet() {
        std::env::set_var(bond_broker::QUIET_OUTPUT_ENV, "1");
    }
    let target = parse_recovery_target(target)?;
    let config = AppConfig::new()?;
    let password = identity_password(&format!("Identity password for {}: ", target.machine_id))?;
    let identity = IdentityManager::derive_client_recovery_identity(&password, &target.machine_id)
        .context("failed to derive recovery identity")?;
    drop(password);

    let executable = current_executable()?;
    if requested == ClientTransport::Auto {
        return connect_over_auto(&config, &target, &identity, invocation, &executable);
    }
    let transport = *client_route_order(requested)
        .first()
        .context("explicit transport has no route")?;
    connect_over_route(
        &config,
        &target,
        &identity,
        transport,
        invocation,
        &executable,
        product_config.external_tor_services(),
    )
    .await
}

fn client_route_order(requested: ClientTransport) -> &'static [ClientTransport] {
    const AUTO: &[ClientTransport] = &[];
    const BOND: &[ClientTransport] = &[ClientTransport::Bond];
    const BOND_TOR: &[ClientTransport] = &[ClientTransport::BondTor];
    const BOND_I2P: &[ClientTransport] = &[ClientTransport::BondI2p];
    const I2P: &[ClientTransport] = &[ClientTransport::I2p];
    const TOR: &[ClientTransport] = &[ClientTransport::Tor];
    match requested {
        ClientTransport::Auto => AUTO,
        ClientTransport::Bond => BOND,
        ClientTransport::BondTor => BOND_TOR,
        ClientTransport::BondI2p => BOND_I2P,
        ClientTransport::I2p => I2P,
        ClientTransport::Tor => TOR,
    }
}

fn connect_over_auto(
    config: &AppConfig,
    target: &RecoveryTarget,
    identity: &DerivedClientRecoveryIdentity,
    invocation: &SshInvocation,
    executable: &std::path::Path,
) -> Result<()> {
    let ssh = resolve_executable("ANONSSH_SSH_BIN", "ssh").context("OpenSSH is unavailable")?;
    let record = HostRecord {
        name: Zeroizing::new(target.machine_id.clone()),
        user: Zeroizing::new(target.user.clone()),
        port: 22,
    };
    let session = RecoverySshSession::materialize(
        config,
        &target.machine_id,
        &identity.ssh_client.private_key,
        &identity.ssh_host_public_key,
    )?;
    let key_file = session.materialize_bond_key(&identity.bond_session_key)?;
    let tor_arguments = identity
        .tor_pool_destinations
        .iter()
        .map(|destination| format!(" --tor-destination {}", shell_word(destination)))
        .collect::<String>();
    let i2p_arguments = identity
        .i2p_pool
        .iter()
        .map(|derived| format!(" --i2p-destination {}", shell_word(&derived.destination)))
        .collect::<String>();
    let proxy_command = format!(
        "{} auto-proxy{}{} --direct-tor-destination {} --direct-i2p-destination {} --key-file {}",
        shell_word(&executable.to_string_lossy()),
        tor_arguments,
        i2p_arguments,
        shell_word(&identity.tor_destination),
        shell_word(&identity.i2p.destination),
        shell_word(&key_file.to_string_lossy()),
    );
    let mut ssh = build_recovery_command(
        &record,
        &proxy_command,
        invocation,
        &session,
        I2P_SSH_TIMEOUT_SECS,
        &ssh,
    )?;
    if !invocation.is_quiet() {
        eprintln!("anonssh  connect  {}@{}", target.user, target.machine_id);
        eprintln!("anonssh  search   choosing the best private route");
    }
    let status = ssh.status().context("failed to launch OpenSSH")?;
    ssh_status_result(status, false)
}

async fn connect_over_route(
    config: &AppConfig,
    target: &RecoveryTarget,
    identity: &DerivedClientRecoveryIdentity,
    transport: ClientTransport,
    invocation: &SshInvocation,
    executable: &std::path::Path,
    external_tor_services: &[ExternalTorService],
) -> Result<()> {
    let dependencies = resolve_client_dependencies(transport)?;
    if transport.is_bond() {
        return connect_over_bond(
            config,
            target,
            identity,
            transport,
            invocation,
            executable,
            dependencies,
        );
    }
    if direct_router_process_required() {
        let runtime = ManagedClientRuntime {
            app: config,
            external_tor_services,
        };
        return connect_over_managed_direct(
            runtime,
            target,
            identity,
            transport,
            invocation,
            executable,
            dependencies,
        )
        .await;
    }
    connect_over_brokered_direct(
        config,
        target,
        identity,
        transport,
        invocation,
        executable,
        &dependencies.ssh,
    )
}

struct ManagedClientRuntime<'a> {
    app: &'a AppConfig,
    external_tor_services: &'a [ExternalTorService],
}

fn direct_router_process_required() -> bool {
    std::env::var_os("ANONSSH_INTERNAL_TEST_DIRECT_ROUTERS").is_some()
        || std::env::var_os("ANONSSH_INTERNAL_TEST_FAIL_BOND").is_some()
}

async fn connect_over_managed_direct(
    runtime: ManagedClientRuntime<'_>,
    target: &RecoveryTarget,
    identity: &DerivedClientRecoveryIdentity,
    transport: ClientTransport,
    invocation: &SshInvocation,
    executable: &std::path::Path,
    dependencies: ClientDependencies,
) -> Result<()> {
    let router_binary = match transport {
        ClientTransport::I2p => dependencies
            .i2pd
            .context("i2pd dependency was not resolved")?,
        ClientTransport::Tor => dependencies
            .tor
            .context("Tor dependency was not resolved")?,
        ClientTransport::Auto
        | ClientTransport::Bond
        | ClientTransport::BondTor
        | ClientTransport::BondI2p => unreachable!("direct route checked"),
    };
    let route = activate_client_route(
        runtime.app,
        identity,
        transport,
        router_binary,
        runtime.external_tor_services,
    )
    .await?;
    let proxy_command = format!(
        "{} proxy --transport {} --destination {} --endpoint {}",
        shell_word(&executable.to_string_lossy()),
        direct_transport_name(route.transport),
        shell_word(&route.destination),
        shell_word(&route.endpoint),
    );
    let operation = run_direct_ssh(
        runtime.app,
        target,
        identity,
        route.transport,
        invocation,
        &dependencies.ssh,
        &proxy_command,
    );
    merge_cleanup(operation, route.router.stop().await)
}

fn connect_over_brokered_direct(
    config: &AppConfig,
    target: &RecoveryTarget,
    identity: &DerivedClientRecoveryIdentity,
    transport: ClientTransport,
    invocation: &SshInvocation,
    executable: &std::path::Path,
    ssh: &std::path::Path,
) -> Result<()> {
    let destination = match transport {
        ClientTransport::Tor => &identity.tor_destination,
        ClientTransport::I2p => &identity.i2p.destination,
        ClientTransport::Auto
        | ClientTransport::Bond
        | ClientTransport::BondTor
        | ClientTransport::BondI2p => unreachable!("direct route checked"),
    };
    let proxy_command = format!(
        "{} broker-proxy --transport {} --destination {}",
        shell_word(&executable.to_string_lossy()),
        direct_transport_name(transport),
        shell_word(destination),
    );
    run_direct_ssh(
        config,
        target,
        identity,
        transport,
        invocation,
        ssh,
        &proxy_command,
    )
}

fn direct_transport_name(transport: ClientTransport) -> &'static str {
    match transport {
        ClientTransport::Tor => "tor",
        ClientTransport::I2p => "i2p",
        ClientTransport::Auto
        | ClientTransport::Bond
        | ClientTransport::BondTor
        | ClientTransport::BondI2p => unreachable!("direct route checked"),
    }
}

fn run_direct_ssh(
    config: &AppConfig,
    target: &RecoveryTarget,
    identity: &DerivedClientRecoveryIdentity,
    transport: ClientTransport,
    invocation: &SshInvocation,
    ssh_binary: &std::path::Path,
    proxy_command: &str,
) -> Result<()> {
    let record = HostRecord {
        name: Zeroizing::new(target.machine_id.clone()),
        user: Zeroizing::new(target.user.clone()),
        port: 22,
    };
    let session = RecoverySshSession::materialize(
        config,
        &target.machine_id,
        &identity.ssh_client.private_key,
        &identity.ssh_host_public_key,
    )?;
    let mut ssh = build_recovery_command(
        &record,
        proxy_command,
        invocation,
        &session,
        match transport {
            ClientTransport::Tor => TOR_SSH_TIMEOUT_SECS,
            ClientTransport::I2p => I2P_SSH_TIMEOUT_SECS,
            _ => unreachable!("direct route checked"),
        },
        ssh_binary,
    )?;
    if !invocation.is_quiet() {
        eprintln!("anonssh  connect  {}@{}", target.user, target.machine_id);
        eprintln!(
            "anonssh  route    {}",
            match transport {
                ClientTransport::Tor => "direct Tor",
                ClientTransport::I2p => "direct I2P",
                _ => unreachable!("direct route checked"),
            }
        );
    }
    let status = ssh.status().context("failed to launch OpenSSH")?;
    ssh_status_result(status, false)
}

fn connect_over_bond(
    config: &AppConfig,
    target: &RecoveryTarget,
    identity: &DerivedClientRecoveryIdentity,
    transport: ClientTransport,
    invocation: &SshInvocation,
    executable: &std::path::Path,
    dependencies: ClientDependencies,
) -> Result<()> {
    if !transport.is_bond() {
        bail!("selected route is not a bonded transport");
    }
    let record = HostRecord {
        name: Zeroizing::new(target.machine_id.clone()),
        user: Zeroizing::new(target.user.clone()),
        port: 22,
    };
    let session = RecoverySshSession::materialize(
        config,
        &target.machine_id,
        &identity.ssh_client.private_key,
        &identity.ssh_host_public_key,
    )?;
    let key_file = session.materialize_bond_key(&identity.bond_session_key)?;
    let i2p_arguments = if transport.uses_i2p() {
        identity
            .i2p_pool
            .iter()
            .map(|derived| format!(" --i2p-destination {}", shell_word(&derived.destination)))
            .collect::<String>()
    } else {
        String::new()
    };
    let tor_arguments = if transport.uses_tor() {
        identity
            .tor_pool_destinations
            .iter()
            .map(|destination| format!(" --tor-destination {}", shell_word(destination)))
            .collect::<String>()
    } else {
        String::new()
    };
    let proxy_command = format!(
        "{} bond-proxy{}{} --key-file {}",
        shell_word(&executable.to_string_lossy()),
        tor_arguments,
        i2p_arguments,
        shell_word(&key_file.to_string_lossy()),
    );
    let internal_control_path =
        std::env::var_os("ANONSSH_INTERNAL_TEST_SSH_CONTROL_PATH").map(PathBuf::from);
    let mut ssh = match internal_control_path.as_deref() {
        Some(control_path) => build_recovery_control_master_command(
            &record,
            &proxy_command,
            invocation,
            &session,
            I2P_SSH_TIMEOUT_SECS,
            &dependencies.ssh,
            control_path,
        )?,
        None => build_recovery_command(
            &record,
            &proxy_command,
            invocation,
            &session,
            I2P_SSH_TIMEOUT_SECS,
            &dependencies.ssh,
        )?,
    };
    if !invocation.is_quiet() {
        eprintln!("anonssh  connect  {}@{}", target.user, target.machine_id);
        eprintln!(
            "anonssh  route    {}",
            match transport {
                ClientTransport::Bond => "adaptive Tor + I2P bond",
                ClientTransport::BondTor => "adaptive Tor bond",
                ClientTransport::BondI2p => "adaptive I2P bond",
                _ => unreachable!("bond route checked"),
            }
        );
    }
    let status = ssh.status().context("failed to launch OpenSSH")?;
    ssh_status_result(status, internal_control_path.is_some())
}

fn ssh_status_result(status: std::process::ExitStatus, controlled_master: bool) -> Result<()> {
    if ssh_exit_succeeded(&status, controlled_master) {
        Ok(())
    } else {
        Err(SshExitStatus(status).into())
    }
}

fn ssh_exit_succeeded(status: &std::process::ExitStatus, controlled_master: bool) -> bool {
    status.success() || (controlled_master && status.code() == Some(255))
}

struct ServerDependencies {
    dropbear: PathBuf,
    sftp_server: PathBuf,
    scp: PathBuf,
    i2pd: Option<PathBuf>,
    tor: Option<PathBuf>,
}

fn resolve_server_dependencies(
    transport: ServerTransport,
    dropbear_override: Option<&std::path::Path>,
) -> Result<ServerDependencies> {
    let dropbear = match dropbear_override {
        Some(path) => std::fs::canonicalize(path).context("invalid Dropbear executable")?,
        None => resolve_executable("ANONSSH_DROPBEAR_BIN", "dropbear")
            .context("Dropbear is unavailable")?,
    };
    let sftp_server = resolve_executable("ANONSSH_SFTP_SERVER_BIN", "sftp-server")
        .context("the OpenSSH SFTP server is unavailable")?;
    let scp = resolve_executable("ANONSSH_SCP_BIN", "scp")
        .context("the legacy scp server helper is unavailable")?;
    let i2pd = transport
        .uses_i2p()
        .then(|| resolve_executable("ANONSSH_I2PD_BIN", "i2pd"))
        .transpose()
        .context("i2pd is unavailable")?;
    let tor = transport
        .uses_tor()
        .then(|| resolve_executable("ANONSSH_TOR_BIN", "tor"))
        .transpose()
        .context("Tor is unavailable")?;
    Ok(ServerDependencies {
        dropbear,
        sftp_server,
        scp,
        i2pd,
        tor,
    })
}

async fn server(
    machine_id: &str,
    transport: ServerTransport,
    backend: SocketAddr,
    dropbear: Option<PathBuf>,
    native_services: Vec<String>,
    product_config: &ProductConfig,
) -> Result<()> {
    validate_component("machine ID", machine_id, 253)?;
    if !backend.ip().is_loopback() || backend.port() == 0 {
        bail!("SSH backend must be a non-zero loopback socket")
    }
    if !transport.is_bond() && !native_services.is_empty() {
        bail!("native services require a bonded server transport");
    }
    let config = AppConfig::new()?;
    let password = identity_password(&format!("Identity password for {machine_id}: "))?;
    let identity = IdentityManager::derive_server_recovery_identity(&password, machine_id)
        .context("failed to derive server recovery identity")?;
    drop(password);
    let native_services = Arc::new(native_service::NativeServiceRegistry::parse(
        &native_services,
    )?);

    let dependencies = resolve_server_dependencies(transport, dropbear.as_deref())?;
    let ssh_programs = SshServerPrograms {
        dropbear: &dependencies.dropbear,
        sftp_server: &dependencies.sftp_server,
        scp: &dependencies.scp,
    };
    let _storage_policy = crate::embedded_runtime::enforce_storage_policy(
        &config,
        product_config.resident_service_policy(),
    )?;
    if transport.is_bond() {
        let pool = router_pool::RouterPool::production(
            &config,
            dependencies.tor,
            dependencies.i2pd,
            product_config.external_tor_services(),
        )?;
        return run_bonded_server(
            &config,
            machine_id,
            ssh_programs,
            identity,
            pool,
            product_config.scaling_policy(),
            BondedApplicationServices {
                ssh_backend: backend,
                native_services,
            },
        )
        .await;
    }
    let i2pd = dependencies
        .i2pd
        .map(|binary| I2pdManager::new(config.i2pd_dir.clone(), binary, sam_endpoint()?))
        .transpose()?;
    let tor = dependencies
        .tor
        .map(|binary| {
            configured_direct_tor_manager(
                config.tor_dir.clone(),
                binary,
                product_config.external_tor_services(),
            )
        })
        .transpose()?;

    let routers = ServerRouters {
        i2pd: i2pd.as_ref(),
        tor: tor.as_ref(),
    };
    let operation = run_server(
        &config,
        machine_id,
        transport,
        backend,
        ssh_programs,
        identity,
        routers,
    )
    .await;
    merge_cleanup(operation, stop_routers(i2pd.as_ref(), tor.as_ref()).await)
}

#[derive(Clone)]
struct BondedApplicationServices {
    ssh_backend: SocketAddr,
    native_services: Arc<native_service::NativeServiceRegistry>,
}

async fn run_bonded_server(
    config: &AppConfig,
    machine_id: &str,
    ssh_programs: SshServerPrograms<'_>,
    identity: crate::identity::DerivedServerRecoveryIdentity,
    pool: router_pool::RouterPool,
    scaling_policy: product_config::ScalingPolicy,
    application_services: BondedApplicationServices,
) -> Result<()> {
    let pool = Arc::new(pool);
    let identity = Arc::new(identity);
    let operation = async {
        let mut ssh_backend = SshBackend::start(
            config,
            machine_id,
            &identity,
            ssh_programs,
            application_services.ssh_backend,
        )
        .await
        .context("failed to start recovery SSH backend")?;

        let mut services = JoinSet::new();
        if !pool.i2p_slots().is_empty() {
            services.spawn(supervise_direct_i2p_recovery(
                pool.clone(),
                identity.clone(),
                application_services.ssh_backend,
            ));
        }
        services.spawn(supervise_bonded_recovery(
            pool.clone(),
            identity,
            scaling_policy,
            application_services,
        ));

        let result = tokio::select! {
            signal = shutdown_signal() => signal.context("failed to wait for shutdown signal"),
            result = ssh_backend.wait_for_exit() => result,
            completed = services.join_next() => {
                match completed {
                    Some(Ok(Ok(()))) => bail_result("recovery service stopped unexpectedly"),
                    Some(Ok(Err(error))) => Err(error.context("recovery service failed")),
                    Some(Err(error)) => Err(anyhow::anyhow!("recovery service task failed: {error}")),
                    None => bail_result("all recovery services stopped unexpectedly"),
                }
            }
        };
        services.abort_all();
        while services.join_next().await.is_some() {}
        merge_cleanup(result, ssh_backend.shutdown().await)
    }
    .await;
    merge_cleanup(operation, pool.stop().await)
}

const RECOVERY_SERVICE_RETRY_DELAY: Duration = Duration::from_secs(5);

async fn supervise_direct_i2p_recovery(
    pool: Arc<router_pool::RouterPool>,
    identity: Arc<crate::identity::DerivedServerRecoveryIdentity>,
    backend: SocketAddr,
) -> Result<()> {
    loop {
        if let Err(error) = serve_direct_i2p_recovery(&pool, &identity, backend).await {
            warn!("direct I2P recovery service failed: {error:#}");
        }
        tokio::time::sleep(RECOVERY_SERVICE_RETRY_DELAY).await;
    }
}

async fn serve_direct_i2p_recovery(
    pool: &router_pool::RouterPool,
    identity: &crate::identity::DerivedServerRecoveryIdentity,
    backend: SocketAddr,
) -> Result<()> {
    pool.ensure_i2p_slot(1)
        .await
        .context("failed to start direct-recovery I2P router")?;
    let router = pool.i2p_slot(1)?;
    let destination = identity.i2p.destination.trim_start_matches("i2p://");
    let listener = SamListener::bind_zeroizing(
        router.sam_endpoint.to_string(),
        recovery_session_id(destination),
        identity.i2p.private_key.clone(),
    )
    .await
    .context("failed to publish direct I2P recovery destination")?;
    announce_route("i2p", &identity.i2p.destination)?;
    let (_stop, stop_rx) = oneshot::channel();
    recovery_server_ingress::run(listener, backend, stop_rx).await
}

async fn supervise_bonded_recovery(
    pool: Arc<router_pool::RouterPool>,
    identity: Arc<crate::identity::DerivedServerRecoveryIdentity>,
    scaling_policy: product_config::ScalingPolicy,
    application_services: BondedApplicationServices,
) -> Result<()> {
    loop {
        if let Err(error) = serve_bonded_recovery(
            &pool,
            &identity,
            scaling_policy,
            application_services.clone(),
        )
        .await
        {
            warn!("bonded recovery service failed: {error:#}");
        }
        tokio::time::sleep(RECOVERY_SERVICE_RETRY_DELAY).await;
    }
}

async fn serve_bonded_recovery(
    pool: &Arc<router_pool::RouterPool>,
    identity: &crate::identity::DerivedServerRecoveryIdentity,
    scaling_policy: product_config::ScalingPolicy,
    application_services: BondedApplicationServices,
) -> Result<()> {
    let ingress = Arc::new(
        bond_transport::BondIngress::publish_with_direct_tor(
            pool,
            identity,
            application_services.ssh_backend,
            scaling_policy,
        )
        .await?,
    );
    announce_route("tor", &identity.tor.destination)?;
    for router in pool.tor_slots() {
        let derived = identity
            .tor_pool
            .get(router.slot as usize - 1)
            .context("server identity omitted a Tor pool slot")?;
        announce_route(&format!("bond-tor-{}", router.slot), &derived.destination)?;
    }
    for router in pool.i2p_slots() {
        let derived = identity
            .i2p_pool
            .get(router.slot as usize - 1)
            .context("server identity omitted an I2P pool slot")?;
        announce_route(&format!("bond-i2p-{}", router.slot), &derived.destination)?;
    }

    let mut sessions = JoinSet::new();
    loop {
        let accepted = tokio::select! {
            accepted = ingress.accept_session() => accepted,
            completed = sessions.join_next(), if !sessions.is_empty() => {
                match completed {
                    Some(Ok(Ok(()))) => continue,
                    Some(Ok(Err(error))) => {
                        warn!("bonded SSH session failed: {error:#}");
                        continue;
                    }
                    Some(Err(error)) => {
                        warn!("bonded SSH session task failed: {error}");
                        continue;
                    }
                    None => continue,
                }
            }
        };
        let session = accepted?;
        let session_ingress = ingress.clone();
        let session_services = application_services.clone();
        sessions.spawn(async move {
            serve_bonded_ssh(
                session,
                session_ingress,
                session_services.ssh_backend,
                session_services.native_services,
            )
            .await
        });
    }
}

async fn serve_bonded_ssh(
    session: anonssh_bond_tokio::BondSession,
    ingress: Arc<bond_transport::BondIngress>,
    backend: SocketAddr,
    service_registry: Arc<native_service::NativeServiceRegistry>,
) -> Result<()> {
    let session_id = session.session_id();
    let session_control = session.control();
    let service_protocol =
        if session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
            let advertisement =
                tokio::time::timeout(Duration::from_secs(30), session.accept_capabilities())
                    .await
                    .context("client capability advertisement timed out")??;
            let intersection = ingress
                .apply_capability_request(&session_control, advertisement)
                .await?;
            intersection
                .features
                .contains(CapabilityFeatures::NATIVE_SERVICES)
        } else {
            false
        };
    if session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V6
        && !service_protocol
    {
        bail!("v6 bond peer did not negotiate native service streams");
    }
    let operation = async {
        tokio::try_join!(
            serve_bonded_ssh_streams(
                &session,
                backend,
                service_protocol,
                service_registry.clone(),
            ),
            serve_bonded_topology(&session, &session_control, &ingress),
        )?;
        Ok::<(), anyhow::Error>(())
    };
    let operation = operation.await;
    let shutdown = session.shutdown().await.map_err(anyhow::Error::from);
    let release = ingress.release_session(session_id).await;
    merge_cleanup(merge_cleanup(operation, shutdown), release)
}

async fn serve_bonded_ssh_streams(
    session: &anonssh_bond_tokio::BondSession,
    backend: SocketAddr,
    service_protocol: bool,
    service_registry: Arc<native_service::NativeServiceRegistry>,
) -> Result<()> {
    let mut relays = JoinSet::new();
    loop {
        tokio::select! {
            stream = session.accept_stream() => {
                let mut stream = stream?;
                let stream_id = stream.stream_id().get();
                if relays.len() >= MAX_SSH_STREAMS_PER_BOND_SESSION {
                    stream.reset(SSH_STREAM_REJECTED).await?;
                    warn!(stream_id, "rejected bond stream at concurrency limit");
                    continue;
                }
                let service_registry = service_registry.clone();
                relays.spawn(async move {
                    let result = dispatch_bonded_stream(
                        stream,
                        backend,
                        service_protocol,
                        service_registry,
                    )
                    .await;
                    (stream_id, result)
                });
            }
            completed = relays.join_next(), if !relays.is_empty() => {
                match completed {
                    Some(Ok((_, Ok(())))) => {}
                    Some(Ok((stream_id, Err(error)))) => {
                        warn!(stream_id, "bonded application stream failed: {error:#}");
                    }
                    Some(Err(error)) => warn!("bonded SSH stream task failed: {error}"),
                    None => {}
                }
            }
        }
    }
}

async fn dispatch_bonded_stream(
    mut stream: anonssh_bond_tokio::BondedStream,
    backend: SocketAddr,
    service_protocol: bool,
    service_registry: Arc<native_service::NativeServiceRegistry>,
) -> Result<()> {
    let stream_id = stream.stream_id().get();
    let requested_service = if service_protocol {
        match tokio::time::timeout(
            application_service::SETUP_TIMEOUT,
            application_service::read_service_request(&mut stream),
        )
        .await
        {
            Ok(Ok(service)) => Some(service),
            Ok(Err(error)) => {
                stream.reset(SSH_STREAM_REJECTED).await?;
                warn!(
                    stream_id,
                    "rejected malformed bond service request: {error:#}"
                );
                return Ok(());
            }
            Err(_) => {
                stream.reset(SSH_STREAM_REJECTED).await?;
                warn!(stream_id, "rejected timed-out bond service request");
                return Ok(());
            }
        }
    } else {
        None
    };
    let is_ssh = requested_service
        .as_ref()
        .is_none_or(|service| service.as_str() == application_service::SSH_SERVICE);
    if is_ssh && stream.traffic_class() != anonssh_bond::TrafficClass::Interactive {
        if service_protocol {
            application_service::reject_service(
                &mut stream,
                application_service::ServiceRejection::ClassDenied,
                "ssh requires interactive class",
            )
            .await?;
        }
        stream.reset(SSH_STREAM_REJECTED).await?;
        warn!(stream_id, "rejected non-interactive SSH bond stream");
        return Ok(());
    }
    if is_ssh {
        if service_protocol {
            application_service::accept_service(&mut stream).await?;
        }
        return relay_bonded_ssh_stream(stream, backend).await;
    }
    let Some(service) = requested_service.as_ref() else {
        bail!("native service dispatch lost its requested service");
    };
    let connection = match service_registry.connect(service).await {
        Ok(connection) => connection,
        Err(native_service::NativeServiceDialError::Unknown) => {
            application_service::reject_service(
                &mut stream,
                application_service::ServiceRejection::UnknownService,
                "service is not configured",
            )
            .await?;
            stream.shutdown().await?;
            return Ok(());
        }
        Err(native_service::NativeServiceDialError::Capacity) => {
            application_service::reject_service(
                &mut stream,
                application_service::ServiceRejection::Capacity,
                "service stream limit reached",
            )
            .await?;
            stream.shutdown().await?;
            return Ok(());
        }
        Err(native_service::NativeServiceDialError::Unavailable(error)) => {
            application_service::reject_service(
                &mut stream,
                application_service::ServiceRejection::Unavailable,
                "service is unavailable",
            )
            .await?;
            stream.shutdown().await?;
            warn!(stream_id, "native service unavailable: {error:#}");
            return Ok(());
        }
    };
    application_service::accept_service(&mut stream).await?;
    relay_bonded_native_stream(stream, connection).await
}

async fn relay_bonded_native_stream(
    mut stream: anonssh_bond_tokio::BondedStream,
    mut service: native_service::NativeServiceConnection,
) -> Result<()> {
    data_stream::relay_bidirectional(&mut stream, &mut service.stream).await?;
    stream.shutdown().await?;
    Ok(())
}

async fn relay_bonded_ssh_stream(
    mut stream: anonssh_bond_tokio::BondedStream,
    backend: SocketAddr,
) -> Result<()> {
    let mut backend = data_stream::connect(backend)
        .await
        .context("failed to connect and configure the local SSH backend")?;
    data_stream::relay_bidirectional(&mut stream, &mut backend).await?;
    stream.shutdown().await?;
    Ok(())
}

async fn serve_bonded_topology(
    session: &anonssh_bond_tokio::BondSession,
    session_control: &anonssh_bond_tokio::BondSessionControl,
    ingress: &bond_transport::BondIngress,
) -> Result<()> {
    loop {
        if session.protocol_version() >= anonssh_bond_tokio::BondProtocolVersion::V4 {
            tokio::select! {
                advertisement = session.accept_capabilities() => {
                    ingress
                        .apply_capability_request(session_control, advertisement?)
                        .await?;
                }
                advertisement = session.accept_topology() => {
                    ingress
                        .apply_topology_request(session_control, advertisement?)
                        .await?;
                }
            }
        } else {
            ingress
                .apply_topology_request(session_control, session.accept_topology().await?)
                .await?;
        }
    }
}

#[derive(Clone, Copy)]
struct ServerRouters<'a> {
    i2pd: Option<&'a I2pdManager>,
    tor: Option<&'a TorManager>,
}

async fn run_server(
    config: &AppConfig,
    machine_id: &str,
    transport: ServerTransport,
    backend: SocketAddr,
    ssh_programs: SshServerPrograms<'_>,
    identity: crate::identity::DerivedServerRecoveryIdentity,
    routers: ServerRouters<'_>,
) -> Result<()> {
    if let Some(i2pd) = routers.i2pd {
        i2pd.ensure_running().await.context("failed to start I2P")?;
    }
    let tor_control = if transport.uses_tor() {
        let tor = routers.tor.context("Tor manager was not initialized")?;
        tor.ensure_running().await.context("failed to start Tor")?;
        Some(tor.control_endpoint().await?)
    } else {
        None
    };

    let mut ssh_backend = SshBackend::start(config, machine_id, &identity, ssh_programs, backend)
        .await
        .context("failed to start recovery SSH backend")?;
    let operation =
        publish_and_serve(transport, backend, identity, tor_control, &mut ssh_backend).await;
    merge_cleanup(operation, ssh_backend.shutdown().await)
}

async fn publish_and_serve(
    transport: ServerTransport,
    backend: SocketAddr,
    identity: crate::identity::DerivedServerRecoveryIdentity,
    tor_control: Option<TorControlEndpoint>,
    ssh_backend: &mut SshBackend,
) -> Result<()> {
    let i2p_listener = if transport.uses_i2p() {
        let destination = identity.i2p.destination.trim_start_matches("i2p://");
        Some(
            SamListener::bind_zeroizing(
                sam_endpoint()?.to_string(),
                recovery_session_id(destination),
                identity.i2p.private_key.clone(),
            )
            .await
            .context("failed to publish I2P destination")?,
        )
    } else {
        None
    };
    let tor_service = if let Some(control) = tor_control {
        Some(
            TorListener::new(control)
                .listen_with_key(
                    22,
                    &backend.to_string(),
                    &identity.tor.destination,
                    &identity.tor.control_private_key,
                )
                .await
                .context("failed to publish Tor destination")?,
        )
    } else {
        None
    };

    if transport.uses_i2p() {
        announce_route("i2p", &identity.i2p.destination)?;
    }
    if transport.uses_tor() {
        announce_route("tor", &identity.tor.destination)?;
    }
    drop(identity);

    let (ingress_stop, ingress_stop_rx) = oneshot::channel();
    let mut ingress = tokio::spawn(async move {
        match i2p_listener {
            Some(listener) => {
                recovery_server_ingress::run(listener, backend, ingress_stop_rx).await
            }
            None => {
                let _ = ingress_stop_rx.await;
                Ok(())
            }
        }
    });
    let mut tor_task = tokio::spawn(wait_for_tor_service(tor_service));

    let operation = tokio::select! {
        signal = shutdown_signal() => signal.context("failed to wait for shutdown signal"),
        result = ssh_backend.wait_for_exit() => result,
        result = &mut ingress => match result {
            Ok(Ok(())) => bail_result("I2P ingress stopped unexpectedly"),
            Ok(Err(error)) => Err(error.context("I2P ingress failed")),
            Err(error) => Err(anyhow::anyhow!("I2P ingress task failed: {error}")),
        },
        result = &mut tor_task => match result {
            Ok(Ok(())) => bail_result("Tor service stopped unexpectedly"),
            Ok(Err(error)) => Err(error.context("Tor service failed")),
            Err(error) => Err(anyhow::anyhow!("Tor service task failed: {error}")),
        },
    };

    let _ = ingress_stop.send(());
    ingress.abort();
    let _ = ingress.await;
    tor_task.abort();
    let _ = tor_task.await;
    operation
}

fn announce_route(label: &str, destination: &str) -> Result<()> {
    let mut stdout = std::io::stdout().lock();
    if let Err(error) = writeln!(stdout, "{label} {destination}") {
        if error.kind() == std::io::ErrorKind::BrokenPipe {
            return Ok(());
        }
        return Err(error.into());
    }
    match stdout.flush() {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::BrokenPipe => Ok(()),
        Err(error) => Err(error.into()),
    }
}

async fn wait_for_tor_service(service: Option<PublishedTorService>) -> Result<()> {
    match service {
        Some(mut service) => service.wait_closed().await,
        None => std::future::pending().await,
    }
}

fn bail_result(message: &str) -> Result<()> {
    Err(anyhow::anyhow!(message.to_string()))
}

async fn proxy(transport: ProxyTransport, destination: &str, endpoint: &str) -> Result<()> {
    match transport {
        ProxyTransport::I2p => proxy::i2p(destination, endpoint).await,
        ProxyTransport::Tor => proxy::tor(destination, endpoint).await,
    }
}

async fn bond_proxy(
    tor_destinations: &[String],
    i2p_destinations: &[String],
    key_file: &std::path::Path,
    resource_profile: product_config::ResourceProfile,
    external_tor_services: &[ExternalTorService],
) -> Result<()> {
    if !direct_bond_proxy_required() {
        return bond_broker::proxy(
            tor_destinations,
            i2p_destinations,
            key_file,
            resource_profile,
        )
        .await;
    }
    direct_bond_proxy(
        tor_destinations,
        i2p_destinations,
        key_file,
        resource_profile.policy(),
        external_tor_services,
    )
    .await
}

fn direct_bond_proxy_required() -> bool {
    [
        "ANONSSH_INTERNAL_TEST_FAIL_BOND",
        "ANONSSH_INTERNAL_TEST_BOND_STATS_ARTIFACT",
        "ANONSSH_INTERNAL_TEST_REPLACE_I2P_SLOT",
        "ANONSSH_INTERNAL_TEST_REPLACEMENT_ARTIFACT",
    ]
    .iter()
    .any(|name| std::env::var_os(name).is_some())
}

async fn direct_bond_proxy(
    tor_destinations: &[String],
    i2p_destinations: &[String],
    key_file: &std::path::Path,
    scaling_policy: product_config::ScalingPolicy,
    external_tor_services: &[ExternalTorService],
) -> Result<()> {
    if std::env::var_os("ANONSSH_INTERNAL_TEST_FAIL_BOND").is_some() {
        bail!("injected bond startup failure");
    }
    let replacement_probe = replacement_probe_from_env()?;
    let stats_artifact = bond_stats_artifact_from_env()?;
    let encoded_key =
        Zeroizing::new(std::fs::read(key_file).context("failed to read the ephemeral bond key")?);
    if encoded_key.len() != 32 {
        bail!("ephemeral bond key has an invalid length");
    }
    let mut key = Zeroizing::new([0_u8; 32]);
    key.copy_from_slice(&encoded_key);
    drop(encoded_key);

    let config = AppConfig::new()?;
    let pool = router_pool::RouterPool::production_client(
        &config,
        (!tor_destinations.is_empty())
            .then(|| resolve_executable("ANONSSH_TOR_BIN", "tor"))
            .transpose()
            .context("Tor is unavailable")?,
        (!i2p_destinations.is_empty())
            .then(|| resolve_executable("ANONSSH_I2PD_BIN", "i2pd"))
            .transpose()
            .context("i2pd is unavailable")?,
        external_tor_services,
    )?;
    let operation = async {
        let tor_socks = if pool.tor_slots().is_empty() {
            pool.ensure_i2p_slot(1).await?;
            Vec::new()
        } else {
            vec![pool.ensure_tor_slot(1).await?]
        };
        let client = bond_transport::ClientBondSession::connect_with_scaling_policy(
            &pool,
            &tor_socks,
            tor_destinations,
            i2p_destinations,
            *key,
            scaling_policy,
        )
        .await?;
        let stream = client.open_ssh_stream().await?;
        let relay = {
            let relay = proxy::bond(stream);
            let supervision = supervise_client_bond(&client, &pool, replacement_probe);
            let stats = observe_bond_stats(stats_artifact.as_deref(), &client, &pool);
            tokio::select! {
                result = relay => result,
                result = supervision => result,
                result = stats => result,
            }
        };
        merge_cleanup(relay, client.shutdown().await)
    }
    .await;
    merge_cleanup(operation, pool.stop().await)
}

fn bond_stats_artifact_from_env() -> Result<Option<PathBuf>> {
    let Some(path) = std::env::var_os("ANONSSH_INTERNAL_TEST_BOND_STATS_ARTIFACT") else {
        return Ok(None);
    };
    let path = PathBuf::from(path);
    if !path.is_absolute() {
        bail!("internal bond statistics artifact must be absolute");
    }
    Ok(Some(path))
}

fn write_bond_stats_artifact(
    path: &std::path::Path,
    stats: &anonssh_bond_tokio::BondRuntimeStats,
    processes: &[router_pool::RouterProcessSample],
    reserved_lanes_with_scheduled_bytes: &BTreeSet<u32>,
    scaling: &bond_transport::AdaptiveScalingProgress,
    observation: u64,
) -> Result<()> {
    let lanes = stats
        .lanes
        .iter()
        .map(|lane| {
            serde_json::json!({
                "id": lane.id.get(),
                "active": lane.active,
                "delivery_measured": lane.delivery_measured,
                "reserved_for_low_latency": lane.reserved_for_low_latency,
                "round_trip_micros": u64::try_from(lane.smoothed_round_trip_time.as_micros())
                    .unwrap_or(u64::MAX),
                "delivery_rate_bps": lane.delivery_rate_bps,
                "queue_delay_micros": u64::try_from(
                    lane.queued_through
                        .duration_since(stats.observed_at)
                        .unwrap_or_default()
                        .as_micros()
                ).unwrap_or(u64::MAX),
                "bytes_scheduled": lane.bytes_scheduled,
                "bytes_acknowledged": lane.bytes_acknowledged,
            })
        })
        .collect::<Vec<_>>();
    let processes = processes
        .iter()
        .map(|process| {
            serde_json::json!({
                "provider": match process.provider {
                    router_pool::RouterProvider::Tor => "tor",
                    router_pool::RouterProvider::I2p => "i2p",
                },
                "slot": process.slot,
                "running": process.usage.is_some(),
                "cpu_time_micros": process.usage.map(|usage| {
                    u64::try_from(usage.cpu_time.as_micros()).unwrap_or(u64::MAX)
                }),
                "resident_bytes": process.usage.map(|usage| usage.resident_bytes),
                "startup_millis": process.startup_latency.map(|latency| {
                    u64::try_from(latency.as_millis()).unwrap_or(u64::MAX)
                }),
            })
        })
        .collect::<Vec<_>>();
    let scaling_events = scaling
        .events
        .iter()
        .map(|event| {
            serde_json::json!({
                "generation": event.generation,
                "elapsed_millis": event.elapsed_millis,
                "learned_generation": event.learned.generation,
                "paths_with_evidence": event.learned.paths_with_evidence,
                "average_confidence": event.learned.average_confidence,
                "scale_up_queue_millis": event.learned.scale_up_queue_millis,
                "scale_down_queue_millis": event.learned.scale_down_queue_millis,
                "minimum_marginal_goodput_bps": event.learned.minimum_marginal_goodput_bps,
                "replacement_gain_percent": event.learned.replacement_gain_percent,
                "maximum_startup_millis": event.learned.maximum_startup_millis,
                "next_control_interval_millis": event.learned.next_control_interval_millis,
                "exploration_lane_id": event.learned.exploration_lane_id,
                "actions": event.actions.iter().copied().map(scaling_action_json).collect::<Vec<_>>(),
            })
        })
        .collect::<Vec<_>>();
    let temporary = path.with_extension("tmp");
    std::fs::write(
        &temporary,
        serde_json::to_vec(&serde_json::json!({
            "schema": "anonssh.internal-bond-stats.v9",
            "observation": observation,
            "lanes": lanes,
            "router_processes": processes,
            "reserved_lanes_with_scheduled_bytes": reserved_lanes_with_scheduled_bytes,
            "new_data_frames": stats.new_data_frames,
            "redundant_realtime_frames": stats.redundant_realtime_frames,
            "dropped_redundant_realtime_frames": stats.dropped_redundant_realtime_frames,
            "retransmitted_frames": stats.retransmitted_frames,
            "ping_frames": stats.ping_frames,
            "pong_frames": stats.pong_frames,
            "liveness_failures": stats.liveness_failures,
            "replayed_control_frames": stats.replayed_control_frames,
            "unacknowledged_bytes": stats.unacknowledged_bytes,
            "send_window_utilization_percent":
                bond_transport::send_window_utilization_percent(stats.unacknowledged_bytes),
            "backpressured_streams": stats.backpressured_streams,
            "stream_backpressure_events": stats.stream_backpressure_events,
            "active_streams": stats.active_streams,
            "retired_stream_tombstones": stats.retired_stream_tombstones,
            "adaptive_scaling": {
                "observed_millis": scaling.observed_millis,
                "desired_lane_ids": &scaling.desired_lane_ids,
                "pending_pressure_lane_ids": &scaling.pending_pressure_lane_ids,
                "learned": {
                    "generation": scaling.learned.generation,
                    "paths_with_evidence": scaling.learned.paths_with_evidence,
                    "average_confidence": scaling.learned.average_confidence,
                    "scale_up_queue_millis": scaling.learned.scale_up_queue_millis,
                    "scale_down_queue_millis": scaling.learned.scale_down_queue_millis,
                    "minimum_marginal_goodput_bps": scaling.learned.minimum_marginal_goodput_bps,
                    "replacement_gain_percent": scaling.learned.replacement_gain_percent,
                    "maximum_startup_millis": scaling.learned.maximum_startup_millis,
                    "next_control_interval_millis": scaling.learned.next_control_interval_millis,
                    "exploration_lane_id": scaling.learned.exploration_lane_id,
                },
                "events": scaling_events,
            },
        }))?,
    )
    .with_context(|| {
        format!(
            "failed to write internal bond statistics artifact {}",
            temporary.display()
        )
    })?;
    std::fs::rename(&temporary, path).with_context(|| {
        format!(
            "failed to publish internal bond statistics artifact {}",
            path.display()
        )
    })
}

fn scaling_action_json(action: ScalingAction) -> serde_json::Value {
    match action {
        ScalingAction::Hold => serde_json::json!({ "kind": "hold" }),
        ScalingAction::Admit { lane_id, reason } => serde_json::json!({
            "kind": "admit",
            "lane_id": lane_id.get(),
            "reason": scaling_reason_label(reason),
        }),
        ScalingAction::Drain { lane_id, reason } => serde_json::json!({
            "kind": "drain",
            "lane_id": lane_id.get(),
            "reason": scaling_reason_label(reason),
        }),
        ScalingAction::Replace {
            remove,
            admit,
            reason,
        } => serde_json::json!({
            "kind": "replace",
            "remove_lane_id": remove.get(),
            "admit_lane_id": admit.get(),
            "reason": scaling_reason_label(reason),
        }),
    }
}

const fn scaling_reason_label(reason: ScalingReason) -> &'static str {
    match reason {
        ScalingReason::MinimumTopology => "minimum-topology",
        ScalingReason::ProviderDiversity => "provider-diversity",
        ScalingReason::QueuePressure => "queue-pressure",
        ScalingReason::ResourcePressure => "resource-pressure",
        ScalingReason::MarginalGoodput => "marginal-goodput",
        ScalingReason::Unhealthy => "unhealthy",
        ScalingReason::BetterCandidate => "better-candidate",
        ScalingReason::PressureCleared => "pressure-cleared",
        ScalingReason::Exploration => "exploration",
    }
}

async fn observe_bond_stats(
    path: Option<&std::path::Path>,
    client: &bond_transport::ClientBondSession,
    pool: &router_pool::RouterPool,
) -> Result<()> {
    let Some(path) = path else {
        return std::future::pending().await;
    };
    let mut reserved_lanes_with_scheduled_bytes = BTreeSet::new();
    let mut observation = 0_u64;
    loop {
        let stats = client.session().statistics().await?;
        let processes = pool.process_samples().await?;
        let scaling = client.scaling_progress()?;
        observation = observation
            .checked_add(1)
            .context("bond statistics observation sequence overflowed")?;
        reserved_lanes_with_scheduled_bytes.extend(
            stats
                .lanes
                .iter()
                .filter(|lane| lane.reserved_for_low_latency && lane.bytes_scheduled > 0)
                .map(|lane| lane.id.get()),
        );
        write_bond_stats_artifact(
            path,
            &stats,
            &processes,
            &reserved_lanes_with_scheduled_bytes,
            &scaling,
            observation,
        )?;
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
}

struct ReplacementProbe {
    slot: u32,
    artifact: PathBuf,
}

fn replacement_probe_from_env() -> Result<Option<ReplacementProbe>> {
    let slot = std::env::var("ANONSSH_INTERNAL_TEST_REPLACE_I2P_SLOT");
    let artifact = std::env::var_os("ANONSSH_INTERNAL_TEST_REPLACEMENT_ARTIFACT");
    match (slot, artifact) {
        (Err(std::env::VarError::NotPresent), None) => Ok(None),
        (Ok(slot), Some(artifact)) => {
            let slot = slot
                .parse::<u32>()
                .context("invalid internal replacement-probe slot")?;
            if slot == 0 {
                bail!("internal replacement-probe slot must be non-zero");
            }
            let artifact = PathBuf::from(artifact);
            if !artifact.is_absolute() {
                bail!("internal replacement-probe artifact must be absolute");
            }
            Ok(Some(ReplacementProbe { slot, artifact }))
        }
        _ => bail!("internal replacement probe requires both slot and artifact variables"),
    }
}

async fn supervise_client_bond(
    client: &bond_transport::ClientBondSession,
    pool: &router_pool::RouterPool,
    replacement_probe: Option<ReplacementProbe>,
) -> Result<()> {
    if let Some(probe) = replacement_probe {
        tokio::time::sleep(Duration::from_secs(20)).await;
        client.repair_i2p_lane(pool, probe.slot).await?;
        let stats = client.session().statistics().await?;
        let lane_id = bond_transport::i2p_lane_id(pool, probe.slot)?;
        let lane = stats
            .lanes
            .iter()
            .find(|lane| lane.id == lane_id)
            .context("replacement probe lane is absent from the client runtime")?;
        if !lane.active {
            bail!("replacement probe lane did not return to active service");
        }
        std::fs::write(
            &probe.artifact,
            serde_json::to_vec(&serde_json::json!({
                "schema": "anonssh.internal-replacement.v1",
                "session_id": client.session().session_id(),
                "slot": probe.slot,
                "lane": lane_id.get(),
                "active": lane.active,
            }))?,
        )
        .with_context(|| {
            format!(
                "failed to write internal replacement artifact {}",
                probe.artifact.display()
            )
        })?;
    }
    client.maintain_lanes(pool).await
}

fn identity_password(prompt: &str) -> Result<Zeroizing<String>> {
    IdentityManager::prompt_passphrase(prompt)
}

fn parse_recovery_target(raw: &str) -> Result<RecoveryTarget> {
    let (user, machine_id) = raw
        .split_once('@')
        .context("target must be user@machine-id")?;
    if machine_id.contains('@') {
        bail!("target must contain exactly one '@'")
    }
    validate_component("SSH user", user, 64)?;
    validate_component("machine ID", machine_id, 253)?;
    Ok(RecoveryTarget {
        user: user.to_string(),
        machine_id: machine_id.to_string(),
    })
}

fn validate_component(label: &str, value: &str, max_len: usize) -> Result<()> {
    let valid = !value.is_empty()
        && value.len() <= max_len
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-' | b'_'))
        && value
            .as_bytes()
            .first()
            .is_some_and(u8::is_ascii_alphanumeric);
    if !valid {
        bail!("invalid {label}: use ASCII letters, digits, '.', '-', and '_'")
    }
    Ok(())
}

fn current_executable() -> Result<PathBuf> {
    let path = std::env::current_exe().context("failed to resolve anonssh executable")?;
    if !path.is_absolute() || !path.is_file() {
        bail!("anonssh executable is not an absolute file")
    }
    Ok(path)
}

fn recovery_session_id(destination: &str) -> String {
    let digest = Sha256::digest(destination.as_bytes());
    let suffix = digest[..10]
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<String>();
    format!("anonssh-{suffix}")
}

async fn stop_routers(i2pd: Option<&I2pdManager>, tor: Option<&TorManager>) -> Result<()> {
    let stop_i2p = async {
        match i2pd {
            Some(router) => router.stop().await,
            None => Ok(()),
        }
    };
    let stop_tor = async {
        match tor {
            Some(router) => router.stop().await,
            None => Ok(()),
        }
    };
    let (i2p, tor) = tokio::join!(stop_i2p, stop_tor);
    merge_cleanup(
        i2p.context("failed to stop I2P"),
        tor.context("failed to stop Tor"),
    )
}

fn shell_word(value: &str) -> String {
    format!("'{}'", value.replace('\'', "'\\''"))
}

fn print_doctor(report: &diagnostics::DoctorReport) {
    println!(
        "ok   config   {:?}/{:?}; max {} lanes, +{}/-{} per {} ms ({})",
        report.configuration.resource_profile,
        report.configuration.transport_profile,
        report.configuration.scaling.maximum_active_lanes,
        report.configuration.scaling.maximum_admissions_per_interval,
        report.configuration.scaling.maximum_drains_per_interval,
        report.configuration.scaling.control_interval_millis,
        report.configuration.source,
    );
    for dependency in &report.dependencies {
        if dependency.available {
            println!(
                "ok   {:8} {}",
                dependency.name,
                dependency
                    .path
                    .as_deref()
                    .map(|path| path.display().to_string())
                    .unwrap_or_default()
            );
        } else if dependency.required {
            println!(
                "fail {:8} {}",
                dependency.name,
                dependency.error.as_deref().unwrap_or("unavailable")
            );
        } else {
            println!(
                "info {:8} optional for the effective transport profile ({})",
                dependency.name,
                dependency.error.as_deref().unwrap_or("unavailable")
            );
        }
    }
    println!(
        "{} bond     {} Tor slots/{} candidates + {} I2P slots; baseline lanes {:?} ({})",
        if report.bond_topology.valid {
            "ok  "
        } else {
            "fail"
        },
        report.bond_topology.tor_slots,
        report.bond_topology.tor_candidates,
        report.bond_topology.i2p_slots,
        report.bond_topology.baseline_lane_ids,
        report.bond_topology.detail
    );
    println!(
        "{} i2p-sam {} ({})",
        if report.i2p_sam.enabled && report.i2p_sam.reachable {
            "ok  "
        } else {
            "info"
        },
        report.i2p_sam.endpoint,
        report.i2p_sam.detail
    );
    println!(
        "{} tor-socks {} ({})",
        if report.tor_socks.enabled && report.tor_socks.reachable {
            "ok  "
        } else {
            "info"
        },
        report.tor_socks.endpoint,
        report.tor_socks.detail
    );
}

fn print_service_status(status: &service::ServiceStatus) {
    if !status.installed {
        println!("service not installed");
        if status.broker_runtime.running {
            println!("broker running outside the installed service lifecycle");
        }
        return;
    }
    println!(
        "service installed: machine={}, transport={}, credential={}/{}",
        status.machine_id.as_deref().unwrap_or("unknown"),
        status.server_transport.as_deref().unwrap_or("unknown"),
        status.credential_policy,
        status.credential_state,
    );
    println!(
        "server {}/{} pid={}; broker {}/{} pid={}",
        status.server.active_state,
        status.server.sub_state,
        status.server.main_pid.unwrap_or_default(),
        status.broker.active_state,
        status.broker.sub_state,
        status.broker.main_pid.unwrap_or_default(),
    );
    println!(
        "topology={} dependencies={} broker-runtime={}",
        if status.topology_valid {
            "valid"
        } else {
            "invalid"
        },
        if status.runtime_dependencies_ready {
            "ready"
        } else {
            "incomplete"
        },
        if status.broker_runtime.running {
            "running"
        } else {
            "stopped"
        },
    );
    if let Some(error) = status.credential_error.as_deref() {
        println!("credential: {error}");
    }
    if let Some(error) = status.server.error.as_deref() {
        println!("server manager: {error}");
    }
    if let Some(error) = status.broker.error.as_deref() {
        println!("broker manager: {error}");
    }
}

fn merge_cleanup<T>(operation: Result<T>, cleanup: Result<()>) -> Result<T> {
    match (operation, cleanup) {
        (Ok(value), Ok(())) => Ok(value),
        (Err(error), Ok(())) => Err(error),
        (Ok(_), Err(error)) => Err(error),
        (Err(operation), Err(cleanup)) => Err(anyhow::anyhow!(
            "{operation:#}; cleanup also failed: {cleanup:#}"
        )),
    }
}

async fn shutdown_signal() -> std::io::Result<()> {
    #[cfg(unix)]
    {
        let mut terminate =
            tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())?;
        tokio::select! {
            result = tokio::signal::ctrl_c() => result,
            signal = terminate.recv() => signal.map(|_| ()).ok_or_else(|| {
                std::io::Error::other("termination signal stream closed")
            }),
        }
    }
    #[cfg(not(unix))]
    tokio::signal::ctrl_c().await
}

#[cfg(test)]
mod tests {
    use std::ffi::OsString;
    use std::fs;
    use std::os::unix::fs::PermissionsExt;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};
    use std::sync::{Arc, Mutex};
    use std::time::Duration;

    #[cfg(unix)]
    use std::os::unix::process::ExitStatusExt;

    use anonssh_bond::{
        FailureDomain, LaneConfig, LaneId, SchedulerConfig, SenderConfig, TrafficClass,
    };
    use anonssh_bond_tokio::{
        authenticate_client_lane, authenticate_server_lane, BondRuntimeConfig, BondSession,
        BondSessionKey, LaneJoin, RuntimeLane, SessionRole,
    };
    use clap::{CommandFactory, Parser};
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::{TcpListener, UnixListener};

    use super::{
        client_route_order, configured_client_transport, configured_server_transport,
        merge_cleanup, normalize_cli_args, parse_recovery_target, resolve_client_dependencies,
        resolve_server_dependencies, serve_bonded_ssh_streams, ssh_exit_succeeded,
        transport_profile_for_server, Cli, ClientTransport, Command, ServerTransport,
        SshExitStatus, SSH_STREAM_REJECTED,
    };
    use crate::product_config::TransportProfile;
    use crate::ssh::SshInvocation;

    static ENVIRONMENT: Mutex<()> = Mutex::new(());
    static SOCKET_SEQUENCE: AtomicU64 = AtomicU64::new(1);

    #[test]
    fn bare_recovery_target_is_the_connect_command() {
        let cli = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("h0p3@m16"),
        ]))
        .unwrap();
        match cli.command {
            Command::Connect {
                target,
                transport,
                ssh_args,
            } => {
                assert_eq!(target, "h0p3@m16");
                assert_eq!(transport, None);
                assert!(ssh_args.is_empty());
            }
            _ => panic!("bare recovery target did not select connect"),
        }
    }

    #[test]
    fn verbose_bare_recovery_target_is_the_connect_command() {
        let cli = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("--verbose"),
            OsString::from("h0p3@m16"),
        ]))
        .unwrap();
        assert!(cli.verbose);
        assert!(matches!(cli.command, Command::Connect { .. }));
    }

    #[test]
    fn remote_shell_shorthand_preserves_rsync_command_arguments() {
        let cli = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("-T"),
            OsString::from("-l"),
            OsString::from("alice"),
            OsString::from("home"),
            OsString::from("rsync"),
            OsString::from("--server"),
            OsString::from("--sender"),
            OsString::from("."),
            OsString::from("path with spaces"),
        ]))
        .unwrap();
        let Command::Connect {
            target,
            transport,
            ssh_args,
        } = cli.command
        else {
            panic!("remote-shell form did not select connect");
        };
        assert_eq!(target, "alice@home");
        assert_eq!(transport, None);
        let invocation = SshInvocation::parse(&ssh_args).unwrap();
        assert_eq!(invocation.options(), [OsString::from("-T")]);
        assert_eq!(
            invocation.remote_command(),
            [
                OsString::from("rsync"),
                OsString::from("--server"),
                OsString::from("--sender"),
                OsString::from("."),
                OsString::from("path with spaces"),
            ]
        );
    }

    #[test]
    fn remote_shell_double_dash_is_a_separator_not_a_command_argument() {
        let cli = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("alice@home"),
            OsString::from("--"),
            OsString::from("-remote-command"),
            OsString::from("value"),
        ]))
        .unwrap();
        let Command::Connect { ssh_args, .. } = cli.command else {
            panic!("remote-shell form did not select connect");
        };
        let invocation = SshInvocation::parse(&ssh_args).unwrap();
        assert_eq!(
            invocation.remote_command(),
            [OsString::from("-remote-command"), OsString::from("value")]
        );
    }

    #[test]
    fn openssh_file_transfer_clients_use_the_remote_shell_contract() {
        let sftp = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("-oForwardX11 no"),
            OsString::from("-oPermitLocalCommand no"),
            OsString::from("-oClearAllForwardings yes"),
            OsString::from("-oControlMaster no"),
            OsString::from("-s"),
            OsString::from("-l"),
            OsString::from("alice"),
            OsString::from("--"),
            OsString::from("home"),
            OsString::from("sftp"),
        ]))
        .unwrap();
        let Command::Connect {
            target, ssh_args, ..
        } = sftp.command
        else {
            panic!("SFTP remote-shell form did not select connect");
        };
        assert_eq!(target, "alice@home");
        let invocation = SshInvocation::parse(&ssh_args).unwrap();
        assert_eq!(invocation.remote_command(), [OsString::from("sftp")]);
        assert!(invocation.options().contains(&OsString::from("-s")));

        let scp = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("-x"),
            OsString::from("-oPermitLocalCommand=no"),
            OsString::from("-oClearAllForwardings=yes"),
            OsString::from("-oRemoteCommand=none"),
            OsString::from("-oRequestTTY=no"),
            OsString::from("-oControlMaster=no"),
            OsString::from("-s"),
            OsString::from("--"),
            OsString::from("alice@home"),
            OsString::from("sftp"),
        ]))
        .unwrap();
        let Command::Connect { ssh_args, .. } = scp.command else {
            panic!("scp remote-shell form did not select connect");
        };
        assert!(SshInvocation::parse(&ssh_args).is_ok());
    }

    #[test]
    fn protected_remote_shell_options_reach_fail_closed_validation() {
        let cli = Cli::try_parse_from(normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("-p"),
            OsString::from("2222"),
            OsString::from("alice@home"),
            OsString::from("true"),
        ]))
        .unwrap();
        let Command::Connect { ssh_args, .. } = cli.command else {
            panic!("remote-shell form did not select connect");
        };
        assert!(SshInvocation::parse(&ssh_args).is_err());
    }

    #[test]
    fn top_level_help_advertises_direct_recovery() {
        let mut help = Vec::new();
        Cli::command().write_long_help(&mut help).unwrap();
        let help = String::from_utf8(help).unwrap();
        assert!(help.contains("anonssh [SAFE-SSH-OPTIONS] <USER@MACHINE-ID> [COMMAND ...]"));
        assert!(help.contains("Quick connect: anonssh user@machine-id"));
        assert!(help.contains("forward"));
    }

    #[test]
    fn named_forward_has_explicit_endpoints_and_transport() {
        let cli = Cli::try_parse_from([
            "anonssh",
            "forward",
            "h0p3@m16",
            "--listen",
            "127.0.0.1:8022",
            "--remote",
            "localhost:22",
            "--transport",
            "bond-tor",
        ])
        .unwrap();
        match cli.command {
            Command::Forward {
                target,
                listen,
                remote,
                transport,
            } => {
                assert_eq!(target, "h0p3@m16");
                assert_eq!(listen, "127.0.0.1:8022".parse().unwrap());
                assert_eq!(remote, "localhost:22");
                assert_eq!(transport, Some(ClientTransport::BondTor));
            }
            _ => panic!("named forward did not select the forwarding command"),
        }
    }

    #[test]
    fn shorthand_preserves_commands_and_strict_target_validation() {
        let doctor = normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("doctor"),
            OsString::from("--json"),
        ]);
        assert_eq!(
            doctor,
            [
                OsString::from("anonssh"),
                OsString::from("doctor"),
                OsString::from("--json")
            ]
        );

        let malformed = normalize_cli_args([
            OsString::from("anonssh"),
            OsString::from("alice@home@other"),
        ]);
        assert_eq!(malformed[1], "connect");
        assert!(parse_recovery_target(malformed[2].to_str().unwrap()).is_err());
    }

    #[cfg(unix)]
    #[test]
    fn intentional_internal_control_master_shutdown_accepts_openssh_255_only() {
        let success = std::process::ExitStatus::from_raw(0);
        let openssh_control_exit = std::process::ExitStatus::from_raw(255 << 8);
        let unrelated_failure = std::process::ExitStatus::from_raw(1 << 8);

        assert!(ssh_exit_succeeded(&success, false));
        assert!(!ssh_exit_succeeded(&openssh_control_exit, false));
        assert!(ssh_exit_succeeded(&openssh_control_exit, true));
        assert!(!ssh_exit_succeeded(&unrelated_failure, true));
        assert_eq!(SshExitStatus(unrelated_failure).process_code(), 1);
    }

    struct EnvironmentVariable {
        name: &'static str,
        previous: Option<OsString>,
    }

    impl EnvironmentVariable {
        fn set(name: &'static str, value: &std::path::Path) -> Self {
            let previous = std::env::var_os(name);
            std::env::set_var(name, value);
            Self { name, previous }
        }
    }

    impl Drop for EnvironmentVariable {
        fn drop(&mut self) {
            match &self.previous {
                Some(value) => std::env::set_var(self.name, value),
                None => std::env::remove_var(self.name),
            }
        }
    }

    #[test]
    fn transport_modes_ignore_unrelated_runtime_dependencies() {
        let _lock = ENVIRONMENT.lock().unwrap();
        let executable = std::env::current_exe().unwrap();
        let missing = PathBuf::from("/anonssh-test/missing-executable");
        let _ssh = EnvironmentVariable::set("ANONSSH_SSH_BIN", &executable);
        let _dropbear = EnvironmentVariable::set("ANONSSH_DROPBEAR_BIN", &executable);
        let _sftp_server = EnvironmentVariable::set("ANONSSH_SFTP_SERVER_BIN", &executable);
        let _scp = EnvironmentVariable::set("ANONSSH_SCP_BIN", &executable);

        let i2pd = EnvironmentVariable::set("ANONSSH_I2PD_BIN", &executable);
        let tor = EnvironmentVariable::set("ANONSSH_TOR_BIN", &missing);
        assert!(resolve_client_dependencies(ClientTransport::I2p).is_ok());
        let i2p_bond = resolve_client_dependencies(ClientTransport::BondI2p).unwrap();
        assert!(i2p_bond.i2pd.is_some());
        assert!(i2p_bond.tor.is_none());
        let i2p_server = resolve_server_dependencies(ServerTransport::I2p, None).unwrap();
        assert!(i2p_server.i2pd.is_some());
        assert!(i2p_server.tor.is_none());
        let i2p_bond_server = resolve_server_dependencies(ServerTransport::BondI2p, None).unwrap();
        assert!(i2p_bond_server.i2pd.is_some());
        assert!(i2p_bond_server.tor.is_none());
        drop(i2pd);
        drop(tor);

        let _i2pd = EnvironmentVariable::set("ANONSSH_I2PD_BIN", &missing);
        let _tor = EnvironmentVariable::set("ANONSSH_TOR_BIN", &executable);
        assert!(resolve_client_dependencies(ClientTransport::Tor).is_ok());
        let tor_bond = resolve_client_dependencies(ClientTransport::BondTor).unwrap();
        assert!(tor_bond.i2pd.is_none());
        assert!(tor_bond.tor.is_some());
        let tor_server = resolve_server_dependencies(ServerTransport::Tor, None).unwrap();
        assert!(tor_server.i2pd.is_none());
        assert!(tor_server.tor.is_some());
        let tor_bond_server = resolve_server_dependencies(ServerTransport::BondTor, None).unwrap();
        assert!(tor_bond_server.i2pd.is_none());
        assert!(tor_bond_server.tor.is_some());
    }

    #[test]
    fn explicit_transport_routes_remain_singular() {
        assert!(client_route_order(ClientTransport::Auto).is_empty());
        assert_eq!(
            client_route_order(ClientTransport::Bond),
            &[ClientTransport::Bond]
        );
        assert_eq!(
            client_route_order(ClientTransport::BondTor),
            &[ClientTransport::BondTor]
        );
        assert_eq!(
            client_route_order(ClientTransport::BondI2p),
            &[ClientTransport::BondI2p]
        );
        assert_eq!(
            client_route_order(ClientTransport::Tor),
            &[ClientTransport::Tor]
        );
        assert_eq!(
            client_route_order(ClientTransport::I2p),
            &[ClientTransport::I2p]
        );
    }

    #[test]
    fn product_transport_profiles_resolve_without_implicit_provider_changes() {
        assert_eq!(
            configured_client_transport(TransportProfile::Auto),
            ClientTransport::Auto
        );
        assert_eq!(
            configured_client_transport(TransportProfile::Mixed),
            ClientTransport::Bond
        );
        assert_eq!(
            configured_client_transport(TransportProfile::TorOnly),
            ClientTransport::BondTor
        );
        assert_eq!(
            configured_client_transport(TransportProfile::I2pOnly),
            ClientTransport::BondI2p
        );
        assert_eq!(
            configured_server_transport(TransportProfile::Auto),
            ServerTransport::Bond
        );
        assert_eq!(
            configured_server_transport(TransportProfile::Mixed),
            ServerTransport::Bond
        );
        assert_eq!(
            configured_server_transport(TransportProfile::TorOnly),
            ServerTransport::BondTor
        );
        assert_eq!(
            configured_server_transport(TransportProfile::I2pOnly),
            ServerTransport::BondI2p
        );
        for transport in [ServerTransport::Bond, ServerTransport::Both] {
            assert_eq!(
                transport_profile_for_server(transport),
                TransportProfile::Mixed
            );
        }
        for transport in [ServerTransport::BondTor, ServerTransport::Tor] {
            assert_eq!(
                transport_profile_for_server(transport),
                TransportProfile::TorOnly
            );
        }
        for transport in [ServerTransport::BondI2p, ServerTransport::I2p] {
            assert_eq!(
                transport_profile_for_server(transport),
                TransportProfile::I2pOnly
            );
        }
    }

    #[test]
    fn recovery_targets_are_unambiguous() {
        let target = parse_recovery_target("alice@home-1").unwrap();
        assert_eq!(target.user, "alice");
        assert_eq!(target.machine_id, "home-1");
        for invalid in [
            "home-1",
            "@home-1",
            "alice@",
            "alice@home@other",
            "-alice@home",
        ] {
            assert!(
                parse_recovery_target(invalid).is_err(),
                "accepted {invalid}"
            );
        }
    }

    #[test]
    fn operation_and_cleanup_errors_are_both_reported() {
        let error = merge_cleanup::<()>(
            Err(anyhow::anyhow!("operation failed")),
            Err(anyhow::anyhow!("cleanup failed")),
        )
        .unwrap_err()
        .to_string();
        assert!(error.contains("operation failed"));
        assert!(error.contains("cleanup also failed: cleanup failed"));
    }

    #[tokio::test]
    async fn bonded_ssh_server_relays_concurrent_streams_on_one_session() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let backend = listener.local_addr().unwrap();
        let backend_task = tokio::spawn(async move {
            let mut echoes = tokio::task::JoinSet::new();
            for _ in 0..2 {
                let (stream, _) = listener.accept().await.unwrap();
                echoes.spawn(async move {
                    let (mut reader, mut writer) = stream.into_split();
                    tokio::io::copy(&mut reader, &mut writer).await.unwrap();
                    writer.shutdown().await.unwrap();
                });
            }
            while let Some(result) = echoes.join_next().await {
                result.unwrap();
            }
        });
        let (client, server) = bonded_session_pair().await;
        let first = b"first independent SSH connection";
        let second = b"second independent SSH connection";

        let received = {
            let service_registry =
                Arc::new(crate::native_service::NativeServiceRegistry::default());
            let service = serve_bonded_ssh_streams(&server, backend, true, service_registry);
            tokio::pin!(service);
            tokio::select! {
                result = &mut service => {
                    panic!("multi-stream service stopped early: {:#}", result.unwrap_err());
                }
                result = tokio::time::timeout(Duration::from_secs(5), async {
                    tokio::try_join!(
                        bonded_round_trip(&client, first),
                        bonded_round_trip(&client, second),
                    )
                }) => result.expect("concurrent SSH streams timed out").unwrap(),
            }
        };

        assert_eq!(received.0, first);
        assert_eq!(received.1, second);
        backend_task.await.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    #[tokio::test]
    async fn bonded_server_dispatches_bulk_to_a_named_native_service() {
        let path = std::env::temp_dir().join(format!(
            "anonssh-native-bond-test-{}-{}",
            std::process::id(),
            SOCKET_SEQUENCE.fetch_add(1, Ordering::Relaxed)
        ));
        let listener = UnixListener::bind(&path).unwrap();
        fs::set_permissions(&path, fs::Permissions::from_mode(0o600)).unwrap();
        let registry = Arc::new(
            crate::native_service::NativeServiceRegistry::parse(&[format!(
                "echo={}",
                path.display()
            )])
            .unwrap(),
        );
        let backend = "127.0.0.1:9".parse().unwrap();
        let service_task = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let (mut reader, mut writer) = stream.into_split();
            tokio::io::copy(&mut reader, &mut writer).await.unwrap();
            writer.shutdown().await.unwrap();
        });
        let (client, server) = bonded_session_pair().await;
        let payload = b"native bulk service over one bonded stream";

        let received = {
            let service = serve_bonded_ssh_streams(&server, backend, true, registry);
            tokio::pin!(service);
            tokio::select! {
                result = &mut service => {
                    panic!("native service dispatcher stopped early: {:#}", result.unwrap_err());
                }
                result = tokio::time::timeout(Duration::from_secs(5), async {
                    let mut stream = client.open_stream(TrafficClass::Bulk).await.unwrap();
                    crate::application_service::request_service(
                        &mut stream,
                        &crate::application_service::ServiceName::parse("echo").unwrap(),
                    )
                    .await
                    .unwrap();
                    stream.write_all(payload).await.unwrap();
                    stream.shutdown().await.unwrap();
                    let mut received = Vec::new();
                    stream.read_to_end(&mut received).await.unwrap();
                    received
                }) => result.expect("native service stream timed out"),
            }
        };

        assert_eq!(received, payload);
        service_task.await.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
        fs::remove_file(path).unwrap();
    }

    #[tokio::test]
    async fn stalled_service_preface_does_not_block_a_sibling_stream() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let backend = listener.local_addr().unwrap();
        let backend_task = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let (mut reader, mut writer) = stream.into_split();
            tokio::io::copy(&mut reader, &mut writer).await.unwrap();
            writer.shutdown().await.unwrap();
        });
        let (client, server) = bonded_session_pair().await;
        let mut stalled = client.open_stream(TrafficClass::Interactive).await.unwrap();
        let payload = b"sibling stream remains live";

        let received = {
            let registry = Arc::new(crate::native_service::NativeServiceRegistry::default());
            let service = serve_bonded_ssh_streams(&server, backend, true, registry);
            tokio::pin!(service);
            tokio::select! {
                result = &mut service => {
                    panic!("service dispatcher stopped early: {:#}", result.unwrap_err());
                }
                result = tokio::time::timeout(
                    Duration::from_secs(5),
                    bonded_round_trip(&client, payload),
                ) => {
                    let received = result
                        .expect("sibling stream was blocked by stalled setup")
                        .unwrap();
                    stalled.reset(SSH_STREAM_REJECTED).await.unwrap();
                    received
                },
            }
        };

        assert_eq!(received, payload);
        backend_task.await.unwrap();
        let (client_shutdown, server_shutdown) = tokio::join!(client.shutdown(), server.shutdown());
        client_shutdown.unwrap();
        server_shutdown.unwrap();
    }

    async fn bonded_round_trip(session: &BondSession, payload: &[u8]) -> std::io::Result<Vec<u8>> {
        let mut stream = session
            .open_stream(TrafficClass::Interactive)
            .await
            .map_err(std::io::Error::other)?;
        crate::application_service::request_service(
            &mut stream,
            &crate::application_service::ServiceName::parse(
                crate::application_service::SSH_SERVICE,
            )
            .map_err(std::io::Error::other)?,
        )
        .await
        .map_err(std::io::Error::other)?;
        stream.write_all(payload).await?;
        stream.shutdown().await?;
        let mut received = Vec::new();
        stream.read_to_end(&mut received).await?;
        Ok(received)
    }

    async fn bonded_session_pair() -> (BondSession, BondSession) {
        let session_id = 0x4142_5053;
        let lane = LaneConfig::new(
            LaneId::new(1).unwrap(),
            FailureDomain::new(1).unwrap(),
            Duration::from_millis(5),
            100_000_000,
        )
        .unwrap();
        let join = LaneJoin::new(session_id, lane.id, lane.failure_domain).unwrap();
        let key = BondSessionKey::new([0x53; 32]);
        let (client_io, server_io) = tokio::io::duplex(256 * 1024);
        let (client_lane, server_lane) = tokio::join!(
            authenticate_client_lane(client_io, &key, join, Duration::from_secs(2)),
            authenticate_server_lane(server_io, &key, join, Duration::from_secs(2)),
        );
        let config = BondRuntimeConfig {
            session_id,
            scheduler: SchedulerConfig::default(),
            sender: SenderConfig::default(),
            max_reorder_bytes_per_stream: 2 * 1024 * 1024,
            max_receive_streams: 64,
            stream_receive_window: 2 * 1024 * 1024,
            max_ack_ranges: 16,
            require_stream_open: true,
            retransmit_after: Duration::from_secs(2),
            retransmit_scan_interval: Duration::from_millis(50),
        };
        (
            BondSession::spawn(
                config,
                vec![RuntimeLane::from_authenticated(lane, client_lane.unwrap())],
                SessionRole::Dialer,
            )
            .unwrap(),
            BondSession::spawn(
                config,
                vec![RuntimeLane::from_authenticated(lane, server_lane.unwrap())],
                SessionRole::Listener,
            )
            .unwrap(),
        )
    }
}
