# Protocol v0

## Envelope

```json
{
  "version": "0.1",
  "request_id": "uuid-or-null",
  "type": "message.type",
  "tab_id": 123,
  "timestamp": "2026-03-06T21:00:00+00:00",
  "payload": {}
}
```

## Shared message types in use

- `health.ping`
- `state.snapshot`
- `prompt.read`
- `prompt.write`
- `prompt.submit`
- `transcript.latest`
- `transcript.delta`
- `selection.read`
- `debug.dom_candidates`
- `adapter.detected`
- `bridge.status`
- `bridge.set_target_tab`
- `bridge.clear_target_tab`
- `bridge.set_receiver_override`
- `bridge.clear_receiver_override`
- `bridge.forward_to_active_tab`
- `error.report`

## Local broker line protocol

The local UNIX socket uses newline-delimited JSON messages.

Requests from CLI to broker include:
- `{"op": "ping"}`
- `{"op": "status"}`
- `{"op": "watch"}`
- `{"op": "submit_browser_request", "message": <envelope>}`

Responses/events are also newline-delimited JSON objects.

## Stability guidance

- prefer additive changes
- keep site-specific data inside `payload`
- keep core names generic

## Native messaging transport notes

- GlassTTY's current envelope still travels over Chromium native messaging, so message size matters as part of protocol design, not only implementation detail.
- Current Chromium docs impose a much tighter host→extension ceiling than extension→host. Future protocol growth should assume that large browser results may need chunking, spill-to-disk, or indirect references before they can safely travel back through the host channel.
- rev0042 therefore adds explicit byte-budget tooling and host-write validation, but the wire envelope itself is still `version/type/tab_id/timestamp/payload` for now.


## Provisional planner step supplements from rev0043

GlassTTY's saved-fixture planner now emits a few scope-oriented fields that are useful for future protocol work, but they are still provisional until a browser-sourced scoped fixture validates the shape:

- `preferred_locator_root`: the locator root object to start from (`page`, a named-form/group locator, or a `frameLocator(... )` chain)
- `preferred_locator_relative`: the relative locator chain below that root (for example `.getByLabel("Message")`)
- `locator_root_strategy`: why that root was chosen (`page`, `form_name`, `fieldset_legend`, `frame_selector+form_name`, etc.)
- `locator_root_candidates`: alternate root scopes that may be more resilient than page-global search when repeated controls exist

The wire envelope is unchanged. These fields only exist in saved planning artifacts for now.


## Provisional receiver-inventory supplements from rev0049

The wire envelope is still unchanged, but extension status/state can now preserve receiver-oriented tab metadata that future protocol work may want to standardize:

- `receivers`: observed content-script receiver contexts for a supported tab, each with optional `documentId`, `frameId`, lifecycle, readiness, and `lastSeenAt`
- `receiverCount` / `readyReceiverCount`: compact inventory counts for operator-facing status and trace review
- `receiverFrameIds` / `receiverDocumentIds`: compact identifiers for the observed receiver set
- `receiverSelectionPolicy`: why the current preferred receiver was chosen (`top_frame`, `single_ready`, `latest_ready`, `single_observed`, `latest_observed`, or `none`)
- `receiverInventoryStatus`: whether the observed receiver set looks like `single_top_frame`, `multi_frame_top_frame`, `single_subframe`, `multi_frame_no_top_frame`, or `none`

These fields are extension/session-state supplements for now, not a stable browser↔CLI wire contract.

## Receiver targeting notes

- The background may route a browser request to a specific content-script receiver using Chrome's native `documentId` or `frameId` targeting rather than always broadcasting to all content scripts in the tab.
- Supported-tab state can now preserve both the default receiver-selection policy and an operator-selected receiver override.
- Live `fixture.capture` payloads may include metadata describing the receiver target policy, override status, and the specific receiver key that answered.


## Provisional probe supplement from rev0051

The wire envelope is unchanged, but `bridge.probe` can now expose a compact `receiverAudit` summary for the selected/targeted supported tab. This is diagnostic sugar rather than a new core transport contract. Current fields include:

- `targetTabId` / `selectedTargetTabId`: which supported tab the audit refers to
- `receiverCount` / `readyReceiverCount`: compact inventory counts
- `receiverSelectionPolicy` / `receiverInventoryStatus`: why the active receiver was chosen and what the observed receiver set looks like
- `receiverOverrideKey` / `receiverOverrideStatus`: whether an operator override exists and whether it is active or stale
- `selectedReceiverKey` / `selectedReceiverLabel`: the currently chosen receiver in compact human-readable form
- `coverageAudit`: optional frame-gap evidence for the selected/targeted tab, including current policy hints and an experiment matrix that projects what candidate manifest deltas would change
- `receivers[]`: compact per-receiver entries with `key`, label, frame/document identifiers, readiness, lifecycle, and `lastSeenAt`

This supplement exists to make saved probe artifacts easier to audit. It is not yet a promise that every future adapter flow will depend on the exact same shape.


## Provisional receiver-frame-context supplement from rev0052

The wire envelope is still unchanged, but receiver-oriented status/probe/fixture metadata can now preserve browser-sourced frame context fields in addition to raw receiver keys:

- `frameType`: Chrome navigation's frame kind (for example main/top frame vs subframe)
- `parentFrameId` / `parentDocumentId`: parent linkage for receiver archaeology and selection
- `frameUrl` / `frameOrigin`: browser-known frame location metadata, useful for operator audits and resolver filters

This supplement exists so multi-frame receiver choice can be explained in human terms before GlassTTY widens content-script policy. It does not yet change the transport contract or prove broader all-frames behavior.

## Provisional content-script experiment supplement from rev0062

The core wire envelope is still unchanged, but GlassTTY now has a reversible runtime experiment lane for frame coverage:

- `bridge.content_script_experiment`: returns the effective content-script policy plus any active GlassTTY dynamic experiment
- `bridge.set_content_script_experiment`: registers a non-persistent dynamic content-script variant (`manifest_all_frames`, `manifest_match_about_blank`, or `manifest_match_origin_as_fallback`) cloned from the existing static GlassTTY content script
- `bridge.clear_content_script_experiment`: removes GlassTTY's dynamic experiment registrations
- `bridge.probe.manifest.contentScriptPolicy`: now reports the effective current policy, not only the static manifest, so active experiments are visible in saved probe artifacts

This remains diagnostic/product-ops sugar rather than a long-term promise that manifest experimentation is part of the stable core transport contract.
