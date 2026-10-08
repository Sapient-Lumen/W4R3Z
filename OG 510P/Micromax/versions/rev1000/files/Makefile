.PHONY: context context-json context-check audit-metrics effect-contracts bootstrap test test-plan test-chunk test-all-chunks test-manifest-summary test-verify-manifest test-verify-current-source test-verify-current-environment test-verify-current test-recommend-chunks test-diff-manifests timely timely-tests release-suite release-verify release-summary release-next release-inputs repro-release lint format typecheck doctor doctor-full doctor-chunked editor init-git pack revzip revzip-verify

# Keep test/evidence supervisors from inheriting one native math thread per
# visible CPU. GNU make preserves explicit environment/command-line overrides.
OPENBLAS_NUM_THREADS ?= 1
OMP_NUM_THREADS ?= 1
MKL_NUM_THREADS ?= 1
NUMEXPR_NUM_THREADS ?= 1
VECLIB_MAXIMUM_THREADS ?= 1
BLIS_NUM_THREADS ?= 1
export OPENBLAS_NUM_THREADS OMP_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS
export VECLIB_MAXIMUM_THREADS BLIS_NUM_THREADS

CHUNKS ?= 64
MAX_NEW_TESTS ?= 60
MAX_NEW_FILES ?= 4
TEST_BATCH_SIZE ?= 10
FILE_TIMEOUT ?= 45
MAX_RUNTIME_SECONDS ?= 18
TEST_MANIFEST ?= .artifacts/mxtest-all-64.json
TIMELY_MANIFEST ?= .artifacts/mxtimely-mxtest.json
RELEASE_MANIFEST ?= .artifacts/mxrelease-full-suite.json
RELEASE_MAX_RUNTIME_SECONDS ?= 8
RELEASE_BATCH_TIMEOUT ?= 20
RELEASE_BATCH_SIZE ?= 12
RELEASE_MAX_NEW_BATCHES ?= 0
REPRO_OUTPUT ?= .artifacts/mxrepro
REPRO_TAG ?= single-source-repro-wheel-release-receipt-ci
REPRO_STAMP ?=
TIMELY_TIMEOUT_SCALE ?= 1
TEST_TIMEOUT ?= 1800
PYTEST_ARGS ?=

bootstrap:
	bash ./scripts/bootstrap.sh

test:
	MXTEST_CHUNK_TIMEOUT_SECONDS="$(TEST_TIMEOUT)" bash ./scripts/test.sh $(PYTEST_ARGS)

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

timely:
	python tools/mxtimely.py --manifest "$(TIMELY_MANIFEST)" --timeout-scale "$(TIMELY_TIMEOUT_SCALE)"

timely-tests:
	python tools/mxtimely.py --with-tests --skip-doctor --manifest "$(TIMELY_MANIFEST)" --timeout-scale "$(TIMELY_TIMEOUT_SCALE)"

release-suite:
	python tools/mxrelease.py --manifest "$(RELEASE_MANIFEST)" --max-runtime-seconds "$(RELEASE_MAX_RUNTIME_SECONDS)" --batch-timeout "$(RELEASE_BATCH_TIMEOUT)" --batch-size "$(RELEASE_BATCH_SIZE)" --max-new-batches "$(RELEASE_MAX_NEW_BATCHES)" --allow-partial

release-verify:
	python tools/mxrelease.py --manifest "$(RELEASE_MANIFEST)" --verify

release-summary:
	python tools/mxrelease.py --manifest "$(RELEASE_MANIFEST)" --summary

release-next:
	python tools/mxrelease.py --manifest "$(RELEASE_MANIFEST)" --next

release-inputs:
	python tools/mxrelease.py --package-inputs

repro-release:
	python tools/mxbuilder.py --root . -- python tools/mxrepro.py --output-dir "$(REPRO_OUTPUT)" --archive-outdir "$(REPRO_OUTPUT)" --archive-tag "$(REPRO_TAG)" $(if $(strip $(REPRO_STAMP)),--archive-stamp "$(REPRO_STAMP)",)

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

effect-contracts:
	python tools/mxeffects.py --check

pack:
	python tools/mxpack.py micromax-pack.zip

revzip:
	@if [ -z "$(TAG)" ]; then echo "Usage: make revzip TAG=feature-summary-codename"; exit 1; fi
	python tools/mkrevzip.py --tag "$(TAG)"

revzip-verify:
	@if [ -z "$(ZIP)" ]; then echo "Usage: make revzip-verify ZIP=Micromax-rev####-stamp-tag.zip"; exit 1; fi
	python tools/mkrevzip.py --verify-archive "$(ZIP)"
