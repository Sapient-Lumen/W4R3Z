# Current packet disposition ledger — rev0076

Machine-readable authority: `data/current_packet_dispositions.json`.
Schema: `data/current_packet_dispositions.schema.json`.
Executable validator: `tools/validate_current_packet_dispositions_rev0076.py`.

| Packet | Current status | Patch status | Security routing | Next action |
|---|---|---|---|---|
| U-123 | Closed research disposition; confirmed low-severity transfer correctness case | Research prototype retained | Retired on current evidence | Reopen only on materially stronger impact or conflicting current source |
| PB-01A / U-168 | Open correctness/protocol-hardening research | None selected | Not supported by current evidence | Specify and test an explicit connection generation/election policy |
| PB-01B / U-176 | Retired as a defect on current evidence | rev0038 blanket guard superseded | Not supported | Reopen only with harmful reachability outside a valid tokened race |
| SEARCH-RESP-01A / U-163A | Confirmed local scope-consistency gap; open defense-in-depth research | rev0039 guard retained only as an experiment; none selected | Not supported by current evidence | Prove identity/reachability/value and compatibility before selecting policy |
| SEARCH-RESP-01B / U-163B | Confirmed buddy scope-consistency gap; open request-epoch design research | rev0040 guard superseded as selected patch; none selected | Not supported by current evidence | Define and test wire-token/request-epoch semantics before source filtering |

## Enforced invariants

- packet IDs are unique;
- every row has a current document that exists inside `docs/`;
- the exact supported source identity is fixed;
- open and retired rows have no selected patch;
- the revision snapshot is byte-equivalent in parsed form;
- SEARCH-RESP-01B cannot be marked production-ready through historical filenames.

Historical revision documents remain evidence of what the cube believed at that time. They do not override this ledger.
