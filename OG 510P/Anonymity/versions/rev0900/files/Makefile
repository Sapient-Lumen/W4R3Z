export PYTHONDONTWRITEBYTECODE=1
OUT_DIR ?= ..

.PHONY: rebuild-surfaces rebuild-revision-bindings rebuild-manifest rebuild-first-pass rebuild-tail queue-compile-smoke hold-compile-triage-verify unqueued-compile-triage unqueued-compile-triage-verify published-compile-triage published-compile-triage-verify auxiliary-tex-compile-triage auxiliary-tex-compile-triage-verify tooling-static-smoke live-compile-lock-self-test python-entrypoint-smoke verify-surfaces verify-surfaces-expanded package

rebuild-surfaces:
	python3 -B publishing/rebuild_archive_surfaces.py --root .

rebuild-revision-bindings:
	python3 -B publishing/rebuild_archive_surfaces.py --root . --phase revision-bindings

rebuild-manifest:
	python3 -B publishing/rebuild_archive_surfaces.py --root . --phase manifest

rebuild-first-pass:
	python3 -B publishing/rebuild_archive_surfaces.py --root . --phase first-pass

rebuild-tail:
	python3 -B publishing/rebuild_archive_surfaces.py --root . --phase tail

queue-compile-smoke:
	bash publishing/run_queue_compile_smoke.sh --root . --write-report reports/queue_compile_smoke.json --timeout-seconds 20 --passes 3 --jobs 1

hold-compile-triage-verify:
	python3 -B publishing/check_queue_compile_smoke.py --root . --report-path release_queue/HOLD_COMPILE_TRIAGE.json --states hold --require-digest-receipts --require-reproducible-receipts

unqueued-compile-triage:
	python3 -B publishing/check_unqueued_compile_triage.py --root . --run-live --write-report release_queue/UNQUEUED_COMPILE_TRIAGE.json --write-md release_queue/UNQUEUED_COMPILE_TRIAGE.md --timeout-seconds 30 --passes 3

unqueued-compile-triage-verify:
	python3 -B publishing/check_unqueued_compile_triage.py --root . --report-path release_queue/UNQUEUED_COMPILE_TRIAGE.json

published-compile-triage:
	python3 -B publishing/check_published_compile_triage.py --root . --run-live --write-report published/PUBLISHED_COMPILE_TRIAGE.json --write-md published/PUBLISHED_COMPILE_TRIAGE.md --timeout-seconds 60 --passes 3

published-compile-triage-verify:
	python3 -B publishing/check_published_compile_triage.py --root . --report-path published/PUBLISHED_COMPILE_TRIAGE.json

auxiliary-tex-compile-triage:
	python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --run-live --write-report index/AUXILIARY_TEX_COMPILE_TRIAGE.json --write-md index/AUXILIARY_TEX_COMPILE_TRIAGE.md --timeout-seconds 30 --passes 3

auxiliary-tex-compile-triage-verify:
	python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --report-path index/AUXILIARY_TEX_COMPILE_TRIAGE.json

tooling-static-smoke:
	python3 -B publishing/check_tooling_static_integrity.py --root .

live-compile-lock-self-test:
	python3 -B publishing/live_compile_lock.py --root . --self-test

python-entrypoint-smoke:
	python3 -B publishing/check_python_entrypoint_smoke.py --root . --write-report reports/python_entrypoint_smoke.json

verify-surfaces:
	python3 -S -B publishing/run_verify_surfaces.py --root .

verify-surfaces-expanded:
	python3 -B publishing/check_toolchain_fingerprint.py --root .
	python3 -B publishing/live_compile_lock.py --root . --self-test
	python3 -B publishing/check_archive_coherence.py --root .
	python3 -B publishing/check_archive_invariants.py --root .
	python3 -B publishing/check_surface_schemas.py --root .
	python3 -B publishing/check_transient_surface.py --root .
	python3 -B publishing/check_tooling_static_integrity.py --root .
	python3 -B publishing/check_python_entrypoint_smoke.py --root .
	python3 -B publishing/check_support_manifest_integrity.py --root .
	python3 -B publishing/check_worked_example_payload_pointers.py --root .
	python3 -B publishing/check_worked_example_validation.py --root .
	python3 -B publishing/check_hostile_review_vectors.py --root .
	python3 -B publishing/check_threat_transfer_matrix.py --root .
	python3 -B publishing/check_external_hostile_review_packet.py --root .
	python3 -B publishing/check_queue_compile_smoke.py --root . --report-path reports/queue_compile_smoke.json --require-digest-receipts --require-reproducible-receipts
	python3 -B publishing/check_queue_compile_smoke.py --root . --report-path release_queue/HOLD_COMPILE_TRIAGE.json --states hold --require-digest-receipts --require-reproducible-receipts
	python3 -B publishing/check_unqueued_compile_triage.py --root . --report-path release_queue/UNQUEUED_COMPILE_TRIAGE.json
	python3 -B publishing/check_published_compile_triage.py --root . --report-path published/PUBLISHED_COMPILE_TRIAGE.json
	python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --report-path index/AUXILIARY_TEX_COMPILE_TRIAGE.json

package: verify-surfaces
	python3 -B publishing/build_archive_zip.py --root . --out-dir $(OUT_DIR)
