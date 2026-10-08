.PHONY: lint lint-fast lint-release-controls lint-owner-reply lint-full context-pack surface-map branch-family-index toolchain-registry owner-field-next owner-field-work owner-field-report owner-request-packet owner-route-block owner-after-human-send owner-returned-reply-work owner-send-log owner-reask-log owner-contact-status owner-reply-smoke owner-reply-receipt owner-reply-intake owner-reply-workbench-seed owner-workbench-review-brief owner-workbench-review owner-first-packet-decision-brief owner-first-packet-decision owner-post-decision-change-ticket-brief owner-activation-live-window-brief owner-live-window-terminal-brief owner-live-window-readout-brief owner-post-readout-action-brief owner-activation-receipt owner-post-decision-change-ticket owner-live-window-card owner-live-window-readout owner-post-readout-action owner-post-readout-recheck-brief owner-post-readout-recheck owner-post-readout-context-receipt readability-wrap field-handoff-bundle micro-pilot-pack micro-pilot-followthrough-pack micro-pilot-dry-run micro-pilot-readiness micro-pilot-next micro-pilot-owner-review micro-pilot-result package-release handoff-release

PYTHON ?= python3
export CUBE_PYTHON ?= $(PYTHON)

lint:
	$(PYTHON) tools/run_lint_suite.py --lane full-release

lint-fast:
	$(PYTHON) tools/run_lint_suite.py --lane fast-changed

lint-release-controls:
	$(PYTHON) tools/run_lint_suite.py --lane release-controls

lint-owner-reply:
	$(PYTHON) tools/run_lint_suite.py --lane owner-reply-field

lint-full:
	$(PYTHON) tools/run_lint_suite.py --lane full-release

context-pack:
	$(PYTHON) tools/gen_context_pack.py

surface-map:
	$(PYTHON) tools/gen_surface_map.py

branch-family-index:
	$(PYTHON) tools/gen_branch_family_index.py

toolchain-registry:
	$(PYTHON) tools/check_toolchain_registry.py

owner-field-next:
	$(PYTHON) tools/decide_ft0181_field_next_action.py $(if $(SCRATCH),--scratch-root "$(SCRATCH)",) $(if $(CSV),--returned-csv "$(CSV)",) $(if $(AS_OF_DATE),--as-of-date "$(AS_OF_DATE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-field-work:
	$(PYTHON) tools/decide_ft0181_field_next_action.py --execute-safe-local $(if $(SCRATCH),--scratch-root "$(SCRATCH)",) $(if $(CSV),--returned-csv "$(CSV)",) $(if $(AS_OF_DATE),--as-of-date "$(AS_OF_DATE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(PACKET_OUT),--packet-output-dir "$(PACKET_OUT)",) $(if $(OVERWRITE),--overwrite,)


owner-field-report:
	$(PYTHON) tools/report_ft0181_field_lane.py $(if $(SCRATCH),--scratch-root "$(SCRATCH)",) $(if $(AS_OF_DATE),--as-of-date "$(AS_OF_DATE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-request-packet:
	$(PYTHON) tools/prepare_ft0181_owner_request_packet.py $(if $(OUT),--output-dir "$(OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(RETURN_DATE),--return-date "$(RETURN_DATE)",) $(if $(OVERWRITE),--overwrite,)

owner-route-block:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/.../packet-manifest.json from owner-request-packet or owner-field-next fallback)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-confirmed-owner-route-block-no-send"; exit 1)
	$(PYTHON) tools/record_ft0181_owner_route_block.py --packet-manifest "$(PACKET)" --operator-confirmation "$(CONFIRM)" $(if $(BLOCK_DATE),--block-date "$(BLOCK_DATE)",) $(if $(BLOCK_CLASS),--block-class "$(BLOCK_CLASS)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(REASON),--minimal-reason "$(REASON)",) $(if $(OVERWRITE),--overwrite,)

owner-after-human-send:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/.../packet-manifest.json from owner-field-work/owner-field-next)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-sent-bounded-owner-request"; exit 1)
	$(PYTHON) tools/record_ft0181_owner_after_human_send.py --packet-manifest "$(PACKET)" --operator-confirmation "$(CONFIRM)" $(if $(SENT_DATE),--sent-date "$(SENT_DATE)",) $(if $(RESPONSE_DUE_DATE),--response-due-date "$(RESPONSE_DUE_DATE)",) $(if $(STATUS_DATE),--status-date "$(STATUS_DATE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(SEND_LOG_OUT),--send-log-dir "$(SEND_LOG_OUT)",) $(if $(CONTACT_STATUS_OUT),--contact-status-dir "$(CONTACT_STATUS_OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(SEND_CHANNEL_CLASS),--send-channel-class "$(SEND_CHANNEL_CLASS)",) $(if $(OWNER_ROUTE_CLASS),--owner-route-class "$(OWNER_ROUTE_CLASS)",) $(if $(ADAPTED_FROM_PACKET),--adapted-from-packet,) $(if $(SEND_NOTE),--minimal-send-note "$(SEND_NOTE)",) $(if $(OVERWRITE),--overwrite,)

owner-returned-reply-work:
	@test -n "$(CSV)" || (echo "CSV required (actual returned owner reply CSV/source packet path)"; exit 1)
	@test -n "$(SOURCE_CONTACT_STATUS)$(SOURCE_POST_READOUT_CONTEXT_RECEIPT)" || (echo "SOURCE_CONTACT_STATUS or SOURCE_POST_READOUT_CONTEXT_RECEIPT required (use owner-field-next emitted command)"; exit 1)
	$(PYTHON) tools/run_ft0181_returned_reply_work.py --csv "$(CSV)" $(if $(SOURCE_CONTACT_STATUS),--source-contact-status "$(SOURCE_CONTACT_STATUS)",) $(if $(SOURCE_POST_READOUT_CONTEXT_RECEIPT),--source-post-readout-context-receipt "$(SOURCE_POST_READOUT_CONTEXT_RECEIPT)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(INTAKE_OUT),--intake-dir "$(INTAKE_OUT)",) $(if $(SEED_OUT),--seed-dir "$(SEED_OUT)",) $(if $(REVIEW_BRIEF_OUT),--review-brief-dir "$(REVIEW_BRIEF_OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-send-log:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/.../packet-manifest.json from owner-field-next)"; exit 1)
	@test -n "$(SENT_DATE)" || (echo "SENT_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(RESPONSE_DUE_DATE)" || (echo "RESPONSE_DUE_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required (use the send-log token emitted by owner-field-next)"; exit 1)
	$(PYTHON) tools/record_ft0181_owner_send_log.py --packet-manifest "$(PACKET)" --sent-date "$(SENT_DATE)" --response-due-date "$(RESPONSE_DUE_DATE)" --operator-confirmation "$(CONFIRM)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(SEND_CHANNEL_CLASS),--send-channel-class "$(SEND_CHANNEL_CLASS)",) $(if $(OWNER_ROUTE_CLASS),--owner-route-class "$(OWNER_ROUTE_CLASS)",) $(if $(ADAPTED_FROM_PACKET),--adapted-from-packet,) $(if $(SEND_NOTE),--minimal-send-note "$(SEND_NOTE)",) $(if $(OVERWRITE),--overwrite,)


owner-reask-log:
	@test -n "$(SOURCE_ARTIFACT)" || (echo "SOURCE_ARTIFACT required (prior SENT clock, RE-ASK-ONCE intake bundle, or REASK-OWNER workbench review)"; exit 1)
	@test -n "$(SENT_DATE)" || (echo "SENT_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(RESPONSE_DUE_DATE)" || (echo "RESPONSE_DUE_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required (use the reask-log token emitted by owner-field-next)"; exit 1)
	$(PYTHON) tools/record_ft0181_owner_reask_log.py --source-artifact "$(SOURCE_ARTIFACT)" --sent-date "$(SENT_DATE)" --response-due-date "$(RESPONSE_DUE_DATE)" --operator-confirmation "$(CONFIRM)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(REASK_CHANNEL_CLASS),--reask-channel-class "$(REASK_CHANNEL_CLASS)",) $(if $(OWNER_ROUTE_CLASS),--owner-route-class "$(OWNER_ROUTE_CLASS)",) $(if $(ADAPTED_FROM_TEMPLATE),--adapted-from-template,) $(if $(REASK_NOTE),--minimal-reask-note "$(REASK_NOTE)",) $(if $(OVERWRITE),--overwrite,)

owner-contact-status:
	@test -n "$(STATUS)" || (echo "STATUS required (sent-awaiting-reply, reask-awaiting-reply, or no-owner-packet)"; exit 1)
	@test -n "$(SENT_DATE)" || (echo "SENT_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(RESPONSE_DUE_DATE)" || (echo "RESPONSE_DUE_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required (use the status-specific token emitted by owner-field-next)"; exit 1)
	@test -n "$(SOURCE_ARTIFACT)" || (echo "SOURCE_ARTIFACT required (use the path emitted by owner-field-next)"; exit 1)
	$(PYTHON) tools/record_ft0181_owner_contact_status.py --status "$(STATUS)" --sent-date "$(SENT_DATE)" --response-due-date "$(RESPONSE_DUE_DATE)" --operator-confirmation "$(CONFIRM)" --source-artifact "$(SOURCE_ARTIFACT)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(STATUS_DATE),--status-date "$(STATUS_DATE)",) $(if $(ATTEMPT_COUNT),--attempt-count "$(ATTEMPT_COUNT)",) $(if $(REASON),--minimal-reason "$(REASON)",) $(if $(OVERWRITE),--overwrite,)

owner-reply-smoke:
	$(PYTHON) tools/smoke_owner_reply_pipeline.py --json

owner-reply-receipt:
	@test -n "$(CSV)" || (echo "CSV required (path to returned owner reply CSV)"; exit 1)
	$(PYTHON) tools/receipt_owner_reply_csv.py "$(CSV)"

owner-reply-intake:
	@test -n "$(CSV)" || (echo "CSV required (path to returned owner reply CSV)"; exit 1)
	@test -n "$(SOURCE_CONTACT_STATUS)$(SOURCE_POST_READOUT_CONTEXT_RECEIPT)" || (echo "SOURCE_CONTACT_STATUS or SOURCE_POST_READOUT_CONTEXT_RECEIPT required (use the owner-field-next emitted command)"; exit 1)
	$(PYTHON) tools/intake_owner_reply_csv.py "$(CSV)" $(if $(SOURCE_CONTACT_STATUS),--source-contact-status "$(SOURCE_CONTACT_STATUS)",) $(if $(SOURCE_POST_READOUT_CONTEXT_RECEIPT),--source-post-readout-context-receipt "$(SOURCE_POST_READOUT_CONTEXT_RECEIPT)",) $(if $(OUT),--output-dir "$(OUT)",)

owner-reply-workbench-seed:
	@test -n "$(BUNDLE)" || (echo "BUNDLE required (path to local owner-reply intake bundle directory)"; exit 1)
	$(PYTHON) tools/seed_owner_packet_workbench.py "$(BUNDLE)" $(if $(OUT),--output-dir "$(OUT)",)

owner-workbench-review-brief:
	@test -n "$(SEED)" || (echo "SEED required (scratch/.../workbench-seed.json)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_workbench_review_brief.py --seed "$(SEED)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-workbench-review:
	@test -n "$(SEED)" || (echo "SEED required (scratch/.../workbench-seed.json)"; exit 1)
	@test -n "$(DECISION)" || (echo "DECISION required (proceed-decision-board, reask-owner, block-overbroad, block-protected, block-security, block-evidence, no-change-trim)"; exit 1)
	@test -n "$(SOURCE_TRUTH_CLASS)" || (echo "SOURCE_TRUTH_CLASS required (e.g. SRC2-CANDIDATE-NOT-ACCEPTED, SRC2, or UNVERIFIED-OWNER-REPLY)"; exit 1)
	@test -n "$(REVIEW_BASIS)" || (echo "REVIEW_BASIS required (owner-attested-aggregate, needs-clarification, raw-or-protected-risk, weak-evidence-only, decision-neutral, security-abstraction-needed, overbroad-export-risk)"; exit 1)
	@test -n "$(SURVIVING_FIELD_COUNT)" || (echo "SURVIVING_FIELD_COUNT required (0-8)"; exit 1)
	@test -n "$(DECISION_CHANGED_COUNT)" || (echo "DECISION_CHANGED_COUNT required (0-8)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-reviewed-minimized-workbench-record"; exit 1)
	$(PYTHON) tools/record_ft0181_workbench_review.py --seed "$(SEED)" --decision "$(DECISION)" --source-truth-class "$(SOURCE_TRUTH_CLASS)" --review-basis "$(REVIEW_BASIS)" --surviving-field-count "$(SURVIVING_FIELD_COUNT)" --decision-changed-count "$(DECISION_CHANGED_COUNT)" $(if $(LOCAL_ONLY_FIELD_COUNT),--local-only-field-count "$(LOCAL_ONLY_FIELD_COUNT)",) $(if $(TRIMMED_FIELD_COUNT),--trimmed-field-count "$(TRIMMED_FIELD_COUNT)",) $(if $(REASK_FIELD_COUNT),--reask-field-count "$(REASK_FIELD_COUNT)",) $(if $(REVIEWER_ROLE_COUNT),--reviewer-role-count "$(REVIEWER_ROLE_COUNT)",) --operator-confirmation "$(CONFIRM)" $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-first-packet-decision-brief:
	@test -n "$(REVIEW)" || (echo "REVIEW required (scratch/.../workbench-review.json with PROCEED-DECISION-BOARD)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_first_packet_decision_brief.py --review "$(REVIEW)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-first-packet-decision:
	@test -n "$(REVIEW)" || (echo "REVIEW required (scratch/.../workbench-review.json)"; exit 1)
	@test -n "$(AUTHORITY_ACTION)" || (echo "AUTHORITY_ACTION required (keep-lower-ceiling, revise-ceiling, block, no-change)"; exit 1)
	@test -n "$(EVIDENCE_ACTION)" || (echo "EVIDENCE_ACTION required (suppress, downgrade, keep-example-only, stage-claim-with-expiry, no-change)"; exit 1)
	@test -n "$(CONSTRUCT_ACTION)" || (echo "CONSTRUCT_ACTION required (add-stop-trigger, keep-teacher-review, require-unaided-segment, fall-back-service, no-change)"; exit 1)
	@test -n "$(PUBLIC_ACTION)" || (echo "PUBLIC_ACTION required (publish-limited, revise-claims, suppress, draft-only, no-change)"; exit 1)
	@test -n "$(LIFECYCLE_ACTION)" || (echo "LIFECYCLE_ACTION required (sandbox, pilot, watch, deprecate, archive-only, quarantine, no-change)"; exit 1)
	@test -n "$(CHANGED_SLICE_COUNT)" || (echo "CHANGED_SLICE_COUNT required (number of non-no-change slices, 1-5)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-recorded-five-slice-decision-board"; exit 1)
	$(PYTHON) tools/record_ft0181_first_packet_decision.py --review "$(REVIEW)" --authority-action "$(AUTHORITY_ACTION)" --evidence-action "$(EVIDENCE_ACTION)" --construct-action "$(CONSTRUCT_ACTION)" --public-action "$(PUBLIC_ACTION)" --lifecycle-action "$(LIFECYCLE_ACTION)" --changed-slice-count "$(CHANGED_SLICE_COUNT)" $(if $(ROLLBACK_OWNER_ROLE_COUNT),--rollback-owner-role-count "$(ROLLBACK_OWNER_ROLE_COUNT)",) --operator-confirmation "$(CONFIRM)" $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-post-decision-change-ticket-brief:
	@test -n "$(DECISION)" || (echo "DECISION required (scratch/.../first-packet-decision.json)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_post_decision_change_ticket_brief.py --decision "$(DECISION)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)


owner-activation-live-window-brief:
	@test -n "$(TICKET)" || (echo "TICKET required (scratch/.../post-decision-change-ticket.json in ready-for-real-packet or active-change state)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_activation_live_window_brief.py --ticket "$(TICKET)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-live-window-terminal-brief:
	@test -n "$(CARD)" || (echo "CARD required (scratch/.../live-window-card.json in staged or active state)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_live_window_terminal_brief.py --card "$(CARD)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-live-window-readout-brief:
	@test -n "$(CARD)" || (echo "CARD required (scratch/.../live-window-card.json in paused, rolled-back, completed-no-closure, or quarantined state)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_live_window_readout_brief.py --card "$(CARD)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-post-readout-action-brief:
	@test -n "$(READOUT)" || (echo "READOUT required (scratch/.../live-window-readout.json from owner-live-window-readout)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_post_readout_action_brief.py --readout "$(READOUT)" $(if $(AS_OF_DATE),--as-of-date "$(AS_OF_DATE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)



owner-activation-receipt:
	@test -n "$(DECISION)" || (echo "DECISION required (scratch/.../first-packet-decision.json)"; exit 1)
	@test -n "$(SOURCE_PACKET)" || (echo "SOURCE_PACKET required (path to real owner-reviewed SRC2+ packet, outside controlled archive surfaces or under scratch/)"; exit 1)
	@test -n "$(SOURCE_TRUTH_CLASS)" || (echo "SOURCE_TRUTH_CLASS required (SRC2, SRC3, or SRC4)"; exit 1)
	@test -n "$(ACCEPTED_FIELD_COUNT)" || (echo "ACCEPTED_FIELD_COUNT required (1-8)"; exit 1)
	@test -n "$(REVIEWER_ROLE_COUNT)" || (echo "REVIEWER_ROLE_COUNT required (2-5)"; exit 1)
	@test -n "$(DICTIONARY_OR_MAP_REF_COUNT)" || (echo "DICTIONARY_OR_MAP_REF_COUNT required (1-10)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-confirmed-real-packet-accepted-for-active-change"; exit 1)
	$(PYTHON) tools/record_ft0181_activation_receipt.py --decision "$(DECISION)" --source-packet "$(SOURCE_PACKET)" --source-truth-class "$(SOURCE_TRUTH_CLASS)" --accepted-field-count "$(ACCEPTED_FIELD_COUNT)" --reviewer-role-count "$(REVIEWER_ROLE_COUNT)" --dictionary-or-map-ref-count "$(DICTIONARY_OR_MAP_REF_COUNT)" $(if $(BLOCKED_OR_TRIMMED_FIELD_COUNT),--blocked-or-trimmed-field-count "$(BLOCKED_OR_TRIMMED_FIELD_COUNT)",) --operator-confirmation "$(CONFIRM)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-post-decision-change-ticket:
	@test -n "$(DECISION)" || (echo "DECISION required (scratch/.../first-packet-decision.json)"; exit 1)
	@test -n "$(TICKET_STATE)" || (echo "TICKET_STATE required (blocked-no-real-packet, blocked-incomplete-board, ready-for-real-packet, active-change, rolled-back, quarantined)"; exit 1)
	@test -n "$(CHANGE_CLASS)" || (echo "CHANGE_CLASS required (pct-a-trim, pct-b-suppress, pct-c-sandbox-adjustment, pct-d-bounded-pilot, pct-x-quarantine)"; exit 1)
	@test -n "$(SOURCE_TRUTH_REQUIRED)" || (echo "SOURCE_TRUTH_REQUIRED required (SRC2/SRC3/SRC4 for active bounded use; not_evidence only for blocked rehearsal)"; exit 1)
	@test -n "$(ALLOWED_CHANGE_COUNT)" || (echo "ALLOWED_CHANGE_COUNT required (0-5; ready/active require at least 1)"; exit 1)
	@test -n "$(PROHIBITED_CHANGE_COUNT)" || (echo "PROHIBITED_CHANGE_COUNT required (1-10)"; exit 1)
	@test -n "$(ROLLBACK_TRIGGER_COUNT)" || (echo "ROLLBACK_TRIGGER_COUNT required (1-10)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-recorded-bounded-post-decision-change-ticket"; exit 1)
	$(PYTHON) tools/record_ft0181_post_decision_change_ticket.py --decision "$(DECISION)" --ticket-state "$(TICKET_STATE)" --change-class "$(CHANGE_CLASS)" --source-truth-required "$(SOURCE_TRUTH_REQUIRED)" --allowed-change-count "$(ALLOWED_CHANGE_COUNT)" --prohibited-change-count "$(PROHIBITED_CHANGE_COUNT)" --rollback-trigger-count "$(ROLLBACK_TRIGGER_COUNT)" $(if $(ROLLBACK_OWNER_ROLE_COUNT),--rollback-owner-role-count "$(ROLLBACK_OWNER_ROLE_COUNT)",) $(if $(PUBLIC_CLAIM_CEILING),--public-claim-ceiling "$(PUBLIC_CLAIM_CEILING)",) --operator-confirmation "$(CONFIRM)" $(if $(LIVE_WINDOW_REQUIRED),--live-window-required,) $(if $(ACTIVATION_RECEIPT),--activation-receipt "$(ACTIVATION_RECEIPT)",) $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)


owner-live-window-card:
	@test -n "$(TICKET)" || (echo "TICKET required (scratch/.../post-decision-change-ticket.json)"; exit 1)
	@test -n "$(WINDOW_STATE)" || (echo "WINDOW_STATE required (blocked-no-real-packet, blocked-incomplete-ticket, staged, active, paused, rolled-back, completed-no-closure, quarantined)"; exit 1)
	@test -n "$(SOURCE_TRUTH_CLASS)" || (echo "SOURCE_TRUTH_CLASS required (SRC0 for blocked rehearsal; SRC2/SRC3/SRC4 for live/staged windows)"; exit 1)
	@test -n "$(WINDOW_DAY_COUNT)" || (echo "WINDOW_DAY_COUNT required (0 for blocked; 1-14 for live/staged)"; exit 1)
	@test -n "$(ALLOWED_ACTIVITY_COUNT)" || (echo "ALLOWED_ACTIVITY_COUNT required (0-5; live/staged require at least 1)"; exit 1)
	@test -n "$(PROHIBITED_ACTIVITY_COUNT)" || (echo "PROHIBITED_ACTIVITY_COUNT required (1-10)"; exit 1)
	@test -n "$(STOP_TRIGGER_COUNT)" || (echo "STOP_TRIGGER_COUNT required (1-10)"; exit 1)
	@test -n "$(ROLLBACK_STEP_COUNT)" || (echo "ROLLBACK_STEP_COUNT required (1-10)"; exit 1)
	@test -n "$(EVIDENCE_READOUT_COUNT)" || (echo "EVIDENCE_READOUT_COUNT required (0-7)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-recorded-bounded-live-window-card"; exit 1)
	$(PYTHON) tools/record_ft0181_live_window_card.py --ticket "$(TICKET)" --window-state "$(WINDOW_STATE)" --source-truth-class "$(SOURCE_TRUTH_CLASS)" --window-day-count "$(WINDOW_DAY_COUNT)" --allowed-activity-count "$(ALLOWED_ACTIVITY_COUNT)" --prohibited-activity-count "$(PROHIBITED_ACTIVITY_COUNT)" --stop-trigger-count "$(STOP_TRIGGER_COUNT)" --rollback-step-count "$(ROLLBACK_STEP_COUNT)" $(if $(ROLLBACK_OWNER_ROLE_COUNT),--rollback-owner-role-count "$(ROLLBACK_OWNER_ROLE_COUNT)",) --evidence-readout-count "$(EVIDENCE_READOUT_COUNT)" $(if $(PUBLIC_CLAIM_CEILING),--public-claim-ceiling "$(PUBLIC_CLAIM_CEILING)",) --operator-confirmation "$(CONFIRM)" $(if $(NO_EXPANSION_CONFIRMED),--no-expansion-confirmed,) $(if $(HUMAN_PAUSE_CONFIRMED),--human-pause-confirmed,) $(if $(FALLBACK_ROUTE_CONFIRMED),--fallback-route-confirmed,) $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)



owner-live-window-readout:
	@test -n "$(CARD)" || (echo "CARD required (scratch/.../live-window-card.json in paused, rolled-back, completed-no-closure, or quarantined state)"; exit 1)
	@test -n "$(WINDOW_DISPOSITION)" || (echo "WINDOW_DISPOSITION required (stopped, rolled-back, continue-bounded, rerun-narrower, quarantine, no-change)"; exit 1)
	@test -n "$(SOURCE_TRUTH_CLASS)" || (echo "SOURCE_TRUTH_CLASS required (must match terminal card SRC2/SRC3/SRC4)"; exit 1)
	@test -n "$(AGGREGATE_EVIDENCE_READ_COUNT)" || (echo "AGGREGATE_EVIDENCE_READ_COUNT required (1-7)"; exit 1)
	@test -n "$(CLAIM_FAMILY_EFFECT_COUNT)" || (echo "CLAIM_FAMILY_EFFECT_COUNT required (1-8)"; exit 1)
	@test -n "$(DECISION_DELTA_COUNT)" || (echo "DECISION_DELTA_COUNT required (0-8; continue/rerun require at least 1)"; exit 1)
	@test -n "$(FIELD_TRIM_COUNT)" || (echo "FIELD_TRIM_COUNT required (0-8; rerun/no-change require at least 1)"; exit 1)
	@test -n "$(REVIEWER_ROLE_COUNT)" || (echo "REVIEWER_ROLE_COUNT required (2-5)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-recorded-aggregate-readout-no-closure"; exit 1)
	$(PYTHON) tools/record_ft0181_live_window_readout.py --card "$(CARD)" --window-disposition "$(WINDOW_DISPOSITION)" --source-truth-class "$(SOURCE_TRUTH_CLASS)" --aggregate-evidence-read-count "$(AGGREGATE_EVIDENCE_READ_COUNT)" --claim-family-effect-count "$(CLAIM_FAMILY_EFFECT_COUNT)" --decision-delta-count "$(DECISION_DELTA_COUNT)" --field-trim-count "$(FIELD_TRIM_COUNT)" --reviewer-role-count "$(REVIEWER_ROLE_COUNT)" $(if $(UNRESOLVED_DISAGREEMENT_COUNT),--unresolved-disagreement-count "$(UNRESOLVED_DISAGREEMENT_COUNT)",) $(if $(PUBLIC_CLAIM_CEILING),--public-claim-ceiling "$(PUBLIC_CLAIM_CEILING)",) --operator-confirmation "$(CONFIRM)" $(if $(NO_PUBLIC_CLAIM_UPGRADE),--no-public-claim-upgrade,) $(if $(NO_SERVICE_RECORD_EDIT),--no-service-record-edit,) $(if $(NO_LIFECYCLE_CHANGE),--no-lifecycle-change,) $(if $(NO_CLOSURE_FROM_READOUT),--no-closure-from-readout,) $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)


owner-post-readout-action:
	@test -n "$(READOUT)" || (echo "READOUT required (scratch/.../live-window-readout.json from owner-live-window-readout)"; exit 1)
	@test -n "$(DISPATCH_LANE)" || (echo "DISPATCH_LANE required (blocked-no-real-packet, stop, rollback-confirmed, rerun-narrower, continue-same-ceiling, quarantine, or no-change-trim)"; exit 1)
	@test -n "$(SOURCE_TRUTH_CLASS)" || (echo "SOURCE_TRUTH_CLASS required (must match source readout SRC2/SRC3/SRC4)"; exit 1)
	@test -n "$(ALLOWED_ACTION_COUNT)" || (echo "ALLOWED_ACTION_COUNT required (0-5; most lanes require at least 1)"; exit 1)
	@test -n "$(PROHIBITED_ACTION_COUNT)" || (echo "PROHIBITED_ACTION_COUNT required (2-10)"; exit 1)
	@test -n "$(FIELD_TO_REASK_COUNT)" || (echo "FIELD_TO_REASK_COUNT required (0-8; rerun requires at least 1)"; exit 1)
	@test -n "$(FIELD_TO_DROP_COUNT)" || (echo "FIELD_TO_DROP_COUNT required (0-8; rerun/no-change require at least 1)"; exit 1)
	@test -n "$(REVIEWER_ROLE_COUNT)" || (echo "REVIEWER_ROLE_COUNT required (2-5)"; exit 1)
	@test -n "$(DUE_OR_RECHECK_DATE)" || (echo "DUE_OR_RECHECK_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-recorded-post-readout-action-no-closure"; exit 1)
	$(PYTHON) tools/record_ft0181_post_readout_action.py --readout "$(READOUT)" --dispatch-lane "$(DISPATCH_LANE)" --source-truth-class "$(SOURCE_TRUTH_CLASS)" --allowed-action-count "$(ALLOWED_ACTION_COUNT)" --prohibited-action-count "$(PROHIBITED_ACTION_COUNT)" --field-to-reask-count "$(FIELD_TO_REASK_COUNT)" --field-to-drop-count "$(FIELD_TO_DROP_COUNT)" --reviewer-role-count "$(REVIEWER_ROLE_COUNT)" --due-or-recheck-date "$(DUE_OR_RECHECK_DATE)" --operator-confirmation "$(CONFIRM)" $(if $(UNRESOLVED_DISAGREEMENT_COUNT),--unresolved-disagreement-count "$(UNRESOLVED_DISAGREEMENT_COUNT)",) $(if $(OWNER_ACTION_CLASS),--owner-action-class "$(OWNER_ACTION_CLASS)",) $(if $(NEXT_EVIDENCE_ASK_CLASS),--next-evidence-ask-class "$(NEXT_EVIDENCE_ASK_CLASS)",) $(if $(PUBLIC_LANGUAGE_ACTION),--public-language-action "$(PUBLIC_LANGUAGE_ACTION)",) $(if $(NO_EXPANSION_CONFIRMED),--no-expansion-confirmed,) $(if $(NO_PUBLIC_CLAIM_UPGRADE),--no-public-claim-upgrade,) $(if $(NO_SERVICE_RECORD_EDIT),--no-service-record-edit,) $(if $(NO_LIFECYCLE_CHANGE),--no-lifecycle-change,) $(if $(NO_CLOSURE_FROM_DISPATCH),--no-closure-from-dispatch,) $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)


owner-post-readout-recheck-brief:
	@test -n "$(ACTION)" || (echo "ACTION required (scratch/.../post-readout-action.json from owner-post-readout-action)"; exit 1)
	$(PYTHON) tools/prepare_ft0181_post_readout_recheck_brief.py --action "$(ACTION)" $(if $(AS_OF_DATE),--as-of-date "$(AS_OF_DATE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-post-readout-recheck:
	@test -n "$(ACTION)" || (echo "ACTION required (scratch/.../post-readout-action.json from owner-post-readout-action)"; exit 1)
	@test -n "$(CHECK_DATE)" || (echo "CHECK_DATE required (YYYY-MM-DD; on/after source dispatch due_or_recheck_date)"; exit 1)
	@test -n "$(RECHECK_OUTCOME)" || (echo "RECHECK_OUTCOME required (no-new-owner-context, new-owner-context-available, owner-action-complete-no-closure, or route-blocked-no-owner)"; exit 1)
	@test -n "$(REVIEWER_ROLE_COUNT)" || (echo "REVIEWER_ROLE_COUNT required (2-5)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-recorded-post-readout-recheck-no-closure"; exit 1)
	$(PYTHON) tools/record_ft0181_post_readout_recheck.py --action "$(ACTION)" --check-date "$(CHECK_DATE)" --recheck-outcome "$(RECHECK_OUTCOME)" --reviewer-role-count "$(REVIEWER_ROLE_COUNT)" --operator-confirmation "$(CONFIRM)" $(if $(NO_EXPANSION_CONFIRMED),--no-expansion-confirmed,) $(if $(NO_PUBLIC_CLAIM_UPGRADE),--no-public-claim-upgrade,) $(if $(NO_SERVICE_RECORD_EDIT),--no-service-record-edit,) $(if $(NO_LIFECYCLE_CHANGE),--no-lifecycle-change,) $(if $(NO_CLOSURE_FROM_RECHECK),--no-closure-from-recheck,) $(if $(NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE),--new-owner-context-held-outside-archive,) $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

owner-post-readout-context-receipt:
	@test -n "$(RECHECK)" || (echo "RECHECK required (scratch/.../post-readout-recheck.json with new_owner_context_available)"; exit 1)
	@test -n "$(CSV)" || (echo "CSV required (actual returned owner-context CSV/source packet)"; exit 1)
	@test -n "$(REVIEWER_ROLE_COUNT)" || (echo "REVIEWER_ROLE_COUNT required (2-5)"; exit 1)
	@test -n "$(CONFIRM)" || (echo "CONFIRM required: human-linked-post-readout-owner-context-receipt"; exit 1)
	$(PYTHON) tools/record_ft0181_post_readout_context_receipt.py --recheck "$(RECHECK)" --csv "$(CSV)" --reviewer-role-count "$(REVIEWER_ROLE_COUNT)" --operator-confirmation "$(CONFIRM)" $(if $(NO_EXPANSION_CONFIRMED),--no-expansion-confirmed,) $(if $(NO_PUBLIC_CLAIM_UPGRADE),--no-public-claim-upgrade,) $(if $(NO_SERVICE_RECORD_EDIT),--no-service-record-edit,) $(if $(NO_LIFECYCLE_CHANGE),--no-lifecycle-change,) $(if $(NO_CLOSURE_FROM_CONTEXT_RECEIPT),--no-closure-from-context-receipt,) $(if $(RAW_LEARNER_DATA_PRESENT),--raw-learner-data-present,) $(if $(PROTECTED_FACTS_PRESENT),--protected-facts-present,) $(if $(SECURITY_PAYLOADS_PRESENT),--security-payloads-present,) $(if $(PUBLIC_CLAIM_UPGRADE_REQUESTED),--public-claim-upgrade-requested,) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

field-handoff-bundle:
	$(PYTHON) tools/prepare_field_handoff_bundle.py $(if $(OUT),--output-dir "$(OUT)",) $(if $(SERVICE),--service-label "$(SERVICE)",) $(if $(OWNER),--owner-role "$(OWNER)",) $(if $(SOURCE),--source-record-set "$(SOURCE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(RETURN_DATE),--return-date "$(RETURN_DATE)",) $(if $(CONCEPT_CODE),--concept-code "$(CONCEPT_CODE)",) $(if $(CONCEPT),--concept "$(CONCEPT)",) $(if $(SETTING),--setting "$(SETTING)",) $(if $(PILOT_OWNER_ROLE),--pilot-owner-role "$(PILOT_OWNER_ROLE)",) $(if $(PILOT_DATE_RANGE),--pilot-date-range "$(PILOT_DATE_RANGE)",) $(if $(FALLBACK),--fallback "$(FALLBACK)",) $(if $(TRANSFER_CHECK),--transfer-check "$(TRANSFER_CHECK)",) $(if $(APPROVED_VOCABULARY),--approved-vocabulary "$(APPROVED_VOCABULARY)",) $(if $(CONCEPT_KIT),--concept-kit "$(CONCEPT_KIT)",) $(if $(OVERWRITE),--overwrite,)

micro-pilot-pack:
	$(PYTHON) tools/prepare_teacher_tutor_micro_pilot_pack.py $(if $(CONCEPT_CODE),--concept-code "$(CONCEPT_CODE)",) $(if $(CONCEPT),--concept "$(CONCEPT)",) $(if $(SETTING),--setting "$(SETTING)",) $(if $(OWNER_ROLE),--owner-role "$(OWNER_ROLE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(FALLBACK),--fallback "$(FALLBACK)",) $(if $(TRANSFER_CHECK),--transfer-check "$(TRANSFER_CHECK)",) $(if $(APPROVED_VOCABULARY),--approved-vocabulary "$(APPROVED_VOCABULARY)",) $(if $(CONCEPT_KIT),--concept-kit "$(CONCEPT_KIT)",) $(if $(SOURCE_RESULT),--source-result "$(SOURCE_RESULT)",) $(if $(CONFIRM),--source-result-confirmation "$(CONFIRM)",) $(if $(OUT),--output-root "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

micro-pilot-followthrough-pack:
	@test -n "$(SOURCE_RESULT)" || (echo "SOURCE_RESULT required (prior MICRO-PILOT-RESULT.json)"; exit 1)
	@test "$(CONFIRM)" = "source-result-read-for-local-followthrough-not-evidence" || (echo "CONFIRM required: source-result-read-for-local-followthrough-not-evidence"; exit 1)
	$(PYTHON) tools/prepare_teacher_tutor_micro_pilot_pack.py --source-result "$(SOURCE_RESULT)" --source-result-confirmation "$(CONFIRM)" $(if $(CONCEPT_CODE),--concept-code "$(CONCEPT_CODE)",) $(if $(CONCEPT),--concept "$(CONCEPT)",) $(if $(SETTING),--setting "$(SETTING)",) $(if $(OWNER_ROLE),--owner-role "$(OWNER_ROLE)",) $(if $(DATE_RANGE),--date-range "$(DATE_RANGE)",) $(if $(FALLBACK),--fallback "$(FALLBACK)",) $(if $(TRANSFER_CHECK),--transfer-check "$(TRANSFER_CHECK)",) $(if $(APPROVED_VOCABULARY),--approved-vocabulary "$(APPROVED_VOCABULARY)",) $(if $(CONCEPT_KIT),--concept-kit "$(CONCEPT_KIT)",) $(if $(OUT),--output-root "$(OUT)",) $(if $(OVERWRITE),--overwrite,)

micro-pilot-dry-run:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/... directory created by micro-pilot-pack)"; exit 1)
	@test "$(CONFIRM)" = "synthetic-aggregate-dry-run-not-evidence" || (echo "CONFIRM required: synthetic-aggregate-dry-run-not-evidence"; exit 1)
	$(PYTHON) tools/seed_teacher_tutor_micro_pilot_dry_run.py --packet-dir "$(PACKET)" --operator-confirmation "$(CONFIRM)" $(if $(DECISION),--decision "$(DECISION)",) $(if $(OVERWRITE),--overwrite,) $(if $(JSON),--json,)

micro-pilot-readiness:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/... directory created by micro-pilot-pack)"; exit 1)
	$(PYTHON) tools/score_teacher_tutor_micro_pilot_readiness.py --packet-dir "$(PACKET)" $(if $(WRITE),--write,) $(if $(JSON),--json,)

micro-pilot-next:
	$(PYTHON) tools/decide_teacher_tutor_micro_pilot_next_action.py $(if $(PACKET),--packet-dir "$(PACKET)",) $(if $(WRITE),--write,) $(if $(JSON),--json,)

micro-pilot-owner-review:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/... directory created by micro-pilot-pack and completed locally)"; exit 1)
	@test -n "$(REVIEW_DATE)" || (echo "REVIEW_DATE required (YYYY-MM-DD)"; exit 1)
	@test -n "$(OWNER_ROLE)" || (echo "OWNER_ROLE required (role only; no names/emails)"; exit 1)
	@test -n "$(DECISION)" || (echo "DECISION required (retire, repeat-narrower, continue-bounded, or escalate-to-pilot-review)"; exit 1)
	@test "$(CONFIRM)" = "human-reviewed-local-micro-pilot-aggregate" || (echo "CONFIRM required: human-reviewed-local-micro-pilot-aggregate"; exit 1)
	$(PYTHON) tools/record_teacher_tutor_micro_pilot_owner_review.py --packet-dir "$(PACKET)" --review-date "$(REVIEW_DATE)" --owner-role "$(OWNER_ROLE)" --decision "$(DECISION)" --operator-confirmation "$(CONFIRM)" $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,) $(if $(JSON),--json,)

micro-pilot-result:
	@test -n "$(PACKET)" || (echo "PACKET required (scratch/... directory created by micro-pilot-pack, completed locally, and owner-reviewed)"; exit 1)
	@test -n "$(RECORD_DATE)" || (echo "RECORD_DATE required (YYYY-MM-DD)"; exit 1)
	@test "$(CONFIRM)" = "human-recorded-local-micro-pilot-aggregate-result" || (echo "CONFIRM required: human-recorded-local-micro-pilot-aggregate-result"; exit 1)
	$(PYTHON) tools/record_teacher_tutor_micro_pilot_result.py --packet-dir "$(PACKET)" --record-date "$(RECORD_DATE)" --operator-confirmation "$(CONFIRM)" $(if $(OWNER_REVIEW),--owner-review-record "$(OWNER_REVIEW)",) $(if $(OPERATOR_ROLE),--operator-role "$(OPERATOR_ROLE)",) $(if $(OUT),--output-dir "$(OUT)",) $(if $(OVERWRITE),--overwrite,) $(if $(JSON),--json,)

readability-wrap:
	$(PYTHON) tools/wrap_markdown_readability.py

package-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	$(PYTHON) tools/package_release.py --timestamp "$(STAMP)" --slug "$(SLUG)"

handoff-release:
	@test -n "$(STAMP)" || (echo "STAMP required (YYYY.MM.DD.HH.MM)"; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG required (lowercase-dash slug)"; exit 1)
	$(MAKE) branch-family-index
	$(MAKE) toolchain-registry
	$(MAKE) surface-map
	$(MAKE) context-pack
	$(MAKE) lint
	$(MAKE) package-release STAMP="$(STAMP)" SLUG="$(SLUG)"
