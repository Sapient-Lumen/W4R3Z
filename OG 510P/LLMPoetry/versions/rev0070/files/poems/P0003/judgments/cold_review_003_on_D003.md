# Cold Review — P0003-D003 “No Cost to Correct” — rev0065

**Verdict:** `revise_not_promote`  
**Temporal status:** later-turn review of the exact rev0064 draft and artifact hashes.  
**Successor boundary:** D004 may be created, but remains same-turn unjudged.

D003 solves the formal mismatch that defeated D002. The database knows inspection items, response state, disagreement details, and occupancy facts; a view renders the surface; a generated column computes the closing classification. Disclosure no longer reveals a line list pretending to be a record.

It still does not earn promotion. The poem now carries two institutional arguments—the HUD normal-wear/correction-cost dispute and the Census vacant-yet-present classification—without making either cause the other. The three domestic traces remain familiar: a less-faded rectangle with pinholes, standing carpet pile, and brass polished at a keyway. Repeating GOOD and zero cost around those traces clarifies the form but does not deepen them. The body spends thirty-one lines to reach the strongest five-line contradiction.

More importantly, D003 inserts the entire occupancy row in the WAL. Presence, usual residence elsewhere, and VACANT therefore arrive together. The artifact computes a classification, but it does not show an already occupied unit becoming vacant while nobody leaves. That unrealized transition is the real poem.

Preserve D003 and its exact database/WAL/spec bytes. D004 should subtract the HUD branch and every room trace. The base must already contain people living in the unit, usual residence here, zero departures, and OCCUPIED status. The WAL should change one field only—usual residence to elsewhere—while an AFTER UPDATE trigger records OCCUPIED becoming VACANT. An exhaustive state contract should prove every user table, including the unchanged empty departures table.

This is one internal cold review, not external reader evidence, admission, or proof that D004 succeeds.
