# Superseded packet and authority index — rev0077

## Current authority mechanism

`tools/validate_current_packet_dispositions_rev0076.py` and the rev0076 schema constants are historical evidence. They no longer define current status. Current authority is:

```text
data/current_packet_dispositions.json
data/rev0077_packet_dispositions.json
data/current_packet_dispositions.schema.json
data/current_packet_disposition_contract.json
tools/validate_current_packet_dispositions.py
```

## SEARCH-AGAIN-SELF-01

No historical packet is promoted. The rev0077 one-line patch is selected only as a research disposition for token bookkeeping. It does not select a refresh-epoch redesign and is not contribution material.

Current authority: `docs/SEARCH-AGAIN-SELF-01-CURRENT-DISPOSITION-REV0077.md`.

## SEARCH-RESP-01B / U-163B

Historical rev0040 production-ready and selected-patch artifacts remain superseded. Current authority remains `docs/SEARCH-RESP-01B-CURRENT-DISPOSITION-REV0076.md`; no patch is selected.

## SEARCH-RESP-01A / U-163A

Historical rev0039 production-ready and selected-patch artifacts remain superseded by the rev0075 identity/reachability boundary. Current authority remains `docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md`.

## PB-01

The rev0038 blanket primary guard remains superseded by rev0074's direct/indirect race counterexample. Current authority remains `docs/PB01-CURRENT-DISPOSITION-REV0074.md`.

## U-123

The selected artifact remains a research prototype under rev0073's low-severity correctness disposition. Historical security-strength wording must not be revived without new evidence.
