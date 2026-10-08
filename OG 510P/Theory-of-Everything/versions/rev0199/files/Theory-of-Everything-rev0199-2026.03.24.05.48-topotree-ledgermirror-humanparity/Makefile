PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE = 1

index:
	$(PYTHON) tools/sync_generated_surfaces.py

lint:
	$(PYTHON) tools/lint_archive.py

package:
	$(PYTHON) tools/package_release.py
