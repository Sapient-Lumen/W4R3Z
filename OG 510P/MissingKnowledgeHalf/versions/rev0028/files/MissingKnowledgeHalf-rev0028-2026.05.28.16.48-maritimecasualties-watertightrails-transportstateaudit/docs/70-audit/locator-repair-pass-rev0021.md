# Locator repair pass — rev0021

Rev0015/0016 exposed weak locator debt. Rev0021 performs a small targeted repair rather than claiming global cleanup.

Repaired source records:
- `MKH-SRC-0037`
- `MKH-SRC-0039`
- `MKH-SRC-0071`

Repaired claim evidence refs:
- `MKH-ENG-0005` / `MKH-CLA-0066`
- `MKH-INF-0013` / `MKH-CLA-0119`

Policy: no factual claim wording changed in this pass. Locator repair cleans evidence surfaces; it does not re-adjudicate record meaning.

Result:
- weak source locators before rev0021: 32
- weak claim/evidence locators before rev0021: 39
- weak source locators after rev0021: 29
- weak claim/evidence locators after rev0021: 37

Remaining weak locators are still open debt, not failure of lint.
