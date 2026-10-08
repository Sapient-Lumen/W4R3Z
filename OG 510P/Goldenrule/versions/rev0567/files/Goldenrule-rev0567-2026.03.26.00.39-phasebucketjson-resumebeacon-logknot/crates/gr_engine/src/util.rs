use sha2::{Digest, Sha256};
use std::fs::{self, File};
use std::io::{self, Write};
use std::path::Path;

pub fn sha256_hex(bytes: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(bytes);
    let out = h.finalize();
    hex::encode(out)
}

pub fn derive_seed_u64(base: u64, label: &str) -> u64 {
    let mut h = Sha256::new();
    h.update(base.to_le_bytes());
    h.update(label.as_bytes());
    let out = h.finalize();

    let mut b = [0u8; 8];
    b.copy_from_slice(&out[..8]);
    u64::from_le_bytes(b)
}

pub fn atomic_write(path: &Path, bytes: &[u8]) -> io::Result<()> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    fs::create_dir_all(parent)?;

    let tmp_name = format!(
        ".{}.tmp.{}",
        path.file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("artifact"),
        std::process::id()
    );
    let tmp_path = parent.join(tmp_name);

    {
        let mut f = File::create(&tmp_path)?;
        f.write_all(bytes)?;
        f.sync_all()?;
    }

    fs::rename(tmp_path, path)?;
    Ok(())
}
