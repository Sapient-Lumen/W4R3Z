.PHONY: lint context-pack package-release

lint:
	python3 tools/run_lint_suite.py

context-pack:
	python3 tools/gen_context_pack.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required"; exit 1)
	python3 tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)"
