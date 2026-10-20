use std::path::PathBuf;
use std::time::Duration;

use anyhow::{bail, Context, Result};
use serde::Serialize;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::time::timeout;
use zeroize::Zeroizing;

use crate::i2p_bootstrap;
use crate::identity::{HostRecord, IdentityManager};
use crate::product_config::{ProductConfig, ProductConfigReport, TransportProfile};
use crate::router_pool::{
    configured_router_topology, ConfiguredRouterTopology, PRODUCTION_I2P_SLOTS,
    PRODUCTION_TOR_CANDIDATES, PRODUCTION_TOR_SLOTS,
};
use crate::runtime::{
    chmod, resolve_executable, resolve_i2pd_certificates, sam_endpoint, tor_socks_endpoint,
    AppConfig,
};
use crate::sam::SamConnector;
use crate::ssh::{
    build_recovery_command, embedded_runtime_login, RecoverySshSession, SshInvocation,
    SshServerPrograms,
};
use crate::tor_transport::tor_v3_service_id_from_control_private_key;

const EMBEDDED_ASYNC_STAGE_TIMEOUT: Duration = Duration::from_secs(60);

#[derive(Debug, Serialize)]
pub struct DoctorReport {
    pub system_ok: bool,
    pub configuration: ProductConfigReport,
    pub dependencies: Vec<DependencyReport>,
    pub bond_topology: BondTopologyReport,
    pub i2p_sam: ServiceReport,
    pub tor_socks: ServiceReport,
    pub embedded_routers: EmbeddedRouterReport,
}

#[derive(Debug, Serialize)]
pub struct EmbeddedRouterReport {
    pub tor_version: Option<&'static str>,
    pub i2pd_version: Option<&'static str>,
    pub openssh_version: Option<&'static str>,
    pub dropbear_version: Option<&'static str>,
    pub sftp_server_version: Option<&'static str>,
    pub scp_version: Option<&'static str>,
}

#[derive(Debug, Serialize)]
pub struct BondTopologyReport {
    pub valid: bool,
    pub tor_slots: usize,
    pub tor_candidates: usize,
    pub i2p_slots: usize,
    pub baseline_lane_ids: [u32; 4],
    pub configured_endpoints: Vec<ConfiguredEndpointReport>,
    pub state_roots: Vec<PathBuf>,
    pub detail: String,
}

#[derive(Debug, Serialize)]
pub struct ConfiguredEndpointReport {
    pub provider: &'static str,
    pub role: &'static str,
    pub slot: u32,
    pub candidate: usize,
    pub endpoint: String,
}

#[derive(Debug, Serialize)]
pub struct DependencyReport {
    pub name: &'static str,
    pub required: bool,
    pub available: bool,
    pub path: Option<PathBuf>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct ServiceReport {
    pub enabled: bool,
    pub endpoint: String,
    pub reachable: bool,
    pub detail: String,
}

pub async fn doctor(product_config: &ProductConfig) -> DoctorReport {
    let (include_tor, include_i2p) = required_providers(product_config.transport_profile());
    let mut dependencies = [
        ("i2pd", "ANONSSH_I2PD_BIN", "i2pd"),
        ("tor", "ANONSSH_TOR_BIN", "tor"),
        ("ssh", "ANONSSH_SSH_BIN", "ssh"),
        ("dropbear", "ANONSSH_DROPBEAR_BIN", "dropbear"),
        ("sftp-server", "ANONSSH_SFTP_SERVER_BIN", "sftp-server"),
        ("scp", "ANONSSH_SCP_BIN", "scp"),
    ]
    .into_iter()
    .map(|(name, variable, executable)| {
        let required = match name {
            "i2pd" => include_i2p,
            "tor" => include_tor,
            _ => true,
        };
        match resolve_executable(variable, executable) {
            Ok(path) => DependencyReport {
                name,
                required,
                available: true,
                path: Some(path),
                error: None,
            },
            Err(error) => DependencyReport {
                name,
                required,
                available: false,
                path: None,
                error: Some(format!("{error:#}")),
            },
        }
    })
    .collect::<Vec<_>>();
    let certificate_report = match dependencies
        .iter()
        .find(|dependency| dependency.name == "i2pd")
        .and_then(|dependency| dependency.path.as_deref())
        .map(resolve_i2pd_certificates)
    {
        Some(Ok(path)) => DependencyReport {
            name: "i2p-certs",
            required: include_i2p,
            available: true,
            path: Some(path),
            error: None,
        },
        Some(Err(error)) => DependencyReport {
            name: "i2p-certs",
            required: include_i2p,
            available: false,
            path: None,
            error: Some(format!("{error:#}")),
        },
        None => DependencyReport {
            name: "i2p-certs",
            required: include_i2p,
            available: false,
            path: None,
            error: Some("i2pd is unavailable".to_owned()),
        },
    };
    dependencies.push(certificate_report);
    let external_tor_report = DependencyReport {
        name: "tor-external-services",
        required: false,
        available: true,
        path: None,
        error: None,
    };
    dependencies.push(external_tor_report);
    let bootstrap_report = match std::env::var_os("ANONSSH_I2PD_BOOTSTRAP_DIR") {
        Some(path) => {
            let path = PathBuf::from(path);
            match i2p_bootstrap::validate(&path) {
                Ok(_) => DependencyReport {
                    name: "i2p-bootstrap",
                    required: include_i2p,
                    available: true,
                    path: Some(path),
                    error: None,
                },
                Err(error) => DependencyReport {
                    name: "i2p-bootstrap",
                    required: include_i2p,
                    available: false,
                    path: Some(path),
                    error: Some(format!("{error:#}")),
                },
            }
        }
        None => match i2p_bootstrap::validate_embedded() {
            Ok(_) => DependencyReport {
                name: "i2p-bootstrap",
                required: include_i2p,
                available: true,
                path: None,
                error: None,
            },
            Err(error) => DependencyReport {
                name: "i2p-bootstrap",
                required: include_i2p,
                available: false,
                path: None,
                error: Some(format!("embedded corpus is invalid: {error:#}")),
            },
        },
    };
    dependencies.push(bootstrap_report);

    let i2p_sam = if !include_i2p {
        ServiceReport {
            enabled: false,
            endpoint: String::new(),
            reachable: false,
            detail: "disabled by the effective transport profile".to_owned(),
        }
    } else {
        match sam_endpoint() {
            Ok(endpoint) => {
                let connector = SamConnector::new(endpoint.to_string(), None);
                let check = async {
                    let mut stream = TcpStream::connect(endpoint).await?;
                    connector.handshake(&mut stream).await
                };
                match timeout(Duration::from_secs(2), check).await {
                    Ok(Ok(())) => ServiceReport {
                        enabled: true,
                        endpoint: endpoint.to_string(),
                        reachable: true,
                        detail: "SAM negotiation succeeded".to_owned(),
                    },
                    Ok(Err(error)) => ServiceReport {
                        enabled: true,
                        endpoint: endpoint.to_string(),
                        reachable: false,
                        detail: format!("{error:#}"),
                    },
                    Err(_) => ServiceReport {
                        enabled: true,
                        endpoint: endpoint.to_string(),
                        reachable: false,
                        detail: "SAM check timed out".to_owned(),
                    },
                }
            }
            Err(error) => ServiceReport {
                enabled: true,
                endpoint: std::env::var("ANONSSH_SAM_ADDR").unwrap_or_default(),
                reachable: false,
                detail: format!("{error:#}"),
            },
        }
    };

    let tor_socks = if !include_tor {
        ServiceReport {
            enabled: false,
            endpoint: String::new(),
            reachable: false,
            detail: "disabled by the effective transport profile".to_owned(),
        }
    } else {
        match tor_socks_endpoint() {
            Ok(endpoint) => {
                match timeout(Duration::from_secs(2), check_tor_socks(endpoint)).await {
                    Ok(Ok(())) => ServiceReport {
                        enabled: true,
                        endpoint: endpoint.to_string(),
                        reachable: true,
                        detail: "SOCKS5 negotiation succeeded".to_owned(),
                    },
                    Ok(Err(error)) => ServiceReport {
                        enabled: true,
                        endpoint: endpoint.to_string(),
                        reachable: false,
                        detail: format!("{error:#}"),
                    },
                    Err(_) => ServiceReport {
                        enabled: true,
                        endpoint: endpoint.to_string(),
                        reachable: false,
                        detail: "SOCKS5 check timed out".to_owned(),
                    },
                }
            }
            Err(error) => ServiceReport {
                enabled: true,
                endpoint: std::env::var("ANONSSH_TOR_SOCKS_ADDR").unwrap_or_default(),
                reachable: false,
                detail: format!("{error:#}"),
            },
        }
    };
    let bond_topology = AppConfig::new()
        .and_then(|config| configured_router_topology(&config, include_tor, include_i2p))
        .and_then(|topology| diagnose_bond_topology(topology, include_tor, include_i2p))
        .unwrap_or_else(|error| invalid_bond_topology(error, include_tor, include_i2p));
    DoctorReport {
        system_ok: dependencies
            .iter()
            .all(|dependency| !dependency.required || dependency.available)
            && bond_topology.valid,
        configuration: product_config.report(),
        dependencies,
        bond_topology,
        i2p_sam,
        tor_socks,
        embedded_routers: {
            let [tor_version, i2pd_version, openssh_version, dropbear_version, sftp_server_version, scp_version] =
                crate::embedded_runtime::versions();
            EmbeddedRouterReport {
                tor_version,
                i2pd_version,
                openssh_version,
                dropbear_version,
                sftp_server_version,
                scp_version,
            }
        },
    }
}

fn required_providers(profile: TransportProfile) -> (bool, bool) {
    match profile {
        TransportProfile::Auto | TransportProfile::Mixed => (true, true),
        TransportProfile::TorOnly => (true, false),
        TransportProfile::I2pOnly => (false, true),
    }
}

fn diagnose_bond_topology(
    topology: ConfiguredRouterTopology,
    include_tor: bool,
    include_i2p: bool,
) -> Result<BondTopologyReport> {
    topology.validate()?;
    let tor_candidates = topology
        .tor
        .iter()
        .map(|(_, candidates, _)| candidates.len())
        .sum::<usize>();
    let expected_tor_slots = usize::from(include_tor) * PRODUCTION_TOR_SLOTS;
    let expected_tor_candidates = usize::from(include_tor) * PRODUCTION_TOR_CANDIDATES;
    let expected_i2p_slots = usize::from(include_i2p) * PRODUCTION_I2P_SLOTS;
    if topology.tor.len() != expected_tor_slots
        || tor_candidates != expected_tor_candidates
        || topology.i2p.len() != expected_i2p_slots
    {
        bail!(
            "default topology cardinality is Tor {} slots/{tor_candidates} candidates and I2P {} slots",
            topology.tor.len(),
            topology.i2p.len()
        );
    }

    let mut configured_endpoints = Vec::with_capacity(2 * tor_candidates + topology.i2p.len());
    let mut state_roots = Vec::with_capacity(tor_candidates + topology.i2p.len());
    for (slot, candidates, _) in &topology.tor {
        for (candidate, (root, socks, control)) in candidates.iter().enumerate() {
            let candidate = candidate + 1;
            state_roots.push(root.clone());
            configured_endpoints.push(ConfiguredEndpointReport {
                provider: "tor",
                role: "socks",
                slot: *slot,
                candidate,
                endpoint: socks.to_string(),
            });
            configured_endpoints.push(ConfiguredEndpointReport {
                provider: "tor",
                role: "control",
                slot: *slot,
                candidate,
                endpoint: control.to_string(),
            });
        }
    }
    for (slot, root, sam, _) in &topology.i2p {
        state_roots.push(root.clone());
        configured_endpoints.push(ConfiguredEndpointReport {
            provider: "i2p",
            role: "sam",
            slot: *slot,
            candidate: 1,
            endpoint: sam.to_string(),
        });
    }
    Ok(BondTopologyReport {
        valid: true,
        tor_slots: topology.tor.len(),
        tor_candidates,
        i2p_slots: topology.i2p.len(),
        baseline_lane_ids: baseline_lane_ids(include_tor, include_i2p),
        configured_endpoints,
        state_roots,
        detail: match (include_tor, include_i2p) {
            (true, true) => "mixed Tor+I2P topology is valid",
            (true, false) => "Tor-only topology is valid",
            (false, true) => "I2P-only topology is valid",
            (false, false) => "empty topology is invalid",
        }
        .to_owned(),
    })
}

fn invalid_bond_topology(
    error: anyhow::Error,
    include_tor: bool,
    include_i2p: bool,
) -> BondTopologyReport {
    BondTopologyReport {
        valid: false,
        tor_slots: usize::from(include_tor) * PRODUCTION_TOR_SLOTS,
        tor_candidates: usize::from(include_tor) * PRODUCTION_TOR_CANDIDATES,
        i2p_slots: usize::from(include_i2p) * PRODUCTION_I2P_SLOTS,
        baseline_lane_ids: baseline_lane_ids(include_tor, include_i2p),
        configured_endpoints: Vec::new(),
        state_roots: Vec::new(),
        detail: format!("{error:#}"),
    }
}

fn baseline_lane_ids(include_tor: bool, include_i2p: bool) -> [u32; 4] {
    if include_tor && !include_i2p {
        return [17, 18, 19, 20];
    }
    if include_i2p && !include_tor {
        return [25, 26, 27, 28];
    }
    let i2p_first = u32::try_from(PRODUCTION_TOR_SLOTS)
        .expect("production Tor slot count fits lane identifiers")
        .checked_add(1)
        .expect("production I2P lane identifier does not overflow");
    [1, 2, i2p_first, i2p_first + 1]
}

async fn check_tor_socks(endpoint: std::net::SocketAddr) -> Result<()> {
    let mut stream = TcpStream::connect(endpoint).await?;
    stream.write_all(&[5, 1, 0]).await?;
    stream.flush().await?;
    let mut reply = [0_u8; 2];
    stream.read_exact(&mut reply).await?;
    validate_socks_reply(reply)
}

fn validate_socks_reply(reply: [u8; 2]) -> Result<()> {
    if reply != [5, 0] {
        bail!("endpoint rejected unauthenticated SOCKS5 negotiation");
    }
    Ok(())
}

pub async fn embedded_fuzz_test(json: bool) -> Result<()> {
    let protocol = anonssh_bond::embedded_protocol_fuzz_test()
        .context("embedded ABP parser fuzz test failed")?;
    let transport = timeout(
        EMBEDDED_ASYNC_STAGE_TIMEOUT,
        anonssh_bond_tokio::embedded_transport_fuzz_test(),
    )
    .await
    .context("embedded transport parser fuzz test timed out")?
    .context("embedded transport parser fuzz test failed")?;
    let bootstrap = i2p_bootstrap::embedded_bootstrap_fuzz_test()
        .context("embedded I2P bootstrap parser fuzz test failed")?;
    let report = serde_json::json!({
        "schema": "anonssh.embedded-parser-fuzz.v1",
        "status": "ok",
        "deterministic": true,
        "protocol": {
            "seed": protocol.seed,
            "frame": fuzz_counts(protocol.frame.cases, protocol.frame.accepted, protocol.frame.rejected),
            "acknowledgement": fuzz_counts(protocol.acknowledgement.cases, protocol.acknowledgement.accepted, protocol.acknowledgement.rejected),
            "stream_control": fuzz_counts(protocol.stream_control.cases, protocol.stream_control.accepted, protocol.stream_control.rejected),
            "capability": fuzz_counts(protocol.capability.cases, protocol.capability.accepted, protocol.capability.rejected),
            "topology": fuzz_counts(protocol.topology.cases, protocol.topology.accepted, protocol.topology.rejected),
        },
        "transport": {
            "seed": transport.seed,
            "handshake_hello": fuzz_counts(transport.handshake_hello.cases, transport.handshake_hello.accepted, transport.handshake_hello.rejected),
            "handshake_accept": fuzz_counts(transport.handshake_accept.cases, transport.handshake_accept.accepted, transport.handshake_accept.rejected),
            "encrypted_record": fuzz_counts(transport.encrypted_record.cases, transport.encrypted_record.accepted, transport.encrypted_record.rejected),
        },
        "i2p_bootstrap": {
            "seed": bootstrap.seed,
            "manifest": fuzz_counts(bootstrap.manifest.cases, bootstrap.manifest.accepted, bootstrap.manifest.rejected),
            "observation_ledger": fuzz_counts(bootstrap.observation_ledger.cases, bootstrap.observation_ledger.accepted, bootstrap.observation_ledger.rejected),
            "peer_profile": fuzz_counts(bootstrap.peer_profile.cases, bootstrap.peer_profile.accepted, bootstrap.peer_profile.rejected),
        },
    });
    if json {
        println!("{}", serde_json::to_string_pretty(&report)?);
    } else {
        let total = protocol.frame.cases
            + protocol.acknowledgement.cases
            + protocol.stream_control.cases
            + protocol.capability.cases
            + protocol.topology.cases
            + transport.handshake_hello.cases
            + transport.handshake_accept.cases
            + transport.encrypted_record.cases
            + bootstrap.manifest.cases
            + bootstrap.observation_ledger.cases
            + bootstrap.peer_profile.cases;
        println!("embedded parser fuzz: ok ({total} deterministic cases)");
    }
    Ok(())
}

fn fuzz_counts(cases: u32, accepted: u32, rejected: u32) -> serde_json::Value {
    serde_json::json!({
        "cases": cases,
        "accepted": accepted,
        "rejected": rejected,
    })
}

pub async fn embedded_test(json: bool) -> Result<()> {
    let password = Zeroizing::new("anonssh embedded deterministic recovery test".to_owned());
    let machine_id = "embedded-test-machine";
    let client = IdentityManager::derive_client_recovery_identity(&password, machine_id)?;
    let server = IdentityManager::derive_server_recovery_identity(&password, machine_id)?;
    if client.i2p.destination != server.i2p.destination
        || client.tor_destination != server.tor.destination
        || client.tor_pool_destinations
            != server
                .tor_pool
                .iter()
                .map(|identity| identity.destination.clone())
                .collect::<Vec<_>>()
        || client.i2p_pool.len() != crate::router_pool::PRODUCTION_I2P_SLOTS
        || server.i2p_pool.len() != crate::router_pool::PRODUCTION_I2P_SLOTS
        || client.tor_pool_destinations.len() != crate::router_pool::PRODUCTION_TOR_SLOTS
        || server.tor_pool.len() != crate::router_pool::PRODUCTION_TOR_SLOTS
        || client.ssh_host_public_key != server.ssh_host.public_key
        || client.ssh_client.public_key != server.ssh_client_public_key
        || *client.bond_session_key != *server.bond_session_key
    {
        bail!("client and server recovery identities diverged");
    }
    for (index, tor) in server.tor_pool.iter().enumerate() {
        let expected_onion = tor
            .destination
            .trim_start_matches("tor://")
            .trim_end_matches(".onion");
        if tor_v3_service_id_from_control_private_key(&tor.control_private_key)? != expected_onion {
            bail!("Tor control key does not reproduce pool slot {}", index + 1);
        }
    }
    if !client.i2p.destination.starts_with("i2p://")
        || !client.i2p.destination.ends_with(".b32.i2p")
        || server.ssh_host.dropbear_private_key.len() != 83
    {
        bail!("derived recovery material has an invalid wire shape");
    }

    let bond = anonssh_bond::embedded_self_test().context("embedded bond self-test failed")?;
    if bond.bulk_lanes < 2 || bond.retransmitted_frames == 0 {
        bail!("embedded bond self-test did not exercise striping and retransmission");
    }
    let bond_runtime = timeout(
        EMBEDDED_ASYNC_STAGE_TIMEOUT,
        anonssh_bond_tokio::embedded_runtime_self_test(),
    )
    .await
    .context("embedded bond runtime self-test timed out")?
    .context("embedded bond runtime self-test failed")?;
    if bond_runtime.bulk_lanes_used < 2
        || bond_runtime.post_failure_payload_bytes == 0
        || bond_runtime.authenticated_lanes < 2
        || bond_runtime.protocol_version != 6
    {
        bail!("embedded bond runtime self-test did not exercise live striping and lane loss");
    }
    let compatibility = timeout(
        EMBEDDED_ASYNC_STAGE_TIMEOUT,
        anonssh_bond_tokio::protocol_compatibility_self_test(),
    )
    .await
    .context("embedded protocol-compatibility test timed out")?
    .context("embedded protocol-compatibility test failed")?;
    if compatibility.current_version != 6
        || compatibility.new_client_v5_server_version != 5
        || compatibility.v5_client_new_server_version != 5
        || compatibility.new_client_v4_server_version != 4
        || compatibility.v4_client_new_server_version != 4
        || compatibility.new_client_v3_server_version != 3
        || compatibility.v3_client_new_server_version != 3
        || compatibility.new_client_v2_server_version != 2
        || compatibility.v2_client_new_server_version != 2
        || compatibility.new_client_legacy_server_version != 1
        || compatibility.legacy_client_new_server_version != 1
        || !compatibility.no_common_rejected
        || !compatibility.authenticated_downgrade_rejected
    {
        bail!("embedded protocol-compatibility test did not cover the compatibility matrix");
    }
    let controlled = timeout(
        EMBEDDED_ASYNC_STAGE_TIMEOUT,
        anonssh_bond_tokio::controlled_goodput_self_test(),
    )
    .await
    .context("embedded controlled-goodput test timed out")?
    .context("embedded controlled-goodput test failed")?;
    if controlled.efficiency_basis_points < 8_000
        || controlled.adaptive_vs_fixed_basis_points < 9_000
        || controlled.bulk_lanes_used < 2
    {
        bail!("embedded controlled-goodput test did not preserve aggregate capacity");
    }
    let concurrent = timeout(
        EMBEDDED_ASYNC_STAGE_TIMEOUT,
        anonssh_bond_tokio::concurrent_progress_self_test(),
    )
    .await
    .context("embedded concurrent-progress test timed out")?
    .context("embedded concurrent-progress test failed")?;
    if concurrent.payload_bytes_per_direction < 2 * 1024 * 1024
        || concurrent.client_received_sha256 == concurrent.server_received_sha256
    {
        bail!("embedded concurrent-progress test did not prove bidirectional progress");
    }
    let topology = timeout(
        EMBEDDED_ASYNC_STAGE_TIMEOUT,
        anonssh_bond_tokio::dynamic_topology_self_test(),
    )
    .await
    .context("embedded dynamic-topology test timed out")?
    .context("embedded dynamic-topology test failed")?;
    if !topology.denied_policy_rejected
        || !topology.denied_domain_rejected
        || !topology.denied_action_rejected
        || !topology.replay_rejected
        || topology.payload_bytes == 0
    {
        bail!("embedded dynamic-topology test did not enforce policy and carry payload data");
    }

    let test_parent = dirs::runtime_dir()
        .or_else(dirs::cache_dir)
        .context("cannot resolve a private directory for the embedded SSH test")?;
    let root = test_parent.join(format!("anonssh-embedded-test-{}", std::process::id()));
    if root.exists() {
        std::fs::remove_dir_all(&root)?;
    }
    std::fs::create_dir(&root)?;
    chmod(&root, 0o700)?;
    let result = (|| -> Result<()> {
        let config = AppConfig::temporary(&root);
        let session = RecoverySshSession::materialize(
            &config,
            machine_id,
            &client.ssh_client.private_key,
            &client.ssh_host_public_key,
        )?;
        let record = HostRecord {
            name: Zeroizing::new(machine_id.to_owned()),
            user: Zeroizing::new("anonssh".to_owned()),
            port: 22,
        };
        let ssh = resolve_executable("ANONSSH_SSH_BIN", "ssh")?;
        let command = build_recovery_command(
            &record,
            "anonssh proxy --transport tor --destination test --endpoint 127.0.0.1:1",
            &SshInvocation::default(),
            &session,
            60,
            &ssh,
        )?;
        let proxy = command
            .get_args()
            .map(|argument| argument.to_string_lossy())
            .find(|argument| argument.starts_with("ProxyCommand="))
            .context("generated OpenSSH command omitted ProxyCommand")?;
        if proxy.starts_with("ProxyCommand=exec ") {
            bail!("ProxyCommand redundantly invokes exec");
        }
        let rendered = command
            .get_args()
            .map(|argument| argument.to_string_lossy())
            .collect::<Vec<_>>()
            .join(" ");
        for required in [
            "StrictHostKeyChecking=yes",
            "PasswordAuthentication=no",
            "IdentitiesOnly=yes",
            "ProxyCommand=",
        ] {
            if !rendered.contains(required) {
                bail!("generated OpenSSH command omitted {required}");
            }
        }
        Ok(())
    })();
    let ssh_runtime = match result {
        Ok(()) => {
            async {
                let username = std::env::var("USER")
                    .ok()
                    .filter(|value| !value.is_empty())
                    .context("USER is required for the embedded SSH runtime test")?;
                let ssh = resolve_executable("ANONSSH_SSH_BIN", "ssh")?;
                let dropbear = resolve_executable("ANONSSH_DROPBEAR_BIN", "dropbear")?;
                let sftp_server = resolve_executable("ANONSSH_SFTP_SERVER_BIN", "sftp-server")?;
                let scp = resolve_executable("ANONSSH_SCP_BIN", "scp")?;
                let config = AppConfig::temporary(&root);
                embedded_runtime_login(
                    &config,
                    machine_id,
                    &username,
                    &client,
                    &server,
                    &ssh,
                    SshServerPrograms {
                        dropbear: &dropbear,
                        sftp_server: &sftp_server,
                        scp: &scp,
                    },
                )
                .await
            }
            .await
        }
        Err(error) => Err(error),
    };
    let cleanup = std::fs::remove_dir_all(&root).with_context(|| {
        format!(
            "failed to remove embedded-test directory {}",
            root.display()
        )
    });
    ssh_runtime?;
    cleanup?;
    if json {
        println!(
            "{}",
            serde_json::to_string_pretty(&serde_json::json!({
                "schema": "anonssh.embedded-test.v3",
                "status": "ok",
                "ssh_runtime": "embedded-openssh-to-embedded-dropbear",
                "bond": {
                    "payload_bytes": bond.payload_bytes,
                    "initial_frames": bond.initial_frames,
                    "retransmitted_frames": bond.retransmitted_frames,
                    "bulk_lanes": bond.bulk_lanes,
                    "realtime_lane": bond.realtime_lane.get(),
                    "interactive_typing_lane": bond.interactive_typing_lane.get(),
                    "interactive_bulk_lanes": bond.interactive_bulk_lanes,
                    "reorder_high_water": bond.reorder_high_water,
                    "scheduler_lanes": bond.scheduler_lanes,
                    "scheduler_decisions": bond.scheduler_decisions,
                    "scheduler_heap_scratch_bytes": bond.scheduler_heap_scratch_bytes,
                },
                "bond_runtime": {
                    "bulk_payload_bytes": bond_runtime.bulk_payload_bytes,
                    "realtime_payload_bytes": bond_runtime.realtime_payload_bytes,
                    "post_failure_payload_bytes": bond_runtime.post_failure_payload_bytes,
                    "bulk_lanes_used": bond_runtime.bulk_lanes_used,
                    "protected_realtime_lane": bond_runtime.protected_realtime_lane,
                    "failed_lane": bond_runtime.failed_lane,
                    "payload_sha256": bond_runtime.payload_sha256,
                    "authenticated_lanes": bond_runtime.authenticated_lanes,
                    "protocol_version": bond_runtime.protocol_version,
                    "key_establishment": bond_runtime.key_establishment,
                    "record_protection": bond_runtime.record_protection,
                },
                "protocol_compatibility": {
                    "current_version": compatibility.current_version,
                    "new_client_v5_server_version": compatibility.new_client_v5_server_version,
                    "v5_client_new_server_version": compatibility.v5_client_new_server_version,
                    "new_client_v4_server_version": compatibility.new_client_v4_server_version,
                    "v4_client_new_server_version": compatibility.v4_client_new_server_version,
                    "new_client_v3_server_version": compatibility.new_client_v3_server_version,
                    "v3_client_new_server_version": compatibility.v3_client_new_server_version,
                    "new_client_v2_server_version": compatibility.new_client_v2_server_version,
                    "v2_client_new_server_version": compatibility.v2_client_new_server_version,
                    "new_client_legacy_server_version": compatibility.new_client_legacy_server_version,
                    "legacy_client_new_server_version": compatibility.legacy_client_new_server_version,
                    "payload_bytes_per_case": compatibility.payload_bytes_per_case,
                    "payload_sha256": compatibility.payload_sha256,
                    "no_common_rejected": compatibility.no_common_rejected,
                    "authenticated_downgrade_rejected": compatibility.authenticated_downgrade_rejected,
                    "legacy_handshake_magic": compatibility.legacy_handshake_magic,
                    "legacy_record_magic": compatibility.legacy_record_magic,
                },
                "controlled_goodput": {
                    "slow_baseline_bps": controlled.slow_baseline_bps,
                    "fast_baseline_bps": controlled.fast_baseline_bps,
                    "aggregate_baseline_bps": controlled.aggregate_baseline_bps,
                    "fixed_chunk_goodput_bps": controlled.fixed_chunk_goodput_bps,
                    "bonded_goodput_bps": controlled.bonded_goodput_bps,
                    "efficiency_basis_points": controlled.efficiency_basis_points,
                    "adaptive_vs_fixed_basis_points": controlled.adaptive_vs_fixed_basis_points,
                    "payload_bytes": controlled.payload_bytes,
                    "payload_sha256": controlled.payload_sha256,
                    "bulk_lanes_used": controlled.bulk_lanes_used,
                    "fixed_new_data_frames": controlled.fixed_new_data_frames,
                    "adaptive_new_data_frames": controlled.adaptive_new_data_frames,
                    "adaptive_bulk_chunk_pressure_limit": controlled.adaptive_bulk_chunk_pressure_limit,
                    "realtime_payload_bytes": controlled.realtime_payload_bytes,
                    "realtime_latency_micros": controlled.realtime_latency_micros,
                },
                "concurrent_progress": {
                    "payload_bytes_per_direction": concurrent.payload_bytes_per_direction,
                    "delayed_read_millis": concurrent.delayed_read_millis,
                    "data_frames_per_direction": concurrent.data_frames_per_direction,
                    "client_acknowledgement_frames": concurrent.client_acknowledgement_frames,
                    "server_acknowledgement_frames": concurrent.server_acknowledgement_frames,
                    "client_window_update_frames": concurrent.client_window_update_frames,
                    "server_window_update_frames": concurrent.server_window_update_frames,
                    "client_received_sha256": concurrent.client_received_sha256,
                    "server_received_sha256": concurrent.server_received_sha256,
                },
                "dynamic_topology": {
                    "generation": topology.generation,
                    "provider": topology.provider,
                    "added_lane": topology.added_lane,
                    "payload_bytes": topology.payload_bytes,
                    "payload_sha256": topology.payload_sha256,
                    "denied_policy_rejected": topology.denied_policy_rejected,
                    "denied_domain_rejected": topology.denied_domain_rejected,
                    "denied_action_rejected": topology.denied_action_rejected,
                    "replay_rejected": topology.replay_rejected,
                }
            }))?
        );
    } else {
        println!(
            "anonssh embedded test: ok (bond_bytes={} bond_lanes={} bond_retransmits={} runtime_bytes={} runtime_lanes={})",
            bond.payload_bytes,
            bond.bulk_lanes,
            bond.retransmitted_frames,
            bond_runtime.bulk_payload_bytes,
            bond_runtime.bulk_lanes_used
        );
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;
    use std::path::PathBuf;

    use super::{
        diagnose_bond_topology, invalid_bond_topology, required_providers, validate_socks_reply,
    };
    use crate::product_config::TransportProfile;
    use crate::router_pool::{
        ConfiguredRouterTopology, PRODUCTION_I2P_SLOTS, PRODUCTION_TOR_CANDIDATES,
        PRODUCTION_TOR_SLOTS,
    };

    #[test]
    fn tor_doctor_requires_a_socks5_endpoint() {
        assert!(validate_socks_reply([5, 0]).is_ok());
        assert!(validate_socks_reply([5, 2]).is_err());
        assert!(validate_socks_reply([1, 0]).is_err());
    }

    #[test]
    fn doctor_validates_the_complete_default_bond_topology() {
        let topology = configured_topology_fixture();
        let report = diagnose_bond_topology(topology.clone(), true, true).unwrap();
        assert!(report.valid);
        assert_eq!(report.tor_slots, PRODUCTION_TOR_SLOTS);
        assert_eq!(report.tor_candidates, PRODUCTION_TOR_CANDIDATES);
        assert_eq!(report.i2p_slots, PRODUCTION_I2P_SLOTS);
        assert_eq!(report.baseline_lane_ids, [1, 2, 9, 10]);
        assert_eq!(report.configured_endpoints.len(), 40);
        assert_eq!(report.state_roots.len(), 24);
        assert_eq!(
            report
                .configured_endpoints
                .iter()
                .map(|endpoint| &endpoint.endpoint)
                .collect::<BTreeSet<_>>()
                .len(),
            40
        );
        assert_eq!(report.state_roots.iter().collect::<BTreeSet<_>>().len(), 24);

        let mut collision = topology.clone();
        collision.i2p[0].2 = collision.tor[0].1[0].1;
        let report = invalid_bond_topology(
            diagnose_bond_topology(collision, true, true).unwrap_err(),
            true,
            true,
        );
        assert!(!report.valid);
        assert!(report.detail.contains("endpoints must be unique"));

        let mut non_loopback = topology;
        non_loopback.i2p[0].2 = "192.0.2.1:7656".parse().unwrap();
        let report = invalid_bond_topology(
            diagnose_bond_topology(non_loopback, true, true).unwrap_err(),
            true,
            true,
        );
        assert!(!report.valid);
        assert!(report.detail.contains("non-zero loopback"));
    }

    #[test]
    fn doctor_topology_follows_the_effective_transport_profile() {
        assert_eq!(required_providers(TransportProfile::Auto), (true, true));
        assert_eq!(required_providers(TransportProfile::Mixed), (true, true));
        assert_eq!(required_providers(TransportProfile::TorOnly), (true, false));
        assert_eq!(required_providers(TransportProfile::I2pOnly), (false, true));

        let mut tor_only = configured_topology_fixture();
        tor_only.i2p.clear();
        let report = diagnose_bond_topology(tor_only, true, false).unwrap();
        assert_eq!(report.tor_slots, PRODUCTION_TOR_SLOTS);
        assert_eq!(report.i2p_slots, 0);
        assert_eq!(report.baseline_lane_ids, [17, 18, 19, 20]);

        let mut i2p_only = configured_topology_fixture();
        i2p_only.tor.clear();
        let report = diagnose_bond_topology(i2p_only, false, true).unwrap();
        assert_eq!(report.tor_slots, 0);
        assert_eq!(report.i2p_slots, PRODUCTION_I2P_SLOTS);
        assert_eq!(report.baseline_lane_ids, [25, 26, 27, 28]);
    }

    fn configured_topology_fixture() -> ConfiguredRouterTopology {
        let tor = (1_u32..=8)
            .map(|slot| {
                (
                    slot,
                    vec![
                        (
                            PathBuf::from(format!("/state/tor-{slot}")),
                            format!("127.0.0.1:{}", 19_049 + slot).parse().unwrap(),
                            format!("127.0.0.1:{}", 19_149 + slot).parse().unwrap(),
                        ),
                        (
                            PathBuf::from(format!("/state/tor-{slot}-reserve")),
                            format!("127.0.0.1:{}", 19_249 + slot).parse().unwrap(),
                            format!("127.0.0.1:{}", 19_349 + slot).parse().unwrap(),
                        ),
                    ],
                    u64::from(slot),
                )
            })
            .collect();
        let i2p = (1_u32..=8)
            .map(|slot| {
                (
                    slot,
                    PathBuf::from(format!("/state/i2pd-{slot}")),
                    format!("127.0.0.1:{}", 7_655 + slot).parse().unwrap(),
                    100 + u64::from(slot),
                )
            })
            .collect();
        ConfiguredRouterTopology { tor, i2p }
    }
}
