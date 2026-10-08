.PHONY: all clean index sources threads control manifest lint

export PYTHONDONTWRITEBYTECODE=1

all: lint

clean:
	find tools -type d -name __pycache__ -prune -exec rm -rf {} +

index: clean
	python3 tools/build_archive_index.py

sources: clean
	python3 tools/build_sources.py

threads: clean
	python3 tools/build_threads.py

control: clean
	python3 tools/build_control_surfaces.py

manifest: index sources threads control
	python3 tools/build_manifest.py

lint: manifest
	python3 tools/lint_archive.py
