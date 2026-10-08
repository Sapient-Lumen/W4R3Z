import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class RepoControlTests(unittest.TestCase):
    def test_required_governance_files_exist(self) -> None:
        required = [
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "docs" / "SCIENCE_PLAN.md",
            ROOT / "docs" / "FORMAL_METHODS.md",
            ROOT / "docs" / "QUALITY_ASSURANCE.md",
            ROOT / "docs" / "REPRODUCIBILITY.md",
            ROOT / "docs" / "CI_POLICY.md",
            ROOT / "docs" / "DEPENDENCY_POLICY.md",
            ROOT / "docs" / "SCHEMA_INVENTORY.md",
            ROOT / "docs" / "ARTIFACT_BUCKETS.md",
            ROOT / "Makefile",
            ROOT / "scripts" / "doctor.sh",
            ROOT / "scripts" / "test" / "run_harness.sh",
            ROOT / "scripts" / "cleanup_artifacts.sh",
            ROOT / "schemas" / "release_manifest.schema.json",
            ROOT / "schemas" / "claim_classes.schema.json",
            ROOT / "schemas" / "claim_register.schema.json",
            ROOT / "schemas" / "risk_register.schema.json",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing required file: {path}")

    def test_golden_artifact_separation(self) -> None:
        self.assertTrue((ROOT / "goldens").exists())
        self.assertTrue((ROOT / "artifacts").exists())
        self.assertNotEqual((ROOT / "goldens").resolve(), (ROOT / "artifacts").resolve())
        for rel in ["timing", "security", "process", "release", "formal", "reports"]:
            self.assertTrue((ROOT / "artifacts" / rel).exists(), f"missing artifacts/{rel}")

    def test_determinism_defaults_in_harness(self) -> None:
        harness = (ROOT / "scripts" / "test" / "run_harness.sh").read_text(encoding="utf-8")
        for token in ["TZ", "LC_ALL", "TEST_SEED", "NO_NETWORK"]:
            self.assertIn(token, harness)
        self.assertIn("record_env_metadata.py", harness)

    def test_seed_artifact_template_valid_json(self) -> None:
        template = {
            "mode": "quick",
            "seed": "424242",
            "tz": "UTC",
            "lang": "C",
            "lc_all": "C",
            "no_network": "1",
        }
        payload = json.dumps(template)
        self.assertIsInstance(json.loads(payload), dict)

    def test_agents_contract_mentions_scientific_posture(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("scientific software project", agents)
        self.assertIn("deterministic", agents)

    def test_makefile_includes_extended_tranche_targets(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        for target in [
            "test-formal-smoke",
            "test-formal-tools",
            "test-examples-json",
            "test-examples-unique-ids",
            "test-required-examples",
            "test-schema-json",
            "test-policy-json",
            "test-hooks-contract",
            "test-artifact-gitkeeps",
            "test-timing-artifacts",
            "test-generated-docs",
            "test-doc-links",
            "test-readme-commands",
            "test-docs-index",
            "test-release-doc",
            "test-tranches",
            "test-tranche-status",
            "test-ci-smoke",
            "test-policy-expirations",
            "test-spec-evidence",
            "test-make-help",
            "test-scripts-exec",
            "test-scripts-compile",
            "test-artifact-layout",
            "test-gitignore-policy",
            "test-spec-dates",
            "test-experiment-catalog",
            "test-command-inventory",
            "test-validator-inventory",
            "test-policy-inventory",
            "test-schema-inventory",
            "test-artifact-buckets",
            "report-artifact-summary",
            "test-reports-json",
            "report-repro-bundle",
            "test-release-manifest-schema",
            "test-release-manifest-entries",
            "test-release-checksums",
            "test-claim-classes",
            "test-claim-matrix",
            "test-claim-register",
            "test-claim-register-summary",
            "test-risk-register",
            "test-risk-register-summary",
        ]:
            self.assertIn(target, makefile)


if __name__ == "__main__":
    unittest.main()
