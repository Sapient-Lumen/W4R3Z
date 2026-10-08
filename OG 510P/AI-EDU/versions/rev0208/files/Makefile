.PHONY: lint context-pack package-release handoff-release

lint:
	python3 tools/run_lint_suite.py

context-pack:
	python3 tools/gen_context_pack.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	python3 tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)"

handoff-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	$(MAKE) context-pack
	$(MAKE) lint
	$(MAKE) package-release STAMP="$(STAMP)" SLUG="$(SLUG)"
