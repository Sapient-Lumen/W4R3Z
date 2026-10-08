.PHONY: all sources note_index threads thread_summary releases control_surfaces assurance_artifacts lifecycle_gates manifest lint

all: lint

sources:
	python3 tools/build_sources_index.py

note_index:
	python3 tools/build_note_index.py

threads: note_index
	python3 tools/build_threads.py

thread_summary: note_index
	python3 tools/build_thread_summary.py

releases:
	python3 tools/build_releases.py

control_surfaces: note_index
	python3 tools/build_control_surfaces.py

assurance_artifacts: note_index
	python3 tools/build_assurance_artifacts.py

lifecycle_gates: note_index
	python3 tools/build_lifecycle_gates.py

manifest: sources note_index threads thread_summary releases control_surfaces assurance_artifacts lifecycle_gates
	python3 tools/build_manifest.py

lint: manifest
	python3 tools/lint_archive.py
