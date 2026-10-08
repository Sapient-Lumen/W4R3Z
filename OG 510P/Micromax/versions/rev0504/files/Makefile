.PHONY: context context-json context-check bootstrap test lint format typecheck doctor editor init-git pack revzip

bootstrap:
	bash ./scripts/bootstrap.sh

test:
	bash ./scripts/test.sh

lint:
	bash ./scripts/lint.sh

format:
	bash ./scripts/format.sh

typecheck:
	bash ./scripts/typecheck.sh

doctor:
	python tools/mxdoctor.py

editor:
	python -m micromax_editor

init-git:
	bash ./tools/init_git.sh

context:
	python tools/mxcontext.py

context-json:
	python tools/mxcontext.py --json

context-check:
	python tools/mxcontext.py --check

pack:
	python tools/mxpack.py micromax-pack.zip

revzip:
	@if [ -z "$(TAG)" ]; then echo "Usage: make revzip TAG=feature-summary-codename"; exit 1; fi
	python tools/mkrevzip.py --tag "$(TAG)"
