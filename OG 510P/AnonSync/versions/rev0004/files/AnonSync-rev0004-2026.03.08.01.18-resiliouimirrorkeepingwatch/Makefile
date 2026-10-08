.PHONY: validate context-pack discovery-check release

validate:
	python scripts/validate_repo.py

context-pack:
	python scripts/generate_context_pack.py

discovery-check:
	python scripts/discovery_service_check.py --config discovery/service-targets.yaml

release:
	python scripts/archive_release.py
