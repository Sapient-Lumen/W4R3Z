#!/usr/bin/env python3
"""Shared lint-step inventory for source and extracted-package replay.

`tools/run_lint_steps.py` and `tools/smoke_package_release.py` must execute the
same semantic checks.  Keeping the step list here prevents package smoke from
silently lagging behind the source-tree `make lint` path when a new audit is
added.
"""
from __future__ import annotations

DEFAULT_LINT_STEPS = [
    ("clean-transients", ["tools/clean_transients.py"]),
    ("release-provenance-sidecars", ["tools/release_provenance_sidecar.py", "--check"]),
    ("candidate-docket-duplication-audit", ["tools/candidate_docket_duplication_audit.py", "--check"]),
    ("familyc-qutrit-reconstruction-benchmark", ["tools/familyc_qutrit_reconstruction_benchmark.py", "--check"]),
    ("familyc-approximate-recovery-scaling-benchmark", ["tools/familyc_approximate_recovery_scaling_benchmark.py", "--check"]),
    ("familyc-jlms-recovery-budget-benchmark", ["tools/familyc_jlms_recovery_budget_benchmark.py", "--check"]),
    ("kernel-testcard-audit", ["tools/kernel_testcard_audit.py", "--check"]),
    # Run the memory-spiky mutation replay before the large archive linter so
    # small cloudtainers do not accumulate pressure across the two heaviest
    # phases before replay starts. The semantic check set is unchanged.
    ("source-role-negative-replay", ["tools/source_role_negative_replay_tests.py"]),
    ("json-schema-validation", ["tools/validate_registered_json_schemas.py"]),
    ("archive-lint", ["tools/lint_archive.py"]),
]
