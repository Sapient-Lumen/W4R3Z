.PHONY: build lint

build:
	python3 tools/build_indices.py
	python3 tools/build_manifest.py

lint: build
	python3 tools/lint_archive.py
