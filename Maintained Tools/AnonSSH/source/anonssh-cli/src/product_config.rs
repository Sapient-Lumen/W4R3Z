use std::fs;
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::time::Duration;

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};

pub const CONFIG_PATH_ENV: &str = "ANONSSH_CONFIG_FILE";
pub const RESOURCE_PROFILE_ENV: &str = "ANONSSH_RESOURCE_PROFILE";
pub const TRANSPORT_PROFILE_ENV: &str = "ANONSSH_TRANSPORT_PROFILE";

const CONFIG_VERSION: u32 = 2;
const MAX_CONFIG_BYTES: u64 = 64 * 1024;
const MAX_EXTERNAL_TOR_SERVICES: usize = 32;
const MIN_CACHE_QUOTA_BYTES: u64 = 256 * 1024 * 1024;
const MIN_STATE_QUOTA_BYTES: u64 = 1024 * 1024 * 1024;
const MIN_RUNTIME_RETENTION_SECONDS: u64 = 24 * 60 * 60;
const MAX_RUNTIME_RETENTION_SECONDS: u64 = 365 * 24 * 60 * 60;

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ResourceProfile {
    Low,
    Balanced,
    Performance,
}

impl ResourceProfile {
    fn parse(value: &str) -> Result<Self> {
        match value {
            "low" => Ok(Self::Low),
            "balanced" => Ok(Self::Balanced),
            "performance" => Ok(Self::Performance),
            _ => bail!("resource profile must be low, balanced, or performance"),
        }
    }

    pub const fn policy(self) -> ScalingPolicy {
        match self {
            Self::Low => ScalingPolicy {
                control_interval_millis: 15_000,
                maximum_active_lanes: 4,
                maximum_admissions_per_interval: 1,
                maximum_drains_per_interval: 1,
                maximum_cpu_millicores: 1_000,
                maximum_memory_bytes: 1024 * 1024 * 1024,
            },
            Self::Balanced => ScalingPolicy {
                control_interval_millis: 10_000,
                maximum_active_lanes: 8,
                maximum_admissions_per_interval: 2,
                maximum_drains_per_interval: 2,
                maximum_cpu_millicores: 3_000,
                maximum_memory_bytes: 2 * 1024 * 1024 * 1024,
            },
            Self::Performance => ScalingPolicy {
                control_interval_millis: 10_000,
                maximum_active_lanes: 16,
                maximum_admissions_per_interval: 4,
                maximum_drains_per_interval: 4,
                maximum_cpu_millicores: 8_000,
                maximum_memory_bytes: 4 * 1024 * 1024 * 1024,
            },
        }
    }

    pub(crate) const fn wire_code(self) -> u8 {
        match self {
            Self::Low => 1,
            Self::Balanced => 2,
            Self::Performance => 3,
        }
    }

    pub(crate) fn from_wire_code(value: u8) -> Result<Self> {
        match value {
            1 => Ok(Self::Low),
            2 => Ok(Self::Balanced),
            3 => Ok(Self::Performance),
            _ => bail!("unsupported resource profile code {value}"),
        }
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum TransportProfile {
    Auto,
    Mixed,
    TorOnly,
    I2pOnly,
}

impl TransportProfile {
    fn parse(value: &str) -> Result<Self> {
        match value {
            "auto" => Ok(Self::Auto),
            "mixed" => Ok(Self::Mixed),
            "tor-only" => Ok(Self::TorOnly),
            "i2p-only" => Ok(Self::I2pOnly),
            _ => bail!("transport profile must be auto, mixed, tor-only, or i2p-only"),
        }
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ScalingPolicy {
    pub control_interval_millis: u64,
    pub maximum_active_lanes: usize,
    pub maximum_admissions_per_interval: usize,
    pub maximum_drains_per_interval: usize,
    pub maximum_cpu_millicores: u32,
    pub maximum_memory_bytes: u64,
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ExternalTorService {
    pub socks: SocketAddr,
    pub control: SocketAddr,
    pub cookie_file: PathBuf,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct ResidentServicePolicy {
    pub maximum_sessions: usize,
    pub maximum_local_connections: usize,
    pub minimum_warm_slots_per_provider: usize,
    pub maximum_warm_slots_per_provider: usize,
    pub cache_quota_bytes: u64,
    pub state_quota_bytes: u64,
    pub old_runtime_retention_seconds: u64,
}

impl ResourceProfile {
    pub const fn resident_policy(self) -> ResidentServicePolicy {
        match self {
            Self::Low => ResidentServicePolicy {
                maximum_sessions: 4,
                maximum_local_connections: 16,
                minimum_warm_slots_per_provider: 1,
                maximum_warm_slots_per_provider: 2,
                cache_quota_bytes: 1024 * 1024 * 1024,
                state_quota_bytes: 8 * 1024 * 1024 * 1024,
                old_runtime_retention_seconds: 30 * 24 * 60 * 60,
            },
            Self::Balanced => ResidentServicePolicy {
                maximum_sessions: 8,
                maximum_local_connections: 32,
                minimum_warm_slots_per_provider: 2,
                maximum_warm_slots_per_provider: 4,
                cache_quota_bytes: 2 * 1024 * 1024 * 1024,
                state_quota_bytes: 16 * 1024 * 1024 * 1024,
                old_runtime_retention_seconds: 30 * 24 * 60 * 60,
            },
            Self::Performance => ResidentServicePolicy {
                maximum_sessions: 16,
                maximum_local_connections: 64,
                minimum_warm_slots_per_provider: 2,
                maximum_warm_slots_per_provider: 8,
                cache_quota_bytes: 4 * 1024 * 1024 * 1024,
                state_quota_bytes: 32 * 1024 * 1024 * 1024,
                old_runtime_retention_seconds: 30 * 24 * 60 * 60,
            },
        }
    }
}

#[derive(Clone, Copy, Debug, Default, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ResidentServiceOverrides {
    #[serde(default)]
    pub maximum_sessions: Option<usize>,
    #[serde(default)]
    pub maximum_local_connections: Option<usize>,
    #[serde(default)]
    pub minimum_warm_slots_per_provider: Option<usize>,
    #[serde(default)]
    pub maximum_warm_slots_per_provider: Option<usize>,
    #[serde(default)]
    pub cache_quota_bytes: Option<u64>,
    #[serde(default)]
    pub state_quota_bytes: Option<u64>,
    #[serde(default)]
    pub old_runtime_retention_seconds: Option<u64>,
}

impl ResidentServiceOverrides {
    fn apply(self, profile: ResourceProfile) -> Result<ResidentServicePolicy> {
        let defaults = profile.resident_policy();
        let policy = ResidentServicePolicy {
            maximum_sessions: self.maximum_sessions.unwrap_or(defaults.maximum_sessions),
            maximum_local_connections: self
                .maximum_local_connections
                .unwrap_or(defaults.maximum_local_connections),
            minimum_warm_slots_per_provider: self
                .minimum_warm_slots_per_provider
                .unwrap_or(defaults.minimum_warm_slots_per_provider),
            maximum_warm_slots_per_provider: self
                .maximum_warm_slots_per_provider
                .unwrap_or(defaults.maximum_warm_slots_per_provider),
            cache_quota_bytes: self.cache_quota_bytes.unwrap_or(defaults.cache_quota_bytes),
            state_quota_bytes: self.state_quota_bytes.unwrap_or(defaults.state_quota_bytes),
            old_runtime_retention_seconds: self
                .old_runtime_retention_seconds
                .unwrap_or(defaults.old_runtime_retention_seconds),
        };
        policy.validate()?;
        Ok(policy)
    }
}

impl ResidentServicePolicy {
    fn validate(self) -> Result<()> {
        if !(1..=256).contains(&self.maximum_sessions) {
            bail!("maximum_sessions must be between 1 and 256");
        }
        if !(self.maximum_sessions..=4_096).contains(&self.maximum_local_connections) {
            bail!("maximum_local_connections must be between maximum_sessions and 4096");
        }
        if self.minimum_warm_slots_per_provider > 8
            || !(self.minimum_warm_slots_per_provider..=8)
                .contains(&self.maximum_warm_slots_per_provider)
        {
            bail!("warm slot limits must satisfy 0 <= minimum <= maximum <= 8");
        }
        if self.cache_quota_bytes < MIN_CACHE_QUOTA_BYTES {
            bail!("cache_quota_bytes must be at least {MIN_CACHE_QUOTA_BYTES}");
        }
        if self.state_quota_bytes < MIN_STATE_QUOTA_BYTES {
            bail!("state_quota_bytes must be at least {MIN_STATE_QUOTA_BYTES}");
        }
        if !(MIN_RUNTIME_RETENTION_SECONDS..=MAX_RUNTIME_RETENTION_SECONDS)
            .contains(&self.old_runtime_retention_seconds)
        {
            bail!(
                "old_runtime_retention_seconds must be between {MIN_RUNTIME_RETENTION_SECONDS} and {MAX_RUNTIME_RETENTION_SECONDS}"
            );
        }
        Ok(())
    }
}

impl ScalingPolicy {
    pub const fn performance() -> Self {
        ResourceProfile::Performance.policy()
    }

    pub const fn control_interval(self) -> Duration {
        Duration::from_millis(self.control_interval_millis)
    }
}

#[derive(Clone, Debug)]
pub struct ProductConfig {
    source: Option<PathBuf>,
    resource_profile: ResourceProfile,
    transport_profile: TransportProfile,
    external_tor_services: Vec<ExternalTorService>,
    resident_overrides: ResidentServiceOverrides,
    resource_override: bool,
    transport_override: bool,
}

#[derive(Clone, Debug, Serialize)]
pub struct ProductConfigReport {
    pub schema: &'static str,
    pub version: u32,
    pub source: String,
    pub resource_profile: ResourceProfile,
    pub transport_profile: TransportProfile,
    pub resource_environment_override: bool,
    pub transport_environment_override: bool,
    pub scaling: ScalingPolicy,
    pub resident_service: ResidentServicePolicy,
    pub external_tor_service_count: usize,
    pub state_root_policy: &'static str,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ConfigFileV1 {
    version: u32,
    #[serde(default)]
    resource_profile: Option<ResourceProfile>,
    #[serde(default)]
    transport_profile: Option<TransportProfile>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ConfigFileV2 {
    version: u32,
    #[serde(default)]
    resource_profile: Option<ResourceProfile>,
    #[serde(default)]
    transport_profile: Option<TransportProfile>,
    #[serde(default)]
    external_tor_services: Vec<ExternalTorService>,
    #[serde(default)]
    resident_service: ResidentServiceOverrides,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ConfigFileV0 {
    version: u32,
    #[serde(default)]
    profile: Option<ResourceProfile>,
    #[serde(default)]
    transport: Option<TransportProfile>,
}

#[derive(Deserialize)]
struct ConfigVersion {
    version: u32,
}

impl Default for ProductConfig {
    fn default() -> Self {
        Self {
            source: None,
            resource_profile: ResourceProfile::Performance,
            transport_profile: TransportProfile::Auto,
            external_tor_services: Vec::new(),
            resident_overrides: ResidentServiceOverrides::default(),
            resource_override: false,
            transport_override: false,
        }
    }
}

impl ProductConfig {
    pub fn load(explicit_path: Option<&Path>) -> Result<Self> {
        let environment_path = std::env::var_os(CONFIG_PATH_ENV).map(PathBuf::from);
        let configured_path = match explicit_path.map(PathBuf::from).or(environment_path) {
            Some(path) => Some(path),
            None => default_config_path()?,
        };
        let resource_override = std::env::var(RESOURCE_PROFILE_ENV)
            .ok()
            .map(|value| ResourceProfile::parse(&value))
            .transpose()?;
        let transport_override = std::env::var(TRANSPORT_PROFILE_ENV)
            .ok()
            .map(|value| TransportProfile::parse(&value))
            .transpose()?;
        Self::load_from(
            configured_path.as_deref(),
            resource_override,
            transport_override,
        )
    }

    pub(crate) fn load_snapshot(path: &Path) -> Result<Self> {
        Self::load_from(Some(path), None, None)
    }

    fn load_from(
        path: Option<&Path>,
        resource_override: Option<ResourceProfile>,
        transport_override: Option<TransportProfile>,
    ) -> Result<Self> {
        let mut config = match path {
            Some(path) => parse_file(path)?,
            None => Self::default(),
        };
        if let Some(profile) = resource_override {
            config.resource_profile = profile;
            config.resource_override = true;
        }
        if let Some(profile) = transport_override {
            config.transport_profile = profile;
            config.transport_override = true;
        }
        Ok(config)
    }

    pub const fn transport_profile(&self) -> TransportProfile {
        self.transport_profile
    }

    pub const fn resource_profile(&self) -> ResourceProfile {
        self.resource_profile
    }

    pub const fn scaling_policy(&self) -> ScalingPolicy {
        self.resource_profile.policy()
    }

    pub fn resident_service_policy(&self) -> ResidentServicePolicy {
        self.resident_overrides
            .apply(self.resource_profile)
            .expect("validated resident service policy")
    }

    pub fn external_tor_services(&self) -> &[ExternalTorService] {
        &self.external_tor_services
    }

    pub fn source(&self) -> Option<&Path> {
        self.source.as_deref()
    }

    pub fn report(&self) -> ProductConfigReport {
        ProductConfigReport {
            schema: "anonssh.product-config.v2",
            version: CONFIG_VERSION,
            source: self
                .source
                .as_deref()
                .map(|path| path.display().to_string())
                .unwrap_or_else(|| "built-in defaults".to_owned()),
            resource_profile: self.resource_profile,
            transport_profile: self.transport_profile,
            resource_environment_override: self.resource_override,
            transport_environment_override: self.transport_override,
            scaling: self.scaling_policy(),
            resident_service: self.resident_service_policy(),
            external_tor_service_count: self.external_tor_services.len(),
            state_root_policy: "persistent-per-provider-slot-v1",
        }
    }
}

fn default_config_path() -> Result<Option<PathBuf>> {
    let Some(directory) = dirs::config_dir() else {
        return Ok(None);
    };
    let path = directory.join("anonssh/config.json");
    match fs::symlink_metadata(&path) {
        Ok(_) => Ok(Some(path)),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(error) => Err(error)
            .with_context(|| format!("cannot inspect configuration path {}", path.display())),
    }
}

fn parse_file(path: &Path) -> Result<ProductConfig> {
    let canonical = fs::canonicalize(path)
        .with_context(|| format!("cannot resolve configuration file {}", path.display()))?;
    let metadata = fs::metadata(&canonical)
        .with_context(|| format!("cannot inspect configuration file {}", canonical.display()))?;
    if !metadata.is_file() {
        bail!("configuration path is not a regular file");
    }
    if metadata.len() > MAX_CONFIG_BYTES {
        bail!("configuration file exceeds {MAX_CONFIG_BYTES} bytes");
    }
    let encoded = fs::read(&canonical)
        .with_context(|| format!("cannot read configuration file {}", canonical.display()))?;
    if encoded.len() as u64 > MAX_CONFIG_BYTES {
        bail!("configuration file exceeds {MAX_CONFIG_BYTES} bytes");
    }
    let envelope: ConfigVersion =
        serde_json::from_slice(&encoded).context("configuration requires one integer version")?;
    let (resource_profile, transport_profile, external_tor_services, resident_overrides) =
        match envelope.version {
            0 => {
                let legacy: ConfigFileV0 = serde_json::from_slice(&encoded)
                    .context("configuration v0 contains invalid or unknown fields")?;
                if legacy.version != 0 {
                    bail!("configuration version changed while parsing");
                }
                (
                    legacy.profile.unwrap_or(ResourceProfile::Performance),
                    legacy.transport.unwrap_or(TransportProfile::Auto),
                    Vec::new(),
                    ResidentServiceOverrides::default(),
                )
            }
            1 => {
                let current: ConfigFileV1 = serde_json::from_slice(&encoded)
                    .context("configuration v1 contains invalid or unknown fields")?;
                if current.version != 1 {
                    bail!("configuration version changed while parsing");
                }
                (
                    current
                        .resource_profile
                        .unwrap_or(ResourceProfile::Performance),
                    current.transport_profile.unwrap_or(TransportProfile::Auto),
                    Vec::new(),
                    ResidentServiceOverrides::default(),
                )
            }
            2 => {
                let current: ConfigFileV2 = serde_json::from_slice(&encoded)
                    .context("configuration v2 contains invalid or unknown fields")?;
                if current.version != CONFIG_VERSION {
                    bail!("configuration version changed while parsing");
                }
                let resource_profile = current
                    .resource_profile
                    .unwrap_or(ResourceProfile::Performance);
                current.resident_service.apply(resource_profile)?;
                let external_tor_services =
                    validate_external_tor_services(current.external_tor_services)?;
                (
                    resource_profile,
                    current.transport_profile.unwrap_or(TransportProfile::Auto),
                    external_tor_services,
                    current.resident_service,
                )
            }
            version => bail!("unsupported configuration version {version}"),
        };
    Ok(ProductConfig {
        source: Some(canonical),
        resource_profile,
        transport_profile,
        external_tor_services,
        resident_overrides,
        resource_override: false,
        transport_override: false,
    })
}

fn validate_external_tor_services(
    services: Vec<ExternalTorService>,
) -> Result<Vec<ExternalTorService>> {
    if services.len() > MAX_EXTERNAL_TOR_SERVICES {
        bail!("external_tor_services contains more than {MAX_EXTERNAL_TOR_SERVICES} entries");
    }
    let mut validated = Vec::with_capacity(services.len());
    for mut service in services {
        if !service.socks.ip().is_loopback()
            || service.socks.port() == 0
            || !service.control.ip().is_loopback()
            || service.control.port() == 0
        {
            bail!("external Tor endpoints must be non-zero loopback sockets");
        }
        if service.socks == service.control {
            bail!("external Tor SOCKS and control endpoints must differ");
        }
        service.cookie_file = crate::runtime::canonical_external_tor_cookie(&service.cookie_file)?;
        if validated.iter().any(|existing: &ExternalTorService| {
            existing.socks == service.socks
                || existing.control == service.control
                || existing.cookie_file == service.cookie_file
        }) {
            bail!("external_tor_services contains a duplicate endpoint or control cookie");
        }
        validated.push(service);
    }
    Ok(validated)
}

#[cfg(test)]
mod tests {
    use std::sync::atomic::{AtomicU64, Ordering};

    use super::{
        ProductConfig, ResourceProfile, ScalingPolicy, TransportProfile, MAX_CONFIG_BYTES,
    };

    static NEXT_TEST: AtomicU64 = AtomicU64::new(1);

    fn config_file(contents: &str) -> std::path::PathBuf {
        let root = std::env::temp_dir().join(format!(
            "anonssh-config-test-{}-{}",
            std::process::id(),
            NEXT_TEST.fetch_add(1, Ordering::Relaxed)
        ));
        std::fs::create_dir_all(&root).unwrap();
        let path = root.join("config.json");
        std::fs::write(&path, contents).unwrap();
        path
    }

    #[test]
    fn absent_configuration_uses_locked_defaults() {
        let config = ProductConfig::load_from(None, None, None).unwrap();
        assert_eq!(
            config.report().resource_profile,
            ResourceProfile::Performance
        );
        assert_eq!(config.transport_profile(), TransportProfile::Auto);
        assert_eq!(config.scaling_policy(), ScalingPolicy::performance());
        assert!(config.source().is_none());
        assert_eq!(
            config.report().state_root_policy,
            "persistent-per-provider-slot-v1"
        );
    }

    #[test]
    fn version_one_is_strict_and_environment_profiles_take_precedence() {
        let path =
            config_file(r#"{"version":1,"resource_profile":"low","transport_profile":"tor-only"}"#);
        let config = ProductConfig::load_from(
            Some(&path),
            Some(ResourceProfile::Balanced),
            Some(TransportProfile::I2pOnly),
        )
        .unwrap();
        assert_eq!(config.report().resource_profile, ResourceProfile::Balanced);
        assert_eq!(config.transport_profile(), TransportProfile::I2pOnly);
        let report = config.report();
        assert!(report.resource_environment_override);
        assert!(report.transport_environment_override);
        std::fs::remove_dir_all(path.parent().unwrap()).unwrap();
    }

    #[test]
    fn version_zero_migrates_legacy_field_names() {
        let path = config_file(r#"{"version":0,"profile":"balanced","transport":"mixed"}"#);
        let config = ProductConfig::load_from(Some(&path), None, None).unwrap();
        assert_eq!(config.report().resource_profile, ResourceProfile::Balanced);
        assert_eq!(config.transport_profile(), TransportProfile::Mixed);
        std::fs::remove_dir_all(path.parent().unwrap()).unwrap();
    }

    #[test]
    fn malformed_unknown_and_future_configuration_fail_closed() {
        for contents in [
            "not-json",
            r#"{"resource_profile":"low"}"#,
            r#"{"version":1,"unknown":true}"#,
            r#"{"version":1,"version":1}"#,
            r#"{"version":1,"resource_profile":"low","resource_profile":"performance"}"#,
            r#"{"version":3}"#,
        ] {
            let path = config_file(contents);
            assert!(ProductConfig::load_from(Some(&path), None, None).is_err());
            std::fs::remove_dir_all(path.parent().unwrap()).unwrap();
        }
    }

    #[test]
    fn resource_profiles_lock_cardinality_ramp_and_budgets() {
        assert_eq!(
            ResourceProfile::Low.policy(),
            ScalingPolicy {
                control_interval_millis: 15_000,
                maximum_active_lanes: 4,
                maximum_admissions_per_interval: 1,
                maximum_drains_per_interval: 1,
                maximum_cpu_millicores: 1_000,
                maximum_memory_bytes: 1024 * 1024 * 1024,
            }
        );
        assert_eq!(ResourceProfile::Balanced.policy().maximum_active_lanes, 8);
        assert_eq!(
            ResourceProfile::Performance.policy().maximum_active_lanes,
            16
        );
        assert_eq!(MAX_CONFIG_BYTES, 64 * 1024);
    }

    #[test]
    fn version_two_validates_external_tor_and_resident_policy() {
        use std::os::unix::fs::PermissionsExt as _;

        let root = std::env::temp_dir().join(format!(
            "anonssh-config-v2-test-{}-{}",
            std::process::id(),
            NEXT_TEST.fetch_add(1, Ordering::Relaxed)
        ));
        std::fs::create_dir_all(&root).unwrap();
        let cookie = root.join("control-cookie");
        std::fs::write(&cookie, [0x5a_u8; 32]).unwrap();
        std::fs::set_permissions(&cookie, std::fs::Permissions::from_mode(0o600)).unwrap();
        let path = root.join("config.json");
        std::fs::write(
            &path,
            format!(
                r#"{{"version":2,"resource_profile":"low","external_tor_services":[{{"socks":"127.0.0.1:19050","control":"127.0.0.1:19150","cookie_file":"{}"}}],"resident_service":{{"maximum_sessions":7,"maximum_local_connections":21,"minimum_warm_slots_per_provider":0,"maximum_warm_slots_per_provider":2,"cache_quota_bytes":536870912,"state_quota_bytes":2147483648,"old_runtime_retention_seconds":172800}}}}"#,
                cookie.display()
            ),
        )
        .unwrap();
        let config = ProductConfig::load_from(Some(&path), None, None).unwrap();
        assert_eq!(config.external_tor_services().len(), 1);
        assert_eq!(config.resident_service_policy().maximum_sessions, 7);
        assert_eq!(
            config.resident_service_policy().maximum_local_connections,
            21
        );
        assert_eq!(config.report().external_tor_service_count, 1);
        assert_eq!(config.report().schema, "anonssh.product-config.v2");
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn version_two_rejects_unsafe_resident_limits() {
        for resident in [
            r#"{"maximum_sessions":0}"#,
            r#"{"maximum_sessions":8,"maximum_local_connections":7}"#,
            r#"{"minimum_warm_slots_per_provider":5,"maximum_warm_slots_per_provider":4}"#,
            r#"{"cache_quota_bytes":1}"#,
            r#"{"state_quota_bytes":1}"#,
            r#"{"old_runtime_retention_seconds":1}"#,
        ] {
            let path = config_file(&format!(r#"{{"version":2,"resident_service":{resident}}}"#));
            assert!(ProductConfig::load_from(Some(&path), None, None).is_err());
            std::fs::remove_dir_all(path.parent().unwrap()).unwrap();
        }
    }
}
