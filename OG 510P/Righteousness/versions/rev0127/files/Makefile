.PHONY: context-pack lint package-release

context-pack:
	python3 tools/gen_context_pack.py

lint: context-pack
	python3 tools/lint_archive.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	python3 tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)"
	python3 tools/gen_context_pack.py
