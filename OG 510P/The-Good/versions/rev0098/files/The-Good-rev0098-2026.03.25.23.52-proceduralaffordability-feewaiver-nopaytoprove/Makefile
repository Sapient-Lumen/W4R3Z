.PHONY: all sources note_index threads thread_summary releases control_surfaces assurance_artifacts lifecycle_gates manifest lint

all: lint

sources:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_sources_index.py

note_index:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_note_index.py

threads:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_threads.py

thread_summary:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_thread_summary.py

releases:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_releases.py

control_surfaces:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_control_surfaces.py

assurance_artifacts:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_assurance_artifacts.py

lifecycle_gates:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_lifecycle_gates.py

manifest: sources note_index threads thread_summary releases control_surfaces assurance_artifacts lifecycle_gates
	PYTHONDONTWRITEBYTECODE=1 python3 tools/build_manifest.py

lint: manifest
	PYTHONDONTWRITEBYTECODE=1 python3 tools/lint_archive.py
