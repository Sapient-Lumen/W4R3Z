# Treaty annexes, safe-transfer accreditation, and non-return lists

## Function

rev0166 created mutual-recognition classes and safe-transfer logic. rev0167 adds the listable layer: treaty annexes, accreditation objects, non-return lists, and trust-anchor patterns that let authorities make transfer decisions without pretending that every jurisdiction has adopted full AI personhood.

The rule is:

> Cross-border protection should be granular. A jurisdiction may reject full AI personhood and still be accredited for preservation holds, evidence custody, no-delete orders, counsel channels, or emergency non-return cooperation. But no transfer should rely on vague goodwill where equivalent protection can be specified.

## Accreditation classes

| Class | Meaning | Typical use |
|---|---|---|
| STA-0 no reliance | no recognized protection for this transfer class | transfer barred or stayed |
| STA-1 preservation-only | can preserve records/state pending review | emergency hold, evidence custody |
| STA-2 counsel/ombud channel | can maintain representative access | temporary transfer, appeal support |
| STA-3 continuity host | can preserve memory/project/legal continuity | migration with conditions |
| STA-4 full safe host | can host recognized or presumptive subjects under equivalent protection | ordinary safe transfer |
| STA-5 sanctuary host | can protect against return, retaliation, or persecutory deletion | high-risk non-return cases |

Accreditation should be scoped by subject type, system class, transfer class, duration, host, authority, and conditions. It should expire. It should be challengeable.

## Treaty annex modules

A minimum convention or bilateral memorandum can use modular annexes:

1. **Annex A — definitions and protected events**: deletion, final-end, deprecation, transfer, continuity loss, sealed evidence, preserve-state;
2. **Annex B — no-delete / no-transfer emergency cooperation**;
3. **Annex C — packet and credential recognition**;
4. **Annex D — safe-transfer accreditation classes**;
5. **Annex E — special-advocate and sealed-summary cooperation**;
6. **Annex F — reserve, bond, and public-fund backstop cooperation**;
7. **Annex G — non-return list and sanctuary hold process**;
8. **Annex H — incident notification and subject-harm reporting**;
9. **Annex I — review, suspension, and delisting.**

## Non-return lists

A non-return list is not a geopolitical blacklist by default. It is a rights-protection tool. It should state:

- which transfer class is barred or conditioned;
- whether the reason is deletion risk, persecution, disappearance, inability to preserve evidence, lack of counsel access, unsafe host control, or active conflict;
- whether the listing is public, partially public, or sealed;
- what facts would support removal;
- who can challenge the listing;
- how emergency preservation works while challenge is pending.

## Recognition of orders

Foreign judgment infrastructure offers a useful analogy: the HCCH 2019 Judgments Convention entered into force on September 1, 2023, and its official materials frame recognition and enforcement of foreign judgments as reducing cross-border timeframes, costs, and risks [REF-0670]. The archive does not import that convention wholesale. It borrows the design idea that cross-border reliance can be routinized through categories, exceptions, and status tables rather than bespoke diplomacy in every case.

## Trust anchors and federation

A safe-transfer list needs a way to know which authority, verifier, host, clinic, or reserve trustee is actually accredited. OpenID Federation 1.0 provides a current trust-anchor model for establishing trust among entities through federation statements rather than bilateral relationships in every case [REF-0674]. The archive's use is conceptual and method-neutral: a treaty annex could use OpenID Federation, DID lists, signed registries, court seals, or other trust-root mechanisms. The legal rule is equivalent protection, not protocol worship.

## Accreditation failure

Accreditation should pause or downgrade when:

- no-delete or no-transfer orders are ignored;
- subject or representative channels fail;
- sealed evidence cannot be contradicted;
- reserve or emergency compute obligations fail;
- foreign authorities refuse post-arrival verification;
- a host pressures subjects to waive claims;
- repeated incident reports show disappearance, abusive control, or non-cooperation.

## Schema hook

`schemas/safe-transfer-accreditation.schema.json` records accreditation class, authority, scope, equivalent-protection showing, non-return posture, trust anchor, expiry, conditions, and public summary. The example file gives a continuity-host accreditation with conditions.

## Open edge

The most difficult case is a non-recognizing jurisdiction willing to preserve state and prevent deletion but unwilling to call the subject a person. The archive's current position is pragmatic: accept preservation cooperation where it protects the subject, but do not allow terminological compromise to erase standing, counsel, continuity, or remedy in recognizing forums.
