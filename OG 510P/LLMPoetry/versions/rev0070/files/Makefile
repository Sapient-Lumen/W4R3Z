.PHONY: bloom-false-positive wal-poem reader-field-kit deep-surface fallback-subtraction candidate-pressure reader-handoff-bundle reader-response-intake candidate-reader validate validation-report manifest package metrics research-law research-pulses invariants quote-receipts human-questions pilot-queue style-firewall poem-records branch-selector selector-map selector-vector loss-budget state-switch ergodic-traversal zero-route return-diff patch-application reader-state external-material source-snapshots release-surfaces render-branch judgment-firewall surface-apparatus surface-freshness revision-lineage open-questions source-health doctor oci-whiteout release-zip

STAMP ?= 2026.06.18.17.17
SLUG ?= allthreebitssaidyes-bloomfalsepresence-releasescaffoldprune-hardwater
DRAFT ?= poems/P0001/draft_010.md
PACKET ?= poems/P0001/branches/branch_packet_010.json
SELECTOR_MAP ?= poems/P0001/verification/selector_map_010.json
SELECTOR_VECTOR ?= poems/P0001/verification/selector_vector_010.json
LOSS_BUDGET ?= poems/P0001/verification/loss_budget_010.json
STATE_SWITCH ?= poems/P0001/verification/state_switch_010.json
ERGODIC_TRAVERSAL ?= poems/P0001/verification/ergodic_traversal_010.json
ZERO_ROUTE ?= poems/P0001/verification/zero_route_008.json
RETURN_DIFF ?= poems/P0001/verification/return_diff_010.json
PATCH_APPLICATION ?= poems/P0001/verification/patch_application_010.json
CURRENT_DRAFT ?= poems/P0005/draft_001.md
EXTERNAL_MATERIAL_PACKET ?= poems/P0005/material/source_material_packet_001.json
PREVIOUS_PACKET ?= poems/P0001/branches/branch_packet_009.json
PREVIOUS_ROUTE_RECEIPT ?= poems/P0001/verification/ergodic_traversal_009.json
OUT ?= ../LLMPoetry-rev0070-2026.06.18.17.17-allthreebitssaidyes-bloomfalsepresence-releasescaffoldprune-hardwater.zip

validate:
	python3 tools/llmpoetry_validate.py --root .

validation-report:
	python3 tools/llmpoetry_validate.py --root . --write-report

research-law:
	python3 tools/check_research_law.py .

research-pulses:
	python3 tools/check_research_pulses.py .

invariants:
	python3 tools/check_archive_invariants.py .

quote-receipts:
	python3 tools/check_quote_receipts.py .

human-questions:
	python3 tools/check_human_questions.py .

pilot-queue:
	python3 tools/check_pilot_queue.py .

style-firewall:
	python3 tools/check_style_firewall.py .

poem-records:
	python3 tools/check_poem_records.py .

branch-selector:
	python3 tools/check_branch_selector.py .

selector-map:
	python3 tools/check_selector_map.py .

selector-vector:
	python3 tools/check_selector_vector.py .

loss-budget:
	python3 tools/check_loss_budget.py .

state-switch:
	python3 tools/check_state_switch.py .

ergodic-traversal:
	python3 tools/check_ergodic_traversal.py .

zero-route:
	python3 tools/check_zero_route.py .

return-diff:
	python3 tools/check_return_diff.py .

patch-application:
	python3 tools/check_patch_application.py .

reader-state:
	python3 tools/check_reader_state_object.py .

external-material:
	python3 tools/check_external_material_pressure.py .

judgment-firewall:
	python3 tools/check_judgment_firewall.py .

surface-apparatus:
	python3 tools/check_surface_apparatus_split.py .

surface-freshness:
	python3 tools/check_surface_freshness.py .

revision-lineage:
	python3 tools/check_revision_lineage_freshness.py .

open-questions:
	python3 tools/check_open_questions_canonical.py .

source-health:
	python3 tools/check_source_health_coverage.py .

source-snapshots:
	python3 tools/check_source_snapshots.py .

release-surfaces:
	python3 tools/check_release_surfaces.py .

candidate-reader:
	python3 tools/check_candidate_reader_packet.py .

reader-response-intake:
	python3 tools/check_reader_response_intake.py .

candidate-pressure:
	python3 tools/check_candidate_pressure.py .

fallback-subtraction:
	python3 tools/check_fallback_subtraction.py .

reader-handoff-bundle:
	python3 tools/build_reader_handoff_bundle.py --root .
	python3 tools/check_reader_handoff_bundle.py .

reader-field-kit:
	python3 tools/build_reader_field_kit.py --root .
	python3 tools/check_pilot_queue.py .

render-branch:
	python3 tools/render_branch_lattice.py "$(PACKET)" --out "$(DRAFT)"
	python3 tools/build_selector_map.py "$(PACKET)" "$(DRAFT)" --out "$(SELECTOR_MAP)"
	python3 tools/build_selector_vector.py "$(PACKET)" "$(SELECTOR_MAP)" --out "$(SELECTOR_VECTOR)"
	python3 tools/build_loss_budget.py "$(PACKET)" "$(DRAFT)" "$(SELECTOR_VECTOR)" --out "$(LOSS_BUDGET)"
	python3 tools/build_state_switch.py "$(PACKET)" "$(SELECTOR_VECTOR)" --out "$(STATE_SWITCH)"
	python3 tools/build_ergodic_traversal.py "$(PACKET)" "$(DRAFT)" --out "$(ERGODIC_TRAVERSAL)"
	python3 tools/build_return_diff.py "$(PREVIOUS_PACKET)" "$(PACKET)" "$(DRAFT)" --previous-route-receipt "$(PREVIOUS_ROUTE_RECEIPT)" --out "$(RETURN_DIFF)"
	python3 tools/build_patch_application.py "$(PACKET)" "$(DRAFT)" "$(ERGODIC_TRAVERSAL)" --previous-route-receipt "$(PREVIOUS_ROUTE_RECEIPT)" --out "$(PATCH_APPLICATION)"
	python3 tools/build_reader_state_object.py --root . --revision rev0024 --turn 16 --timestamp 2026-06-14T19:47:00-04:00

metrics:
	python3 tools/poem_metrics.py "$(DRAFT)" --root .

deep-surface:
	python3 tools/check_deep_surface_consistency.py .

bloom-false-positive:
	python3 tools/check_bloom_false_positive_poem.py .

oci-whiteout:
	python3 tools/check_oci_whiteout_poem.py .

release-zip:
	python3 tools/check_release_zip.py --zip "$(OUT)" --root .

wal-poem:
	python3 tools/check_wal_poem.py .

doctor:
	python3 tools/doctor.py --root .

manifest:
	python3 tools/build_manifest.py --root .

package: manifest validate
	python3 tools/package_release.py --root . --out $(OUT)
