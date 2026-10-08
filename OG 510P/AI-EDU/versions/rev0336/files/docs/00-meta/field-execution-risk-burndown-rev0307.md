# rev0307 field execution risk burndown

| Risk | rev0307 control | Residual boundary |
|---|---|---|
| Checker/release scratch packet is passed as activation receipt `SOURCE_PACKET`. | Activation source-packet guard allows only external paths or `scratch/field/ft0181` and blocks checker, release, legacy, smoke, test, and fixture scratch. | Real packets must still be held outside the archive or deliberately staged in the field lane by a human operator. |
| Hash equality is mistaken for source legitimacy. | Same-hash checker-scratch regression now fails with `ACTIVATION-RECEIPT-SOURCE-PACKET-BLOCKED`. | Hash lineage remains necessary, but source-path legitimacy is checked separately. |
| Validator harness forces new doctrine copies. | Tests were refactored to use field-lane validation packet sources while keeping checker outputs under `scratch/checks`; no new schema or registry family was added. | Some upstream synthetic chain artifacts still live in checker scratch for validator coverage; the near-acceptance packet argument is now firebroken. |
| Field work stalls in controls instead of real owner action. | Operator docs emphasize the same narrow path: route real returns through `owner-field-next`, then use only emitted commands. | The actual unblocker remains a real owner-reviewed packet or documented route block. |

`FT-0181` remains live. This pass does not contact an owner, import a real CSV, accept `SRC2+`, authorize a real active-change window, upgrade a public claim, or close the followthrough.
