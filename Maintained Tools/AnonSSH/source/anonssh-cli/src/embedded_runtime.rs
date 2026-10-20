use std::collections::BTreeSet;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
use std::path::{Component, Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, SystemTime};

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::product_config::ResidentServicePolicy;
use crate::runtime::AppConfig;

const MAX_EMBEDDED_FILE_BYTES: usize = 256 * 1024 * 1024;
const MAX_STORAGE_ENTRIES: usize = 100_000;
const STORAGE_REPORT_SCHEMA: &str = "anonssh.storage-policy.v1";
static NEXT_TEMPORARY_FILE: AtomicU64 = AtomicU64::new(1);

mod payload {
    include!(concat!(env!("OUT_DIR"), "/embedded_router_runtime.rs"));
}

struct EmbeddedProgram {
    name: &'static str,
    version: &'static str,
    executable: &'static [u8],
    certificates: &'static [(&'static str, &'static [u8])],
}

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
pub struct StoragePolicyReport {
    pub schema: String,
    pub cache_bytes: u64,
    pub state_bytes: u64,
    pub cache_quota_bytes: u64,
    pub state_quota_bytes: u64,
    pub runtime_entries_removed: usize,
    pub runtime_bytes_removed: u64,
    pub cache_within_quota: bool,
    pub state_within_quota: bool,
}

pub fn materialize(name: &str) -> Result<Option<PathBuf>> {
    embedded_program(name)
        .map(|program| materialize_at(&AppConfig::new()?.cache_dir.join("runtime"), &program))
        .transpose()
}

fn embedded_program(name: &str) -> Option<EmbeddedProgram> {
    match name {
        "tor" => payload::TOR.map(|(version, executable)| EmbeddedProgram {
            name: "tor",
            version,
            executable,
            certificates: &[],
        }),
        "i2pd" => payload::I2PD.map(|(version, executable)| EmbeddedProgram {
            name: "i2pd",
            version,
            executable,
            certificates: payload::I2PD_CERTIFICATES,
        }),
        "ssh" => payload::SSH.map(|(version, executable)| EmbeddedProgram {
            name: "ssh",
            version,
            executable,
            certificates: &[],
        }),
        "dropbear" => payload::DROPBEAR.map(|(version, executable)| EmbeddedProgram {
            name: "dropbear",
            version,
            executable,
            certificates: &[],
        }),
        "sftp-server" => payload::SFTP_SERVER.map(|(version, executable)| EmbeddedProgram {
            name: "sftp-server",
            version,
            executable,
            certificates: &[],
        }),
        "scp" => payload::SCP.map(|(version, executable)| EmbeddedProgram {
            name: "scp",
            version,
            executable,
            certificates: &[],
        }),
        _ => None,
    }
}

pub fn versions() -> [Option<&'static str>; 6] {
    [
        payload::TOR.map(|(version, _)| version),
        payload::I2PD.map(|(version, _)| version),
        payload::SSH.map(|(version, _)| version),
        payload::DROPBEAR.map(|(version, _)| version),
        payload::SFTP_SERVER.map(|(version, _)| version),
        payload::SCP.map(|(version, _)| version),
    ]
}

pub fn enforce_storage_policy(
    config: &AppConfig,
    policy: ResidentServicePolicy,
) -> Result<StoragePolicyReport> {
    let runtime = config.cache_dir.join("runtime");
    let protected = ["tor", "i2pd", "ssh", "dropbear", "sftp-server", "scp"]
        .into_iter()
        .filter_map(embedded_program)
        .map(|program| runtime_root_name(&program))
        .collect::<BTreeSet<_>>();
    let (runtime_entries_removed, runtime_bytes_removed) = collect_runtime_cache(
        &config.cache_dir,
        &runtime,
        &protected,
        policy.cache_quota_bytes,
        Duration::from_secs(policy.old_runtime_retention_seconds),
        SystemTime::now(),
    )?;
    let cache_bytes = directory_bytes(&config.cache_dir)?;
    if cache_bytes > policy.cache_quota_bytes {
        bail!(
            "AnonSSH cache uses {cache_bytes} bytes after safe cleanup, exceeding its {} byte quota",
            policy.cache_quota_bytes
        );
    }
    let state_bytes = directory_bytes(&config.state_dir)?;
    Ok(StoragePolicyReport {
        schema: STORAGE_REPORT_SCHEMA.to_owned(),
        cache_bytes,
        state_bytes,
        cache_quota_bytes: policy.cache_quota_bytes,
        state_quota_bytes: policy.state_quota_bytes,
        runtime_entries_removed,
        runtime_bytes_removed,
        cache_within_quota: true,
        state_within_quota: state_bytes <= policy.state_quota_bytes,
    })
}

pub fn state_within_quota(config: &AppConfig, policy: ResidentServicePolicy) -> Result<bool> {
    Ok(directory_bytes(&config.state_dir)? <= policy.state_quota_bytes)
}

fn runtime_root_name(program: &EmbeddedProgram) -> String {
    let digest = digest(program.executable);
    format!(
        "{}-{}-{}",
        program.name,
        program.version,
        encode_hex(&digest[..16])
    )
}

fn collect_runtime_cache(
    cache_root: &Path,
    runtime_root: &Path,
    protected: &BTreeSet<String>,
    cache_quota_bytes: u64,
    retention: Duration,
    now: SystemTime,
) -> Result<(usize, u64)> {
    let metadata = match fs::symlink_metadata(runtime_root) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok((0, 0)),
        Err(error) => return Err(error.into()),
    };
    if !metadata.is_dir() || metadata.file_type().is_symlink() {
        bail!("embedded runtime cache is not a real directory");
    }
    let mut candidates = Vec::new();
    for entry in fs::read_dir(runtime_root)? {
        let entry = entry?;
        let name = entry
            .file_name()
            .into_string()
            .map_err(|_| anyhow::anyhow!("embedded runtime cache name is not UTF-8"))?;
        let metadata = fs::symlink_metadata(entry.path())?;
        if metadata.file_type().is_symlink() || !metadata.is_dir() {
            bail!("embedded runtime cache contains an unsafe entry");
        }
        if !["tor-", "i2pd-", "ssh-", "dropbear-", "sftp-server-", "scp-"]
            .iter()
            .any(|prefix| name.starts_with(prefix))
        {
            bail!("embedded runtime cache contains an unknown entry");
        }
        if protected.contains(&name) {
            continue;
        }
        let modified = metadata.modified()?;
        candidates.push((entry.path(), modified, directory_bytes(&entry.path())?));
        if candidates.len() > MAX_STORAGE_ENTRIES {
            bail!("embedded runtime cache contains too many entries");
        }
    }
    candidates.sort_by_key(|(_, modified, _)| *modified);
    let mut removed = 0_usize;
    let mut removed_bytes = 0_u64;
    for (path, modified, bytes) in &candidates {
        if now.duration_since(*modified).unwrap_or(Duration::ZERO) >= retention {
            remove_runtime_entry(runtime_root, path)?;
            removed = removed.saturating_add(1);
            removed_bytes = removed_bytes.saturating_add(*bytes);
        }
    }
    let mut cache_bytes = directory_bytes(cache_root)?;
    if cache_bytes > cache_quota_bytes {
        for (path, _, bytes) in candidates {
            if !path.exists() {
                continue;
            }
            remove_runtime_entry(runtime_root, &path)?;
            removed = removed.saturating_add(1);
            removed_bytes = removed_bytes.saturating_add(bytes);
            cache_bytes = directory_bytes(cache_root)?;
            if cache_bytes <= cache_quota_bytes {
                break;
            }
        }
    }
    Ok((removed, removed_bytes))
}

fn remove_runtime_entry(runtime_root: &Path, entry: &Path) -> Result<()> {
    let metadata = fs::symlink_metadata(entry)?;
    if metadata.file_type().is_symlink()
        || !metadata.is_dir()
        || entry.parent() != Some(runtime_root)
    {
        bail!("refusing to remove an unsafe runtime cache entry");
    }
    fs::remove_dir_all(entry).with_context(|| {
        format!(
            "failed to remove old runtime cache entry {}",
            entry.display()
        )
    })
}

fn directory_bytes(root: &Path) -> Result<u64> {
    let metadata = match fs::symlink_metadata(root) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(0),
        Err(error) => return Err(error.into()),
    };
    if metadata.file_type().is_symlink() || !metadata.is_dir() {
        bail!("AnonSSH storage root is not a real directory");
    }
    let mut bytes = 0_u64;
    let mut entries = 0_usize;
    let mut pending = vec![root.to_owned()];
    while let Some(directory) = pending.pop() {
        for entry in fs::read_dir(directory)? {
            let entry = entry?;
            entries = entries.saturating_add(1);
            if entries > MAX_STORAGE_ENTRIES {
                bail!("AnonSSH storage contains too many entries");
            }
            let metadata = fs::symlink_metadata(entry.path())?;
            if metadata.file_type().is_symlink() {
                bail!("AnonSSH storage contains a symbolic link");
            }
            if metadata.is_dir() {
                pending.push(entry.path());
            } else if metadata.is_file() {
                bytes = bytes.saturating_add(metadata.len());
            } else {
                bail!("AnonSSH storage contains an unsupported filesystem object");
            }
        }
    }
    Ok(bytes)
}

fn materialize_at(cache: &Path, program: &EmbeddedProgram) -> Result<PathBuf> {
    validate_version(program.version)?;
    if program.executable.is_empty() || program.executable.len() > MAX_EMBEDDED_FILE_BYTES {
        bail!("embedded {} executable has an invalid size", program.name);
    }
    let root = cache.join(runtime_root_name(program));
    if !cache.exists() {
        fs::create_dir_all(cache)?;
        fs::set_permissions(cache, fs::Permissions::from_mode(0o700))?;
    }
    ensure_private_directory(cache)?;
    ensure_private_directory(&root)?;
    let bin = root.join("bin");
    ensure_private_directory(&bin)?;
    let executable = bin.join(program.name);
    materialize_file(&executable, program.executable, 0o500)?;

    if !program.certificates.is_empty() {
        let certificates = root.join("share/i2pd/certificates");
        ensure_private_directory(&root.join("share"))?;
        ensure_private_directory(&root.join("share/i2pd"))?;
        ensure_private_directory(&certificates)?;
        for (relative, bytes) in program.certificates {
            if bytes.is_empty() || bytes.len() > MAX_EMBEDDED_FILE_BYTES {
                bail!("embedded certificate has an invalid size");
            }
            let relative = safe_relative_path(relative)?;
            let destination = certificates.join(relative);
            if let Some(parent) = destination.parent() {
                ensure_private_directory_tree(&certificates, parent)?;
            }
            materialize_file(&destination, bytes, 0o400)?;
        }
    }
    Ok(executable)
}

fn validate_version(version: &str) -> Result<()> {
    if version.is_empty()
        || !version
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'-' | b'_'))
    {
        bail!("embedded router version is unsafe");
    }
    Ok(())
}

fn safe_relative_path(value: &str) -> Result<PathBuf> {
    let path = Path::new(value);
    if value.is_empty()
        || path.is_absolute()
        || !path
            .components()
            .all(|component| matches!(component, Component::Normal(_)))
    {
        bail!("embedded certificate path is unsafe");
    }
    Ok(path.to_owned())
}

fn ensure_private_directory_tree(root: &Path, directory: &Path) -> Result<()> {
    let relative = directory
        .strip_prefix(root)
        .context("embedded certificate escaped its root")?;
    let mut current = root.to_owned();
    for component in relative.components() {
        let Component::Normal(component) = component else {
            bail!("embedded certificate directory is unsafe");
        };
        current.push(component);
        ensure_private_directory(&current)?;
    }
    Ok(())
}

fn ensure_private_directory(path: &Path) -> Result<()> {
    match fs::create_dir(path) {
        Ok(()) => fs::set_permissions(path, fs::Permissions::from_mode(0o700))?,
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
        Err(error) => return Err(error.into()),
    }
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() {
        bail!("embedded runtime directory is not a real directory");
    }
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("embedded runtime directory is accessible by another user");
    }
    Ok(())
}

fn materialize_file(path: &Path, bytes: &[u8], mode: u32) -> Result<()> {
    if path.exists() {
        return validate_materialized_file(path, bytes, mode);
    }
    let temporary = path.with_extension(format!(
        "tmp-{}-{}",
        std::process::id(),
        NEXT_TEMPORARY_FILE.fetch_add(1, Ordering::Relaxed)
    ));
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .mode(mode)
        .open(&temporary)
        .with_context(|| format!("failed to create {}", temporary.display()))?;
    let operation = (|| -> Result<()> {
        file.write_all(bytes)?;
        file.sync_all()?;
        drop(file);
        match fs::hard_link(&temporary, path) {
            Ok(()) => {}
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
            Err(error) => return Err(error.into()),
        }
        validate_materialized_file(path, bytes, mode)
    })();
    let _ = fs::remove_file(&temporary);
    operation
}

fn validate_materialized_file(path: &Path, bytes: &[u8], mode: u32) -> Result<()> {
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.file_type().is_file() || metadata.file_type().is_symlink() {
        bail!("embedded runtime payload is not a regular file");
    }
    if metadata.len() != u64::try_from(bytes.len()).expect("embedded payload length fits u64")
        || digest(&fs::read(path)?) != digest(bytes)
    {
        bail!("embedded runtime payload failed digest validation");
    }
    if metadata.permissions().mode() & 0o777 != mode {
        bail!("embedded runtime payload has unsafe permissions");
    }
    Ok(())
}

fn digest(bytes: &[u8]) -> [u8; 32] {
    Sha256::digest(bytes).into()
}

fn encode_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut encoded = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        encoded.push(char::from(HEX[usize::from(byte >> 4)]));
        encoded.push(char::from(HEX[usize::from(byte & 0x0f)]));
    }
    encoded
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;
    use std::os::unix::fs::symlink;
    use std::time::{Duration, SystemTime};

    use super::{collect_runtime_cache, directory_bytes, materialize_at, EmbeddedProgram};

    #[test]
    fn extraction_is_content_addressed_idempotent_and_fail_closed() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-embedded-runtime-test-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&root);
        let program = EmbeddedProgram {
            name: "i2pd",
            version: "2.61.0",
            executable: b"router-executable",
            certificates: &[
                ("reseed/example.crt", b"reseed"),
                ("family/a.crt", b"family"),
            ],
        };
        let first = materialize_at(&root, &program).unwrap();
        let second = materialize_at(&root, &program).unwrap();
        assert_eq!(first, second);
        assert_eq!(std::fs::read(&first).unwrap(), program.executable);
        let prefix = first.parent().unwrap().parent().unwrap();
        assert_eq!(
            std::fs::read(prefix.join("share/i2pd/certificates/reseed/example.crt")).unwrap(),
            b"reseed"
        );

        use std::os::unix::fs::PermissionsExt as _;
        std::fs::set_permissions(&first, std::fs::Permissions::from_mode(0o700)).unwrap();
        std::fs::write(&first, b"corrupt").unwrap();
        assert!(materialize_at(&root, &program).is_err());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn extraction_rejects_a_symlink_payload() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-embedded-runtime-symlink-test-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&root);
        let program = EmbeddedProgram {
            name: "ssh",
            version: "1",
            executable: b"client-executable",
            certificates: &[],
        };
        let executable = materialize_at(&root, &program).unwrap();
        std::fs::remove_file(&executable).unwrap();
        symlink("/bin/true", &executable).unwrap();
        assert!(materialize_at(&root, &program).is_err());
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn unsafe_versions_and_certificate_paths_are_rejected() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-embedded-runtime-invalid-test-{}",
            std::process::id()
        ));
        let invalid_version = EmbeddedProgram {
            name: "tor",
            version: "../tor",
            executable: b"router",
            certificates: &[],
        };
        assert!(materialize_at(&root, &invalid_version).is_err());
        let invalid_certificate = EmbeddedProgram {
            name: "i2pd",
            version: "1",
            executable: b"router",
            certificates: &[("../escape", b"bad")],
        };
        assert!(materialize_at(&root, &invalid_certificate).is_err());
        let _ = std::fs::remove_dir_all(&root);
    }

    #[test]
    fn runtime_collection_preserves_current_payloads_and_removes_only_runtime_entries() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-runtime-collection-test-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&root);
        let runtime = root.join("runtime");
        let current = runtime.join("tor-current-digest");
        let old = runtime.join("i2pd-old-digest");
        std::fs::create_dir_all(current.join("bin")).unwrap();
        std::fs::create_dir_all(old.join("bin")).unwrap();
        std::fs::write(current.join("bin/tor"), [1_u8; 32]).unwrap();
        std::fs::write(old.join("bin/i2pd"), [2_u8; 64]).unwrap();
        let protected = BTreeSet::from(["tor-current-digest".to_owned()]);
        let report = collect_runtime_cache(
            &root,
            &runtime,
            &protected,
            u64::MAX,
            Duration::ZERO,
            SystemTime::now(),
        )
        .unwrap();
        assert_eq!(report, (1, 64));
        assert!(current.exists());
        assert!(!old.exists());
        assert_eq!(directory_bytes(&root).unwrap(), 32);
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn storage_walk_and_runtime_collection_reject_links() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-runtime-collection-link-test-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&root);
        let runtime = root.join("runtime");
        std::fs::create_dir_all(&runtime).unwrap();
        symlink("/tmp", runtime.join("tor-unsafe-digest")).unwrap();
        assert!(collect_runtime_cache(
            &root,
            &runtime,
            &BTreeSet::new(),
            u64::MAX,
            Duration::ZERO,
            SystemTime::now(),
        )
        .is_err());
        assert!(directory_bytes(&root).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }
}
