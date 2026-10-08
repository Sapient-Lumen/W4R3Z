.PHONY: context context-json context-check audit-metrics bootstrap test test-plan test-chunk test-all-chunks test-manifest-summary test-verify-manifest test-verify-current-source test-verify-current-environment test-verify-current test-recommend-chunks test-diff-manifests lint format typecheck doctor doctor-full doctor-chunked editor init-git pack revzip

CHUNKS ?= 64
MAX_NEW_TESTS ?= 120
MAX_NEW_FILES ?= 8
TEST_BATCH_SIZE ?= 0
FILE_TIMEOUT ?= 180
MAX_RUNTIME_SECONDS ?= 25
TEST_MANIFEST ?= .artifacts/mxtest-all-64.json

bootstrap:
	bash ./scripts/bootstrap.sh

test:
	bash ./scripts/test.sh

test-plan:
	python tools/mxtest.py --plan --chunks 8 --strategy segment

test-chunk:
	@if [ -z "$(CHUNK)" ]; then echo "Usage: make test-chunk CHUNK=1/8"; exit 1; fi
	python tools/mxtest.py --chunk "$(CHUNK)" --strategy segment --isolate-files

test-all-chunks:
	python tools/mxtest.py --run-chunks "$(CHUNKS)" --strategy segment --isolate-files --resume --checkpoint-tests --max-new-tests "$(MAX_NEW_TESTS)" --max-new-files "$(MAX_NEW_FILES)" --test-batch-size "$(TEST_BATCH_SIZE)" --file-timeout "$(FILE_TIMEOUT)" --max-runtime-seconds "$(MAX_RUNTIME_SECONDS)" --json "$(TEST_MANIFEST)"

test-manifest-summary:
	python tools/mxtest.py --manifest-summary "$(TEST_MANIFEST)"

test-verify-manifest:
	python tools/mxtest.py --verify-manifest "$(TEST_MANIFEST)"

test-verify-current-source:
	python tools/mxtest.py --verify-current-source "$(TEST_MANIFEST)"

test-verify-current-environment:
	python tools/mxtest.py --verify-current-environment "$(TEST_MANIFEST)"

test-verify-current:
	python tools/mxtest.py --verify-current "$(TEST_MANIFEST)"

test-recommend-chunks:
	python tools/mxtest.py --recommend-chunks "$(TEST_MANIFEST)"

test-diff-manifests:
	@if [ -z "$(OLD)" ] || [ -z "$(NEW)" ]; then echo "Usage: make test-diff-manifests OLD=.artifacts/old.json NEW=.artifacts/new.json"; exit 1; fi
	python tools/mxtest.py --diff-manifests "$(OLD)" "$(NEW)"

lint:
	bash ./scripts/lint.sh

format:
	bash ./scripts/format.sh

typecheck:
	bash ./scripts/typecheck.sh

doctor:
	python tools/mxdoctor.py

doctor-full:
	python tools/mxdoctor.py --full

doctor-chunked:
	python tools/mxdoctor.py --chunked --chunks "$(CHUNKS)" --manifest "$(TEST_MANIFEST)" --max-runtime-seconds "$(MAX_RUNTIME_SECONDS)" --max-new-tests "$(MAX_NEW_TESTS)" --max-new-files "$(MAX_NEW_FILES)" --test-batch-size "$(TEST_BATCH_SIZE)" --file-timeout "$(FILE_TIMEOUT)"

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

audit-metrics:
	python tools/mxaudit.py --check

pack:
	python tools/mxpack.py micromax-pack.zip

revzip:
	@if [ -z "$(TAG)" ]; then echo "Usage: make revzip TAG=feature-summary-codename"; exit 1; fi
	python tools/mkrevzip.py --tag "$(TAG)"
