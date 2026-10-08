PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE = 1

clean:
	$(PYTHON) tools/clean_transients.py

index:
	$(PYTHON) tools/sync_generated_surfaces.py
	$(PYTHON) tools/familyc_qutrit_reconstruction_benchmark.py --write
	$(PYTHON) tools/familyc_approximate_recovery_scaling_benchmark.py --write
	$(PYTHON) tools/familyc_jlms_recovery_budget_benchmark.py --write
	$(PYTHON) tools/candidate_docket_duplication_audit.py
	$(PYTHON) tools/kernel_testcard_audit.py
	$(PYTHON) tools/release_provenance_sidecar.py

lint:
	$(PYTHON) tools/run_lint_steps.py

package: index lint
	$(PYTHON) tools/package_release.py
	$(PYTHON) tools/smoke_package_release.py
