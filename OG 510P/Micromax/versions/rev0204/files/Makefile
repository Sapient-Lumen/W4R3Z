.PHONY: context bootstrap test lint format typecheck doctor editor init-git pack

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

pack:
	python tools/mxpack.py micromax-pack.zip
