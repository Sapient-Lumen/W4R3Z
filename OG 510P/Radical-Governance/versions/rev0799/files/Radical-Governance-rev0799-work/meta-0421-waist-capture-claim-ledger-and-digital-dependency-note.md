# Meta 0421 — Waist capture, claim ledger, procedural digital waist, and supplier dependency revision note

This meta note records the rev0720 rebuild.

Rev0720 adds notes `856` through `859`, introduces `metadata/claims.json`, generates `generated/CLAIMS.json` and `generated/CLAIMS.md`, and hardens the archive against two failure modes that became visible after rev0719: narrow-waist capture and note-level proof laundering.

The revision also adds the Interoperable Europe Act as the first procedural digital-waist case packet, adds a cloud/model-provider dependency lens, removes unreferenced duplicate WHO source-key aliases, adds duplicate URL linting for source keys, and changes fallback tag inference from substring matching to boundary-aware matching.

The intended effect is not more doctrine for its own sake. The next archive should be able to ask, for any serious claim: what is the claim, how strong is it, what sources carry it, who can capture it, who is harmed if it is wrong, what would falsify it, and when should it be reopened?
