import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
package = ROOT / "tools" / "package_release.py"
helper = ROOT / "tools" / "package_preflight_lib.py"
if not package.exists() or not helper.exists():
    raise SystemExit("missing package-release preflight surfaces")
package_text = package.read_text(encoding="utf-8")
helper_text = helper.read_text(encoding="utf-8")
required_package_needles = [
    "from package_preflight_lib import run_artifact_smoke, run_lint_preflight, write_deterministic_zip, write_verified_sha256_sidecar",
    "refresh_generated_surfaces(ROOT, include_release_integrity=True)",
    "run_lint_preflight(ROOT)",
    "write_deterministic_zip(ROOT, bundle_path, bundle_name)",
    "run_artifact_smoke(ROOT, bundle_path, bundle_name)",
    "write_verified_sha256_sidecar(bundle_path, sidecar, bundle_name)",
]
for needle in required_package_needles:
    if needle not in package_text:
        raise SystemExit(f"package_release.py missing {needle}")
refresh_at = package_text.rfind("refresh_generated_surfaces(ROOT, include_release_integrity=True)")
preflight_at = package_text.find("run_lint_preflight(ROOT)")
zip_at = package_text.find("write_deterministic_zip(ROOT, bundle_path, bundle_name)")
smoke_at = package_text.find("run_artifact_smoke(ROOT, bundle_path, bundle_name)")
sha_at = package_text.find("write_verified_sha256_sidecar(bundle_path, sidecar, bundle_name)")
if not (refresh_at < preflight_at < zip_at < smoke_at < sha_at):
    raise SystemExit("package_release.py must refresh generated surfaces, run lint preflight, zip, smoke-test the artifact, then write and verify the sidecar")
required_helper_needles = [
    "tools/run_lint_suite.py",
    "PYTHONDONTWRITEBYTECODE",
    "zipfile.ZipFile",
    "testzip()",
    "expected_zip_members",
    "PackagePreflightError",
    "safe_zip_member_target",
    "duplicate zip member detected",
    "unsafe zip member path",
    "release-hygiene-excluded path present",
    "zip member order drifted from release paths",
    "zip member set drifted from release paths",
    "extract_zip_safely",
    "run_lint_preflight(extract_root)",
    "FIXED_ZIP_DT",
    "FIXED_EXTERNAL_ATTR",
    "package_determinism_canary_results",
    "package_sidecar_canary_results",
    "write_verified_sha256_sidecar",
    "verify_sha256_sidecar",
    "sha256 sidecar content mismatch",
    "sha256 sidecar filename mismatch",
    "deterministic-writer-identical-bytes",
    "deterministic-writer-fixed-metadata",
    "package_artifact_negative_canary_results",
    "zip-unsafe-traversal-member",
    "safe-extract-direct-traversal",
    "tempfile.TemporaryDirectory",
    "check=True",
]
for needle in required_helper_needles:
    if needle not in helper_text:
        raise SystemExit(f"package_preflight_lib.py missing {needle}")
for forbidden in ["package-release-court", "release-legitimacy-board", "lint-waiver-sovereign"]:
    # The contract is intentionally operational; these names must not appear as
    # invited authority surfaces in the helper/package source.
    if forbidden in package_text or forbidden in helper_text:
        raise SystemExit(f"forbidden authority term leaked into package preflight source: {forbidden}")
print("check_package_release_preflight_contract: OK")
