use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::io;
use std::net::{SocketAddr, TcpListener};
use std::os::unix::fs::{FileTypeExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;

use anyhow::{anyhow, bail, Context, Result};
use sha2::{Digest, Sha256};
use tokio::io::{AsyncBufReadExt, AsyncReadExt, AsyncWriteExt, BufReader};
use tokio::process::{Child, ChildStdin, ChildStdout, Command};
use tokio::time::{timeout, Instant};

use crate::bond_transport::{I2P_ONLY_LANE_OFFSET, TOR_ONLY_LANE_OFFSET};
use crate::identity::IdentityManager;
use crate::router_pool::{PRODUCTION_I2P_SLOTS, PRODUCTION_TOR_CANDIDATES, PRODUCTION_TOR_SLOTS};
use crate::runtime::{chmod, configure_owned_child, resolve_executable, stop_child};
use crate::LiveTransport;

const LIVE_TEST_PASSWORD: &str = "anonssh deterministic live recovery test";
const PUBLICATION_TIMEOUT: Duration = Duration::from_secs(600);
const CONNECTION_TIMEOUT: Duration = Duration::from_secs(900);
const TYPING_PROBE_TIMEOUT: Duration = Duration::from_secs(30);
const TYPING_PROBE_COUNT: usize = 8;
const ADAPTIVE_BULK_BYTES: usize = 8 * 1024 * 1024;
const ADAPTIVE_BULK_CHUNK_BYTES: usize = 64 * 1024;
const CONCURRENT_BULK_MIN_BYTES: usize = 16 * 1024 * 1024;
const CONCURRENT_BULK_MAX_BYTES: usize = 128 * 1024 * 1024;
const CONCURRENT_WORKLOAD_TIMEOUT: Duration = Duration::from_secs(20 * 60);
const CONCURRENT_TYPING_P95_LIMIT: Duration = Duration::from_secs(10);
const CONCURRENT_RESOURCE_PROFILE: &str = "low";

pub async fn run(transport: LiveTransport) -> Result<()> {
    if transport == LiveTransport::AutoFallback {
        return run_auto_fallback().await;
    }
    if transport == LiveTransport::AutoTopology {
        return run_auto_topology().await;
    }
    if transport == LiveTransport::Bond {
        return crate::bond_e2e::run().await;
    }
    if transport == LiveTransport::BondScale {
        return crate::bond_e2e::run_scale().await;
    }
    if transport == LiveTransport::BondEndurance {
        return crate::bond_e2e::run_endurance().await;
    }
    if matches!(
        transport,
        LiveTransport::BondForward
            | LiveTransport::BondSsh
            | LiveTransport::BondTorSsh
            | LiveTransport::BondI2pSsh
    ) {
        return run_bond_ssh(transport).await;
    }
    if transport == LiveTransport::BondTools {
        return run_bond_tools().await;
    }
    if transport == LiveTransport::BondNative {
        return run_bond_native().await;
    }
    if transport == LiveTransport::ConcurrentBondSsh {
        return run_concurrent_bond_ssh().await;
    }
    if transport == LiveTransport::I2pPool {
        return crate::bond_e2e::run_i2p_pool().await;
    }
    if transport == LiveTransport::PoolRecovery {
        return crate::bond_e2e::run_pool_recovery().await;
    }
    if transport == LiveTransport::ProcessRestart {
        return run_process_restart().await;
    }
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for a live recovery test")?;
    let machine_id = format!("anonssh-live-test-{}", std::process::id());
    let root = live_test_root(transport);
    remove_if_present(&root)?;

    let endpoints = LiveEndpoints::allocate(transport)?;
    let mut server = match server_command(&executable, &root, &machine_id, transport, endpoints)
        .and_then(|mut command| command.spawn().context("failed to start live-test server"))
    {
        Ok(server) => server,
        Err(error) => return join_results(Err(error), remove_if_present(&root)),
    };
    let server_stdout = server.stdout.take();

    let operation = async {
        let server_stdout = server_stdout.context("live-test server stdout was not piped")?;
        let destination = wait_for_publication(server_stdout, transport).await?;
        let status = run_client(
            &executable,
            &root,
            transport,
            endpoints,
            &username,
            &machine_id,
        )
        .await?;
        if !status.success() {
            bail!("live-test client exited with {status}");
        }
        if transport == LiveTransport::I2pFresh {
            let retained_router_infos = verify_fresh_i2p_bootstrap(&root)?;
            let packaged_router_infos = crate::i2p_bootstrap::validate_embedded()?;
            println!(
                "{}",
                serde_json::to_string_pretty(&serde_json::json!({
                    "schema": "anonssh.live-i2p-fresh.v2",
                    "status": "ok",
                    "transport": "i2p",
                    "ssh": "derived-key-login",
                    "network_reseed": "disabled",
                    "packaged_router_infos": packaged_router_infos,
                    "retained_router_infos_after_login": retained_router_infos,
                    "destination": destination,
                }))?
            );
        } else {
            println!(
                "anonssh live {} test: ok ({destination})",
                transport_label(transport)
            );
        }
        Ok(())
    }
    .await;

    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop live-test server");
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove live-test state");
    join_results(operation, join_results(server_cleanup, filesystem_cleanup))
}

#[derive(Clone, Copy)]
struct LiveEndpoints {
    backend: SocketAddr,
    sam: Option<SocketAddr>,
    server_socks: Option<SocketAddr>,
    server_control: Option<SocketAddr>,
    client_socks: Option<SocketAddr>,
    client_control: Option<SocketAddr>,
}

impl LiveEndpoints {
    fn allocate(transport: LiveTransport) -> Result<Self> {
        let count = match transport {
            LiveTransport::AutoFallback
            | LiveTransport::AutoTopology
            | LiveTransport::Bond
            | LiveTransport::BondEndurance
            | LiveTransport::BondScale
            | LiveTransport::I2pPool
            | LiveTransport::PoolRecovery
            | LiveTransport::ProcessRestart => {
                bail!("bond test uses its own endpoint pool")
            }
            LiveTransport::BondForward
            | LiveTransport::BondNative
            | LiveTransport::BondSsh
            | LiveTransport::BondTools
            | LiveTransport::BondTorSsh
            | LiveTransport::BondI2pSsh
            | LiveTransport::ConcurrentBondSsh => {
                bail!("bonded SSH test uses its own endpoint pool")
            }
            LiveTransport::I2p => 1,
            LiveTransport::I2pFresh => 2,
            LiveTransport::Tor => 5,
        };
        let listeners = (0..count)
            .map(|_| TcpListener::bind("127.0.0.1:0"))
            .collect::<std::io::Result<Vec<_>>>()?;
        let addresses = listeners
            .iter()
            .map(TcpListener::local_addr)
            .collect::<std::io::Result<Vec<_>>>()?;
        Ok(Self {
            backend: addresses[0],
            sam: (transport == LiveTransport::I2pFresh).then(|| addresses[1]),
            server_socks: (transport == LiveTransport::Tor).then(|| addresses[1]),
            server_control: (transport == LiveTransport::Tor).then(|| addresses[2]),
            client_socks: (transport == LiveTransport::Tor).then(|| addresses[3]),
            client_control: (transport == LiveTransport::Tor).then(|| addresses[4]),
        })
    }
}

fn server_command(
    executable: &Path,
    root: &Path,
    machine_id: &str,
    transport: LiveTransport,
    endpoints: LiveEndpoints,
) -> Result<Command> {
    let mut command = Command::new(executable);
    command
        .arg("server")
        .arg("--machine-id")
        .arg(machine_id)
        .arg("--transport")
        .arg(transport_name(transport))
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_i2p_endpoint(&mut command, endpoints.sam);
    if transport == LiveTransport::I2pFresh {
        command.env("ANONSSH_INTERNAL_TEST_DISABLE_I2P_RESEED", "1");
    }
    configure_tor_endpoints(
        &mut command,
        endpoints.server_socks,
        endpoints.server_control,
    )?;
    Ok(command)
}

fn verify_fresh_i2p_bootstrap(root: &Path) -> Result<usize> {
    let i2pd = root.join("server/data/anonssh/i2pd");
    let config = fs::read_to_string(i2pd.join("i2pd.conf"))?;
    if !config.contains("[reseed]\nverify = true\nthreshold = 0\n") {
        bail!("fresh-I2P proof did not disable ordinary network reseeding");
    }
    let mut count = 0;
    for bucket in fs::read_dir(i2pd.join("netDb"))? {
        let bucket = bucket?;
        if !bucket.file_type()?.is_dir() {
            continue;
        }
        for entry in fs::read_dir(bucket.path())? {
            let entry = entry?;
            if entry.file_type()?.is_file()
                && entry
                    .file_name()
                    .to_str()
                    .is_some_and(|name| name.starts_with("routerInfo-") && name.ends_with(".dat"))
            {
                count += 1;
            }
        }
    }
    if count < 25 {
        bail!("i2pd retained only {count} packaged RouterInfos");
    }
    Ok(count)
}

async fn run_client(
    executable: &Path,
    root: &Path,
    transport: LiveTransport,
    endpoints: LiveEndpoints,
    username: &str,
    machine_id: &str,
) -> Result<std::process::ExitStatus> {
    let mut command = Command::new(executable);
    command
        .arg("connect")
        .arg(format!("{username}@{machine_id}"))
        .arg("--transport")
        .arg(transport_name(transport))
        .arg("--")
        .arg("-T")
        .arg("-n")
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("ANONSSH_INTERNAL_TEST_DIRECT_ROUTERS", "1")
        .env("XDG_CACHE_HOME", root.join("client/cache"))
        .env("XDG_DATA_HOME", root.join("client/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_i2p_endpoint(&mut command, endpoints.sam);
    configure_tor_endpoints(
        &mut command,
        endpoints.client_socks,
        endpoints.client_control,
    )?;
    let mut child = command
        .spawn()
        .context("failed to start live-test client")?;
    match timeout(CONNECTION_TIMEOUT, child.wait()).await {
        Ok(status) => status.context("failed to wait for live-test client"),
        Err(_) => {
            stop_child(&mut child).await?;
            bail!("live-test client exceeded its 15-minute deadline")
        }
    }
}

fn configure_i2p_endpoint(command: &mut Command, sam: Option<SocketAddr>) {
    if let Some(sam) = sam {
        command.env("ANONSSH_SAM_ADDR", sam.to_string());
    }
}

fn configure_tor_endpoints(
    command: &mut Command,
    socks: Option<SocketAddr>,
    control: Option<SocketAddr>,
) -> Result<()> {
    match (socks, control) {
        (Some(socks), Some(control)) => {
            command
                .env("ANONSSH_TOR_SOCKS_ADDR", socks.to_string())
                .env("ANONSSH_TOR_CONTROL_ADDR", control.to_string());
            Ok(())
        }
        (None, None) => Ok(()),
        _ => Err(anyhow!("incomplete live-test Tor endpoints")),
    }
}

async fn wait_for_publication(
    stdout: tokio::process::ChildStdout,
    transport: LiveTransport,
) -> Result<String> {
    let prefix = format!("{} ", transport_name(transport));
    timeout(PUBLICATION_TIMEOUT, async {
        let mut lines = BufReader::new(stdout).lines();
        while let Some(line) = lines.next_line().await? {
            if let Some(destination) = line.strip_prefix(&prefix) {
                if destination.is_empty() {
                    bail!("live-test server published an empty destination")
                }
                return Ok(destination.to_owned());
            }
        }
        bail!("live-test server exited before publishing {prefix}")
    })
    .await
    .context("live-test server did not publish within ten minutes")?
}

fn live_test_root(transport: LiveTransport) -> PathBuf {
    let base = std::env::var_os("XDG_RUNTIME_DIR")
        .map(PathBuf::from)
        .filter(|path| path.is_absolute())
        .or_else(dirs::data_local_dir)
        .unwrap_or_else(std::env::temp_dir);
    base.join(format!(
        "anonssh-live-{}-{}",
        transport_label(transport),
        std::process::id()
    ))
}

fn transport_name(transport: LiveTransport) -> &'static str {
    match transport {
        LiveTransport::AutoFallback => "auto-fallback",
        LiveTransport::AutoTopology => "auto-topology",
        LiveTransport::Bond => "bond",
        LiveTransport::BondEndurance => "bond-endurance",
        LiveTransport::BondForward => "bond",
        LiveTransport::BondNative => "bond",
        LiveTransport::BondScale => "bond-scale",
        LiveTransport::BondSsh => "bond",
        LiveTransport::BondTools => "bond",
        LiveTransport::BondTorSsh => "bond-tor",
        LiveTransport::BondI2pSsh => "bond-i2p",
        LiveTransport::ConcurrentBondSsh => "bond",
        LiveTransport::I2pPool => "i2p-pool",
        LiveTransport::PoolRecovery => "pool-recovery",
        LiveTransport::ProcessRestart => "process-restart",
        LiveTransport::I2p | LiveTransport::I2pFresh => "i2p",
        LiveTransport::Tor => "tor",
    }
}

fn transport_label(transport: LiveTransport) -> &'static str {
    match transport {
        LiveTransport::AutoFallback => "auto-fallback",
        LiveTransport::AutoTopology => "auto-topology",
        LiveTransport::Bond => "bond",
        LiveTransport::BondEndurance => "bond-endurance",
        LiveTransport::BondForward => "bond-forward",
        LiveTransport::BondNative => "bond-native",
        LiveTransport::BondScale => "bond-scale",
        LiveTransport::BondSsh => "bond-ssh",
        LiveTransport::BondTools => "bond-tools",
        LiveTransport::BondTorSsh => "bond-tor-ssh",
        LiveTransport::BondI2pSsh => "bond-i2p-ssh",
        LiveTransport::ConcurrentBondSsh => "concurrent-bond-ssh",
        LiveTransport::I2p => "i2p",
        LiveTransport::I2pFresh => "i2p-fresh",
        LiveTransport::I2pPool => "i2p-pool",
        LiveTransport::PoolRecovery => "pool-recovery",
        LiveTransport::ProcessRestart => "process-restart",
        LiveTransport::Tor => "tor",
    }
}

async fn run_auto_fallback() -> Result<()> {
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for a live recovery test")?;
    let machine_id = format!("anonssh-live-auto-fallback-{}", std::process::id());
    let root = live_test_root(LiveTransport::AutoFallback);
    remove_if_present(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let client_runtime = root.join("client/runtime");

    let mut server = Command::new(&executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg("bond")
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    let mut server = server
        .spawn()
        .context("failed to start automatic-fallback server")?;
    let server_stdout = server.stdout.take();

    let operation = async {
        let stdout = server_stdout.context("automatic-fallback server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, "tor ").await?;
        let mut client = Command::new(&executable);
        client
            .arg("connect")
            .arg(format!("{username}@{machine_id}"))
            .arg("--transport")
            .arg("auto")
            .arg("--")
            .arg("-T")
            .arg("-n")
            .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
            .env("ANONSSH_VERBOSE_OUTPUT", "1")
            .env("ANONSSH_INTERNAL_TEST_STALL_BOND_MILLIS", "120000")
            .env("ANONSSH_I2PD_BIN", root.join("missing-client-i2pd"))
            .env(
                "ANONSSH_TOR_SOCKS_ADDR",
                endpoints.client.socks[0].to_string(),
            )
            .env(
                "ANONSSH_TOR_CONTROL_ADDR",
                endpoints.client.control[0].to_string(),
            )
            .env("XDG_CACHE_HOME", root.join("client/cache"))
            .env("XDG_DATA_HOME", root.join("client/data"))
            .env("XDG_RUNTIME_DIR", &client_runtime)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::piped())
            .kill_on_drop(true);
        configure_client_bond_pool(&mut client, endpoints.client);
        let output = timeout(CONNECTION_TIMEOUT, client.output())
            .await
            .context("automatic fallback client exceeded its 15-minute deadline")??;
        if !output.status.success() {
            bail!(
                "automatic fallback client exited with {}: {}",
                output.status,
                String::from_utf8_lossy(&output.stderr)
            );
        }
        let stderr = String::from_utf8_lossy(&output.stderr);
        let route_report = stderr
            .lines()
            .find_map(|line| line.strip_prefix("anonssh-route: "))
            .context("automatic fallback omitted its structured route report")?;
        let route_report: serde_json::Value = serde_json::from_str(route_report)
            .context("automatic fallback emitted invalid route-report JSON")?;
        if route_report
            .get("winner")
            .and_then(serde_json::Value::as_str)
            != Some("tor")
        {
            bail!("automatic fallback did not select direct Tor: {route_report}");
        }
        let attempts = route_report
            .get("attempts")
            .and_then(serde_json::Value::as_array)
            .context("automatic fallback report omitted attempts")?;
        let outcome = |route: &str| {
            attempts.iter().find_map(|attempt| {
                (attempt.get("route").and_then(serde_json::Value::as_str) == Some(route))
                    .then(|| attempt.get("outcome").and_then(serde_json::Value::as_str))
                    .flatten()
            })
        };
        if outcome("bond-tor") != Some("canceled") || outcome("tor") != Some("succeeded") {
            bail!("automatic fallback did not cancel stalled bond after Tor won: {route_report}");
        }
        println!(
            "{}",
            serde_json::json!({
                "schema": "anonssh.live-auto-fallback.v2",
                "status": "ok",
                "server_transport": "bond",
                "stalled_client_route": "bond-tor",
                "fallback_route": "tor",
                "direct_destination": destination,
                "ssh": "derived-key-login",
                "route_report": route_report,
            })
        );
        Ok(())
    }
    .await;

    let broker_cleanup = stop_test_broker(&executable, &client_runtime)
        .await
        .context("failed to stop automatic-fallback broker");
    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop automatic-fallback server");
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove live-test state");
    join_results(
        operation,
        join_results(
            broker_cleanup,
            join_results(server_cleanup, filesystem_cleanup),
        ),
    )
}

async fn run_auto_topology() -> Result<()> {
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for a live recovery test")?;
    let mut cases = Vec::new();
    for transport in [
        LiveTransport::BondSsh,
        LiveTransport::BondTorSsh,
        LiveTransport::BondI2pSsh,
    ] {
        cases.push(run_auto_topology_case(&executable, &username, transport).await?);
    }
    println!(
        "{}",
        serde_json::json!({
            "schema": "anonssh.live-auto-topology.v1",
            "status": "ok",
            "cases": cases,
        })
    );
    Ok(())
}

async fn run_auto_topology_case(
    executable: &Path,
    username: &str,
    transport: LiveTransport,
) -> Result<serde_json::Value> {
    let topology = bond_ssh_topology(transport)?;
    let machine_id = format!(
        "anonssh-live-auto-{}-{}",
        transport_label(transport),
        std::process::id()
    );
    let root = live_test_root(transport).with_file_name(format!(
        "anonssh-live-auto-{}-{}",
        transport_label(transport),
        std::process::id()
    ));
    remove_if_present(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let client_runtime = root.join("client/runtime");

    let mut server = Command::new(executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg(topology.transport)
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    isolate_unused_provider(&mut server, &root, topology);
    let mut server = server
        .spawn()
        .context("failed to start automatic-topology server")?;
    let server_stdout = server.stdout.take();

    let operation = async {
        let stdout = server_stdout.context("automatic-topology server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, topology.publication_prefix).await?;
        let mut client = Command::new(executable);
        client
            .arg("connect")
            .arg(format!("{username}@{machine_id}"))
            .arg("--transport")
            .arg("auto")
            .arg("--")
            .arg("-T")
            .arg("-n")
            .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
            .env("ANONSSH_VERBOSE_OUTPUT", "1")
            .env("ANONSSH_INTERNAL_TEST_FAIL_DIRECT", "1")
            .env("XDG_CACHE_HOME", root.join("client/cache"))
            .env("XDG_DATA_HOME", root.join("client/data"))
            .env("XDG_RUNTIME_DIR", &client_runtime)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::piped())
            .kill_on_drop(true);
        configure_client_bond_pool(&mut client, endpoints.client);
        isolate_unused_provider(&mut client, &root, topology);
        let output = timeout(CONNECTION_TIMEOUT, client.output())
            .await
            .context("automatic topology client exceeded its 15-minute deadline")??;
        if !output.status.success() {
            bail!(
                "automatic topology client exited with {}: {}",
                output.status,
                String::from_utf8_lossy(&output.stderr)
            );
        }
        let stderr = String::from_utf8_lossy(&output.stderr);
        let report = parse_auto_route_report(&stderr)?;
        let expected_route = match transport {
            LiveTransport::BondSsh => "bond-mixed",
            LiveTransport::BondTorSsh => "bond-tor",
            LiveTransport::BondI2pSsh => "bond-i2p",
            _ => bail!("automatic topology case is not bonded"),
        };
        if report.get("winner").and_then(serde_json::Value::as_str) != Some(expected_route) {
            bail!("automatic topology selected the wrong route: {report}");
        }
        let broker_status = read_test_broker_status(executable, &client_runtime).await?;
        let session = broker_status
            .bond_session_topologies
            .iter()
            .find(|session| session.topology == expected_route)
            .context("broker status omitted the selected automatic topology")?;
        let candidate_lane_ids = topology.candidate_lane_ids();
        if !session.statistics_available
            || session.candidate_lanes != topology.candidate_lanes()
            || session.active_lane_ids.is_empty()
            || !session
                .active_lane_ids
                .iter()
                .all(|lane_id| candidate_lane_ids.contains(lane_id))
        {
            bail!("automatic topology broker status was inconsistent: {broker_status:?}");
        }
        Ok(serde_json::json!({
            "server_transport": topology.transport,
            "selected_route": expected_route,
            "unrelated_provider_executable": if topology.tor_slots == 0 || topology.i2p_slots == 0 {
                "unavailable"
            } else {
                "not-applicable"
            },
            "direct_candidates": "failed-by-test-policy",
            "publication_destination": destination,
            "declared_candidate_lane_ids": candidate_lane_ids,
            "active_lane_ids": session.active_lane_ids,
            "broker_status_schema": broker_status.schema,
            "route_report": report,
            "ssh": "derived-key-login",
        }))
    }
    .await;

    let broker_cleanup = stop_test_broker(executable, &client_runtime)
        .await
        .context("failed to stop automatic-topology broker");
    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop automatic-topology server");
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove live-test state");
    merge_value_cleanup(
        operation,
        join_results(
            broker_cleanup,
            join_results(server_cleanup, filesystem_cleanup),
        ),
    )
}

fn parse_auto_route_report(stderr: &str) -> Result<serde_json::Value> {
    let report = stderr
        .lines()
        .find_map(|line| line.strip_prefix("anonssh-route: "))
        .context("automatic connection omitted its structured route report")?;
    serde_json::from_str(report).context("automatic connection emitted invalid route-report JSON")
}

fn merge_value_cleanup<T>(operation: Result<T>, cleanup: Result<()>) -> Result<T> {
    match (operation, cleanup) {
        (Ok(value), Ok(())) => Ok(value),
        (Err(error), Ok(())) | (Ok(_), Err(error)) => Err(error),
        (Err(operation), Err(cleanup)) => {
            Err(anyhow!("{operation:#}; cleanup also failed: {cleanup:#}"))
        }
    }
}

#[derive(Clone, Copy)]
struct BondSshEndpoints {
    backend: SocketAddr,
    local_forward: SocketAddr,
    remote_service: SocketAddr,
    server: ClientPoolEndpoints,
    client: ClientPoolEndpoints,
}

impl BondSshEndpoints {
    fn allocate() -> Result<Self> {
        let pool_size = ClientPoolEndpoints::address_count();
        let listeners = (0..3 + 2 * pool_size)
            .map(|_| TcpListener::bind("127.0.0.1:0"))
            .collect::<std::io::Result<Vec<_>>>()?;
        let addresses = listeners
            .iter()
            .map(TcpListener::local_addr)
            .collect::<std::io::Result<Vec<_>>>()?;
        Ok(Self {
            backend: addresses[0],
            local_forward: addresses[1],
            remote_service: addresses[2],
            server: ClientPoolEndpoints::from_addresses(&addresses[3..3 + pool_size])?,
            client: ClientPoolEndpoints::from_addresses(&addresses[3 + pool_size..])?,
        })
    }
}

#[derive(Clone, Copy)]
struct ClientPoolEndpoints {
    sam: [SocketAddr; PRODUCTION_I2P_SLOTS],
    socks: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
    control: [SocketAddr; PRODUCTION_TOR_CANDIDATES],
}

impl ClientPoolEndpoints {
    const fn address_count() -> usize {
        PRODUCTION_I2P_SLOTS + 2 * PRODUCTION_TOR_CANDIDATES
    }

    fn from_addresses(addresses: &[SocketAddr]) -> Result<Self> {
        if addresses.len() != Self::address_count() {
            bail!("bond endpoint pool has the wrong size");
        }
        let socks_end = PRODUCTION_I2P_SLOTS + PRODUCTION_TOR_CANDIDATES;
        Ok(Self {
            sam: addresses[..PRODUCTION_I2P_SLOTS].try_into()?,
            socks: addresses[PRODUCTION_I2P_SLOTS..socks_end].try_into()?,
            control: addresses[socks_end..].try_into()?,
        })
    }

    fn all(self) -> Vec<SocketAddr> {
        self.sam
            .into_iter()
            .chain(self.socks)
            .chain(self.control)
            .collect()
    }
}

struct ConcurrentBondSshEndpoints {
    backend: SocketAddr,
    secondary_backend: SocketAddr,
    server: ClientPoolEndpoints,
    secondary_server: ClientPoolEndpoints,
    client: ClientPoolEndpoints,
}

impl ConcurrentBondSshEndpoints {
    fn allocate() -> Result<Self> {
        let pool_size = ClientPoolEndpoints::address_count();
        let listeners = (0..2 + 3 * pool_size)
            .map(|_| TcpListener::bind("127.0.0.1:0"))
            .collect::<std::io::Result<Vec<_>>>()?;
        let addresses = listeners
            .iter()
            .map(TcpListener::local_addr)
            .collect::<std::io::Result<Vec<_>>>()?;
        Ok(Self {
            backend: addresses[0],
            secondary_backend: addresses[1],
            server: ClientPoolEndpoints::from_addresses(&addresses[2..2 + pool_size])?,
            secondary_server: ClientPoolEndpoints::from_addresses(
                &addresses[2 + pool_size..2 + 2 * pool_size],
            )?,
            client: ClientPoolEndpoints::from_addresses(&addresses[2 + 2 * pool_size..])?,
        })
    }
}

#[derive(Clone, Copy)]
struct BondSshTopology {
    transport: &'static str,
    publication_prefix: &'static str,
    tor_slots: usize,
    i2p_slots: usize,
}

impl BondSshTopology {
    const fn candidate_lanes(self) -> usize {
        self.tor_slots + self.i2p_slots
    }

    fn required_lane_ids(self) -> Vec<u64> {
        if self.tor_slots > 0 && self.i2p_slots > 0 {
            let i2p_first = u64::try_from(self.tor_slots).expect("pool cardinality fits u64") + 1;
            vec![1, 2, i2p_first, i2p_first + 1]
        } else if self.tor_slots > 0 {
            let first = u64::from(TOR_ONLY_LANE_OFFSET) + 1;
            (first..first + u64::try_from(self.candidate_lanes().min(4)).unwrap_or(4)).collect()
        } else {
            let first = u64::from(I2P_ONLY_LANE_OFFSET) + 1;
            (first..first + u64::try_from(self.candidate_lanes().min(4)).unwrap_or(4)).collect()
        }
    }

    fn candidate_lane_ids(self) -> Vec<u64> {
        let first = if self.tor_slots > 0 && self.i2p_slots > 0 {
            1
        } else if self.tor_slots > 0 {
            u64::from(TOR_ONLY_LANE_OFFSET) + 1
        } else {
            u64::from(I2P_ONLY_LANE_OFFSET) + 1
        };
        (first..first + u64::try_from(self.candidate_lanes()).unwrap_or(0)).collect()
    }
}

fn bond_ssh_topology(transport: LiveTransport) -> Result<BondSshTopology> {
    match transport {
        LiveTransport::BondForward
        | LiveTransport::BondNative
        | LiveTransport::BondSsh
        | LiveTransport::BondTools => Ok(BondSshTopology {
            transport: "bond",
            publication_prefix: "bond-tor-1 ",
            tor_slots: PRODUCTION_TOR_SLOTS,
            i2p_slots: PRODUCTION_I2P_SLOTS,
        }),
        LiveTransport::BondTorSsh => Ok(BondSshTopology {
            transport: "bond-tor",
            publication_prefix: "bond-tor-1 ",
            tor_slots: PRODUCTION_TOR_SLOTS,
            i2p_slots: 0,
        }),
        LiveTransport::BondI2pSsh => Ok(BondSshTopology {
            transport: "bond-i2p",
            publication_prefix: "bond-i2p-1 ",
            tor_slots: 0,
            i2p_slots: PRODUCTION_I2P_SLOTS,
        }),
        _ => bail!("live transport is not a bonded SSH topology"),
    }
}

async fn run_bond_ssh(transport: LiveTransport) -> Result<()> {
    if transport == LiveTransport::BondForward {
        return run_bond_forward().await;
    }
    let topology = bond_ssh_topology(transport)?;
    let adaptive_load = std::env::var_os("ANONSSH_INTERNAL_TEST_ADAPTIVE_LOAD").is_some();
    if adaptive_load && transport != LiveTransport::BondSsh {
        bail!("adaptive SSH load proof requires the mixed bond topology");
    }
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for a live recovery test")?;
    let machine_id = format!(
        "anonssh-live-{}-{}",
        transport_label(transport),
        std::process::id()
    );
    let root = live_test_root(transport);
    remove_if_present(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let bond_stats_artifact = root.join("client-bond-stats.json");
    let control_socket = root.join("ssh-control");

    let mut server = Command::new(&executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg(topology.transport)
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    isolate_unused_provider(&mut server, &root, topology);
    let mut server = server
        .spawn()
        .context("failed to start bonded SSH server")?;
    let server_stdout = server.stdout.take();

    let operation = async {
        let stdout = server_stdout.context("bonded SSH server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, topology.publication_prefix).await?;
        let mut client = Command::new(&executable);
        client
            .arg("connect")
            .arg(format!("{username}@{machine_id}"))
            .arg("--transport")
            .arg(topology.transport)
            .arg("--");
        if !adaptive_load {
            client.arg("-T");
        }
        client
            .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
            .env(
                "ANONSSH_INTERNAL_TEST_BOND_STATS_ARTIFACT",
                &bond_stats_artifact,
            )
            .env("XDG_CACHE_HOME", root.join("client/cache"))
            .env("XDG_DATA_HOME", root.join("client/data"))
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .kill_on_drop(true);
        if adaptive_load {
            client.env(
                "ANONSSH_INTERNAL_TEST_SSH_CONTROL_PATH",
                &control_socket,
            );
        }
        configure_client_bond_pool(&mut client, endpoints.client);
        isolate_unused_provider(&mut client, &root, topology);
        let mut client = client
            .spawn()
            .context("failed to start bonded SSH client")?;
        if adaptive_load {
            let workload = run_adaptive_ssh_workload(
                &control_socket,
                &bond_stats_artifact,
                &username,
                &machine_id,
                topology,
            );
            tokio::pin!(workload);
            let evidence = match tokio::select! {
                result = &mut workload => result,
                status = client.wait() => {
                    let status = status.context(
                        "failed to wait for adaptive bonded SSH client during startup"
                    )?;
                    bail!(
                        "adaptive bonded SSH client exited before the workload became ready: {status}"
                    );
                }
            } {
                Ok(evidence) => evidence,
                Err(error) => {
                    stop_child(&mut client).await?;
                    return Err(error);
                }
            };
            request_mux_master_exit(&control_socket, &username, &machine_id).await?;
            let status = match timeout(CONNECTION_TIMEOUT, client.wait()).await {
                Ok(status) => status.context("failed to wait for adaptive bonded SSH client")?,
                Err(_) => {
                    stop_child(&mut client).await?;
                    bail!("adaptive bonded SSH client exceeded its 15-minute deadline")
                }
            };
            if !status.success() {
                bail!("adaptive bonded SSH client exited with {status}");
            }
            println!(
                "{}",
                serde_json::json!({
                    "schema": "anonssh.live-adaptive-bond-ssh.v2",
                    "status": "ok",
                    "transport": topology.transport,
                    "discovery_destination": destination,
                    "candidate_lanes": topology.candidate_lanes(),
                    "required_lane_ids": topology.required_lane_ids(),
                    "initial_active_lanes": evidence.initial_active_lanes,
                    "bulk_bytes": evidence.bulk_bytes,
                    "bulk_sha256": evidence.bulk_sha256,
                    "max_active_lanes": evidence.max_active_lanes,
                    "demand_to_batch_admission_millis": evidence.demand_to_batch_admission_millis,
                    "demand_to_first_optional_active_millis":
                        evidence.demand_to_first_optional_active_millis,
                    "demand_to_useful_capacity_millis":
                        evidence.demand_to_useful_capacity_millis,
                    "max_parallel_admissions": evidence.max_parallel_admissions,
                    "controller_events": evidence.controller_events,
                    "expanded_lane_ids": evidence.expanded_lane_ids,
                    "expanded_lane_acknowledged_bytes": evidence.expanded_lane_acknowledged_bytes,
                    "lane_acknowledged_bytes": evidence.lane_acknowledged_bytes,
                    "final_active_lanes": evidence.final_active_lanes,
                    "final_running_router_processes": evidence.final_running_router_processes,
                    "max_queue_delay_micros": evidence.max_queue_delay_micros,
                    "max_send_window_utilization_percent":
                        evidence.max_send_window_utilization_percent,
                    "max_backpressured_streams": evidence.max_backpressured_streams,
                    "stream_backpressure_events": evidence.stream_backpressure_events,
                    "max_client_router_rss_bytes": evidence.max_client_router_rss_bytes,
                    "max_client_router_cpu_time_micros": evidence.max_client_router_cpu_time_micros,
                    "max_router_startup_millis": evidence.max_router_startup_millis,
                    "retransmitted_frames": evidence.retransmitted_frames,
                    "liveness_failures": evidence.liveness_failures,
                    "typing": {
                        "samples": evidence.typing_samples,
                        "round_trip_micros_p50": evidence.typing_p50_micros,
                        "round_trip_micros_p95": evidence.typing_p95_micros,
                        "round_trip_micros_max": evidence.typing_max_micros,
                    },
                    "ssh": "derived-key-multiplexed-channels",
                })
            );
            return Ok(());
        }
        let typing = match run_interactive_ssh_workload(
            &mut client,
            &bond_stats_artifact,
            topology,
        )
        .await
        {
            Ok(typing) => typing,
            Err(error) => {
                stop_child(&mut client).await?;
                return Err(error);
            }
        };
        let status = match timeout(CONNECTION_TIMEOUT, client.wait()).await {
            Ok(status) => status.context("failed to wait for bonded SSH client")?,
            Err(_) => {
                stop_child(&mut client).await?;
                bail!("bonded SSH client exceeded its 15-minute deadline")
            }
        };
        if !status.success() {
            bail!("bonded SSH client exited with {status}");
        }
        let (reserved_lane, final_active_lanes) =
            verify_bond_stats(&bond_stats_artifact, topology)?;
        println!(
            "{}",
            serde_json::json!({
                "schema": "anonssh.live-bond-ssh.v6",
                "status": "ok",
                "transport": topology.transport,
                "discovery_destination": destination,
                "tor_routers_per_endpoint": topology.tor_slots,
                "i2p_routers_per_endpoint": topology.i2p_slots,
                "router_candidates": 2 * topology.candidate_lanes(),
                "required_router_processes": 2 * topology.required_lane_ids().len(),
                "candidate_lanes": topology.candidate_lanes(),
                "required_lane_ids": topology.required_lane_ids(),
                "unused_provider_executable": if topology.tor_slots == 0 || topology.i2p_slots == 0 {
                    "unavailable"
                } else {
                    "not-applicable"
                },
                "ssh": "derived-key-login",
                "interactive": {
                    "initial_active_lanes": typing.initial_active_lanes,
                    "initial_observation": typing.initial_observation,
                    "exact_responses": typing.samples,
                    "round_trip_micros_p50": typing.p50_micros,
                    "round_trip_micros_p95": typing.p95_micros,
                    "round_trip_micros_max": typing.max_micros,
                    "post_workload_active_observation": typing.active_observation,
                    "post_workload_active_lanes": final_active_lanes,
                    "reserved_lane_with_scheduled_bytes": reserved_lane,
                }
            })
        );
        Ok(())
    }
    .await;

    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop bonded SSH server");
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove live-test state");
    join_results(operation, join_results(server_cleanup, filesystem_cleanup))
}

async fn run_bond_tools() -> Result<()> {
    let topology = bond_ssh_topology(LiveTransport::BondTools)?;
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let borg = resolve_executable("ANONSSH_BORG_BIN", "borg")?;
    let rsync = resolve_executable("ANONSSH_RSYNC_BIN", "rsync")?;
    let scp = resolve_executable("ANONSSH_SCP_CLIENT_BIN", "scp")?;
    let sftp = resolve_executable("ANONSSH_SFTP_CLIENT_BIN", "sftp")?;
    let git = resolve_executable("ANONSSH_GIT_BIN", "git")?;
    let git_receive_pack = resolve_executable("ANONSSH_GIT_RECEIVE_PACK_BIN", "git-receive-pack")?;
    let git_upload_pack = resolve_executable("ANONSSH_GIT_UPLOAD_PACK_BIN", "git-upload-pack")?;
    let sshfs = resolve_executable("ANONSSH_SSHFS_BIN", "sshfs")?;
    let fusermount = resolve_executable("ANONSSH_FUSERMOUNT_BIN", "fusermount3")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for the bonded tool test")?;
    let machine_id = format!("anonssh-live-bond-tools-{}", std::process::id());
    let root = live_test_root(LiveTransport::BondTools);
    remove_if_present(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let client_runtime = root.join("client/runtime");

    let mut server = Command::new(&executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg(topology.transport)
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    let mut server = server
        .spawn()
        .context("failed to start bonded tool-test server")?;
    let server_stdout = server.stdout.take();

    let operation = async {
        let stdout = server_stdout.context("bonded tool-test server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, topology.publication_prefix).await?;
        let remote_shell = format!("{} --transport bond -q", executable.display());
        let target = format!("{username}@{machine_id}");

        let rsync_evidence = run_bonded_rsync_proof(
            &rsync,
            &remote_shell,
            &target,
            &root,
            &client_runtime,
            endpoints.client,
        )
        .await?;
        let borg_evidence = run_bonded_borg_proof(
            &borg,
            &executable,
            &target,
            &root,
            &client_runtime,
            endpoints.client,
        )
        .await?;
        let file_transfer_evidence = run_bonded_file_transfer_proof(
            &scp,
            &sftp,
            &executable,
            &target,
            &root,
            &client_runtime,
            endpoints.client,
        )
        .await?;
        let sshfs_evidence = run_bonded_sshfs_proof(
            &sshfs,
            &fusermount,
            &executable,
            &target,
            &root,
            &client_runtime,
            endpoints.client,
        )
        .await?;
        let git_evidence = run_bonded_git_proof(
            &git,
            &git_receive_pack,
            &git_upload_pack,
            &remote_shell,
            &username,
            &machine_id,
            &root,
            &client_runtime,
            endpoints.client,
        )
        .await?;
        let process_evidence = run_remote_process_contract_proof(
            &executable,
            &target,
            &root,
            &client_runtime,
            endpoints.client,
        )
        .await?;
        let broker = read_test_broker_status(&executable, &client_runtime).await?;
        if broker.bond_sessions != 1 || broker.recent_bond_streams.len() < 6 {
            bail!("tool proof did not reuse one bond session across independent SSH streams");
        }
        Ok(serde_json::json!({
            "schema": "anonssh.live-bond-tools.v1",
            "status": "ok",
            "transport": "bond",
            "discovery_destination": destination,
            "rsync": rsync_evidence,
            "borg": borg_evidence,
            "openssh_file_transfer": file_transfer_evidence,
            "sshfs": sshfs_evidence,
            "git": git_evidence,
            "process_contract": process_evidence,
            "bond_sessions": broker.bond_sessions,
            "independent_streams_observed": broker.recent_bond_streams.len(),
        }))
    }
    .await;

    let broker_cleanup = stop_test_broker(&executable, &client_runtime)
        .await
        .context("failed to stop bonded tool-test broker");
    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop bonded tool-test server");
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove tool-test state");
    let report = merge_value_cleanup(
        operation,
        join_results(
            broker_cleanup,
            join_results(server_cleanup, filesystem_cleanup),
        ),
    )?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

const NATIVE_BULK_BYTES: usize = 8 * 1024 * 1024;
const NATIVE_REALTIME_BYTES: usize = 1024;

async fn run_bond_native() -> Result<()> {
    let transport = LiveTransport::BondNative;
    let topology = bond_ssh_topology(transport)?;
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for the bonded native-service test")?;
    let machine_id = format!("anonssh-live-bond-native-{}", std::process::id());
    let target = format!("{username}@{machine_id}");
    let root = live_test_root(transport);
    remove_if_present(&root)?;
    fs::create_dir_all(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let client_runtime = root.join("client/runtime");
    let service_socket = root.join("native-echo.sock");
    let service_listener = tokio::net::UnixListener::bind(&service_socket)
        .context("failed to bind the native echo service")?;
    fs::set_permissions(&service_socket, fs::Permissions::from_mode(0o600))?;
    let mut service_task = tokio::spawn(run_native_echo_service(service_listener, 2));

    let mut server = Command::new(&executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg(topology.transport)
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .arg("--native-service")
        .arg(format!("echo={}", service_socket.display()))
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    let mut server = match server.spawn() {
        Ok(server) => server,
        Err(error) => {
            service_task.abort();
            let _ = service_task.await;
            return join_results(
                Err(error).context("failed to start bonded native-service server"),
                remove_if_present(&root),
            );
        }
    };
    let server_stdout = server.stdout.take();

    let operation = async {
        let stdout = server_stdout.context("bonded native-service server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, topology.publication_prefix).await?;

        let mut authorize = Command::new(&executable);
        authorize.arg("authorize").arg(&target);
        configure_bond_tool_command(&mut authorize, &root, &client_runtime, endpoints.client);
        checked_tool_output(authorize, "native-service target authorization").await?;
        let socket_evidence = verify_public_transport_socket(&client_runtime)?;

        let bulk = (0..NATIVE_BULK_BYTES)
            .map(|index| ((index * 31 + 17) % 251) as u8)
            .collect::<Vec<_>>();
        let realtime = (0..NATIVE_REALTIME_BYTES)
            .map(|index| ((index * 47 + 29) % 251) as u8)
            .collect::<Vec<_>>();
        let bulk_dial = run_native_dial(
            &executable,
            &target,
            "bulk",
            bulk,
            &root,
            &client_runtime,
            endpoints.client,
        );
        let realtime_dial = run_native_dial(
            &executable,
            &target,
            "realtime",
            realtime,
            &root,
            &client_runtime,
            endpoints.client,
        );
        let (bulk, realtime) = tokio::try_join!(bulk_dial, realtime_dial)?;

        let broker = read_test_broker_status(&executable, &client_runtime).await?;
        if broker.authorized_targets != 1
            || broker.bond_sessions != 1
            || broker.recent_bond_streams.len() < 2
        {
            bail!(
                "native service proof did not retain one authorization and one reused bond session"
            );
        }
        let session_ids = broker
            .recent_bond_streams
            .iter()
            .map(|stream| stream.session_id)
            .collect::<BTreeSet<_>>();
        let stream_ids = broker
            .recent_bond_streams
            .iter()
            .map(|stream| stream.stream_id)
            .collect::<BTreeSet<_>>();
        if session_ids.len() != 1 || stream_ids.len() < 2 {
            bail!("native service streams were not independent members of one bond session");
        }

        Ok(serde_json::json!({
            "schema": "anonssh.live-bond-native.v1",
            "status": "ok",
            "transport": "bond",
            "discovery_destination": destination,
            "service": "echo",
            "authorization": "password-derived-broker-generation",
            "socket": socket_evidence,
            "simultaneous_streams": true,
            "bulk": bulk,
            "realtime": realtime,
            "bond_sessions": broker.bond_sessions,
            "independent_streams_observed": stream_ids.len(),
            "single_session_reused": true,
        }))
    }
    .await;

    let service_cleanup = if operation.is_ok() {
        match timeout(Duration::from_secs(10), &mut service_task).await {
            Ok(Ok(Ok(bytes)))
                if bytes.len() == 2
                    && bytes.iter().sum::<u64>()
                        == u64::try_from(NATIVE_BULK_BYTES + NATIVE_REALTIME_BYTES).unwrap() =>
            {
                Ok(())
            }
            Ok(Ok(Ok(bytes))) => bail!("native echo service observed unexpected bytes: {bytes:?}"),
            Ok(Ok(Err(error))) => Err(error).context("native echo service failed"),
            Ok(Err(error)) => Err(error).context("native echo service task failed"),
            Err(_) => {
                service_task.abort();
                let _ = service_task.await;
                bail!("native echo service did not finish after both streams closed")
            }
        }
    } else {
        service_task.abort();
        let _ = service_task.await;
        Ok(())
    };
    let broker_cleanup = stop_test_broker(&executable, &client_runtime)
        .await
        .context("failed to stop bonded native-service broker");
    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop bonded native-service server");
    #[cfg(target_os = "linux")]
    let server_cleanup = join_results(
        server_cleanup,
        wait_for_endpoints_released(server_endpoints(endpoints)).await,
    );
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove native-test state");
    let report = merge_value_cleanup(
        operation,
        join_results(
            service_cleanup,
            join_results(
                broker_cleanup,
                join_results(server_cleanup, filesystem_cleanup),
            ),
        ),
    )?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

async fn run_native_echo_service(
    listener: tokio::net::UnixListener,
    expected_connections: usize,
) -> Result<Vec<u64>> {
    let mut connections = tokio::task::JoinSet::new();
    for _ in 0..expected_connections {
        let (stream, _) = timeout(CONNECTION_TIMEOUT, listener.accept())
            .await
            .context("native echo service was not reached")??;
        connections.spawn(async move {
            let (mut reader, mut writer) = tokio::io::split(stream);
            let bytes = tokio::io::copy(&mut reader, &mut writer).await?;
            writer.shutdown().await?;
            Ok::<_, anyhow::Error>(bytes)
        });
    }
    let mut bytes = Vec::with_capacity(expected_connections);
    while let Some(result) = connections.join_next().await {
        bytes.push(result.context("native echo connection task failed")??);
    }
    Ok(bytes)
}

#[allow(clippy::too_many_arguments)]
async fn run_native_dial(
    executable: &Path,
    target: &str,
    class: &str,
    payload: Vec<u8>,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    let expected_bytes = payload.len();
    let expected_sha256 = format!("{:x}", Sha256::digest(&payload));
    let mut command = Command::new(executable);
    command
        .arg("dial")
        .arg(target)
        .arg("echo")
        .arg("--class")
        .arg(class)
        .arg("--transport")
        .arg("mixed")
        .arg("--deadline-seconds")
        .arg(CONNECTION_TIMEOUT.as_secs().to_string());
    configure_bond_tool_command(&mut command, root, client_runtime, endpoints);
    command.stdin(Stdio::piped()).stderr(Stdio::inherit());
    let started = Instant::now();
    let mut child = command
        .spawn()
        .with_context(|| format!("failed to start {class} native dial"))?;
    let mut stdin = child
        .stdin
        .take()
        .with_context(|| format!("{class} native dial omitted stdin"))?;
    let mut stdout = child
        .stdout
        .take()
        .with_context(|| format!("{class} native dial omitted stdout"))?;
    let transfer = async {
        let write = async move {
            stdin.write_all(&payload).await?;
            stdin.shutdown().await?;
            drop(stdin);
            Ok::<(), io::Error>(())
        };
        let read = async {
            let mut received = Vec::with_capacity(expected_bytes);
            stdout.read_to_end(&mut received).await?;
            Ok::<_, io::Error>(received)
        };
        let wait = child.wait();
        tokio::try_join!(write, read, wait)
    };
    let (_, received, status) = timeout(CONNECTION_TIMEOUT, transfer)
        .await
        .with_context(|| format!("{class} native dial exceeded its deadline"))??;
    if !status.success() {
        bail!("{class} native dial exited with {status}");
    }
    let actual_sha256 = format!("{:x}", Sha256::digest(&received));
    if received.len() != expected_bytes || actual_sha256 != expected_sha256 {
        bail!("{class} native dial changed its payload");
    }
    Ok(serde_json::json!({
        "class": class,
        "bytes": expected_bytes,
        "sha256": actual_sha256,
        "round_trip_micros": u64::try_from(started.elapsed().as_micros()).unwrap_or(u64::MAX),
        "byte_exact": true,
    }))
}

fn verify_public_transport_socket(runtime: &Path) -> Result<serde_json::Value> {
    let directory = runtime.join("anonssh");
    let socket = directory.join("transport.sock");
    let directory_metadata =
        fs::symlink_metadata(&directory).context("ALP runtime directory was not created")?;
    let socket_metadata =
        fs::symlink_metadata(&socket).context("ALP public transport socket was not created")?;
    let directory_mode = directory_metadata.permissions().mode() & 0o777;
    let socket_mode = socket_metadata.permissions().mode() & 0o777;
    if !directory_metadata.is_dir()
        || !socket_metadata.file_type().is_socket()
        || directory_mode != 0o700
        || socket_mode != 0o600
    {
        bail!("ALP public transport socket permissions or type are unsafe");
    }
    Ok(serde_json::json!({
        "runtime_directory_mode": format!("{directory_mode:04o}"),
        "transport_socket_mode": format!("{socket_mode:04o}"),
        "peer_credentials": "same-uid-required",
    }))
}

#[allow(clippy::too_many_arguments)]
async fn run_bonded_file_transfer_proof(
    scp: &Path,
    sftp: &Path,
    executable: &Path,
    target: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    let directory = root.join("openssh-file-transfer");
    fs::create_dir_all(&directory)?;
    let payload = (0..2 * 1024 * 1024)
        .map(|index| ((index * 43 + 19) % 251) as u8)
        .collect::<Vec<_>>();
    let source = directory.join("source.bin");
    fs::write(&source, &payload)?;

    let modern_remote = directory.join("modern-remote.bin");
    let modern_pull = directory.join("modern-pull.bin");
    run_scp(
        scp,
        executable,
        target,
        &source,
        &modern_remote,
        false,
        root,
        client_runtime,
        endpoints,
    )
    .await?;
    pull_scp(
        scp,
        executable,
        target,
        &modern_remote,
        &modern_pull,
        false,
        root,
        client_runtime,
        endpoints,
    )
    .await?;
    verify_file_transfer(&modern_remote, &payload, "modern scp upload")?;
    verify_file_transfer(&modern_pull, &payload, "modern scp download")?;

    let sftp_remote = directory.join("sftp-remote.bin");
    let sftp_pull = directory.join("sftp-pull.bin");
    let batch = directory.join("sftp.batch");
    fs::write(
        &batch,
        format!(
            "put {} {}\nget {} {}\n",
            source.display(),
            sftp_remote.display(),
            sftp_remote.display(),
            sftp_pull.display()
        ),
    )?;
    let mut sftp_command = Command::new(sftp);
    sftp_command
        .arg("-q")
        .arg("-b")
        .arg(&batch)
        .arg("-S")
        .arg(executable)
        .arg(target);
    configure_file_transfer_command(&mut sftp_command, root, client_runtime, endpoints);
    checked_tool_output(sftp_command, "SFTP batch upload/download").await?;
    verify_file_transfer(&sftp_remote, &payload, "SFTP upload")?;
    verify_file_transfer(&sftp_pull, &payload, "SFTP download")?;

    let legacy_remote = directory.join("legacy-remote.bin");
    let legacy_pull = directory.join("legacy-pull.bin");
    run_scp(
        scp,
        executable,
        target,
        &source,
        &legacy_remote,
        true,
        root,
        client_runtime,
        endpoints,
    )
    .await?;
    pull_scp(
        scp,
        executable,
        target,
        &legacy_remote,
        &legacy_pull,
        true,
        root,
        client_runtime,
        endpoints,
    )
    .await?;
    verify_file_transfer(&legacy_remote, &payload, "legacy scp upload")?;
    verify_file_transfer(&legacy_pull, &payload, "legacy scp download")?;

    Ok(serde_json::json!({
        "transport_hook": "stock-clients-with--S-anonssh",
        "payload_bytes": payload.len(),
        "scp_default": "bidirectional-exact",
        "sftp_batch": "bidirectional-exact",
        "scp_legacy": "bidirectional-exact",
    }))
}

#[allow(clippy::too_many_arguments)]
async fn run_scp(
    scp: &Path,
    executable: &Path,
    target: &str,
    source: &Path,
    remote: &Path,
    legacy: bool,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<()> {
    let mut command = Command::new(scp);
    command.arg("-q");
    if legacy {
        command.arg("-O");
    }
    command
        .arg("-S")
        .arg(executable)
        .arg(source)
        .arg(format!("{target}:{}", remote.display()));
    configure_file_transfer_command(&mut command, root, client_runtime, endpoints);
    checked_tool_output(
        command,
        if legacy {
            "legacy scp upload"
        } else {
            "scp upload"
        },
    )
    .await?;
    Ok(())
}

#[allow(clippy::too_many_arguments)]
async fn pull_scp(
    scp: &Path,
    executable: &Path,
    target: &str,
    remote: &Path,
    destination: &Path,
    legacy: bool,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<()> {
    let mut command = Command::new(scp);
    command.arg("-q");
    if legacy {
        command.arg("-O");
    }
    command
        .arg("-S")
        .arg(executable)
        .arg(format!("{target}:{}", remote.display()))
        .arg(destination);
    configure_file_transfer_command(&mut command, root, client_runtime, endpoints);
    checked_tool_output(
        command,
        if legacy {
            "legacy scp download"
        } else {
            "scp download"
        },
    )
    .await?;
    Ok(())
}

fn configure_file_transfer_command(
    command: &mut Command,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) {
    configure_bond_tool_command(command, root, client_runtime, endpoints);
    command.env("ANONSSH_TRANSPORT_PROFILE", "mixed");
}

fn verify_file_transfer(path: &Path, payload: &[u8], label: &str) -> Result<()> {
    if fs::read(path).with_context(|| format!("failed to read {label}"))? != payload {
        bail!("{label} changed the payload");
    }
    Ok(())
}

#[allow(clippy::too_many_arguments)]
async fn run_bonded_borg_proof(
    borg: &Path,
    executable: &Path,
    target: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    use std::os::unix::fs::symlink;

    let directory = root.join("borg");
    let source = directory.join("source");
    let repository = directory.join("repository");
    let extracted = directory.join("extracted");
    fs::create_dir_all(source.join("nested"))?;
    fs::create_dir_all(&extracted)?;
    let payload = (0..4 * 1024 * 1024)
        .map(|index| ((index * 37 + 23) % 251) as u8)
        .collect::<Vec<_>>();
    fs::write(source.join("nested/payload.bin"), &payload)?;
    fs::write(source.join("named file.txt"), b"anonssh-borg\n")?;
    fs::set_permissions(
        source.join("named file.txt"),
        fs::Permissions::from_mode(0o640),
    )?;
    symlink("named file.txt", source.join("link"))?;

    let remote_repository = format!("{target}:{}", repository.display());
    let archive = format!("{remote_repository}::snapshot");
    let remote_shell = format!("{} --transport bond -q", executable.display());

    let mut init = borg_command(borg, &remote_shell, root, client_runtime, endpoints);
    init.arg("init")
        .arg("--encryption=none")
        .arg(&remote_repository);
    checked_tool_output(init, "Borg repository initialization").await?;

    let mut create = borg_command(borg, &remote_shell, root, client_runtime, endpoints);
    create
        .arg("create")
        .arg("--compression=none")
        .arg(&archive)
        .arg("source")
        .current_dir(&directory);
    checked_tool_output(create, "Borg archive creation").await?;

    let mut check = borg_command(borg, &remote_shell, root, client_runtime, endpoints);
    check.arg("check").arg(&remote_repository);
    checked_tool_output(check, "Borg repository check").await?;

    let mut extract = borg_command(borg, &remote_shell, root, client_runtime, endpoints);
    extract.arg("extract").arg(&archive).current_dir(&extracted);
    checked_tool_output(extract, "Borg archive extraction").await?;

    let restored = extracted.join("source");
    if fs::read(restored.join("nested/payload.bin"))? != payload
        || fs::read(restored.join("named file.txt"))? != b"anonssh-borg\n"
        || fs::read_link(restored.join("link"))? != Path::new("named file.txt")
        || fs::metadata(restored.join("named file.txt"))?
            .permissions()
            .mode()
            & 0o777
            != 0o640
    {
        bail!("Borg did not restore the exact payload and metadata");
    }

    Ok(serde_json::json!({
        "transport_hook": "BORG_RSH=anonssh",
        "repository": "initialized-and-checked",
        "archive": "created-and-extracted",
        "payload_bytes": payload.len(),
        "metadata": ["mode", "symlink", "spaces"],
    }))
}

fn borg_command(
    borg: &Path,
    remote_shell: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Command {
    let mut command = Command::new(borg);
    command
        .arg("--remote-path")
        .arg(borg)
        .env("BORG_RSH", remote_shell)
        .env("BORG_CACHE_DIR", root.join("borg/client/cache"))
        .env("BORG_CONFIG_DIR", root.join("borg/client/config"))
        .env("BORG_SECURITY_DIR", root.join("borg/client/security"))
        .env("BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK", "yes")
        .env("BORG_RELOCATED_REPO_ACCESS_IS_OK", "yes");
    configure_bond_tool_command(&mut command, root, client_runtime, endpoints);
    command
}

#[allow(clippy::too_many_arguments)]
async fn run_bonded_sshfs_proof(
    sshfs: &Path,
    fusermount: &Path,
    executable: &Path,
    target: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    let directory = root.join("sshfs");
    let remote = directory.join("remote");
    let mountpoint = directory.join("mount");
    fs::create_dir_all(&remote)?;
    fs::create_dir_all(&mountpoint)?;
    let remote_payload = (0..2 * 1024 * 1024)
        .map(|index| ((index * 41 + 29) % 251) as u8)
        .collect::<Vec<_>>();
    let written_payload = (0..2 * 1024 * 1024)
        .map(|index| ((index * 47 + 31) % 251) as u8)
        .collect::<Vec<_>>();
    fs::write(remote.join("remote.bin"), &remote_payload)?;

    let remote_specification = format!("{target}:{}", remote.display());
    let ssh_command = format!("{} --transport bond -q", executable.display());
    let mut command = Command::new(sshfs);
    command
        .arg(&remote_specification)
        .arg(&mountpoint)
        .arg("-f")
        .arg("-s")
        .arg("-o")
        .arg(format!("ssh_command={ssh_command}"))
        .arg("-o")
        .arg("idmap=none")
        .arg("-o")
        .arg("dir_cache=no");
    configure_bond_tool_command(&mut command, root, client_runtime, endpoints);
    let mut child = command.spawn().context("failed to start SSHFS")?;
    let mut stdout = child.stdout.take().context("SSHFS stdout was not piped")?;
    let mut stderr = child.stderr.take().context("SSHFS stderr was not piped")?;
    let stdout_reader = tokio::spawn(async move {
        let mut bytes = Vec::new();
        stdout.read_to_end(&mut bytes).await.map(|_| bytes)
    });
    let stderr_reader = tokio::spawn(async move {
        let mut bytes = Vec::new();
        stderr.read_to_end(&mut bytes).await.map(|_| bytes)
    });

    let operation = async {
        wait_for_sshfs_mount(&mut child, &mountpoint).await?;
        if fs::read(mountpoint.join("remote.bin"))? != remote_payload {
            bail!("SSHFS changed the remotely created payload");
        }
        let mounted_written = mountpoint.join("written.bin");
        fs::write(&mounted_written, &written_payload)?;
        fs::OpenOptions::new()
            .read(true)
            .write(true)
            .open(&mounted_written)?
            .sync_all()?;
        fs::rename(&mounted_written, mountpoint.join("renamed.bin"))?;
        if fs::read(remote.join("renamed.bin"))? != written_payload {
            bail!("SSHFS changed the locally written payload");
        }
        Ok::<_, anyhow::Error>(())
    }
    .await;

    let unmount = if sshfs_mount_present(&mountpoint)? {
        unmount_sshfs(fusermount, &mountpoint).await
    } else {
        Ok(())
    };
    if operation.is_err() || unmount.is_err() {
        let _ = child.start_kill();
    }
    let status = timeout(Duration::from_secs(30), child.wait())
        .await
        .context("SSHFS did not stop after unmount")??;
    let stdout = stdout_reader
        .await
        .context("SSHFS stdout reader failed")??;
    let stderr = stderr_reader
        .await
        .context("SSHFS stderr reader failed")??;
    operation.and(unmount)?;
    if !status.success() || sshfs_mount_present(&mountpoint)? {
        bail!(
            "SSHFS cleanup failed with {status}: stdout={} stderr={}",
            String::from_utf8_lossy(&stdout).trim(),
            String::from_utf8_lossy(&stderr).trim()
        );
    }

    Ok(serde_json::json!({
        "transport_hook": "sshfs_-o_ssh_command=anonssh",
        "remote_read": "byte-exact",
        "remote_write": "byte-exact",
        "rename": "verified",
        "payload_bytes_each_direction": remote_payload.len(),
        "managed_unmount": true,
    }))
}

async fn wait_for_sshfs_mount(child: &mut Child, mountpoint: &Path) -> Result<()> {
    timeout(Duration::from_secs(120), async {
        loop {
            if sshfs_mount_present(mountpoint)? {
                return Ok(());
            }
            if let Some(status) = child.try_wait()? {
                bail!("SSHFS exited before mounting with {status}");
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("SSHFS did not mount within its deadline")?
}

fn sshfs_mount_present(mountpoint: &Path) -> Result<bool> {
    let mountpoint = fs::canonicalize(mountpoint)?;
    let mountpoint = mountpoint.to_string_lossy();
    let mountinfo = fs::read_to_string("/proc/self/mountinfo")?;
    Ok(mountinfo.lines().any(|line| {
        line.split_ascii_whitespace()
            .nth(4)
            .is_some_and(|candidate| candidate == mountpoint.as_ref())
    }))
}

async fn unmount_sshfs(fusermount: &Path, mountpoint: &Path) -> Result<()> {
    let mut command = Command::new(fusermount);
    command
        .arg("-u")
        .arg(mountpoint)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    let output = timeout(Duration::from_secs(30), command.output())
        .await
        .context("fusermount did not finish within its deadline")??;
    if !output.status.success() {
        bail!(
            "fusermount failed with {}: {}",
            output.status,
            String::from_utf8_lossy(&output.stderr).trim()
        );
    }
    Ok(())
}

async fn run_bonded_rsync_proof(
    rsync: &Path,
    remote_shell: &str,
    target: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    use std::os::unix::fs::{symlink, PermissionsExt};

    let source = root.join("rsync/source");
    let remote = root.join("rsync/remote");
    let pulled = root.join("rsync/pulled");
    fs::create_dir_all(source.join("nested"))?;
    fs::create_dir_all(&remote)?;
    fs::create_dir_all(&pulled)?;
    let payload = (0..8 * 1024 * 1024)
        .map(|index| ((index * 31 + 17) % 251) as u8)
        .collect::<Vec<_>>();
    fs::write(source.join("partial.bin"), &payload)?;
    fs::write(remote.join("partial.bin"), &payload[..payload.len() / 2])?;
    fs::write(
        source.join("nested/file with spaces.txt"),
        b"anonssh-rsync\n",
    )?;
    fs::write(source.join("nested/unicode-\u{03bb}.txt"), b"lambda\n")?;
    fs::set_permissions(
        source.join("nested/file with spaces.txt"),
        fs::Permissions::from_mode(0o640),
    )?;
    symlink("file with spaces.txt", source.join("nested/link"))?;

    let mut push = Command::new(rsync);
    push.arg("-a")
        .arg("--checksum")
        .arg("--append-verify")
        .arg("--rsh")
        .arg(remote_shell)
        .arg(format!("--rsync-path={}", rsync.display()))
        .arg(format!("{}/", source.display()))
        .arg(format!("{target}:{}/", remote.display()));
    configure_bond_tool_command(&mut push, root, client_runtime, endpoints);
    checked_tool_output(push, "rsync push").await?;
    verify_rsync_tree(&remote, &payload)?;

    fs::write(remote.join("returned.txt"), b"remote-to-local\n")?;
    let mut pull = Command::new(rsync);
    pull.arg("-a")
        .arg("--checksum")
        .arg("--rsh")
        .arg(remote_shell)
        .arg(format!("--rsync-path={}", rsync.display()))
        .arg(format!("{target}:{}/", remote.display()))
        .arg(format!("{}/", pulled.display()));
    configure_bond_tool_command(&mut pull, root, client_runtime, endpoints);
    checked_tool_output(pull, "rsync pull").await?;
    verify_rsync_tree(&pulled, &payload)?;
    if fs::read(pulled.join("returned.txt"))? != b"remote-to-local\n" {
        bail!("rsync pull did not preserve the remote-only file");
    }

    Ok(serde_json::json!({
        "push": "verified",
        "pull": "verified",
        "resume": "append-verify-from-half",
        "payload_bytes": payload.len(),
        "metadata": ["mode", "symlink", "spaces", "unicode"],
    }))
}

fn verify_rsync_tree(root: &Path, payload: &[u8]) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;

    if fs::read(root.join("partial.bin"))? != payload {
        bail!("rsync payload did not arrive exactly");
    }
    if fs::read(root.join("nested/file with spaces.txt"))? != b"anonssh-rsync\n"
        || fs::read(root.join("nested/unicode-\u{03bb}.txt"))? != b"lambda\n"
    {
        bail!("rsync named-file payload did not arrive exactly");
    }
    if fs::metadata(root.join("nested/file with spaces.txt"))?
        .permissions()
        .mode()
        & 0o777
        != 0o640
    {
        bail!("rsync did not preserve file mode");
    }
    if fs::read_link(root.join("nested/link"))? != Path::new("file with spaces.txt") {
        bail!("rsync did not preserve the symbolic link");
    }
    Ok(())
}

#[allow(clippy::too_many_arguments)]
async fn run_bonded_git_proof(
    git: &Path,
    git_receive_pack: &Path,
    git_upload_pack: &Path,
    remote_shell: &str,
    username: &str,
    machine_id: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    let source = root.join("git/source");
    let remote = root.join("git/remote.git");
    let checkout = root.join("git/checkout");
    fs::create_dir_all(root.join("git"))?;

    checked_git(
        git,
        ["init", "--bare", remote.to_str().unwrap()],
        "git init bare",
    )
    .await?;
    checked_git(git, ["init", source.to_str().unwrap()], "git init source").await?;
    checked_git(
        git,
        [
            "-C",
            source.to_str().unwrap(),
            "config",
            "user.name",
            "AnonSSH Test",
        ],
        "git configure user name",
    )
    .await?;
    checked_git(
        git,
        [
            "-C",
            source.to_str().unwrap(),
            "config",
            "user.email",
            "anonssh@example.invalid",
        ],
        "git configure user email",
    )
    .await?;
    fs::write(source.join("payload.txt"), b"first\n")?;
    checked_git(
        git,
        ["-C", source.to_str().unwrap(), "add", "payload.txt"],
        "git add",
    )
    .await?;
    checked_git(
        git,
        ["-C", source.to_str().unwrap(), "commit", "-m", "first"],
        "git first commit",
    )
    .await?;

    let remote_url = format!("ssh://{username}@{machine_id}{}", remote.display());
    let mut push = Command::new(git);
    push.arg("-C")
        .arg(&source)
        .arg("push")
        .arg(format!("--receive-pack={}", git_receive_pack.display()))
        .arg(&remote_url)
        .arg("HEAD:refs/heads/main");
    configure_git_transport(&mut push, remote_shell, root, client_runtime, endpoints);
    checked_tool_output(push, "Git push").await?;

    let mut clone = Command::new(git);
    clone
        .arg("clone")
        .arg(format!("--upload-pack={}", git_upload_pack.display()))
        .arg("--branch")
        .arg("main")
        .arg(&remote_url)
        .arg(&checkout);
    configure_git_transport(&mut clone, remote_shell, root, client_runtime, endpoints);
    checked_tool_output(clone, "Git clone").await?;

    fs::write(source.join("payload.txt"), b"second\n")?;
    checked_git(
        git,
        ["-C", source.to_str().unwrap(), "add", "payload.txt"],
        "git add update",
    )
    .await?;
    checked_git(
        git,
        ["-C", source.to_str().unwrap(), "commit", "-m", "second"],
        "git second commit",
    )
    .await?;
    let mut second_push = Command::new(git);
    second_push
        .arg("-C")
        .arg(&source)
        .arg("push")
        .arg(format!("--receive-pack={}", git_receive_pack.display()))
        .arg(&remote_url)
        .arg("HEAD:refs/heads/main");
    configure_git_transport(
        &mut second_push,
        remote_shell,
        root,
        client_runtime,
        endpoints,
    );
    checked_tool_output(second_push, "Git second push").await?;

    let mut fetch = Command::new(git);
    fetch
        .arg("-C")
        .arg(&checkout)
        .arg("fetch")
        .arg(format!("--upload-pack={}", git_upload_pack.display()))
        .arg("origin");
    configure_git_transport(&mut fetch, remote_shell, root, client_runtime, endpoints);
    checked_tool_output(fetch, "Git fetch").await?;
    let source_head = git_stdout(git, &source, ["rev-parse", "HEAD"]).await?;
    let fetched_head = git_stdout(git, &checkout, ["rev-parse", "origin/main"]).await?;
    if source_head != fetched_head {
        bail!("Git fetch did not retrieve the pushed commit");
    }

    Ok(serde_json::json!({
        "push": "verified",
        "clone": "verified",
        "fetch": "verified",
        "head": source_head.trim(),
    }))
}

async fn run_remote_process_contract_proof(
    executable: &Path,
    target: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<serde_json::Value> {
    let mut exact = Command::new(executable);
    exact
        .arg("--transport")
        .arg("bond")
        .arg("-q")
        .arg("-T")
        .arg(target)
        .arg("printf 'tool-stdout\\n'; printf 'tool-stderr\\n' >&2; exit 23");
    configure_bond_tool_command(&mut exact, root, client_runtime, endpoints);
    let output = timeout(CONNECTION_TIMEOUT, exact.output())
        .await
        .context("remote process-contract proof exceeded its deadline")??;
    if output.status.code() != Some(23)
        || output.stdout != b"tool-stdout\n"
        || output.stderr != b"tool-stderr\n"
    {
        bail!(
            "remote process contract was not exact: status={} stdout={:?} stderr={:?}",
            output.status,
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
    }

    let mut missing = Command::new(executable);
    missing
        .arg("--transport")
        .arg("bond")
        .arg("-q")
        .arg("-T")
        .arg(target)
        .arg("anonssh-command-that-does-not-exist");
    configure_bond_tool_command(&mut missing, root, client_runtime, endpoints);
    let output = timeout(CONNECTION_TIMEOUT, missing.output())
        .await
        .context("missing-command proof exceeded its deadline")??;
    if output.status.success() || output.stderr.is_empty() {
        bail!("missing remote command did not fail cleanly");
    }

    Ok(serde_json::json!({
        "stdout": "byte-exact",
        "stderr": "byte-exact",
        "remote_exit_status": 23,
        "missing_command": "failed-cleanly",
    }))
}

fn configure_bond_tool_command(
    command: &mut Command,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) {
    command
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("client/cache"))
        .env("XDG_DATA_HOME", root.join("client/data"))
        .env("XDG_RUNTIME_DIR", client_runtime)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    configure_client_bond_pool(command, endpoints);
}

fn configure_git_transport(
    command: &mut Command,
    remote_shell: &str,
    root: &Path,
    client_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) {
    configure_bond_tool_command(command, root, client_runtime, endpoints);
    command
        .env("GIT_SSH_COMMAND", remote_shell)
        .env("GIT_SSH_VARIANT", "ssh");
}

async fn checked_tool_output(mut command: Command, label: &str) -> Result<std::process::Output> {
    let output = timeout(CONNECTION_TIMEOUT, command.output())
        .await
        .with_context(|| format!("{label} exceeded its deadline"))??;
    if !output.status.success() {
        bail!(
            "{label} failed with {}: {}",
            output.status,
            String::from_utf8_lossy(&output.stderr)
        );
    }
    Ok(output)
}

async fn checked_git<const N: usize>(git: &Path, arguments: [&str; N], label: &str) -> Result<()> {
    let mut command = Command::new(git);
    command
        .args(arguments)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    checked_tool_output(command, label).await?;
    Ok(())
}

async fn git_stdout<const N: usize>(
    git: &Path,
    root: &Path,
    arguments: [&str; N],
) -> Result<String> {
    let mut command = Command::new(git);
    command.arg("-C").arg(root).args(arguments);
    let output = checked_tool_output(command, "Git revision lookup").await?;
    String::from_utf8(output.stdout).context("Git revision output was not UTF-8")
}

async fn run_bond_forward() -> Result<()> {
    let transport = LiveTransport::BondForward;
    let topology = bond_ssh_topology(transport)?;
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for the bonded forwarding test")?;
    let machine_id = format!("anonssh-live-bond-forward-{}", std::process::id());
    let root = live_test_root(transport);
    remove_if_present(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let bond_stats_artifact = root.join("client-bond-stats.json");
    let remote_listener = tokio::net::TcpListener::bind(endpoints.remote_service)
        .await
        .context("failed to bind the remote forwarding test service")?;

    let mut server = Command::new(&executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg(topology.transport)
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    let mut server = server
        .spawn()
        .context("failed to start bonded forwarding server")?;
    let server_stdout = server.stdout.take();

    let operation = async {
        let stdout = server_stdout.context("bonded forwarding server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, topology.publication_prefix).await?;
        let request = (0..2 * 1024 * 1024)
            .map(|index| ((index * 31 + 17) % 251) as u8)
            .collect::<Vec<_>>();
        let response = (0..3 * 1024 * 1024)
            .map(|index| ((index * 47 + 29) % 251) as u8)
            .collect::<Vec<_>>();

        let service = async {
            let (mut stream, peer) = timeout(CONNECTION_TIMEOUT, remote_listener.accept())
                .await
                .context("remote forwarding service was never reached")??;
            if !peer.ip().is_loopback() {
                bail!("remote forwarding service accepted a non-loopback peer");
            }
            let mut received = vec![0_u8; request.len()];
            timeout(CONNECTION_TIMEOUT, stream.read_exact(&mut received))
                .await
                .context("remote forwarding service did not receive the exact request")??;
            if received != request {
                bail!("remote forwarding service received a changed request");
            }
            timeout(CONNECTION_TIMEOUT, stream.write_all(&response))
                .await
                .context("remote forwarding service could not send its response")??;
            stream.shutdown().await?;
            Ok::<_, anyhow::Error>(received)
        };

        let client = async {
            let mut command = Command::new(&executable);
            command
                .arg("forward")
                .arg(format!("{username}@{machine_id}"))
                .arg("--listen")
                .arg(endpoints.local_forward.to_string())
                .arg("--remote")
                .arg(endpoints.remote_service.to_string())
                .arg("--transport")
                .arg(topology.transport)
                .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
                .env(
                    "ANONSSH_INTERNAL_TEST_BOND_STATS_ARTIFACT",
                    &bond_stats_artifact,
                )
                .env("XDG_CACHE_HOME", root.join("client/cache"))
                .env("XDG_DATA_HOME", root.join("client/data"))
                .env("XDG_RUNTIME_DIR", root.join("client/runtime"))
                .stdin(Stdio::null())
                .stdout(Stdio::null())
                .stderr(Stdio::inherit())
                .kill_on_drop(true);
            configure_client_bond_pool(&mut command, endpoints.client);
            let mut child = command
                .spawn()
                .context("failed to start bonded forwarding client")?;

            let transfer = async {
                let mut stream = timeout(CONNECTION_TIMEOUT, async {
                    loop {
                        if let Some(status) = child.try_wait()? {
                            bail!("bonded forwarding client exited before listening: {status}");
                        }
                        match tokio::net::TcpStream::connect(endpoints.local_forward).await {
                            Ok(stream) => return Ok::<_, anyhow::Error>(stream),
                            Err(error) if error.kind() == io::ErrorKind::ConnectionRefused => {
                                tokio::time::sleep(Duration::from_millis(100)).await;
                            }
                            Err(error) => return Err(error.into()),
                        }
                    }
                })
                .await
                .context("named forward did not become ready")??;
                stream
                    .write_all(&request)
                    .await
                    .context("failed to write the local forwarded request")?;
                stream.shutdown().await?;
                let mut received = Vec::with_capacity(response.len());
                timeout(CONNECTION_TIMEOUT, stream.read_to_end(&mut received))
                    .await
                    .context("local forward did not return its response")??;
                if received != response {
                    bail!("local forward returned a changed response");
                }
                let stats = wait_for_verified_bond_stats(&bond_stats_artifact, topology).await?;
                Ok::<_, anyhow::Error>((received, stats))
            }
            .await;
            let cleanup = stop_child(&mut child)
                .await
                .context("failed to stop bonded forwarding client");
            let result = merge_value_cleanup(transfer, cleanup)?;
            #[cfg(target_os = "linux")]
            wait_for_endpoints_released(
                std::iter::once(endpoints.local_forward)
                    .chain(endpoints.client.all())
                    .collect(),
            )
            .await?;
            Ok::<_, anyhow::Error>(result)
        };

        let (received_request, (received_response, (reserved_lane, active_lanes))) =
            tokio::try_join!(service, client)?;
        Ok::<_, anyhow::Error>(serde_json::json!({
            "schema": "anonssh.live-bond-forward.v1",
            "status": "ok",
            "transport": topology.transport,
            "discovery_destination": destination,
            "local_listener": endpoints.local_forward,
            "remote_service": endpoints.remote_service,
            "request_bytes": received_request.len(),
            "request_sha256": format!("{:x}", Sha256::digest(&received_request)),
            "response_bytes": received_response.len(),
            "response_sha256": format!("{:x}", Sha256::digest(&received_response)),
            "active_lanes": active_lanes,
            "reserved_lane_with_scheduled_bytes": reserved_lane,
            "local_listener_released": true,
            "client_router_endpoints_released": true,
            "server_router_endpoints_released": true,
            "test_state_removed": true,
            "ssh": "derived-key-local-forward",
        }))
    }
    .await;

    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop bonded forwarding server");
    #[cfg(target_os = "linux")]
    let server_cleanup = join_results(
        server_cleanup,
        wait_for_endpoints_released(server_endpoints(endpoints)).await,
    );
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove live-test state");
    let report = merge_value_cleanup(operation, join_results(server_cleanup, filesystem_cleanup))?;
    println!("{}", serde_json::to_string_pretty(&report)?);
    Ok(())
}

async fn wait_for_verified_bond_stats(
    path: &Path,
    topology: BondSshTopology,
) -> Result<(u64, usize)> {
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            if let Ok(stats) = verify_bond_stats(path, topology) {
                return Ok::<_, anyhow::Error>(stats);
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("bond statistics did not prove the forwarding path")?
}

struct AdaptiveSshEvidence {
    initial_active_lanes: usize,
    bulk_bytes: usize,
    bulk_sha256: String,
    max_active_lanes: usize,
    demand_to_batch_admission_millis: u64,
    demand_to_first_optional_active_millis: u64,
    demand_to_useful_capacity_millis: u64,
    max_parallel_admissions: usize,
    controller_events: Vec<serde_json::Value>,
    expanded_lane_ids: Vec<u64>,
    expanded_lane_acknowledged_bytes: BTreeMap<u64, u64>,
    lane_acknowledged_bytes: BTreeMap<u64, u64>,
    final_active_lanes: usize,
    final_running_router_processes: usize,
    max_queue_delay_micros: u64,
    max_send_window_utilization_percent: u64,
    max_backpressured_streams: u64,
    stream_backpressure_events: u64,
    max_client_router_rss_bytes: u64,
    max_client_router_cpu_time_micros: u64,
    max_router_startup_millis: u64,
    retransmitted_frames: u64,
    liveness_failures: u64,
    typing_samples: usize,
    typing_p50_micros: u64,
    typing_p95_micros: u64,
    typing_max_micros: u64,
}

struct AdaptiveMonitorEvidence {
    max_active_lanes: usize,
    demand_to_batch_admission_millis: u64,
    demand_to_first_optional_active_millis: u64,
    demand_to_useful_capacity_millis: u64,
    max_parallel_admissions: usize,
    controller_events: Vec<serde_json::Value>,
    expanded_lane_ids: Vec<u64>,
    expanded_lane_acknowledged_bytes: BTreeMap<u64, u64>,
    lane_acknowledged_bytes: BTreeMap<u64, u64>,
    final_active_lanes: usize,
    final_running_router_processes: usize,
    max_queue_delay_micros: u64,
    max_send_window_utilization_percent: u64,
    max_backpressured_streams: u64,
    stream_backpressure_events: u64,
    max_client_router_rss_bytes: u64,
    max_client_router_cpu_time_micros: u64,
    max_router_startup_millis: u64,
    retransmitted_frames: u64,
    liveness_failures: u64,
}

async fn run_adaptive_ssh_workload(
    control_socket: &Path,
    bond_stats_artifact: &Path,
    username: &str,
    machine_id: &str,
    topology: BondSshTopology,
) -> Result<AdaptiveSshEvidence> {
    wait_for_path(control_socket, CONNECTION_TIMEOUT).await?;
    eprintln!("anonssh-test: adaptive SSH control master is ready");
    let initial_active_lanes = wait_for_minimum_viable_lane(bond_stats_artifact, topology).await?;
    let baseline = read_bond_stats(bond_stats_artifact)?;
    let scaling_baseline_millis = adaptive_scaling_observed_millis(&baseline)?;
    let required = topology
        .required_lane_ids()
        .into_iter()
        .collect::<BTreeSet<_>>();
    if bond_stats_lanes(&baseline)?.iter().any(|lane| {
        let lane_id = lane.get("id").and_then(serde_json::Value::as_u64);
        lane_id.is_some_and(|lane_id| !required.contains(&lane_id))
            && (lane.get("active") == Some(&serde_json::Value::Bool(true))
                || lane
                    .get("bytes_acknowledged")
                    .and_then(serde_json::Value::as_u64)
                    .unwrap_or(0)
                    > 0)
    }) {
        bail!("adaptive topology used optional capacity before the measured load began");
    }
    eprintln!("anonssh-test: starting adaptive load from {initial_active_lanes} active lane(s)");
    let ssh = resolve_executable("ANONSSH_SSH_BIN", "ssh")?;
    let target = format!("{username}@{machine_id}");
    let bulk_active = Arc::new(AtomicBool::new(true));
    let bulk = {
        let ssh = ssh.clone();
        let control_socket = control_socket.to_owned();
        let target = target.clone();
        let bulk_active = bulk_active.clone();
        async move {
            let result = run_mux_bulk_upload(&ssh, &control_socket, &target).await;
            bulk_active.store(false, Ordering::Release);
            result
        }
    };
    let typing = run_mux_typing(&ssh, control_socket, &target, 12);
    let monitor = monitor_adaptive_stats(
        bond_stats_artifact,
        topology,
        bulk_active.clone(),
        scaling_baseline_millis,
    );
    let (bulk_sha256, mut typing, monitor) = tokio::try_join!(bulk, typing, monitor)?;
    eprintln!("anonssh-test: adaptive workload and topology convergence completed");
    typing.sort_unstable();
    Ok(AdaptiveSshEvidence {
        initial_active_lanes,
        bulk_bytes: ADAPTIVE_BULK_BYTES,
        bulk_sha256,
        max_active_lanes: monitor.max_active_lanes,
        demand_to_batch_admission_millis: monitor.demand_to_batch_admission_millis,
        demand_to_first_optional_active_millis: monitor.demand_to_first_optional_active_millis,
        demand_to_useful_capacity_millis: monitor.demand_to_useful_capacity_millis,
        max_parallel_admissions: monitor.max_parallel_admissions,
        controller_events: monitor.controller_events,
        expanded_lane_ids: monitor.expanded_lane_ids,
        expanded_lane_acknowledged_bytes: monitor.expanded_lane_acknowledged_bytes,
        lane_acknowledged_bytes: monitor.lane_acknowledged_bytes,
        final_active_lanes: monitor.final_active_lanes,
        final_running_router_processes: monitor.final_running_router_processes,
        max_queue_delay_micros: monitor.max_queue_delay_micros,
        max_send_window_utilization_percent: monitor.max_send_window_utilization_percent,
        max_backpressured_streams: monitor.max_backpressured_streams,
        stream_backpressure_events: monitor.stream_backpressure_events,
        max_client_router_rss_bytes: monitor.max_client_router_rss_bytes,
        max_client_router_cpu_time_micros: monitor.max_client_router_cpu_time_micros,
        max_router_startup_millis: monitor.max_router_startup_millis,
        retransmitted_frames: monitor.retransmitted_frames,
        liveness_failures: monitor.liveness_failures,
        typing_samples: typing.len(),
        typing_p50_micros: percentile(&typing, 50),
        typing_p95_micros: percentile(&typing, 95),
        typing_max_micros: *typing
            .last()
            .context("adaptive typing produced no samples")?,
    })
}

async fn run_mux_bulk_upload(ssh: &Path, control_socket: &Path, target: &str) -> Result<String> {
    eprintln!(
        "anonssh-test: starting {} MiB multiplexed SSH upload",
        ADAPTIVE_BULK_BYTES / (1024 * 1024)
    );
    let mut child = Command::new(ssh)
        .arg("-S")
        .arg(control_socket)
        .arg("-o")
        .arg("ControlMaster=no")
        .arg("-T")
        .arg(target)
        .arg("sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true)
        .spawn()
        .context("failed to start multiplexed SSH bulk channel")?;
    let mut stdin = child
        .stdin
        .take()
        .context("multiplexed SSH bulk channel omitted stdin")?;
    let chunk = vec![0x5a; ADAPTIVE_BULK_CHUNK_BYTES];
    let repetitions = ADAPTIVE_BULK_BYTES / ADAPTIVE_BULK_CHUNK_BYTES;
    let expected = {
        let mut digest = Sha256::new();
        for _ in 0..repetitions {
            digest.update(&chunk);
        }
        format!("{:x}", digest.finalize())
    };
    let writer = tokio::spawn(async move {
        for _ in 0..repetitions {
            stdin.write_all(&chunk).await?;
        }
        stdin.shutdown().await
    });
    let output = timeout(CONNECTION_TIMEOUT, child.wait_with_output())
        .await
        .context("multiplexed SSH bulk channel exceeded its deadline")?
        .context("failed to wait for multiplexed SSH bulk channel")?;
    writer
        .await
        .context("multiplexed SSH bulk writer task failed")??;
    if !output.status.success() {
        bail!(
            "multiplexed SSH bulk channel failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    let actual = String::from_utf8(output.stdout)
        .context("multiplexed SSH bulk hash was not UTF-8")?
        .split_whitespace()
        .next()
        .context("multiplexed SSH bulk hash was empty")?
        .to_owned();
    if actual != expected {
        bail!("multiplexed SSH bulk hash mismatch");
    }
    eprintln!("anonssh-test: multiplexed SSH upload hash verified");
    Ok(actual)
}

async fn run_mux_typing(
    ssh: &Path,
    control_socket: &Path,
    target: &str,
    samples: usize,
) -> Result<Vec<u64>> {
    let mut latencies = Vec::with_capacity(samples);
    for index in 0..samples {
        tokio::time::sleep(Duration::from_millis(750)).await;
        let marker = format!("anonssh-adaptive-typing-{index}");
        let started = Instant::now();
        let output = timeout(
            TYPING_PROBE_TIMEOUT,
            Command::new(ssh)
                .arg("-S")
                .arg(control_socket)
                .arg("-o")
                .arg("ControlMaster=no")
                .arg("-T")
                .arg(target)
                .arg(format!("printf '%s\\n' '{marker}'"))
                .stdin(Stdio::null())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .kill_on_drop(true)
                .output(),
        )
        .await
        .with_context(|| format!("adaptive typing sample {index} exceeded its deadline"))?
        .context("failed to run multiplexed SSH typing channel")?;
        if !output.status.success() || output.stdout != format!("{marker}\n").as_bytes() {
            bail!(
                "adaptive typing sample {index} failed: {}",
                String::from_utf8_lossy(&output.stderr)
            );
        }
        latencies.push(u64::try_from(started.elapsed().as_micros()).unwrap_or(u64::MAX));
    }
    eprintln!("anonssh-test: {samples} multiplexed typing probes verified");
    Ok(latencies)
}

async fn monitor_adaptive_stats(
    path: &Path,
    topology: BondSshTopology,
    bulk_active: Arc<AtomicBool>,
    scaling_baseline_millis: u64,
) -> Result<AdaptiveMonitorEvidence> {
    let required = topology
        .required_lane_ids()
        .into_iter()
        .collect::<BTreeSet<_>>();
    timeout(CONNECTION_TIMEOUT, async {
        let mut max_active_lanes = 0;
        let mut demand_to_batch_admission_millis = None;
        let mut demand_to_first_optional_active_millis = None;
        let mut demand_to_useful_capacity_millis = None;
        let mut max_parallel_admissions = 0;
        let mut controller_events = BTreeMap::<u64, serde_json::Value>::new();
        let mut expanded_lane_ids = BTreeSet::new();
        let mut expanded_lane_acknowledged_bytes = BTreeMap::<u64, u64>::new();
        let mut lane_acknowledged_bytes = BTreeMap::<u64, u64>::new();
        let mut max_queue_delay_micros = 0;
        let mut max_send_window_utilization_percent = 0;
        let mut max_backpressured_streams = 0;
        let mut stream_backpressure_events = 0;
        let mut max_client_router_rss_bytes = 0;
        let mut max_client_router_cpu_time_micros = 0;
        let mut max_router_startup_millis = 0;
        let mut retransmitted_frames = 0;
        let mut liveness_failures = 0;
        let mut expansion_observation = None;
        let mut contribution_reported = false;
        loop {
            if let Ok(document) = read_bond_stats(path) {
                let observation = bond_stats_observation(&document)?;
                let scaling = document
                    .get("adaptive_scaling")
                    .context("adaptive stats omitted scaling progress")?;
                let scaling_observed_millis = scaling
                    .get("observed_millis")
                    .and_then(serde_json::Value::as_u64)
                    .context("adaptive stats omitted the scaling clock")?;
                let scaling_elapsed = scaling_observed_millis
                    .saturating_sub(scaling_baseline_millis);
                let events = scaling
                    .get("events")
                    .and_then(serde_json::Value::as_array)
                    .context("adaptive stats omitted scaling events")?;
                for event in events {
                    let generation = event
                        .get("generation")
                        .and_then(serde_json::Value::as_u64)
                        .context("adaptive scaling event omitted its generation")?;
                    if controller_events.contains_key(&generation) {
                        continue;
                    }
                    let event_elapsed = event
                        .get("elapsed_millis")
                        .and_then(serde_json::Value::as_u64)
                        .context("adaptive scaling event omitted elapsed time")?;
                    if event_elapsed < scaling_baseline_millis {
                        continue;
                    }
                    let admissions = event
                        .get("actions")
                        .and_then(serde_json::Value::as_array)
                        .context("adaptive scaling event omitted actions")?
                        .iter()
                        .filter(|action| {
                            action.get("kind").and_then(serde_json::Value::as_str)
                                == Some("admit")
                        })
                        .count();
                    if admissions > 0 {
                        demand_to_batch_admission_millis.get_or_insert_with(|| {
                            event_elapsed.saturating_sub(scaling_baseline_millis)
                        });
                        max_parallel_admissions = max_parallel_admissions.max(admissions);
                    }
                    controller_events.insert(generation, event.clone());
                }
                let lanes = bond_stats_lanes(&document)?;
                let active = lanes
                    .iter()
                    .filter(|lane| lane.get("active") == Some(&serde_json::Value::Bool(true)))
                    .filter_map(|lane| lane.get("id").and_then(serde_json::Value::as_u64))
                    .collect::<BTreeSet<_>>();
                max_active_lanes = max_active_lanes.max(active.len());
                if active.iter().any(|lane_id| !required.contains(lane_id)) {
                    demand_to_first_optional_active_millis.get_or_insert(scaling_elapsed);
                }
                for lane in lanes {
                    let Some(lane_id) = lane.get("id").and_then(serde_json::Value::as_u64) else {
                        continue;
                    };
                    max_queue_delay_micros = max_queue_delay_micros.max(
                        lane.get("queue_delay_micros")
                            .and_then(serde_json::Value::as_u64)
                            .unwrap_or(0),
                    );
                    let acknowledged = lane
                        .get("bytes_acknowledged")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0);
                    lane_acknowledged_bytes
                        .entry(lane_id)
                        .and_modify(|value| *value = (*value).max(acknowledged))
                        .or_insert(acknowledged);
                    if !required.contains(&lane_id) && acknowledged > 0 {
                        demand_to_useful_capacity_millis.get_or_insert(scaling_elapsed);
                    }
                    if !required.contains(&lane_id) && active.contains(&lane_id) {
                        expanded_lane_ids.insert(lane_id);
                        if expansion_observation.is_none() {
                            eprintln!(
                                "anonssh-test: adaptive topology expanded at observation {observation}"
                            );
                            expansion_observation = Some(observation);
                        }
                    }
                    if !required.contains(&lane_id) {
                        expanded_lane_acknowledged_bytes
                            .entry(lane_id)
                            .and_modify(|value| *value = (*value).max(acknowledged))
                            .or_insert(acknowledged);
                    }
                }
                retransmitted_frames = retransmitted_frames.max(
                    document
                        .get("retransmitted_frames")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0),
                );
                liveness_failures = liveness_failures.max(
                    document
                        .get("liveness_failures")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0),
                );
                max_send_window_utilization_percent = max_send_window_utilization_percent.max(
                    document
                        .get("send_window_utilization_percent")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0),
                );
                max_backpressured_streams = max_backpressured_streams.max(
                    document
                        .get("backpressured_streams")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0),
                );
                stream_backpressure_events = stream_backpressure_events.max(
                    document
                        .get("stream_backpressure_events")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0),
                );
                let processes = document
                    .get("router_processes")
                    .and_then(serde_json::Value::as_array)
                    .context("adaptive stats omitted router processes")?;
                let running = processes
                    .iter()
                    .filter(|process| {
                        process.get("running") == Some(&serde_json::Value::Bool(true))
                    })
                    .count();
                let rss = processes
                    .iter()
                    .filter_map(|process| {
                        process
                            .get("resident_bytes")
                            .and_then(serde_json::Value::as_u64)
                    })
                    .fold(0_u64, u64::saturating_add);
                let cpu = processes
                    .iter()
                    .filter_map(|process| {
                        process
                            .get("cpu_time_micros")
                            .and_then(serde_json::Value::as_u64)
                    })
                    .fold(0_u64, u64::saturating_add);
                let startup = processes
                    .iter()
                    .filter_map(|process| {
                        process
                            .get("startup_millis")
                            .and_then(serde_json::Value::as_u64)
                    })
                    .max()
                    .unwrap_or(0);
                max_client_router_rss_bytes = max_client_router_rss_bytes.max(rss);
                max_client_router_cpu_time_micros = max_client_router_cpu_time_micros.max(cpu);
                max_router_startup_millis = max_router_startup_millis.max(startup);
                let all_candidates_contributed = lane_acknowledged_bytes.len()
                    == topology.candidate_lanes()
                    && lane_acknowledged_bytes.values().all(|bytes| *bytes > 0);
                if all_candidates_contributed && !contribution_reported {
                    eprintln!("anonssh-test: every candidate lane contributed acknowledged bytes");
                    contribution_reported = true;
                }
                if !bulk_active.load(Ordering::Acquire)
                    && expansion_observation.is_some_and(|expanded| observation > expanded)
                    && max_active_lanes == topology.candidate_lanes()
                    && all_candidates_contributed
                    && required.is_subset(&active)
                    && active.len() < max_active_lanes
                    && active
                        .difference(&required)
                        .all(|lane_id| {
                            lanes.iter().any(|lane| {
                                lane.get("id").and_then(serde_json::Value::as_u64)
                                    == Some(*lane_id)
                                    && lane.get("reserved_for_low_latency")
                                        == Some(&serde_json::Value::Bool(true))
                            })
                        })
                    && running == active.len()
                {
                    eprintln!(
                        "anonssh-test: adaptive topology contracted from {max_active_lanes} to {} active lanes",
                        active.len()
                    );
                    return Ok::<_, anyhow::Error>(AdaptiveMonitorEvidence {
                        max_active_lanes,
                        demand_to_batch_admission_millis: demand_to_batch_admission_millis
                            .context("adaptive controller never admitted a load-driven batch")?,
                        demand_to_first_optional_active_millis:
                            demand_to_first_optional_active_millis.context(
                                "adaptive topology never activated optional capacity",
                            )?,
                        demand_to_useful_capacity_millis: demand_to_useful_capacity_millis
                            .context("adaptive optional capacity never acknowledged payload")?,
                        max_parallel_admissions,
                        controller_events: controller_events.into_values().collect(),
                        expanded_lane_ids: expanded_lane_ids.into_iter().collect(),
                        expanded_lane_acknowledged_bytes: expanded_lane_acknowledged_bytes
                            .into_iter()
                            .filter(|(_, bytes)| *bytes > 0)
                            .collect(),
                        lane_acknowledged_bytes,
                        final_active_lanes: active.len(),
                        final_running_router_processes: running,
                        max_queue_delay_micros,
                        max_send_window_utilization_percent,
                        max_backpressured_streams,
                        stream_backpressure_events,
                        max_client_router_rss_bytes,
                        max_client_router_cpu_time_micros,
                        max_router_startup_millis,
                        retransmitted_frames,
                        liveness_failures,
                    });
                }
            }
            tokio::time::sleep(Duration::from_millis(250)).await;
        }
    })
    .await
    .context("adaptive bond did not expand, contribute, and drain before its deadline")?
}

fn adaptive_scaling_observed_millis(document: &serde_json::Value) -> Result<u64> {
    document
        .get("adaptive_scaling")
        .and_then(|scaling| scaling.get("observed_millis"))
        .and_then(serde_json::Value::as_u64)
        .context("adaptive stats omitted the scaling clock")
}

async fn wait_for_minimum_viable_lane(path: &Path, topology: BondSshTopology) -> Result<usize> {
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            if let Ok(document) = read_bond_stats(path) {
                let lanes = bond_stats_lanes(&document)?;
                if lanes.len() == topology.candidate_lanes() {
                    let active = lanes
                        .iter()
                        .filter(|lane| lane.get("active") == Some(&serde_json::Value::Bool(true)))
                        .count();
                    if active > 0 {
                        return Ok::<usize, anyhow::Error>(active);
                    }
                }
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("adaptive bond did not form a minimum viable authenticated topology")?
}

async fn request_mux_master_exit(
    control_socket: &Path,
    username: &str,
    machine_id: &str,
) -> Result<()> {
    let ssh = resolve_executable("ANONSSH_SSH_BIN", "ssh")?;
    let output = timeout(
        Duration::from_secs(30),
        Command::new(ssh)
            .arg("-S")
            .arg(control_socket)
            .arg("-O")
            .arg("exit")
            .arg(format!("{username}@{machine_id}"))
            .stdin(Stdio::null())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .kill_on_drop(true)
            .output(),
    )
    .await
    .context("multiplexed SSH master exit timed out")?
    .context("failed to request multiplexed SSH master exit")?;
    if !output.status.success() {
        bail!(
            "multiplexed SSH master rejected exit: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    Ok(())
}

struct InteractiveSshEvidence {
    initial_active_lanes: usize,
    initial_observation: u64,
    samples: usize,
    p50_micros: u64,
    p95_micros: u64,
    max_micros: u64,
    active_observation: u64,
}

async fn run_interactive_ssh_workload(
    client: &mut tokio::process::Child,
    bond_stats_artifact: &Path,
    topology: BondSshTopology,
) -> Result<InteractiveSshEvidence> {
    let mut stdin = client
        .stdin
        .take()
        .context("bonded SSH client stdin was not piped")?;
    let stdout = client
        .stdout
        .take()
        .context("bonded SSH client stdout was not piped")?;
    let mut lines = BufReader::new(stdout).lines();

    shell_round_trip(
        &mut stdin,
        &mut lines,
        "anonssh-interactive-ready",
        CONNECTION_TIMEOUT,
    )
    .await?;
    let (initial_observation, initial_active_lanes) =
        wait_for_bond_stats_observation(bond_stats_artifact).await?;

    let mut latencies = Vec::with_capacity(TYPING_PROBE_COUNT);
    for index in 0..TYPING_PROBE_COUNT {
        tokio::time::sleep(Duration::from_millis(125)).await;
        latencies.push(
            shell_round_trip(
                &mut stdin,
                &mut lines,
                &format!("anonssh-typing-{index}"),
                TYPING_PROBE_TIMEOUT,
            )
            .await?,
        );
    }
    let active_observation =
        wait_for_post_workload_active_lanes(bond_stats_artifact, topology).await?;
    stdin.write_all(b"exit\n").await?;
    stdin.shutdown().await?;

    latencies.sort_unstable();
    Ok(InteractiveSshEvidence {
        initial_active_lanes,
        initial_observation,
        samples: latencies.len(),
        p50_micros: percentile(&latencies, 50),
        p95_micros: percentile(&latencies, 95),
        max_micros: *latencies
            .last()
            .context("typing probe produced no samples")?,
        active_observation,
    })
}

async fn wait_for_bond_stats_observation(path: &Path) -> Result<(u64, usize)> {
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            if let Ok(document) = read_bond_stats(path) {
                let observation = bond_stats_observation(&document)?;
                let active = bond_stats_lanes(&document)?
                    .iter()
                    .filter(|lane| lane.get("active") == Some(&serde_json::Value::Bool(true)))
                    .count();
                return Ok::<_, anyhow::Error>((observation, active));
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("bond statistics did not appear after SSH became usable")?
}

async fn wait_for_post_workload_active_lanes(
    path: &Path,
    topology: BondSshTopology,
) -> Result<u64> {
    let previous_observation = read_bond_stats(path)
        .ok()
        .and_then(|document| bond_stats_observation(&document).ok())
        .unwrap_or(0);
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            if let Ok(document) = read_bond_stats(path) {
                let observation = bond_stats_observation(&document)?;
                if observation > previous_observation
                    && bond_stats_has_required_lanes(&document, topology)?
                {
                    return Ok(observation);
                }
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("bond topology did not reconverge after the interactive workload")?
}

async fn shell_round_trip(
    stdin: &mut tokio::process::ChildStdin,
    lines: &mut tokio::io::Lines<BufReader<tokio::process::ChildStdout>>,
    marker: &str,
    deadline: Duration,
) -> Result<u64> {
    let command = format!("printf '%s\\n' '{marker}'\n");
    let started = Instant::now();
    stdin.write_all(command.as_bytes()).await?;
    stdin.flush().await?;
    timeout(deadline, async {
        while let Some(line) = lines.next_line().await? {
            if line == marker {
                return Ok::<(), anyhow::Error>(());
            }
        }
        bail!("bonded SSH shell exited before returning marker {marker}")
    })
    .await
    .with_context(|| format!("typing marker {marker} exceeded its deadline"))??;
    Ok(u64::try_from(started.elapsed().as_micros()).unwrap_or(u64::MAX))
}

fn percentile(sorted: &[u64], percentile: usize) -> u64 {
    let rank = sorted.len().saturating_mul(percentile).div_ceil(100);
    sorted[rank.saturating_sub(1).min(sorted.len() - 1)]
}

fn verify_bond_stats(path: &Path, topology: BondSshTopology) -> Result<(u64, usize)> {
    let document = read_bond_stats(path)?;
    bond_stats_observation(&document)?;
    let lanes = bond_stats_lanes(&document)?;
    if lanes.len() != topology.candidate_lanes() {
        bail!(
            "bond statistics reported {} candidates instead of {}",
            lanes.len(),
            topology.candidate_lanes()
        );
    }
    let active = lanes
        .iter()
        .filter(|lane| lane.get("active") == Some(&serde_json::Value::Bool(true)))
        .filter_map(|lane| lane.get("id").and_then(serde_json::Value::as_u64))
        .collect::<Vec<_>>();
    let missing = topology
        .required_lane_ids()
        .into_iter()
        .filter(|lane_id| !active.contains(lane_id))
        .collect::<Vec<_>>();
    if !missing.is_empty() {
        bail!("bond statistics omitted required active lanes {missing:?}");
    }
    let reserved = document
        .get("reserved_lanes_with_scheduled_bytes")
        .and_then(serde_json::Value::as_array)
        .and_then(|lanes| lanes.first())
        .and_then(serde_json::Value::as_u64)
        .context("no dynamically reserved lane carried scheduled bytes")?;
    Ok((reserved, active.len()))
}

fn bond_stats_has_required_lanes(
    document: &serde_json::Value,
    topology: BondSshTopology,
) -> Result<bool> {
    let lanes = bond_stats_lanes(document)?;
    if lanes.len() != topology.candidate_lanes() {
        return Ok(false);
    }
    Ok(topology.required_lane_ids().into_iter().all(|required| {
        lanes.iter().any(|lane| {
            lane.get("id").and_then(serde_json::Value::as_u64) == Some(required)
                && lane.get("active") == Some(&serde_json::Value::Bool(true))
        })
    }))
}

fn read_bond_stats(path: &Path) -> Result<serde_json::Value> {
    serde_json::from_slice(
        &fs::read(path).with_context(|| format!("failed to read {}", path.display()))?,
    )
    .with_context(|| format!("failed to parse {}", path.display()))
}

fn bond_stats_observation(document: &serde_json::Value) -> Result<u64> {
    document
        .get("observation")
        .and_then(serde_json::Value::as_u64)
        .context("bond statistics omitted the observation sequence")
}

fn bond_stats_lanes(document: &serde_json::Value) -> Result<&Vec<serde_json::Value>> {
    document
        .get("lanes")
        .and_then(serde_json::Value::as_array)
        .context("bond statistics omitted lanes")
}

fn isolate_unused_provider(command: &mut Command, root: &Path, topology: BondSshTopology) {
    if topology.tor_slots == 0 {
        command.env("ANONSSH_TOR_BIN", root.join("missing-tor"));
    }
    if topology.i2p_slots == 0 {
        command.env("ANONSSH_I2PD_BIN", root.join("missing-i2pd"));
    }
}

#[cfg(not(target_os = "linux"))]
async fn run_process_restart() -> Result<()> {
    bail!("the process-restart proof currently requires Linux parent-death signaling")
}

#[cfg(target_os = "linux")]
async fn run_process_restart() -> Result<()> {
    let test_started = Instant::now();
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for the process-restart test")?;
    let machine_id = format!("anonssh-live-process-restart-{}", std::process::id());
    let root = live_test_root(LiveTransport::ProcessRestart);
    remove_if_present(&root)?;
    let endpoints = BondSshEndpoints::allocate()?;
    let client_root = root.join("client");
    let broker_runtime = client_root.join("runtime");
    let server_marker = root.join("server/data/anonssh/process-restart.marker");
    let client_marker = root.join("client/data/anonssh/process-restart.marker");
    let marker = format!("{machine_id}\n");
    let mut final_server = None;

    let operation = async {
        let mut killed_descendants = BTreeSet::new();

        // An idle resident broker owns endpoint reservations but no routers.
        let mut idle_broker = process_restart_broker_command(
            &executable,
            &client_root,
            &broker_runtime,
            endpoints.client,
        )
        .spawn()
        .context("failed to start idle process-restart broker")?;
        let idle_status = wait_for_running_broker(&executable, &broker_runtime).await?;
        let idle_broker_pid = idle_status
            .process_id
            .context("idle broker status omitted its process ID")?;
        if idle_broker.id() != Some(idle_broker_pid) {
            bail!("idle broker status identified the wrong process");
        }
        kill_child_with_sigkill(&mut idle_broker, "idle broker").await?;
        assert_stale_broker_control(&broker_runtime)?;
        wait_for_endpoints_released(endpoints.client.all()).await?;
        eprintln!("anonssh-test: idle broker crash and reclaim preconditions verified");

        // Crash the server as soon as Dropbear and a router child exist.
        let mut startup_server =
            process_restart_server_command(&executable, &root, &machine_id, endpoints);
        let mut startup_server = startup_server
            .spawn()
            .context("failed to start startup-crash server")?;
        let startup_server_pid = startup_server
            .id()
            .context("startup-crash server omitted its process ID")?;
        let startup_descendants = wait_for_linux_descendants(
            startup_server_pid,
            2,
            PUBLICATION_TIMEOUT,
            "starting server",
        )
        .await?;
        killed_descendants.extend(startup_descendants.iter().copied());
        kill_child_with_sigkill(&mut startup_server, "starting server").await?;
        wait_for_linux_processes_gone(&startup_descendants, Duration::from_secs(15)).await?;
        wait_for_endpoints_released(server_endpoints(endpoints)).await?;
        eprintln!("anonssh-test: server startup crash released every owned child and endpoint");

        // Reach publication, then prove that an otherwise idle server also cleans up.
        let idle_server_started = Instant::now();
        let mut idle_server_command =
            process_restart_server_command(&executable, &root, &machine_id, endpoints);
        let mut idle_server = idle_server_command
            .spawn()
            .context("failed to restart server after its startup crash")?;
        let idle_server_stdout = idle_server
            .stdout
            .take()
            .context("idle restart server stdout was not piped")?;
        let expected_destination = wait_for_prefix(idle_server_stdout, "bond-tor-1 ").await?;
        let startup_recovery_millis = elapsed_millis(idle_server_started.elapsed());
        let idle_server_pid = idle_server
            .id()
            .context("idle server omitted its process ID")?;
        let idle_server_descendants = wait_for_linux_descendants(
            idle_server_pid,
            1,
            Duration::from_secs(30),
            "published idle server",
        )
        .await?;
        killed_descendants.extend(idle_server_descendants.iter().copied());
        kill_child_with_sigkill(&mut idle_server, "idle server").await?;
        wait_for_linux_processes_gone(&idle_server_descendants, Duration::from_secs(15)).await?;
        wait_for_endpoints_released(server_endpoints(endpoints)).await?;
        eprintln!(
            "anonssh-test: published idle server crash recovered in {startup_recovery_millis} ms"
        );

        // Keep the third server alive while the client broker is crashed in startup.
        let mut active_server_command =
            process_restart_server_command(&executable, &root, &machine_id, endpoints);
        let mut active_server = active_server_command
            .spawn()
            .context("failed to start active process-restart server")?;
        let active_server_stdout = active_server
            .stdout
            .take()
            .context("active restart server stdout was not piped")?;
        let active_destination = wait_for_prefix(active_server_stdout, "bond-tor-1 ").await?;
        if active_destination != expected_destination {
            bail!("derived server destination changed across process restart");
        }

        let mut startup_client = process_restart_exact_client_command(
            &executable,
            &username,
            &machine_id,
            &client_root,
            &broker_runtime,
            endpoints.client,
            "anonssh-startup-crash",
        );
        startup_client.stdout(Stdio::null());
        let mut startup_client = startup_client
            .spawn()
            .context("failed to start broker-startup client")?;
        let mut startup_stderr = startup_client
            .stderr
            .take()
            .context("broker-startup client stderr was not piped")?;
        let startup_stderr = tokio::spawn(async move {
            let mut bytes = Vec::new();
            startup_stderr.read_to_end(&mut bytes).await?;
            Ok::<_, io::Error>(bytes)
        });
        let starting_broker = wait_for_starting_broker(&executable, &broker_runtime);
        tokio::pin!(starting_broker);
        let (startup_broker_status, startup_broker_descendants) = tokio::select! {
            result = &mut starting_broker => result?,
            status = startup_client.wait() => {
                let status = status.context("failed to wait for broker-startup client")?;
                let stderr = startup_stderr.await
                    .context("broker-startup stderr task failed")??;
                bail!(
                    "broker-startup client exited with {status} before router startup: {}",
                    String::from_utf8_lossy(&stderr),
                );
            }
        };
        let startup_broker_pid = startup_broker_status
            .process_id
            .context("starting broker status omitted its process ID")?;
        killed_descendants.extend(startup_broker_descendants.iter().copied());
        kill_process_with_sigkill(startup_broker_pid, "starting broker").await?;
        wait_for_linux_processes_gone(&startup_broker_descendants, Duration::from_secs(15)).await?;
        let startup_client_status = timeout(Duration::from_secs(30), startup_client.wait())
            .await
            .context("startup client did not fail after its broker crashed")??;
        let startup_stderr = startup_stderr
            .await
            .context("broker-startup stderr task failed")??;
        if startup_client_status.success() {
            bail!(
                "startup client survived destruction of its broker: {}",
                String::from_utf8_lossy(&startup_stderr)
            );
        }
        assert_stale_broker_control(&broker_runtime)?;
        wait_for_endpoints_released(endpoints.client.all()).await?;
        eprintln!("anonssh-test: broker startup crash released every owned child and endpoint");

        let broker_recovery_started = Instant::now();
        let mut old_stream = start_broker_typing_channel_with_timeout(
            &executable,
            &username,
            &machine_id,
            &client_root,
            &broker_runtime,
            endpoints.client,
            None,
            CONNECTION_TIMEOUT,
        )
        .await?;
        let active_broker_status =
            wait_for_broker_status_with_streams(&executable, &broker_runtime, 1).await?;
        let broker_recovery_millis = elapsed_millis(broker_recovery_started.elapsed());
        let active_broker_pid = active_broker_status
            .process_id
            .context("active broker status omitted its process ID")?;
        if active_broker_pid == idle_broker_pid || active_broker_pid == startup_broker_pid {
            bail!("broker process identity did not change after a crash");
        }
        let active_broker_descendants = linux_descendants(active_broker_pid)?;
        let expected_broker_children = active_broker_status
            .tor_routers_running
            .saturating_add(active_broker_status.i2p_routers_running);
        if expected_broker_children == 0
            || active_broker_descendants.len() < expected_broker_children
        {
            bail!("active broker did not expose every running router as an owned descendant");
        }
        let active_server_pid = active_server
            .id()
            .context("active server omitted its process ID")?;
        let active_server_descendants = linux_descendants(active_server_pid)?;
        if active_server_descendants.len() < 2 {
            bail!("active server did not retain its owned service processes");
        }

        let active_marker = "anonssh-active-before-crash\n";
        old_stream.stdin.write_all(active_marker.as_bytes()).await?;
        old_stream.stdin.flush().await?;
        let mut echoed = String::new();
        timeout(
            TYPING_PROBE_TIMEOUT,
            old_stream.stdout.read_line(&mut echoed),
        )
        .await
        .context("active stream did not echo before the crash")??;
        if echoed != active_marker {
            bail!("active stream returned corrupt data before the crash");
        }
        eprintln!("anonssh-test: active bonded SSH stream verified before crash");
        write_restart_marker(&server_marker, &marker)?;
        write_restart_marker(&client_marker, &marker)?;

        killed_descendants.extend(active_server_descendants.iter().copied());
        kill_child_with_sigkill(&mut active_server, "active server").await?;
        let old_stream_status = timeout(Duration::from_secs(90), old_stream.child.wait())
            .await
            .context("old SSH stream did not terminate after its server was replaced")??;
        if old_stream_status.success() {
            bail!("old SSH stream reported success after its server was replaced");
        }
        wait_for_linux_processes_gone(&active_server_descendants, Duration::from_secs(15)).await?;
        wait_for_endpoints_released(server_endpoints(endpoints)).await?;
        if !linux_process_is_live(active_broker_pid) {
            bail!("broker exited while only the server was replaced");
        }
        eprintln!("anonssh-test: server-only replacement terminated the old stream cleanly");

        let replacement_server_started = Instant::now();
        let mut final_server_command =
            process_restart_server_command(&executable, &root, &machine_id, endpoints);
        let mut restarted_server = final_server_command
            .spawn()
            .context("failed to start replacement server")?;
        let restarted_stdout = restarted_server
            .stdout
            .take()
            .context("replacement server stdout was not piped")?;
        let restarted_destination = wait_for_prefix(restarted_stdout, "bond-tor-1 ").await?;
        if restarted_destination != expected_destination {
            bail!("server destination changed during rolling replacement");
        }
        let server_recovery_millis = elapsed_millis(replacement_server_started.elapsed());

        let server_marker_exact = "anonssh-exact-after-server-replacement";
        let server_reconnect_started = Instant::now();
        let output = timeout(
            CONNECTION_TIMEOUT,
            process_restart_exact_client_command(
                &executable,
                &username,
                &machine_id,
                &client_root,
                &broker_runtime,
                endpoints.client,
                server_marker_exact,
            )
            .output(),
        )
        .await
        .context("new SSH connection exceeded the server-replacement deadline")??;
        if !output.status.success() {
            bail!(
                "new SSH connection failed after server replacement: {}",
                String::from_utf8_lossy(&output.stderr)
            );
        }
        if output.stdout != format!("{server_marker_exact}\n").as_bytes() {
            bail!("new SSH connection returned corrupt data after server replacement");
        }
        let server_reconnect_millis = elapsed_millis(server_reconnect_started.elapsed());
        let after_server_status =
            wait_for_broker_status_with_streams(&executable, &broker_runtime, 2).await?;
        if after_server_status.process_id != Some(active_broker_pid) {
            bail!("server replacement also replaced the resident broker");
        }
        eprintln!("anonssh-test: exact SSH reconnect succeeded after server-only replacement");

        let mut broker_old_stream = start_broker_typing_channel_with_timeout(
            &executable,
            &username,
            &machine_id,
            &client_root,
            &broker_runtime,
            endpoints.client,
            None,
            CONNECTION_TIMEOUT,
        )
        .await?;
        let broker_upgrade_descendants = linux_descendants(active_broker_pid)?;
        killed_descendants.extend(broker_upgrade_descendants.iter().copied());
        kill_process_with_sigkill(active_broker_pid, "active broker").await?;
        let broker_old_stream_status =
            timeout(Duration::from_secs(30), broker_old_stream.child.wait())
                .await
                .context("old SSH stream did not terminate after its broker was replaced")??;
        if broker_old_stream_status.success() {
            bail!("old SSH stream reported success after its broker was replaced");
        }
        wait_for_linux_processes_gone(&broker_upgrade_descendants, Duration::from_secs(15)).await?;
        assert_stale_broker_control(&broker_runtime)?;
        wait_for_endpoints_released(endpoints.client.all()).await?;
        let restarted_server_pid = restarted_server
            .id()
            .context("replacement server omitted its process ID")?;
        if !linux_process_is_live(restarted_server_pid) {
            bail!("server exited while only the broker was replaced");
        }
        eprintln!("anonssh-test: broker-only replacement terminated the old stream cleanly");

        let broker_marker_exact = "anonssh-exact-after-broker-replacement";
        let broker_reconnect_started = Instant::now();
        let output = timeout(
            CONNECTION_TIMEOUT,
            process_restart_exact_client_command(
                &executable,
                &username,
                &machine_id,
                &client_root,
                &broker_runtime,
                endpoints.client,
                broker_marker_exact,
            )
            .output(),
        )
        .await
        .context("new SSH connection exceeded the broker-replacement deadline")??;
        if !output.status.success() {
            bail!(
                "new SSH connection failed after broker replacement: {}",
                String::from_utf8_lossy(&output.stderr)
            );
        }
        if output.stdout != format!("{broker_marker_exact}\n").as_bytes() {
            bail!("new SSH connection returned corrupt data after broker replacement");
        }
        let broker_reconnect_millis = elapsed_millis(broker_reconnect_started.elapsed());
        let final_broker_status =
            wait_for_broker_status_with_streams(&executable, &broker_runtime, 1).await?;
        let final_broker_pid = final_broker_status
            .process_id
            .context("recovered broker status omitted its process ID")?;
        if [idle_broker_pid, startup_broker_pid, active_broker_pid].contains(&final_broker_pid) {
            bail!("recovered broker reused a crashed process ID");
        }
        assert_restart_marker(&server_marker, &marker)?;
        assert_restart_marker(&client_marker, &marker)?;
        wait_for_linux_processes_gone(&killed_descendants, Duration::from_secs(1)).await?;
        eprintln!("anonssh-test: rolling replacement retained identity and router roots");

        final_server = Some(restarted_server);
        Ok(serde_json::json!({
            "schema": "anonssh.live-process-restart.v1",
            "status": "ok",
            "transport": "bond",
            "crash_signal": "SIGKILL",
            "phase_coverage": {
                "broker": ["idle", "startup", "active-transfer", "rolling-replacement"],
                "server": ["startup", "idle", "active-transfer", "rolling-replacement"],
            },
            "opposite_endpoint_remained_live": true,
            "stale_control_reclaimed": true,
            "managed_endpoints_reclaimed": true,
            "router_state_retained": true,
            "derived_destination_retained": true,
            "old_stream_terminated": true,
            "new_connection_exact": true,
            "captured_owned_processes": killed_descendants.len(),
            "orphan_process_count": 0,
            "recovery_millis": {
                "server_after_startup_crash": startup_recovery_millis,
                "broker_after_startup_crash": broker_recovery_millis,
                "server_rolling_replacement": server_recovery_millis,
                "client_after_server_replacement": server_reconnect_millis,
                "client_after_broker_replacement": broker_reconnect_millis,
            },
            "router_processes_after_recovery": {
                "tor": final_broker_status.tor_routers_running,
                "i2p": final_broker_status.i2p_routers_running,
            },
            "elapsed_millis": elapsed_millis(test_started.elapsed()),
        }))
    }
    .await;

    let broker_cleanup = stop_test_broker(&executable, &broker_runtime)
        .await
        .context("failed to stop recovered process-restart broker");
    let server_cleanup = match &mut final_server {
        Some(server) => stop_child(server)
            .await
            .context("failed to stop recovered process-restart server"),
        None => Ok(()),
    };
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove restart state");
    let cleanup = join_results(
        broker_cleanup,
        join_results(server_cleanup, filesystem_cleanup),
    );
    match (operation, cleanup) {
        (Ok(report), Ok(())) => {
            println!("{report}");
            Ok(())
        }
        (Err(error), Ok(())) | (Ok(_), Err(error)) => {
            println!(
                "{}",
                process_restart_failure_artifact(&error, test_started.elapsed())
            );
            Err(error)
        }
        (Err(operation), Err(cleanup)) => {
            let error = anyhow!("{operation:#}; cleanup also failed: {cleanup:#}");
            println!(
                "{}",
                process_restart_failure_artifact(&error, test_started.elapsed())
            );
            Err(error)
        }
    }
}

#[cfg(target_os = "linux")]
fn process_restart_server_command(
    executable: &Path,
    root: &Path,
    machine_id: &str,
    endpoints: BondSshEndpoints,
) -> Command {
    let mut command = Command::new(executable);
    command
        .arg("server")
        .arg("--machine-id")
        .arg(machine_id)
        .arg("--transport")
        .arg("bond")
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit());
    configure_server_bond_pool(&mut command, endpoints.server);
    configure_owned_child(&mut command);
    command
}

#[cfg(target_os = "linux")]
fn process_restart_broker_command(
    executable: &Path,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Command {
    let mut command = Command::new(executable);
    command
        .arg("bond-broker")
        .env("XDG_RUNTIME_DIR", broker_runtime)
        .env("XDG_CACHE_HOME", root.join("cache"))
        .env("XDG_DATA_HOME", root.join("data"))
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_client_bond_pool(&mut command, endpoints);
    command
}

#[cfg(target_os = "linux")]
#[allow(clippy::too_many_arguments)]
fn process_restart_exact_client_command(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
    marker: &str,
) -> Command {
    let mut command = brokered_bond_client_command(
        executable,
        username,
        machine_id,
        root,
        broker_runtime,
        endpoints,
        None,
    );
    command
        .arg("--")
        .arg("-T")
        .arg("-o")
        .arg(format!("RemoteCommand=printf '{marker}\\n'"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    configure_owned_child(&mut command);
    command
}

#[cfg(target_os = "linux")]
async fn wait_for_running_broker(
    executable: &Path,
    runtime: &Path,
) -> Result<crate::bond_broker::BrokerStatus> {
    timeout(Duration::from_secs(30), async {
        loop {
            let status = read_test_broker_status(executable, runtime).await?;
            if status.running {
                return Ok(status);
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
    })
    .await
    .context("broker did not become reachable before its startup deadline")?
}

#[cfg(target_os = "linux")]
async fn wait_for_starting_broker(
    executable: &Path,
    runtime: &Path,
) -> Result<(crate::bond_broker::BrokerStatus, BTreeSet<u32>)> {
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            let status = read_test_broker_status(executable, runtime).await?;
            if let Some(process_id) = status.process_id {
                let descendants = linux_descendants(process_id)?;
                if status.running && !descendants.is_empty() {
                    return Ok((status, descendants));
                }
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
    })
    .await
    .context("broker did not enter router startup before its deadline")?
}

#[cfg(target_os = "linux")]
async fn wait_for_broker_status_with_streams(
    executable: &Path,
    runtime: &Path,
    minimum_streams: usize,
) -> Result<crate::bond_broker::BrokerStatus> {
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            let status = read_test_broker_status(executable, runtime).await?;
            if status.running
                && status.bond_sessions == 1
                && status.recent_bond_stream_ids.len() >= minimum_streams
            {
                return Ok(status);
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("broker did not report the recovered bond session before its deadline")?
}

#[cfg(target_os = "linux")]
async fn kill_child_with_sigkill(child: &mut Child, label: &str) -> Result<u32> {
    let process_id = child
        .id()
        .with_context(|| format!("{label} omitted its process ID"))?;
    send_sigkill(process_id, label)?;
    timeout(Duration::from_secs(15), child.wait())
        .await
        .with_context(|| format!("{label} did not exit after SIGKILL"))??;
    Ok(process_id)
}

#[cfg(target_os = "linux")]
async fn kill_process_with_sigkill(process_id: u32, label: &str) -> Result<()> {
    send_sigkill(process_id, label)?;
    timeout(Duration::from_secs(15), async {
        while linux_process_is_live(process_id) {
            tokio::time::sleep(Duration::from_millis(25)).await;
        }
    })
    .await
    .with_context(|| format!("{label} remained live after SIGKILL"))?;
    Ok(())
}

#[cfg(target_os = "linux")]
fn send_sigkill(process_id: u32, label: &str) -> Result<()> {
    let process_id = i32::try_from(process_id).context("process ID exceeded Linux pid_t")?;
    // SAFETY: the PID was read from an owned Child or authenticated local broker status.
    if unsafe { libc::kill(process_id, libc::SIGKILL) } == 0 {
        Ok(())
    } else {
        Err(std::io::Error::last_os_error()).with_context(|| format!("failed to kill {label}"))
    }
}

#[cfg(target_os = "linux")]
async fn wait_for_linux_descendants(
    process_id: u32,
    minimum: usize,
    deadline: Duration,
    label: &str,
) -> Result<BTreeSet<u32>> {
    timeout(deadline, async {
        loop {
            let descendants = linux_descendants(process_id)?;
            if descendants.len() >= minimum {
                return Ok(descendants);
            }
            if !linux_process_is_live(process_id) {
                bail!("process exited before it owned {minimum} descendants");
            }
            tokio::time::sleep(Duration::from_millis(25)).await;
        }
    })
    .await
    .with_context(|| {
        format!("{label} did not start {minimum} owned descendants before its deadline")
    })?
}

#[cfg(target_os = "linux")]
fn linux_descendants(process_id: u32) -> Result<BTreeSet<u32>> {
    let mut descendants = BTreeSet::new();
    let mut pending = vec![process_id];
    while let Some(parent) = pending.pop() {
        let task_root = format!("/proc/{parent}/task");
        let tasks = match fs::read_dir(task_root) {
            Ok(tasks) => tasks,
            Err(error) if error.kind() == io::ErrorKind::NotFound => continue,
            Err(error) => return Err(error).context("failed to inspect process descendants"),
        };
        for task in tasks {
            let children = match fs::read_to_string(task?.path().join("children")) {
                Ok(children) => children,
                Err(error) if error.kind() == io::ErrorKind::NotFound => continue,
                Err(error) => {
                    return Err(error).context("failed to inspect thread-owned descendants")
                }
            };
            for child in children.split_whitespace() {
                let child = child
                    .parse::<u32>()
                    .context("Linux children file contained an invalid PID")?;
                if descendants.insert(child) {
                    pending.push(child);
                }
            }
        }
    }
    Ok(descendants)
}

#[cfg(target_os = "linux")]
async fn wait_for_linux_processes_gone(
    process_ids: &BTreeSet<u32>,
    deadline: Duration,
) -> Result<()> {
    timeout(deadline, async {
        loop {
            let remaining = process_ids
                .iter()
                .copied()
                .filter(|process_id| linux_process_is_live(*process_id))
                .collect::<Vec<_>>();
            if remaining.is_empty() {
                return Ok(());
            }
            tokio::time::sleep(Duration::from_millis(25)).await;
        }
    })
    .await
    .context("owned subprocesses remained live after their owner exited")?
}

#[cfg(target_os = "linux")]
fn linux_process_is_live(process_id: u32) -> bool {
    let Ok(stat) = fs::read_to_string(format!("/proc/{process_id}/stat")) else {
        return false;
    };
    stat.rsplit_once(") ")
        .and_then(|(_, fields)| fields.as_bytes().first())
        .is_some_and(|state| *state != b'Z')
}

#[cfg(target_os = "linux")]
fn assert_stale_broker_control(runtime: &Path) -> Result<()> {
    let directory = runtime.join("anonssh");
    if !directory.join("bond-broker.sock").exists() || !directory.join("bond-broker.lease").is_dir()
    {
        bail!("SIGKILL did not leave the broker control state needed for reclaim proof");
    }
    Ok(())
}

#[cfg(target_os = "linux")]
async fn wait_for_endpoints_released(addresses: Vec<SocketAddr>) -> Result<()> {
    timeout(Duration::from_secs(30), async {
        loop {
            let mut reservations = Vec::with_capacity(addresses.len());
            let mut complete = true;
            for address in &addresses {
                match TcpListener::bind(address) {
                    Ok(listener) => reservations.push(listener),
                    Err(error) if error.kind() == io::ErrorKind::AddrInUse => {
                        complete = false;
                        break;
                    }
                    Err(error) => return Err(error.into()),
                }
            }
            if complete {
                return Ok::<(), anyhow::Error>(());
            }
            drop(reservations);
            tokio::time::sleep(Duration::from_millis(25)).await;
        }
    })
    .await
    .context("managed loopback endpoints remained occupied after process death")??;
    Ok(())
}

#[cfg(target_os = "linux")]
fn server_endpoints(endpoints: BondSshEndpoints) -> Vec<SocketAddr> {
    let mut addresses = vec![endpoints.backend];
    addresses.extend(endpoints.server.all());
    addresses
}

#[cfg(target_os = "linux")]
fn write_restart_marker(path: &Path, marker: &str) -> Result<()> {
    fs::create_dir_all(path.parent().context("restart marker has no parent")?)?;
    fs::write(path, marker)?;
    Ok(())
}

#[cfg(target_os = "linux")]
fn assert_restart_marker(path: &Path, marker: &str) -> Result<()> {
    let actual = fs::read_to_string(path)
        .with_context(|| format!("persistent router root lost {}", path.display()))?;
    if actual != marker {
        bail!("persistent router root changed its restart marker");
    }
    Ok(())
}

#[cfg(target_os = "linux")]
fn elapsed_millis(duration: Duration) -> u64 {
    u64::try_from(duration.as_millis()).unwrap_or(u64::MAX)
}

#[cfg(target_os = "linux")]
fn process_restart_failure_artifact(error: &anyhow::Error, elapsed: Duration) -> serde_json::Value {
    serde_json::json!({
        "schema": "anonssh.live-process-restart.v1",
        "status": "error",
        "error": format!("{error:#}"),
        "elapsed_millis": elapsed_millis(elapsed),
    })
}

async fn run_concurrent_bond_ssh() -> Result<()> {
    let test_started = Instant::now();
    let executable = std::env::current_exe().context("failed to resolve the test executable")?;
    let username = std::env::var("USER")
        .ok()
        .filter(|value| !value.is_empty())
        .context("USER is required for a live recovery test")?;
    let machine_id = format!("anonssh-live-concurrent-bond-ssh-{}", std::process::id());
    let secondary_machine_id = format!("{machine_id}-secondary");
    let root = live_test_root(LiveTransport::ConcurrentBondSsh);
    remove_if_present(&root)?;
    let endpoints = ConcurrentBondSshEndpoints::allocate()?;
    let client_root = root.join("client");
    let broker_runtime = client_root.join("runtime");

    let mut server = Command::new(&executable);
    server
        .arg("server")
        .arg("--machine-id")
        .arg(&machine_id)
        .arg("--transport")
        .arg("bond")
        .arg("--backend")
        .arg(endpoints.backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("server/cache"))
        .env("XDG_DATA_HOME", root.join("server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut server, endpoints.server);
    let mut server = server
        .spawn()
        .context("failed to start concurrent bonded SSH server")?;
    let server_stdout = server.stdout.take();
    let mut secondary_server = Command::new(&executable);
    secondary_server
        .arg("server")
        .arg("--machine-id")
        .arg(&secondary_machine_id)
        .arg("--transport")
        .arg("bond")
        .arg("--backend")
        .arg(endpoints.secondary_backend.to_string())
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_CACHE_HOME", root.join("secondary-server/cache"))
        .env("XDG_DATA_HOME", root.join("secondary-server/data"))
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    configure_server_bond_pool(&mut secondary_server, endpoints.secondary_server);
    let mut secondary_server = secondary_server
        .spawn()
        .context("failed to start secondary concurrent bonded SSH server")?;
    let secondary_server_stdout = secondary_server.stdout.take();
    let mut clients = [None, None, None];
    let mut drains = Vec::new();
    let bulk_progress = Arc::new(AtomicU64::new(0));
    let latest_broker_status = Arc::new(tokio::sync::Mutex::new(None));

    let operation = async {
        let stdout = server_stdout.context("bonded SSH server stdout was not piped")?;
        let destination = wait_for_prefix(stdout, "bond-tor-1 ").await?;
        let secondary_destination = wait_for_prefix(
            secondary_server_stdout.context("secondary bonded SSH server stdout was not piped")?,
            "bond-tor-1 ",
        )
        .await?;
        for (index, client_slot) in clients.iter_mut().enumerate() {
            let selected_machine = if index == 2 {
                &secondary_machine_id
            } else {
                &machine_id
            };
            let mut command = held_bond_client_command(
                &executable,
                &username,
                selected_machine,
                &client_root,
                &broker_runtime,
                endpoints.client,
            );
            *client_slot = Some(
                command
                    .spawn()
                    .with_context(|| format!("failed to start bonded SSH client {}", index + 1))?,
            );
        }

        let first_stderr = clients[0]
            .as_mut()
            .and_then(|client| client.stderr.take())
            .context("first bonded SSH client stderr was not piped")?;
        let second_stderr = clients[1]
            .as_mut()
            .and_then(|client| client.stderr.take())
            .context("second bonded SSH client stderr was not piped")?;
        let third_stderr = clients[2]
            .as_mut()
            .and_then(|client| client.stderr.take())
            .context("third bonded SSH client stderr was not piped")?;
        drains.push(wait_for_ssh_authentication(first_stderr, 1).await?);
        drains.push(wait_for_ssh_authentication(second_stderr, 2).await?);
        drains.push(wait_for_ssh_authentication(third_stderr, 3).await?);
        let initial_status = wait_for_broker_status(&executable, &broker_runtime, 2, 3).await?;
        *latest_broker_status.lock().await = Some(initial_status.clone());
        let initial_streams = initial_status
            .recent_bond_streams
            .iter()
            .copied()
            .collect::<BTreeSet<_>>();
        let initial_governor = initial_status
            .resource_governor
            .as_ref()
            .context("broker status omitted the shared resource governor")?;
        if initial_status.router_pool_instances != 1
            || initial_status.bond_sessions != 2
            || initial_status.bond_session_ids.len() != 2
            || initial_streams.len() < 3
            || initial_governor.sessions != 2
            || initial_governor.physical_slots != 4
        {
            bail!(
                "concurrent destinations did not share one governed broker pool: {}",
                serde_json::to_string(&initial_status)?
            );
        }
        assert_broker_rejects_wrong_key(&executable, &machine_id, &client_root, &broker_runtime)
            .await?;
        let authenticated_status =
            wait_for_broker_status(&executable, &broker_runtime, 2, 3).await?;
        if authenticated_status.process_id != initial_status.process_id
            || authenticated_status.bond_session_ids != initial_status.bond_session_ids
            || authenticated_status.bond_sessions != 2
        {
            bail!("wrong-key broker request changed authenticated session ownership");
        }

        let typing_channel = start_broker_typing_channel(
            &executable,
            &username,
            &machine_id,
            &client_root,
            &broker_runtime,
            endpoints.client,
        )
        .await?;
        let bulk_started = Arc::new(AtomicBool::new(false));
        let bulk_done = Arc::new(AtomicBool::new(false));
        let typing_done = Arc::new(AtomicBool::new(false));
        let bulk = run_broker_bulk_upload(
            &executable,
            &username,
            &machine_id,
            &client_root,
            &broker_runtime,
            endpoints.client,
            bulk_started.clone(),
            bulk_done.clone(),
            typing_done.clone(),
            bulk_progress.clone(),
        );
        let typing = async {
            let result = run_broker_typing(typing_channel, &bulk_started, &bulk_done).await;
            typing_done.store(true, Ordering::Release);
            result
        };
        let (bulk, mut typing) = timeout(CONCURRENT_WORKLOAD_TIMEOUT, async {
            tokio::try_join!(bulk, typing)
        })
        .await
        .context("concurrent broker workload exceeded its deadline")??;
        typing.latencies.sort_unstable();
        let typing_p95 = percentile(&typing.latencies, 95);
        if typing_p95 > u64::try_from(CONCURRENT_TYPING_P95_LIMIT.as_micros()).unwrap_or(u64::MAX) {
            bail!("independent typing p95 exceeded the product limit");
        }
        let warm_reconnect = run_broker_warm_reconnect(
            &executable,
            &username,
            &machine_id,
            &client_root,
            &broker_runtime,
            endpoints.client,
        )
        .await?;

        let status = wait_for_broker_status(&executable, &broker_runtime, 2, 6).await?;
        *latest_broker_status.lock().await = Some(status.clone());
        let distinct_streams = status
            .recent_bond_streams
            .iter()
            .copied()
            .collect::<BTreeSet<_>>();
        let expected_streams = 3 + 2 + 1;
        if status.process_id != initial_status.process_id
            || status.bond_session_ids != initial_status.bond_session_ids
            || status.router_pool_instances != 1
            || status.bond_sessions != 2
            || distinct_streams.len() < expected_streams
        {
            bail!("broker workload did not reuse one warm pool and bond session");
        }
        for (index, client) in clients.iter_mut().enumerate() {
            if let Some(status) = client
                .as_mut()
                .context("bonded SSH client disappeared")?
                .try_wait()?
            {
                bail!(
                    "bonded SSH client {} exited during the concurrent workload with {status}",
                    index + 1
                );
            }
        }
        Ok(serde_json::json!({
        "schema": "anonssh.live-concurrent-bond-ssh.v5",
        "status": "ok",
        "transport": "bond",
        "tor_destination": destination,
        "secondary_tor_destination": secondary_destination,
        "active_ssh_sessions": 3,
        "broker_process_id": status.process_id,
        "router_pool_instances": status.router_pool_instances,
        "bond_sessions": status.bond_sessions,
        "bond_session_ids": status.bond_session_ids,
        "distinct_bond_streams": distinct_streams,
        "tor_routers_running": status.tor_routers_running,
            "i2p_routers_running": status.i2p_routers_running,
            "resource_governor": status.resource_governor,
            "per_session_topologies": status.bond_session_topologies,
            "router_progress": status.router_progress,
            "wrong_key_request_rejected": true,
            "bulk": {
            "bytes": bulk.bytes,
            "sha256": bulk.sha256,
            "ssh_startup_micros": bulk.ssh_startup_micros,
            "duration_micros": bulk.duration_micros,
            "goodput_bytes_per_second": bulk.goodput_bytes_per_second,
        },
        "typing": {
            "independent_streams": 1,
            "ssh_startup_micros": typing.ssh_startup_micros,
            "exact_responses": typing.latencies.len(),
            "all_overlapped_bulk": true,
            "round_trip_micros_p50": percentile(&typing.latencies, 50),
            "round_trip_micros_p95": typing_p95,
            "round_trip_micros_max": typing.latencies.last().copied().unwrap_or(0),
                "p95_limit_micros": CONCURRENT_TYPING_P95_LIMIT.as_micros(),
            },
            "warm_reconnect": {
                "exact_response": true,
                "ssh_startup_micros": warm_reconnect,
            },
        }))
    }
    .await;

    let broker_cleanup = stop_test_broker(&executable, &broker_runtime).await;
    let mut client_cleanup = Ok(());
    for (index, client) in clients.iter_mut().enumerate() {
        if let Some(client) = client {
            if let Err(error) = wait_for_brokered_client_exit(client).await {
                client_cleanup =
                    Err(error.context(format!("failed to stop bonded SSH client {}", index + 1)));
            }
        }
    }
    for drain in drains {
        drain.abort();
        let _ = drain.await;
    }
    let server_cleanup = stop_child(&mut server)
        .await
        .context("failed to stop concurrent bonded SSH server");
    let secondary_server_cleanup = stop_child(&mut secondary_server)
        .await
        .context("failed to stop secondary concurrent bonded SSH server");
    let process_cleanup = join_results(
        client_cleanup,
        join_results(
            broker_cleanup,
            join_results(server_cleanup, secondary_server_cleanup),
        ),
    );
    let filesystem_cleanup = remove_if_present(&root).context("failed to remove live-test state");
    let report = operation.as_ref().ok().cloned();
    let result = join_results(
        operation.map(drop),
        join_results(process_cleanup, filesystem_cleanup),
    );
    match result {
        Ok(()) => {
            println!("{}", report.context("concurrent live report disappeared")?);
            Ok(())
        }
        Err(error) => {
            let broker_status = latest_broker_status.lock().await.clone();
            println!(
                "{}",
                concurrent_bond_ssh_failure_artifact(
                    &format!("{error:#}"),
                    test_started.elapsed(),
                    bulk_progress.load(Ordering::Acquire),
                    broker_status.as_ref(),
                )
            );
            Err(error)
        }
    }
}

async fn assert_broker_rejects_wrong_key(
    executable: &Path,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
) -> Result<()> {
    let password = zeroize::Zeroizing::new(LIVE_TEST_PASSWORD.to_owned());
    let identity = IdentityManager::derive_client_recovery_identity(&password, machine_id)?;
    let key_path = root.join("wrong-bond-session.key");
    fs::write(&key_path, [0xa5; 32])?;
    chmod(&key_path, 0o600)?;

    let mut command = Command::new(executable);
    command.arg("bond-proxy");
    for destination in &identity.tor_pool_destinations {
        command.arg("--tor-destination").arg(destination);
    }
    for identity in &identity.i2p_pool {
        command.arg("--i2p-destination").arg(&identity.destination);
    }
    command
        .arg("--key-file")
        .arg(&key_path)
        .env("ANONSSH_RESOURCE_PROFILE", CONCURRENT_RESOURCE_PROFILE)
        .env("XDG_RUNTIME_DIR", broker_runtime)
        .env("XDG_CACHE_HOME", root.join("cache"))
        .env("XDG_DATA_HOME", root.join("data"))
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    let output = timeout(Duration::from_secs(10), command.output())
        .await
        .context("wrong-key broker request was not rejected promptly")??;
    if output.status.success() {
        bail!("wrong-key broker request unexpectedly succeeded");
    }
    let stderr = String::from_utf8_lossy(&output.stderr);
    if !stderr.contains("could not establish the requested session") {
        bail!("wrong-key broker request returned an unexpected failure");
    }
    Ok(())
}

async fn run_broker_warm_reconnect(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<u64> {
    let mut command = brokered_bond_client_command(
        executable,
        username,
        machine_id,
        root,
        broker_runtime,
        endpoints,
        Some(CONCURRENT_RESOURCE_PROFILE),
    );
    command
        .arg("--")
        .arg("-T")
        .arg("-o")
        .arg("RemoteCommand=printf 'anonssh-warm-reconnect\\n'")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    let started = Instant::now();
    let output = timeout(TYPING_PROBE_TIMEOUT, command.output())
        .await
        .context("warm broker reconnect exceeded its deadline")??;
    if !output.status.success() {
        bail!("warm broker reconnect failed with {}", output.status);
    }
    if output.stdout != b"anonssh-warm-reconnect\n" {
        bail!("warm broker reconnect returned an invalid response");
    }
    Ok(u64::try_from(started.elapsed().as_micros()).unwrap_or(u64::MAX))
}

fn concurrent_bond_ssh_failure_artifact(
    error: &str,
    elapsed: Duration,
    bulk_bytes_written: u64,
    broker_status: Option<&crate::bond_broker::BrokerStatus>,
) -> serde_json::Value {
    serde_json::json!({
        "schema": "anonssh.live-concurrent-bond-ssh.v5",
        "status": "error",
        "error": error,
        "elapsed_micros": u64::try_from(elapsed.as_micros()).unwrap_or(u64::MAX),
        "broker_status": broker_status,
        "bulk": {
            "bytes_written": bulk_bytes_written,
            "minimum_bytes": CONCURRENT_BULK_MIN_BYTES,
            "workload_timeout_micros": CONCURRENT_WORKLOAD_TIMEOUT.as_micros(),
        },
    })
}

struct BrokerBulkEvidence {
    bytes: usize,
    sha256: String,
    ssh_startup_micros: u64,
    duration_micros: u64,
    goodput_bytes_per_second: u64,
}

struct BrokerTypingChannel {
    child: Child,
    stdin: ChildStdin,
    stdout: BufReader<ChildStdout>,
    ssh_startup_micros: u64,
}

struct BrokerTypingEvidence {
    latencies: Vec<u64>,
    ssh_startup_micros: u64,
}

#[allow(clippy::too_many_arguments)]
async fn run_broker_bulk_upload(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
    bulk_started: Arc<AtomicBool>,
    bulk_done: Arc<AtomicBool>,
    typing_done: Arc<AtomicBool>,
    bulk_progress: Arc<AtomicU64>,
) -> Result<BrokerBulkEvidence> {
    let mut command = brokered_bond_client_command(
        executable,
        username,
        machine_id,
        root,
        broker_runtime,
        endpoints,
        Some(CONCURRENT_RESOURCE_PROFILE),
    );
    command
        .arg("--")
        .arg("-T")
        .arg("-o")
        .arg("RemoteCommand=printf 'anonssh-bulk-ready\\n'; sha256sum")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    let command_started = Instant::now();
    let mut child = command
        .spawn()
        .context("failed to start brokered bulk SSH command")?;
    let mut stdin = child
        .stdin
        .take()
        .context("brokered bulk SSH command omitted stdin")?;
    let stdout = child
        .stdout
        .take()
        .context("brokered bulk SSH command omitted stdout")?;
    let mut stdout = BufReader::new(stdout);
    let mut ready = String::new();
    timeout(TYPING_PROBE_TIMEOUT, stdout.read_line(&mut ready))
        .await
        .context("brokered bulk SSH command did not become ready")??;
    if ready != "anonssh-bulk-ready\n" {
        bail!("brokered bulk SSH command emitted an invalid readiness marker");
    }
    let ssh_startup_micros =
        u64::try_from(command_started.elapsed().as_micros()).unwrap_or(u64::MAX);
    let payload_started = Instant::now();
    bulk_started.store(true, Ordering::Release);
    let chunk = vec![0x5a; ADAPTIVE_BULK_CHUNK_BYTES];
    let mut digest = Sha256::new();
    let mut bytes = 0_usize;
    while bytes < CONCURRENT_BULK_MIN_BYTES || !typing_done.load(Ordering::Acquire) {
        if bytes >= CONCURRENT_BULK_MAX_BYTES {
            bail!("typing probes did not finish within the bounded bulk workload");
        }
        stdin
            .write_all(&chunk)
            .await
            .context("failed to write brokered bulk payload")?;
        digest.update(&chunk);
        bytes += chunk.len();
        bulk_progress.store(u64::try_from(bytes).unwrap_or(u64::MAX), Ordering::Release);
        if bytes.is_multiple_of(1024 * 1024) {
            tokio::task::yield_now().await;
        }
    }
    stdin.shutdown().await?;
    drop(stdin);
    let mut hash_line = String::new();
    timeout(CONNECTION_TIMEOUT, stdout.read_line(&mut hash_line))
        .await
        .context("brokered bulk SSH hash exceeded its deadline")??;
    let status = timeout(CONNECTION_TIMEOUT, child.wait())
        .await
        .context("brokered bulk SSH command exceeded its deadline")??;
    bulk_done.store(true, Ordering::Release);
    if !status.success() {
        bail!("brokered bulk SSH command failed with {status}");
    }
    let expected = format!("{:x}", digest.finalize());
    let actual = hash_line
        .split_whitespace()
        .next()
        .context("brokered bulk hash was empty")?
        .to_owned();
    if actual != expected {
        bail!("brokered bulk hash mismatch");
    }
    let duration_micros = u64::try_from(payload_started.elapsed().as_micros()).unwrap_or(u64::MAX);
    Ok(BrokerBulkEvidence {
        bytes,
        sha256: actual.to_owned(),
        ssh_startup_micros,
        duration_micros,
        goodput_bytes_per_second: u64::try_from(bytes)
            .unwrap_or(u64::MAX)
            .saturating_mul(1_000_000)
            .checked_div(duration_micros.max(1))
            .unwrap_or(0),
    })
}

async fn start_broker_typing_channel(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Result<BrokerTypingChannel> {
    start_broker_typing_channel_with_timeout(
        executable,
        username,
        machine_id,
        root,
        broker_runtime,
        endpoints,
        Some(CONCURRENT_RESOURCE_PROFILE),
        TYPING_PROBE_TIMEOUT,
    )
    .await
}

#[allow(clippy::too_many_arguments)]
async fn start_broker_typing_channel_with_timeout(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
    resource_profile: Option<&str>,
    readiness_timeout: Duration,
) -> Result<BrokerTypingChannel> {
    let mut command = brokered_bond_client_command(
        executable,
        username,
        machine_id,
        root,
        broker_runtime,
        endpoints,
        resource_profile,
    );
    command
        .arg("--")
        .arg("-T")
        .arg("-o")
        .arg("RemoteCommand=printf 'anonssh-typing-ready\\n'; cat")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .kill_on_drop(true);
    let started = Instant::now();
    let mut child = command
        .spawn()
        .context("failed to start brokered interactive SSH command")?;
    let stdin = child
        .stdin
        .take()
        .context("brokered interactive SSH command omitted stdin")?;
    let stdout = child
        .stdout
        .take()
        .context("brokered interactive SSH command omitted stdout")?;
    let mut stdout = BufReader::new(stdout);
    let mut ready = String::new();
    timeout(readiness_timeout, stdout.read_line(&mut ready))
        .await
        .context("brokered interactive SSH command did not become ready")??;
    if ready != "anonssh-typing-ready\n" {
        bail!("brokered interactive SSH command emitted an invalid readiness marker");
    }
    Ok(BrokerTypingChannel {
        child,
        stdin,
        stdout,
        ssh_startup_micros: u64::try_from(started.elapsed().as_micros()).unwrap_or(u64::MAX),
    })
}

async fn run_broker_typing(
    mut channel: BrokerTypingChannel,
    bulk_started: &AtomicBool,
    bulk_done: &AtomicBool,
) -> Result<BrokerTypingEvidence> {
    timeout(TYPING_PROBE_TIMEOUT, async {
        while !bulk_started.load(Ordering::Acquire) {
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
    })
    .await
    .context("brokered bulk did not start before typing probes")?;

    let mut latencies = Vec::with_capacity(TYPING_PROBE_COUNT);
    for index in 0..TYPING_PROBE_COUNT {
        tokio::time::sleep(Duration::from_millis(250)).await;
        if bulk_done.load(Ordering::Acquire) {
            bail!("brokered bulk ended before typing probe {index}");
        }
        let marker = format!("anonssh-broker-typing-{index}");
        let encoded = format!("{marker}\n");
        let mut response = String::new();
        let started = Instant::now();
        timeout(TYPING_PROBE_TIMEOUT, async {
            channel.stdin.write_all(encoded.as_bytes()).await?;
            channel.stdin.flush().await?;
            channel.stdout.read_line(&mut response).await?;
            Ok::<(), io::Error>(())
        })
        .await
        .with_context(|| format!("brokered typing probe {index} exceeded its deadline"))??;
        if bulk_done.load(Ordering::Acquire) {
            bail!("brokered bulk ended during typing probe {index}");
        }
        if response != encoded {
            bail!("brokered typing probe {index} returned an invalid response");
        }
        latencies.push(u64::try_from(started.elapsed().as_micros()).unwrap_or(u64::MAX));
    }
    channel.stdin.shutdown().await?;
    drop(channel.stdin);
    let status = timeout(TYPING_PROBE_TIMEOUT, channel.child.wait())
        .await
        .context("brokered interactive SSH command did not stop")??;
    if !status.success() {
        bail!("brokered interactive SSH command failed with {status}");
    }
    Ok(BrokerTypingEvidence {
        latencies,
        ssh_startup_micros: channel.ssh_startup_micros,
    })
}

async fn wait_for_brokered_client_exit(client: &mut tokio::process::Child) -> Result<()> {
    match timeout(Duration::from_secs(15), client.wait()).await {
        Ok(status) => {
            status.context("failed to wait for brokered SSH client")?;
            Ok(())
        }
        Err(_) => {
            stop_child(client).await?;
            bail!("brokered SSH client did not exit after broker shutdown")
        }
    }
}

async fn wait_for_broker_status(
    executable: &Path,
    runtime: &Path,
    expected_sessions: usize,
    minimum_streams: usize,
) -> Result<crate::bond_broker::BrokerStatus> {
    timeout(CONNECTION_TIMEOUT, async {
        loop {
            let status = read_test_broker_status(executable, runtime).await?;
            if status.running
                && status.bond_sessions == expected_sessions
                && status.recent_bond_stream_ids.len() >= minimum_streams
            {
                return Ok(status);
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("live bond broker did not report shared sessions before its deadline")?
}

async fn read_test_broker_status(
    executable: &Path,
    runtime: &Path,
) -> Result<crate::bond_broker::BrokerStatus> {
    let output = Command::new(executable)
        .arg("broker")
        .arg("status")
        .arg("--json")
        .env("XDG_RUNTIME_DIR", runtime)
        .output()
        .await
        .context("failed to inspect the live bond broker")?;
    if !output.status.success() {
        bail!(
            "live bond broker status failed with {}: {}",
            output.status,
            String::from_utf8_lossy(&output.stderr)
        );
    }
    serde_json::from_slice(&output.stdout).context("live bond broker emitted invalid status JSON")
}

async fn stop_test_broker(executable: &Path, runtime: &Path) -> Result<()> {
    let output = Command::new(executable)
        .arg("broker")
        .arg("stop")
        .env("XDG_RUNTIME_DIR", runtime)
        .output()
        .await
        .context("failed to stop the live bond broker")?;
    if !output.status.success() {
        bail!(
            "live bond broker stop failed with {}: {}",
            output.status,
            String::from_utf8_lossy(&output.stderr)
        );
    }
    timeout(Duration::from_secs(30), async {
        loop {
            let status = Command::new(executable)
                .arg("broker")
                .arg("status")
                .arg("--json")
                .env("XDG_RUNTIME_DIR", runtime)
                .output()
                .await?;
            if status.status.success()
                && serde_json::from_slice::<crate::bond_broker::BrokerStatus>(&status.stdout)
                    .is_ok_and(|status| !status.running)
            {
                return Ok::<(), anyhow::Error>(());
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .context("live bond broker did not stop before its cleanup deadline")??;
    Ok(())
}

fn held_bond_client_command(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
) -> Command {
    let mut client = brokered_bond_client_command(
        executable,
        username,
        machine_id,
        root,
        broker_runtime,
        endpoints,
        Some(CONCURRENT_RESOURCE_PROFILE),
    );
    client
        .arg("--")
        .arg("-N")
        .arg("-T")
        .arg("-n")
        .arg("-vv")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::piped())
        .kill_on_drop(true);
    client
}

fn brokered_bond_client_command(
    executable: &Path,
    username: &str,
    machine_id: &str,
    root: &Path,
    broker_runtime: &Path,
    endpoints: ClientPoolEndpoints,
    resource_profile: Option<&str>,
) -> Command {
    let mut client = Command::new(executable);
    client
        .arg("connect")
        .arg(format!("{username}@{machine_id}"))
        .arg("--transport")
        .arg("bond")
        .env("ANONSSH_PASSPHRASE", LIVE_TEST_PASSWORD)
        .env("XDG_RUNTIME_DIR", broker_runtime)
        .env("XDG_CACHE_HOME", root.join("cache"))
        .env("XDG_DATA_HOME", root.join("data"));
    if let Some(resource_profile) = resource_profile {
        client.env("ANONSSH_RESOURCE_PROFILE", resource_profile);
    }
    configure_client_bond_pool(&mut client, endpoints);
    client
}

async fn wait_for_ssh_authentication(
    stderr: tokio::process::ChildStderr,
    client: usize,
) -> Result<tokio::task::JoinHandle<()>> {
    timeout(CONNECTION_TIMEOUT, async {
        let mut lines = BufReader::new(stderr).lines();
        while let Some(line) = lines.next_line().await? {
            if line.contains("Authenticated to ") {
                return Ok(tokio::spawn(async move {
                    while matches!(lines.next_line().await, Ok(Some(_))) {}
                }));
            }
        }
        bail!("bonded SSH client {client} exited before authentication")
    })
    .await
    .with_context(|| format!("bonded SSH client {client} did not authenticate in time"))?
}

async fn wait_for_path(path: &Path, deadline: Duration) -> Result<()> {
    timeout(deadline, async {
        loop {
            if path.exists() {
                return;
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    })
    .await
    .with_context(|| format!("timed out waiting for {}", path.display()))
}

fn configure_server_bond_pool(command: &mut Command, endpoints: ClientPoolEndpoints) {
    command
        .env("ANONSSH_I2P_POOL_ADDRS", pool_endpoints(&endpoints.sam))
        .env(
            "ANONSSH_TOR_POOL_SOCKS_ADDRS",
            pool_endpoints(&endpoints.socks[..PRODUCTION_TOR_SLOTS]),
        )
        .env(
            "ANONSSH_TOR_POOL_CONTROL_ADDRS",
            pool_endpoints(&endpoints.control[..PRODUCTION_TOR_SLOTS]),
        )
        .env(
            "ANONSSH_TOR_RESERVE_SOCKS_ADDRS",
            pool_endpoints(&endpoints.socks[PRODUCTION_TOR_SLOTS..]),
        )
        .env(
            "ANONSSH_TOR_RESERVE_CONTROL_ADDRS",
            pool_endpoints(&endpoints.control[PRODUCTION_TOR_SLOTS..]),
        );
}

fn configure_client_bond_pool(command: &mut Command, endpoints: ClientPoolEndpoints) {
    command
        .env(
            "ANONSSH_CLIENT_I2P_POOL_ADDRS",
            pool_endpoints(&endpoints.sam),
        )
        .env(
            "ANONSSH_CLIENT_TOR_POOL_SOCKS_ADDRS",
            pool_endpoints(&endpoints.socks[..PRODUCTION_TOR_SLOTS]),
        )
        .env(
            "ANONSSH_CLIENT_TOR_POOL_CONTROL_ADDRS",
            pool_endpoints(&endpoints.control[..PRODUCTION_TOR_SLOTS]),
        )
        .env(
            "ANONSSH_CLIENT_TOR_RESERVE_SOCKS_ADDRS",
            pool_endpoints(&endpoints.socks[PRODUCTION_TOR_SLOTS..]),
        )
        .env(
            "ANONSSH_CLIENT_TOR_RESERVE_CONTROL_ADDRS",
            pool_endpoints(&endpoints.control[PRODUCTION_TOR_SLOTS..]),
        );
}

fn pool_endpoints(endpoints: &[SocketAddr]) -> String {
    endpoints
        .iter()
        .map(SocketAddr::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

async fn wait_for_prefix(stdout: tokio::process::ChildStdout, prefix: &str) -> Result<String> {
    timeout(PUBLICATION_TIMEOUT, async {
        let mut lines = BufReader::new(stdout).lines();
        while let Some(line) = lines.next_line().await? {
            if let Some(destination) = line.strip_prefix(prefix) {
                if destination.is_empty() {
                    bail!("live-test server published an empty destination")
                }
                return Ok(destination.to_owned());
            }
        }
        bail!("live-test server exited before publishing {prefix}")
    })
    .await
    .context("live-test server did not publish within ten minutes")?
}

fn remove_if_present(path: &Path) -> Result<()> {
    const ATTEMPTS: usize = 20;
    const RETRY_DELAY: Duration = Duration::from_millis(50);

    for attempt in 1..=ATTEMPTS {
        match fs::remove_dir_all(path) {
            Ok(()) => return Ok(()),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
            Err(error)
                if attempt < ATTEMPTS
                    && matches!(
                        error.kind(),
                        std::io::ErrorKind::DirectoryNotEmpty | std::io::ErrorKind::Interrupted
                    ) =>
            {
                std::thread::sleep(RETRY_DELAY);
            }
            Err(error) => return Err(error.into()),
        }
    }
    unreachable!("bounded cleanup loop always returns")
}

fn join_results(first: Result<()>, second: Result<()>) -> Result<()> {
    match (first, second) {
        (Ok(()), Ok(())) => Ok(()),
        (Err(error), Ok(())) | (Ok(()), Err(error)) => Err(error),
        (Err(first), Err(second)) => Err(anyhow!("{first:#}; additional failure: {second:#}")),
    }
}

#[cfg(test)]
mod tests {
    #[cfg(unix)]
    use super::wait_for_path;
    use super::{
        concurrent_bond_ssh_failure_artifact, configure_client_bond_pool,
        configure_server_bond_pool, transport_label, transport_name, BondSshEndpoints,
        ConcurrentBondSshEndpoints, LiveEndpoints,
    };
    use crate::LiveTransport;
    #[cfg(unix)]
    use std::os::unix::net::UnixListener;
    #[cfg(unix)]
    use std::time::Duration;

    #[test]
    fn allocates_distinct_loopback_endpoints() {
        let endpoints = LiveEndpoints::allocate(LiveTransport::Tor).unwrap();
        let addresses = [
            Some(endpoints.backend),
            endpoints.server_socks,
            endpoints.server_control,
            endpoints.client_socks,
            endpoints.client_control,
        ];
        for address in addresses.into_iter().flatten() {
            assert!(address.ip().is_loopback());
            assert_ne!(address.port(), 0);
        }
        let unique = addresses
            .into_iter()
            .flatten()
            .collect::<std::collections::HashSet<_>>();
        assert_eq!(unique.len(), 5);
        assert_eq!(transport_name(LiveTransport::Tor), "tor");
        assert_eq!(transport_name(LiveTransport::Bond), "bond");
        assert_eq!(transport_name(LiveTransport::BondSsh), "bond");
        assert_eq!(transport_name(LiveTransport::BondTorSsh), "bond-tor");
        assert_eq!(transport_name(LiveTransport::BondI2pSsh), "bond-i2p");
        assert_eq!(transport_name(LiveTransport::I2pPool), "i2p-pool");
        assert_eq!(transport_name(LiveTransport::I2p), "i2p");
        assert_eq!(transport_name(LiveTransport::I2pFresh), "i2p");
        assert_eq!(transport_label(LiveTransport::I2pFresh), "i2p-fresh");

        let fresh = LiveEndpoints::allocate(LiveTransport::I2pFresh).unwrap();
        assert!(fresh.sam.is_some());
        assert!(fresh.server_socks.is_none());
    }

    #[test]
    fn live_endpoint_configuration_keeps_client_and_server_roles_separate() {
        let endpoints = BondSshEndpoints::allocate().unwrap();
        let mut server = tokio::process::Command::new("anonssh-test");
        configure_server_bond_pool(&mut server, endpoints.server);
        let server_environment = server
            .as_std()
            .get_envs()
            .filter_map(|(name, value)| value.map(|value| (name, value)))
            .collect::<std::collections::BTreeMap<_, _>>();
        assert!(
            server_environment.contains_key(std::ffi::OsStr::new("ANONSSH_TOR_POOL_SOCKS_ADDRS"))
        );
        assert!(!server_environment
            .contains_key(std::ffi::OsStr::new("ANONSSH_CLIENT_TOR_POOL_SOCKS_ADDRS")));

        let mut client = tokio::process::Command::new("anonssh-test");
        configure_client_bond_pool(&mut client, endpoints.client);
        let client_environment = client
            .as_std()
            .get_envs()
            .filter_map(|(name, value)| value.map(|value| (name, value)))
            .collect::<std::collections::BTreeMap<_, _>>();
        assert!(client_environment
            .contains_key(std::ffi::OsStr::new("ANONSSH_CLIENT_TOR_POOL_SOCKS_ADDRS")));
        assert!(
            !client_environment.contains_key(std::ffi::OsStr::new("ANONSSH_TOR_POOL_SOCKS_ADDRS"))
        );
    }

    #[cfg(target_os = "linux")]
    #[test]
    fn descendant_scan_aggregates_children_from_worker_threads() {
        let (pid_sender, pid_receiver) = std::sync::mpsc::channel();
        let (stop_sender, stop_receiver) = std::sync::mpsc::channel();
        let worker = std::thread::spawn(move || {
            let mut child = std::process::Command::new("sleep")
                .arg("30")
                .spawn()
                .unwrap();
            pid_sender.send(child.id()).unwrap();
            stop_receiver.recv().unwrap();
            child.kill().unwrap();
            child.wait().unwrap();
        });
        let child = pid_receiver.recv().unwrap();
        let deadline = std::time::Instant::now() + Duration::from_secs(2);
        loop {
            if super::linux_descendants(std::process::id())
                .unwrap()
                .contains(&child)
            {
                break;
            }
            if std::time::Instant::now() >= deadline {
                stop_sender.send(()).unwrap();
                worker.join().unwrap();
                panic!("worker-thread child was absent from descendant scan");
            }
            std::thread::sleep(Duration::from_millis(10));
        }
        stop_sender.send(()).unwrap();
        worker.join().unwrap();
    }

    #[test]
    fn allocates_complete_adaptive_product_pools() {
        BondSshEndpoints::allocate().unwrap();
        ConcurrentBondSshEndpoints::allocate().unwrap();
    }

    #[test]
    fn concurrent_failure_artifact_preserves_progress_and_cause() {
        let artifact = concurrent_bond_ssh_failure_artifact(
            "workload deadline elapsed",
            std::time::Duration::from_micros(123),
            456,
            None,
        );
        assert_eq!(artifact["schema"], "anonssh.live-concurrent-bond-ssh.v5");
        assert_eq!(artifact["status"], "error");
        assert_eq!(artifact["error"], "workload deadline elapsed");
        assert_eq!(artifact["elapsed_micros"], 123);
        assert_eq!(artifact["bulk"]["bytes_written"], 456);
        assert!(artifact["broker_status"].is_null());
    }

    #[cfg(unix)]
    #[tokio::test]
    async fn control_socket_readiness_accepts_a_unix_socket() {
        let path = std::env::temp_dir().join(format!(
            "anonssh-control-socket-test-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_file(&path);
        let socket = UnixListener::bind(&path).unwrap();
        wait_for_path(&path, Duration::from_secs(1)).await.unwrap();
        drop(socket);
        std::fs::remove_file(path).unwrap();
    }
}
