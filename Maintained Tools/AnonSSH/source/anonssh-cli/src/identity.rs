use std::fmt;
use std::fs::OpenOptions;
use std::io::Read;
use std::os::unix::fs::{MetadataExt, OpenOptionsExt, PermissionsExt};
use std::path::Path;

use anonssh_bond::MAX_TOPOLOGY_DESCRIPTORS;
use anyhow::{bail, Context, Result};
use argon2::Argon2;
use data_encoding::{Specification, BASE32_NOPAD, BASE64};
use ed25519_dalek::{hazmat::ExpandedSecretKey, SigningKey, VerifyingKey};
use sha2::{Digest, Sha256, Sha512};
use sha3::Sha3_256;
use ssh_key::{private::Ed25519Keypair, LineEnding, PrivateKey};
use zeroize::{Zeroize, Zeroizing};

/// The SSH target assembled by AnonSSH.
pub struct HostRecord {
    pub name: Zeroizing<String>,
    pub user: Zeroizing<String>,
    pub port: u16,
}

#[derive(Clone, PartialEq, Eq)]
pub struct DerivedI2pIdentity {
    pub destination: String,
    pub private_key: Zeroizing<String>,
}

impl fmt::Debug for DerivedI2pIdentity {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter
            .debug_struct("DerivedI2pIdentity")
            .field("destination", &self.destination)
            .field("private_key", &"[REDACTED]")
            .finish()
    }
}

pub struct DerivedTorServiceIdentity {
    pub destination: String,
    pub control_private_key: Zeroizing<String>,
}

pub struct DerivedSshClientIdentity {
    pub public_key: String,
    pub private_key: Zeroizing<String>,
}

pub struct DerivedSshHostIdentity {
    pub public_key: String,
    pub dropbear_private_key: Zeroizing<Vec<u8>>,
}

pub struct DerivedClientRecoveryIdentity {
    pub i2p: DerivedI2pIdentity,
    pub i2p_pool: Vec<DerivedI2pIdentity>,
    pub tor_destination: String,
    pub tor_pool_destinations: Vec<String>,
    pub ssh_host_public_key: String,
    pub ssh_client: DerivedSshClientIdentity,
    pub bond_session_key: Zeroizing<[u8; 32]>,
}

pub struct DerivedServerRecoveryIdentity {
    pub i2p: DerivedI2pIdentity,
    pub i2p_pool: Vec<DerivedI2pIdentity>,
    pub tor: DerivedTorServiceIdentity,
    pub tor_pool: Vec<DerivedTorServiceIdentity>,
    pub ssh_host: DerivedSshHostIdentity,
    pub ssh_client_public_key: String,
    pub bond_session_key: Zeroizing<[u8; 32]>,
}

pub struct IdentityManager;

const ARGON2_MEMORY_KIB: u32 = 65_536;
const ARGON2_ITERATIONS: u32 = 3;
const ARGON2_LANES: u32 = 4;
pub const RECOVERY_TOR_POOL_SLOTS: u32 = 8;
pub const RECOVERY_I2P_POOL_SLOTS: u32 = 8;
const MAX_PASSPHRASE_FILE_BYTES: u64 = 64 * 1024;

impl IdentityManager {
    pub fn prompt_passphrase(prompt: &str) -> Result<Zeroizing<String>> {
        let passphrase = match std::env::var("ANONSSH_PASSPHRASE") {
            Ok(passphrase) => passphrase,
            Err(std::env::VarError::NotUnicode(_)) => bail!("ANONSSH_PASSPHRASE is not UTF-8"),
            Err(std::env::VarError::NotPresent) => match std::env::var("ANONSSH_PASSPHRASE_FILE") {
                Ok(path) => normalize_passphrase_file(read_passphrase_file(Path::new(&path))?),
                Err(std::env::VarError::NotUnicode(_)) => {
                    bail!("ANONSSH_PASSPHRASE_FILE is not UTF-8")
                }
                Err(std::env::VarError::NotPresent) => rpassword::prompt_password(prompt)?,
            },
        };
        if passphrase.is_empty() {
            bail!("identity password must not be empty");
        }
        Ok(Zeroizing::new(passphrase))
    }

    /// This KDF is the root of password-plus-machine-ID recovery. Its parameters and
    /// domain must remain stable for version 1 identities.
    pub fn derive_master_seed(
        password: &Zeroizing<String>,
        machine_id: &str,
    ) -> Result<Zeroizing<[u8; 32]>> {
        if password.is_empty() {
            bail!("identity password must not be empty");
        }
        let domain = format!("anonssh:v1:{machine_id}");
        let mut seed = Zeroizing::new([0_u8; 32]);
        Self::argon2id(password.as_bytes(), domain.as_bytes(), &mut seed)?;
        Ok(seed)
    }

    pub fn derive_client_recovery_identity(
        password: &Zeroizing<String>,
        machine_id: &str,
    ) -> Result<DerivedClientRecoveryIdentity> {
        Self::derive_client_recovery_identity_with_pool_slots(
            password,
            machine_id,
            RECOVERY_TOR_POOL_SLOTS,
            RECOVERY_I2P_POOL_SLOTS,
        )
    }

    pub(crate) fn derive_client_recovery_identity_with_pool_slots(
        password: &Zeroizing<String>,
        machine_id: &str,
        tor_slots: u32,
        i2p_slots: u32,
    ) -> Result<DerivedClientRecoveryIdentity> {
        Self::validate_recovery_pool_slots(tor_slots, i2p_slots)?;
        let master_seed = Self::derive_master_seed(password, machine_id)?;
        Self::derive_client_recovery_identity_from_master(&master_seed, tor_slots, i2p_slots)
    }

    fn derive_client_recovery_identity_from_master(
        master_seed: &[u8; 32],
        tor_slots: u32,
        i2p_slots: u32,
    ) -> Result<DerivedClientRecoveryIdentity> {
        let ssh_client = Self::derive_ssh_client_identity_from_master(master_seed)?;
        Ok(DerivedClientRecoveryIdentity {
            i2p: Self::derive_i2p_identity_from_master(master_seed)?,
            i2p_pool: Self::derive_i2p_pool_from_master(master_seed, i2p_slots)?,
            tor_destination: Self::derive_tor_destination_from_master(master_seed),
            tor_pool_destinations: Self::derive_tor_pool_from_master(master_seed, tor_slots)
                .into_iter()
                .map(|identity| identity.destination)
                .collect(),
            ssh_host_public_key: Self::derive_ssh_public_key(master_seed, b"ssh-host-ed25519-v1")?,
            ssh_client,
            bond_session_key: Zeroizing::new(Self::derive_subseed(
                master_seed,
                b"bond-session-auth-v1",
            )),
        })
    }

    pub fn derive_server_recovery_identity(
        password: &Zeroizing<String>,
        machine_id: &str,
    ) -> Result<DerivedServerRecoveryIdentity> {
        Self::derive_server_recovery_identity_with_pool_slots(
            password,
            machine_id,
            RECOVERY_TOR_POOL_SLOTS,
            RECOVERY_I2P_POOL_SLOTS,
        )
    }

    pub(crate) fn derive_server_recovery_identity_with_pool_slots(
        password: &Zeroizing<String>,
        machine_id: &str,
        tor_slots: u32,
        i2p_slots: u32,
    ) -> Result<DerivedServerRecoveryIdentity> {
        Self::validate_recovery_pool_slots(tor_slots, i2p_slots)?;
        let master_seed = Self::derive_master_seed(password, machine_id)?;
        Self::derive_server_recovery_identity_from_master(&master_seed, tor_slots, i2p_slots)
    }

    fn derive_server_recovery_identity_from_master(
        master_seed: &[u8; 32],
        tor_slots: u32,
        i2p_slots: u32,
    ) -> Result<DerivedServerRecoveryIdentity> {
        Ok(DerivedServerRecoveryIdentity {
            i2p: Self::derive_i2p_identity_from_master(master_seed)?,
            i2p_pool: Self::derive_i2p_pool_from_master(master_seed, i2p_slots)?,
            tor: Self::derive_tor_service_identity_from_master(master_seed),
            tor_pool: Self::derive_tor_pool_from_master(master_seed, tor_slots),
            ssh_host: Self::derive_ssh_host_identity_from_master(master_seed)?,
            ssh_client_public_key: Self::derive_ssh_public_key(
                master_seed,
                b"ssh-client-auth-ed25519-v1",
            )?,
            bond_session_key: Zeroizing::new(Self::derive_subseed(
                master_seed,
                b"bond-session-auth-v1",
            )),
        })
    }

    fn validate_recovery_pool_slots(tor_slots: u32, i2p_slots: u32) -> Result<()> {
        let total = tor_slots
            .checked_add(i2p_slots)
            .context("recovery pool lane count overflow")?;
        if total == 0 {
            bail!("recovery pool requires at least one provider slot");
        }
        let total = usize::try_from(total).context("recovery pool lane count is unsupported")?;
        if total > MAX_TOPOLOGY_DESCRIPTORS {
            bail!(
                "recovery pool requests {total} lanes but the maximum is {MAX_TOPOLOGY_DESCRIPTORS}"
            );
        }
        Ok(())
    }

    pub fn derive_i2p_pool_identity(
        password: &Zeroizing<String>,
        machine_id: &str,
        slot: u32,
    ) -> Result<DerivedI2pIdentity> {
        if slot == 0 {
            bail!("I2P pool slot must be non-zero");
        }
        let master_seed = Self::derive_master_seed(password, machine_id)?;
        Self::derive_i2p_pool_identity_from_master(&master_seed, slot)
    }

    #[cfg(test)]
    pub fn derive_tor_pool_identity(
        password: &Zeroizing<String>,
        machine_id: &str,
        slot: u32,
    ) -> Result<DerivedTorServiceIdentity> {
        if slot == 0 {
            bail!("Tor pool slot must be non-zero");
        }
        let master_seed = Self::derive_master_seed(password, machine_id)?;
        Ok(Self::derive_tor_pool_identity_from_master(
            &master_seed,
            slot,
        ))
    }

    fn derive_tor_pool_from_master(
        master_seed: &[u8; 32],
        slots: u32,
    ) -> Vec<DerivedTorServiceIdentity> {
        (1..=slots)
            .map(|slot| Self::derive_tor_pool_identity_from_master(master_seed, slot))
            .collect()
    }

    fn derive_tor_pool_identity_from_master(
        master_seed: &[u8; 32],
        slot: u32,
    ) -> DerivedTorServiceIdentity {
        if slot == 1 {
            return Self::derive_tor_service_identity_from_master(master_seed);
        }
        let mut label = b"tor-bond-router-v1\0".to_vec();
        label.extend_from_slice(&slot.to_be_bytes());
        let pool_seed = Zeroizing::new(Self::derive_subseed(master_seed, &label));
        Self::derive_tor_service_identity_from_master(&pool_seed)
    }

    fn derive_i2p_pool_from_master(
        master_seed: &[u8; 32],
        slots: u32,
    ) -> Result<Vec<DerivedI2pIdentity>> {
        (1..=slots)
            .map(|slot| Self::derive_i2p_pool_identity_from_master(master_seed, slot))
            .collect()
    }

    fn derive_i2p_pool_identity_from_master(
        master_seed: &[u8; 32],
        slot: u32,
    ) -> Result<DerivedI2pIdentity> {
        let mut label = b"i2p-bond-router-v1\0".to_vec();
        label.extend_from_slice(&slot.to_be_bytes());
        let pool_seed = Zeroizing::new(Self::derive_subseed(master_seed, &label));
        Self::derive_i2p_identity_from_master(&pool_seed)
    }

    fn derive_i2p_identity_from_master(master_seed: &[u8; 32]) -> Result<DerivedI2pIdentity> {
        let signing_seed =
            Zeroizing::new(Self::derive_subseed(master_seed, b"i2p-signing-ed25519-v1"));
        let signing_public = SigningKey::from_bytes(&signing_seed)
            .verifying_key()
            .to_bytes();

        // I2P permits random-compressible data in the unused ElGamal encryption-key
        // field. Deterministic fill keeps the complete KeysAndCert blob recoverable.
        let public_fill = Self::repeat_subseed(master_seed, b"i2p-public-fill-v1", 256);
        let padding_fill = Self::repeat_subseed(master_seed, b"i2p-padding-fill-v1", 96);
        let private_fill = Self::repeat_subseed(master_seed, b"i2p-private-fill-v1", 256);

        let mut destination_bytes = Vec::with_capacity(391);
        destination_bytes.extend_from_slice(&public_fill);
        destination_bytes.extend_from_slice(&padding_fill);
        destination_bytes.extend_from_slice(&signing_public);
        destination_bytes.extend_from_slice(&[5, 0, 4, 0, 7, 0, 0]);

        let destination_hash = Sha256::digest(&destination_bytes);
        let destination = format!(
            "i2p://{}.b32.i2p",
            BASE32_NOPAD.encode(&destination_hash).to_ascii_lowercase()
        );

        let mut private_key_bytes = Vec::with_capacity(destination_bytes.len() + 288);
        private_key_bytes.extend_from_slice(&destination_bytes);
        private_key_bytes.extend_from_slice(&private_fill);
        private_key_bytes.extend_from_slice(&signing_seed[..]);

        Ok(DerivedI2pIdentity {
            destination,
            private_key: Zeroizing::new(Self::i2p_base64_encode(&private_key_bytes)),
        })
    }

    fn derive_tor_destination_from_master(master_seed: &[u8; 32]) -> String {
        Self::derive_tor_material_from_master(master_seed).0
    }

    fn derive_tor_service_identity_from_master(
        master_seed: &[u8; 32],
    ) -> DerivedTorServiceIdentity {
        let (destination, expanded) = Self::derive_tor_material_from_master(master_seed);
        DerivedTorServiceIdentity {
            destination,
            control_private_key: Zeroizing::new(BASE64.encode(&expanded[..])),
        }
    }

    fn derive_tor_material_from_master(master_seed: &[u8; 32]) -> (String, Zeroizing<[u8; 64]>) {
        let seed = Zeroizing::new(Self::derive_subseed(master_seed, b"tor-onion-ed25519-v1"));
        let mut digest = Sha512::digest(&seed[..]);
        let mut expanded = Zeroizing::new([0_u8; 64]);
        expanded.copy_from_slice(&digest);
        digest.as_mut_slice().zeroize();
        expanded[0] &= 248;
        expanded[31] &= 63;
        expanded[31] |= 64;

        let public_key = VerifyingKey::from(&ExpandedSecretKey::from_bytes(&expanded)).to_bytes();
        let version = [3_u8];
        let mut checksum_hasher = Sha3_256::new();
        checksum_hasher.update(b".onion checksum");
        checksum_hasher.update(public_key);
        checksum_hasher.update(version);
        let checksum = checksum_hasher.finalize();

        let mut address = [0_u8; 35];
        address[..32].copy_from_slice(&public_key);
        address[32..34].copy_from_slice(&checksum[..2]);
        address[34] = version[0];
        let service_id = BASE32_NOPAD.encode(&address).to_ascii_lowercase();
        (format!("tor://{service_id}.onion"), expanded)
    }

    fn derive_ssh_client_identity_from_master(
        master_seed: &[u8; 32],
    ) -> Result<DerivedSshClientIdentity> {
        let seed = Zeroizing::new(Self::derive_subseed(
            master_seed,
            b"ssh-client-auth-ed25519-v1",
        ));
        let private_key = PrivateKey::from(Ed25519Keypair::from_seed(&seed));
        let public_key = private_key
            .public_key()
            .to_openssh()
            .context("failed to encode derived SSH client public key")?;
        let private_key = private_key
            .to_openssh(LineEnding::LF)
            .context("failed to encode derived SSH client private key")?;
        Ok(DerivedSshClientIdentity {
            public_key,
            private_key,
        })
    }

    fn derive_ssh_host_identity_from_master(
        master_seed: &[u8; 32],
    ) -> Result<DerivedSshHostIdentity> {
        let seed = Zeroizing::new(Self::derive_subseed(master_seed, b"ssh-host-ed25519-v1"));
        let public = SigningKey::from_bytes(&seed).verifying_key().to_bytes();
        let public_key = Self::derive_ssh_public_key(master_seed, b"ssh-host-ed25519-v1")?;

        let mut private_and_public = Zeroizing::new([0_u8; 64]);
        private_and_public[..32].copy_from_slice(&seed[..]);
        private_and_public[32..].copy_from_slice(&public);
        let mut dropbear_private_key = Vec::with_capacity(83);
        Self::append_ssh_string(&mut dropbear_private_key, b"ssh-ed25519");
        Self::append_ssh_string(&mut dropbear_private_key, &private_and_public[..]);

        Ok(DerivedSshHostIdentity {
            public_key,
            dropbear_private_key: Zeroizing::new(dropbear_private_key),
        })
    }

    fn derive_ssh_public_key(master_seed: &[u8; 32], label: &[u8]) -> Result<String> {
        let seed = Zeroizing::new(Self::derive_subseed(master_seed, label));
        PrivateKey::from(Ed25519Keypair::from_seed(&seed))
            .public_key()
            .to_openssh()
            .context("failed to encode derived SSH public key")
    }

    fn append_ssh_string(output: &mut Vec<u8>, value: &[u8]) {
        output.extend_from_slice(&(value.len() as u32).to_be_bytes());
        output.extend_from_slice(value);
    }

    fn argon2id(password: &[u8], salt: &[u8], output: &mut [u8; 32]) -> Result<()> {
        let params =
            argon2::Params::new(ARGON2_MEMORY_KIB, ARGON2_ITERATIONS, ARGON2_LANES, Some(32))
                .map_err(|error| anyhow::anyhow!("invalid Argon2 parameters: {error}"))?;
        Argon2::new(argon2::Algorithm::Argon2id, argon2::Version::V0x13, params)
            .hash_password_into(password, salt, output)
            .map_err(|error| anyhow::anyhow!("identity KDF failed: {error}"))
    }

    fn derive_subseed(master_seed: &[u8; 32], label: &[u8]) -> [u8; 32] {
        let mut hasher = Sha256::new();
        hasher.update(label);
        hasher.update(master_seed);
        let digest = hasher.finalize();
        let mut output = [0_u8; 32];
        output.copy_from_slice(&digest);
        output
    }

    fn repeat_subseed(master_seed: &[u8; 32], label: &[u8], length: usize) -> Vec<u8> {
        let block = Self::derive_subseed(master_seed, label);
        let mut output = Vec::with_capacity(length);
        while output.len() < length {
            let remaining = length - output.len();
            output.extend_from_slice(&block[..remaining.min(block.len())]);
        }
        output
    }

    fn i2p_base64_encode(bytes: &[u8]) -> String {
        let mut specification = Specification::new();
        specification
            .symbols
            .push_str("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-~");
        specification.padding = Some('=');
        specification
            .encoding()
            .expect("the I2P base64 alphabet is valid")
            .encode(bytes)
    }
}

fn read_passphrase_file(path: &Path) -> Result<String> {
    let file = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_CLOEXEC | libc::O_NOFOLLOW)
        .open(path)
        .with_context(|| format!("cannot open password file {}", path.display()))?;
    let metadata = file
        .metadata()
        .with_context(|| format!("cannot inspect password file {}", path.display()))?;
    if !metadata.is_file() {
        bail!("password file must be a regular file, not a symlink")
    }
    if metadata.uid() != unsafe { libc::geteuid() } {
        bail!("password file must be owned by the current user")
    }
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("password file must not be accessible by group or other users")
    }
    if metadata.nlink() != 1 {
        bail!("password file must not have multiple filesystem links")
    }
    if metadata.len() == 0 || metadata.len() > MAX_PASSPHRASE_FILE_BYTES {
        bail!("password file must contain 1..={MAX_PASSPHRASE_FILE_BYTES} bytes")
    }
    let mut passphrase = String::with_capacity(metadata.len() as usize);
    file.take(MAX_PASSPHRASE_FILE_BYTES + 1)
        .read_to_string(&mut passphrase)
        .with_context(|| format!("cannot read password file {}", path.display()))?;
    if passphrase.is_empty() || passphrase.len() as u64 > MAX_PASSPHRASE_FILE_BYTES {
        bail!("password file changed while being read")
    }
    Ok(passphrase)
}

fn normalize_passphrase_file(mut passphrase: String) -> String {
    if passphrase.ends_with('\n') {
        passphrase.pop();
        if passphrase.ends_with('\r') {
            passphrase.pop();
        }
    }
    passphrase
}

#[cfg(test)]
mod tests {
    use std::os::unix::fs::{symlink, PermissionsExt};

    use sha2::{Digest, Sha256};
    use ssh_key::PrivateKey;
    use zeroize::Zeroizing;

    use super::{
        normalize_passphrase_file, read_passphrase_file, IdentityManager, ARGON2_ITERATIONS,
        ARGON2_LANES, ARGON2_MEMORY_KIB, RECOVERY_I2P_POOL_SLOTS, RECOVERY_TOR_POOL_SLOTS,
    };

    fn password() -> Zeroizing<String> {
        Zeroizing::new("correct horse battery staple".to_owned())
    }

    #[test]
    fn recovery_protocol_constants_are_locked() {
        assert_eq!(
            (ARGON2_MEMORY_KIB, ARGON2_ITERATIONS, ARGON2_LANES),
            (65_536, 3, 4)
        );
    }

    #[test]
    fn recovery_identities_are_deterministic_and_role_separated() {
        let client =
            IdentityManager::derive_client_recovery_identity(&password(), "monster-16").unwrap();
        let server =
            IdentityManager::derive_server_recovery_identity(&password(), "monster-16").unwrap();
        assert_eq!(client.i2p.destination, server.i2p.destination);
        assert_eq!(client.tor_destination, server.tor.destination);
        assert_eq!(
            client.tor_pool_destinations,
            server
                .tor_pool
                .iter()
                .map(|identity| identity.destination.clone())
                .collect::<Vec<_>>()
        );
        assert_eq!(
            client.tor_pool_destinations.len(),
            usize::try_from(RECOVERY_TOR_POOL_SLOTS).unwrap()
        );
        assert_eq!(
            client.i2p_pool.len(),
            usize::try_from(RECOVERY_I2P_POOL_SLOTS).unwrap()
        );
        assert_eq!(client.ssh_host_public_key, server.ssh_host.public_key);
        assert_eq!(client.ssh_client.public_key, server.ssh_client_public_key);
        assert_eq!(*client.bond_session_key, *server.bond_session_key);
        assert_ne!(client.ssh_host_public_key, client.ssh_client.public_key);
        assert_eq!(
            hex::encode(Sha256::digest(&client.bond_session_key[..])),
            "b44cf73827c4d43b95c433d07dcb5630f0ac8f6ec5cd51cea1e307cd093908ad"
        );

        let parsed = PrivateKey::from_openssh(client.ssh_client.private_key.as_bytes()).unwrap();
        assert_eq!(
            parsed.public_key().to_openssh().unwrap(),
            client.ssh_client.public_key
        );
    }

    #[test]
    fn recovery_identity_pool_can_extend_to_thirty_two_stable_lanes() {
        let master = IdentityManager::derive_master_seed(&password(), "monster-16").unwrap();
        let legacy =
            IdentityManager::derive_client_recovery_identity_from_master(&master, 4, 4).unwrap();
        let client =
            IdentityManager::derive_client_recovery_identity_from_master(&master, 8, 8).unwrap();
        let server =
            IdentityManager::derive_server_recovery_identity_from_master(&master, 8, 8).unwrap();

        assert_eq!(client.tor_pool_destinations.len(), 8);
        assert_eq!(client.i2p_pool.len(), 8);
        assert_eq!(
            legacy.tor_pool_destinations.as_slice(),
            &client.tor_pool_destinations[..4]
        );
        assert_eq!(legacy.i2p_pool.as_slice(), &client.i2p_pool[..4]);
        assert_eq!(
            client.tor_pool_destinations,
            server
                .tor_pool
                .iter()
                .map(|identity| identity.destination.clone())
                .collect::<Vec<_>>()
        );
        assert_eq!(client.i2p_pool, server.i2p_pool);
        assert_eq!(*client.bond_session_key, *server.bond_session_key);
        assert!(IdentityManager::validate_recovery_pool_slots(0, 0).is_err());
        let extended_client =
            IdentityManager::derive_client_recovery_identity_from_master(&master, 16, 16).unwrap();
        let extended_server =
            IdentityManager::derive_server_recovery_identity_from_master(&master, 16, 16).unwrap();
        assert_eq!(extended_client.tor_pool_destinations.len(), 16);
        assert_eq!(extended_client.i2p_pool.len(), 16);
        assert_eq!(
            client.tor_pool_destinations,
            extended_client.tor_pool_destinations[..8]
        );
        assert_eq!(client.i2p_pool, extended_client.i2p_pool[..8]);
        assert_eq!(
            extended_client.tor_pool_destinations,
            extended_server
                .tor_pool
                .iter()
                .map(|identity| identity.destination.clone())
                .collect::<Vec<_>>()
        );
        assert_eq!(extended_client.i2p_pool, extended_server.i2p_pool);
        assert!(IdentityManager::validate_recovery_pool_slots(17, 16).is_err());
    }

    #[test]
    fn machine_id_changes_every_public_identity() {
        let first =
            IdentityManager::derive_client_recovery_identity(&password(), "monster-16").unwrap();
        let second =
            IdentityManager::derive_client_recovery_identity(&password(), "monster-17").unwrap();
        assert_ne!(first.i2p.destination, second.i2p.destination);
        assert_ne!(first.tor_destination, second.tor_destination);
        assert_ne!(first.ssh_host_public_key, second.ssh_host_public_key);
        assert_ne!(first.ssh_client.public_key, second.ssh_client.public_key);
        assert_ne!(*first.bond_session_key, *second.bond_session_key);
    }

    #[test]
    fn i2p_pool_destinations_are_stable_and_slot_separated() {
        let first =
            IdentityManager::derive_i2p_pool_identity(&password(), "monster-16", 1).unwrap();
        let repeated =
            IdentityManager::derive_i2p_pool_identity(&password(), "monster-16", 1).unwrap();
        let second =
            IdentityManager::derive_i2p_pool_identity(&password(), "monster-16", 2).unwrap();
        let other_machine =
            IdentityManager::derive_i2p_pool_identity(&password(), "monster-17", 1).unwrap();
        assert_eq!(first, repeated);
        assert_ne!(first.destination, second.destination);
        assert_ne!(first.destination, other_machine.destination);
        assert_eq!(
            first.destination,
            "i2p://tiapedkjhualopedvscdcufllb4eh3vknd3zqgvby6l2iwbmi2gq.b32.i2p"
        );
        assert!(IdentityManager::derive_i2p_pool_identity(&password(), "monster-16", 0).is_err());
    }

    #[test]
    fn tor_pool_destinations_are_stable_slot_separated_and_compatible() {
        let first =
            IdentityManager::derive_tor_pool_identity(&password(), "monster-16", 1).unwrap();
        let repeated =
            IdentityManager::derive_tor_pool_identity(&password(), "monster-16", 1).unwrap();
        let second =
            IdentityManager::derive_tor_pool_identity(&password(), "monster-16", 2).unwrap();
        let other_machine =
            IdentityManager::derive_tor_pool_identity(&password(), "monster-17", 1).unwrap();
        let direct = IdentityManager::derive_server_recovery_identity(&password(), "monster-16")
            .unwrap()
            .tor;
        assert_eq!(first.destination, repeated.destination);
        assert_eq!(first.destination, direct.destination);
        assert_eq!(first.control_private_key, direct.control_private_key);
        assert_ne!(first.destination, second.destination);
        assert_ne!(first.destination, other_machine.destination);
        assert!(IdentityManager::derive_tor_pool_identity(&password(), "monster-16", 0).is_err());
    }

    #[test]
    fn tor_v3_derivation_vector_is_locked() {
        let identity = IdentityManager::derive_server_recovery_identity(&password(), "monster-16")
            .unwrap()
            .tor;
        assert_eq!(
            identity.destination,
            "tor://zega2zvmocqvmkpgjpcjezbbwo3ashththoy3jw4qylgfcpjmwnvxbad.onion"
        );
        assert_eq!(
            hex::encode(Sha256::digest(identity.control_private_key.as_bytes())),
            "dca0999b072586e1d57c7ca4a69d54f06be7c32bef92d1102f6fe1486ce14f06"
        );
        assert_eq!(identity.control_private_key.len(), 88);
    }

    #[test]
    fn recovery_public_identity_vector_is_locked() {
        let identity =
            IdentityManager::derive_client_recovery_identity(&password(), "monster-16").unwrap();
        let actual = (
            identity.i2p.destination,
            hex::encode(Sha256::digest(identity.i2p.private_key.as_bytes())),
            identity.ssh_client.public_key,
            identity.ssh_host_public_key,
        );
        assert_eq!(
            actual,
            (
                "i2p://yxf5vmlva4lf7xpji2jatohyf757dtk323abty4sxjj6jszoplzq.b32.i2p".to_owned(),
                "fbc980c2cd606ee24b72f9ef52aacee658c183501541eff797d79ecd6fdfb17a".to_owned(),
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICIj8Y7bgHknAf6W+rc5143puMhtaoQGCpaVH4TlB6Mw"
                    .to_owned(),
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICRKqv/CLGJCakSzuow5Bqi9KahJEkLpbCV73kbswJ3r"
                    .to_owned(),
            )
        );
    }

    #[test]
    fn dropbear_host_key_has_the_expected_wire_shape() {
        let server =
            IdentityManager::derive_server_recovery_identity(&password(), "monster-16").unwrap();
        let encoded = &*server.ssh_host.dropbear_private_key;
        assert_eq!(&encoded[..4], &11_u32.to_be_bytes());
        assert_eq!(&encoded[4..15], b"ssh-ed25519");
        assert_eq!(&encoded[15..19], &64_u32.to_be_bytes());
        assert_eq!(encoded.len(), 83);
    }

    #[test]
    fn passphrase_files_remove_only_one_line_ending() {
        assert_eq!(
            normalize_passphrase_file(" secret \n".to_owned()),
            " secret "
        );
        assert_eq!(normalize_passphrase_file("secret\r\n".to_owned()), "secret");
        assert_eq!(
            normalize_passphrase_file("secret\n\n".to_owned()),
            "secret\n"
        );
    }

    #[test]
    fn passphrase_file_is_owner_only_regular_and_nonempty() {
        let root = std::env::temp_dir().join(format!(
            "anonssh-identity-passphrase-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(&root).unwrap();
        let path = root.join("password");
        std::fs::write(&path, b"secret\n").unwrap();
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o600)).unwrap();
        assert_eq!(read_passphrase_file(&path).unwrap(), "secret\n");

        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o640)).unwrap();
        assert!(read_passphrase_file(&path).is_err());
        std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o600)).unwrap();
        let link = root.join("link");
        symlink(&path, &link).unwrap();
        assert!(read_passphrase_file(&link).is_err());
        let hard_link = root.join("hard-link");
        std::fs::hard_link(&path, &hard_link).unwrap();
        assert!(read_passphrase_file(&path).is_err());
        std::fs::remove_file(hard_link).unwrap();
        std::fs::write(&path, b"").unwrap();
        assert!(read_passphrase_file(&path).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn empty_identity_password_is_rejected() {
        let empty = Zeroizing::new(String::new());
        assert!(IdentityManager::derive_master_seed(&empty, "machine").is_err());
    }
}
