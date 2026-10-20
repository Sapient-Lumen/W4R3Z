use std::collections::BTreeMap;
use std::fs;
use std::os::unix::fs::{FileTypeExt, MetadataExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::sync::Arc;

use anyhow::{bail, Context, Result};
use tokio::net::UnixStream;
use tokio::sync::{OwnedSemaphorePermit, Semaphore, TryAcquireError};

use crate::application_service::{ServiceName, SSH_SERVICE};

const DEFAULT_SERVICE_CONCURRENCY: usize = 16;

#[derive(Clone, Default)]
pub struct NativeServiceRegistry {
    services: BTreeMap<ServiceName, NativeService>,
}

#[derive(Clone)]
struct NativeService {
    path: PathBuf,
    permits: Arc<Semaphore>,
}

pub struct NativeServiceConnection {
    pub stream: UnixStream,
    _permit: OwnedSemaphorePermit,
}

#[derive(Debug)]
pub enum NativeServiceDialError {
    Unknown,
    Capacity,
    Unavailable(anyhow::Error),
}

impl NativeServiceRegistry {
    pub fn parse(specifications: &[String]) -> Result<Self> {
        let mut services = BTreeMap::new();
        for specification in specifications {
            let (name, path) = specification
                .split_once('=')
                .context("native service must be NAME=/ABSOLUTE/SOCKET")?;
            let name = ServiceName::parse(name)?;
            if name.as_str() == SSH_SERVICE {
                bail!("native service name 'ssh' is reserved");
            }
            let path = PathBuf::from(path);
            validate_service_socket(&path)?;
            if services
                .insert(
                    name.clone(),
                    NativeService {
                        path,
                        permits: Arc::new(Semaphore::new(DEFAULT_SERVICE_CONCURRENCY)),
                    },
                )
                .is_some()
            {
                bail!(
                    "native service '{}' was configured more than once",
                    name.as_str()
                );
            }
        }
        Ok(Self { services })
    }

    pub async fn connect(
        &self,
        name: &ServiceName,
    ) -> std::result::Result<NativeServiceConnection, NativeServiceDialError> {
        let service = self
            .services
            .get(name)
            .ok_or(NativeServiceDialError::Unknown)?;
        let permit = service
            .permits
            .clone()
            .try_acquire_owned()
            .map_err(|error| match error {
                TryAcquireError::NoPermits | TryAcquireError::Closed => {
                    NativeServiceDialError::Capacity
                }
            })?;
        validate_service_socket(&service.path).map_err(NativeServiceDialError::Unavailable)?;
        let stream = UnixStream::connect(&service.path)
            .await
            .with_context(|| format!("failed to connect native service '{}'", name.as_str()))
            .map_err(NativeServiceDialError::Unavailable)?;
        validate_service_peer(&stream).map_err(NativeServiceDialError::Unavailable)?;
        Ok(NativeServiceConnection {
            stream,
            _permit: permit,
        })
    }
}

fn validate_service_peer(stream: &UnixStream) -> Result<()> {
    let credentials = stream
        .peer_cred()
        .context("failed to authenticate native service peer credentials")?;
    if credentials.uid() != unsafe { libc::geteuid() } {
        bail!("native service peer is not owned by the AnonSSH server user");
    }
    Ok(())
}

fn validate_service_socket(path: &Path) -> Result<()> {
    if !path.is_absolute() {
        bail!("native service socket path must be absolute");
    }
    let metadata = fs::symlink_metadata(path).context("native service socket is unavailable")?;
    if !metadata.file_type().is_socket() {
        bail!("native service path is not a Unix socket");
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("native service socket is not owned by the AnonSSH server user");
    }
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("native service socket must not grant group or other permissions");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::sync::atomic::{AtomicU64, Ordering};

    use tokio::net::UnixListener;

    use super::*;

    static SEQUENCE: AtomicU64 = AtomicU64::new(1);

    fn temporary_path(label: &str) -> PathBuf {
        std::env::temp_dir().join(format!(
            "anonssh-native-service-{label}-{}-{}",
            std::process::id(),
            SEQUENCE.fetch_add(1, Ordering::Relaxed)
        ))
    }

    #[tokio::test]
    async fn registry_connects_only_to_owner_private_sockets() {
        let path = temporary_path("valid");
        let listener = UnixListener::bind(&path).unwrap();
        fs::set_permissions(&path, fs::Permissions::from_mode(0o600)).unwrap();
        let registry = NativeServiceRegistry::parse(&[format!("echo={}", path.display())]).unwrap();
        let connection = registry
            .connect(&ServiceName::parse("echo").unwrap())
            .await
            .unwrap();
        let _ = listener.accept().await.unwrap();
        drop(connection);
        drop(listener);
        fs::remove_file(path).unwrap();
    }

    #[tokio::test]
    async fn registry_revalidates_replaced_paths_and_rejects_symlinks() {
        let path = temporary_path("replace");
        let target = temporary_path("target");
        let listener = UnixListener::bind(&path).unwrap();
        fs::set_permissions(&path, fs::Permissions::from_mode(0o600)).unwrap();
        let registry = NativeServiceRegistry::parse(&[format!("echo={}", path.display())]).unwrap();
        drop(listener);
        fs::remove_file(&path).unwrap();
        let target_listener = UnixListener::bind(&target).unwrap();
        fs::set_permissions(&target, fs::Permissions::from_mode(0o600)).unwrap();
        std::os::unix::fs::symlink(&target, &path).unwrap();
        assert!(matches!(
            registry.connect(&ServiceName::parse("echo").unwrap()).await,
            Err(NativeServiceDialError::Unavailable(_))
        ));
        fs::remove_file(path).unwrap();
        drop(target_listener);
        fs::remove_file(target).unwrap();
    }

    #[test]
    fn registry_rejects_reserved_duplicate_and_non_socket_entries() {
        let file = temporary_path("file");
        fs::write(&file, b"not a socket").unwrap();
        assert!(NativeServiceRegistry::parse(&[format!("ssh={}", file.display())]).is_err());
        assert!(NativeServiceRegistry::parse(&[format!("echo={}", file.display())]).is_err());
        fs::remove_file(file).unwrap();
    }
}
