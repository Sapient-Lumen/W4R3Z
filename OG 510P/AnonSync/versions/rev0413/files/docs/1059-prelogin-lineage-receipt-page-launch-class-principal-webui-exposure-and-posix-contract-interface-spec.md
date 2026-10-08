# Pre-login lineage receipt page, launch class, principal, WebUI exposure, and POSIX contract interface spec

## Purpose

This receipt proves what pre-login/headless mode was actually accepted, what execution world it created, and what operator contract came with it.
It exists so later operators do not need old setup steps, shell memory, or support folklore to answer:

- did we switch launch class?
- under which principal did the runtime come up?
- which storage world and control audience were accepted?
- what file-creation contract and caveats were part of the deal?

## Receipt sections

### A. Launch mutation summary

Show:

- prior launch class
- new launch class
- start trigger
- keepalive posture
- expected start delay class

### B. Principal and storage world

Show:

- prior principal / new principal
- prior storage home / new storage home
- world-lineage verdict
- whether continuity was proven, only inferred, or explicitly not preserved

### C. Control surface and exposure

Show:

- GUI present/suppressed
- WebUI bind posture
- transport posture
- credential posture
- reviewed audience delta

### D. POSIX/file-creation contract

Show:

- expected delivery owner/group class
- expected writeability class
- local-writer compatibility verdict
- exact failure sentence accepted

### E. Mode caveats accepted

List accepted caveats such as:

- placeholder caveat
- manual link/key intake
- browser-only control
- delayed startup witness
- self-signed trust bootstrap

### F. Strongest safe sentence and blocked overstatement

Examples:

- strongest safe sentence: `Seat now runs as a reviewed pre-login headless runtime under dedicated principal with browser-mediated control and a mode-specific POSIX write contract.`
- blocked overstatement: `Sync now simply starts earlier with no other semantic change.`

## Public object

### `prelogin_lineage_receipt`

Fields:

- `prelogin_lineage_receipt_id`
- `seat_ref`
- `prior_launch_class`
- `new_launch_class`
- `start_trigger`
- `keepalive_posture`
- `expected_start_delay_class`
- `prior_principal`
- `new_principal`
- `prior_storage_home`
- `new_storage_home`
- `world_lineage_verdict`
- `gui_state`
- `webui_bind_posture`
- `transport_posture`
- `credential_posture`
- `audience_delta_summary`
- `expected_writeability_class`
- `local_writer_compatibility_verdict`
- `accepted_caveats[]`
- `strongest_safe_sentence`
- `blocked_overstatement`
- `issued_at`

## Main surface language

Compact receipt rows should read like:

- `Pre-login headless runtime adopted under dedicated principal; LAN WebUI exposure reviewed`
- `Launch class changed; new POSIX write contract accepted`
- `Browser-only intake caveat accepted; continuity limited to reviewed storage world`

## Design tests

The receipt is insufficient if:

- it records only that startup was enabled
- principal/world changes are omitted
- control-audience widening is absent
- accepted POSIX contract and caveats are not preserved

## Non-clone reason

Current official Resilio docs still leave later readers needing setup memory to reconstruct what `run before login` really meant.
AnonSync should instead leave one durable receipt naming launch class, principal, exposure, and contract.
