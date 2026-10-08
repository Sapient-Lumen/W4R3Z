.PHONY: lint context-pack manifest package-release handoff-release

lint:
	python3 tools/lint_archive.py

context-pack:
	python3 tools/gen_context_pack.py

manifest:
	python3 tools/build_manifest.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	python3 tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)"

handoff-release: context-pack manifest lint package-release
