use std::env;
use std::fs;
use std::path::{Path, PathBuf};

fn main() {
    let manifest_dir = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").expect("manifest dir"));
    let corpus = manifest_dir.join("../bootstrap/i2p");
    println!("cargo:rerun-if-changed={}", corpus.display());

    let mut files = Vec::new();
    collect_files(&corpus, &corpus, &mut files);
    files.sort_by(|left, right| left.0.cmp(&right.0));

    let manifest = corpus.join("manifest.json");
    assert!(manifest.is_file(), "embedded bootstrap manifest is missing");
    let mut generated = format!(
        "pub(crate) static MANIFEST: &[u8] = include_bytes!({manifest:?});\n\
         pub(crate) static FILES: &[(&str, &[u8])] = &[\n"
    );
    for (relative, absolute) in files {
        if relative == "manifest.json" {
            continue;
        }
        generated.push_str(&format!(
            "    ({relative:?}, include_bytes!({absolute:?})),\n"
        ));
    }
    generated.push_str("];\n");

    let output = PathBuf::from(env::var_os("OUT_DIR").expect("output dir"))
        .join("embedded_i2p_bootstrap.rs");
    fs::write(output, generated).expect("write embedded bootstrap source");

    generate_embedded_router_runtime();
}

fn generate_embedded_router_runtime() {
    for variable in [
        "ANONSSH_EMBEDDED_TOR_BIN",
        "ANONSSH_EMBEDDED_TOR_VERSION",
        "ANONSSH_EMBEDDED_I2PD_BIN",
        "ANONSSH_EMBEDDED_I2PD_VERSION",
        "ANONSSH_EMBEDDED_I2PD_CERTS_DIR",
        "ANONSSH_EMBEDDED_SSH_BIN",
        "ANONSSH_EMBEDDED_SSH_VERSION",
        "ANONSSH_EMBEDDED_DROPBEAR_BIN",
        "ANONSSH_EMBEDDED_DROPBEAR_VERSION",
        "ANONSSH_EMBEDDED_SFTP_SERVER_BIN",
        "ANONSSH_EMBEDDED_SFTP_SERVER_VERSION",
        "ANONSSH_EMBEDDED_SCP_BIN",
        "ANONSSH_EMBEDDED_SCP_VERSION",
    ] {
        println!("cargo:rerun-if-env-changed={variable}");
    }

    let tor = embedded_executable("TOR");
    let i2pd = embedded_executable("I2PD");
    let ssh = embedded_executable("SSH");
    let dropbear = embedded_executable("DROPBEAR");
    let sftp_server = embedded_executable("SFTP_SERVER");
    let scp = embedded_executable("SCP");
    let mut generated = format!(
        "pub(crate) static TOR: Option<(&str, &[u8])> = {tor};\n\
         pub(crate) static I2PD: Option<(&str, &[u8])> = {i2pd};\n\
         pub(crate) static SSH: Option<(&str, &[u8])> = {ssh};\n\
         pub(crate) static DROPBEAR: Option<(&str, &[u8])> = {dropbear};\n\
         pub(crate) static SFTP_SERVER: Option<(&str, &[u8])> = {sftp_server};\n\
         pub(crate) static SCP: Option<(&str, &[u8])> = {scp};\n\
         pub(crate) static I2PD_CERTIFICATES: &[(&str, &[u8])] = &[\n"
    );
    if let Some(root) = env::var_os("ANONSSH_EMBEDDED_I2PD_CERTS_DIR").map(PathBuf::from) {
        assert!(
            root.is_dir(),
            "embedded i2pd certificate directory is missing"
        );
        println!("cargo:rerun-if-changed={}", root.display());
        let mut files = Vec::new();
        collect_files(&root, &root, &mut files);
        files.sort_by(|left, right| left.0.cmp(&right.0));
        for (relative, absolute) in files {
            generated.push_str(&format!(
                "    ({relative:?}, include_bytes!({absolute:?})),\n"
            ));
        }
    }
    generated.push_str("];\n");
    let output = PathBuf::from(env::var_os("OUT_DIR").expect("output dir"))
        .join("embedded_router_runtime.rs");
    fs::write(output, generated).expect("write embedded router runtime source");
}

fn embedded_executable(name: &str) -> String {
    let binary_variable = format!("ANONSSH_EMBEDDED_{name}_BIN");
    let version_variable = format!("ANONSSH_EMBEDDED_{name}_VERSION");
    let Some(binary) = env::var_os(&binary_variable).map(PathBuf::from) else {
        return "None".to_owned();
    };
    assert!(binary.is_file(), "{binary_variable} is not a file");
    println!("cargo:rerun-if-changed={}", binary.display());
    let version = env::var(&version_variable)
        .unwrap_or_else(|_| panic!("{version_variable} is required with {binary_variable}"));
    assert!(!version.is_empty(), "embedded router version is empty");
    format!("Some(({version:?}, include_bytes!({binary:?})))")
}

fn collect_files(root: &Path, directory: &Path, files: &mut Vec<(String, PathBuf)>) {
    let mut entries = fs::read_dir(directory)
        .expect("read bootstrap directory")
        .collect::<Result<Vec<_>, _>>()
        .expect("read bootstrap entries");
    entries.sort_by_key(std::fs::DirEntry::file_name);
    for entry in entries {
        let file_type = entry.file_type().expect("read bootstrap file type");
        let path = entry.path();
        if file_type.is_symlink() {
            panic!(
                "embedded bootstrap corpus contains a symlink: {}",
                path.display()
            );
        }
        if file_type.is_dir() {
            collect_files(root, &path, files);
        } else if file_type.is_file() {
            let relative = path
                .strip_prefix(root)
                .expect("bootstrap file beneath corpus")
                .to_str()
                .expect("UTF-8 bootstrap path")
                .replace(std::path::MAIN_SEPARATOR, "/");
            files.push((relative, path));
        } else {
            panic!("unsupported embedded bootstrap entry: {}", path.display());
        }
    }
}
