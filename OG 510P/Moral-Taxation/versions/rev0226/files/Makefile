.PHONY: manifest package check

manifest:
	python3 tools/build_manifest.py .

check:
	python3 tools/check_archive.py .

package: check manifest
	@echo "archive ready"
