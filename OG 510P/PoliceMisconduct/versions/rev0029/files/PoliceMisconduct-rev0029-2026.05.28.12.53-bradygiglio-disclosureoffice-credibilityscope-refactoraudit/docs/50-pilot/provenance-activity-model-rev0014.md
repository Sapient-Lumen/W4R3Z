# Provenance activity model — rev0014

Rev0014 adds a small provenance activity template layer. The point is to make future operators record not only what data exists, but **which activity produced it** and which gates were crossed.

The model is inspired by PROV-style entity/activity/agent thinking, but it remains cube-native and privacy-first. The minimum chain is:

1. observe source page;
2. compare against baseline;
3. resolve document link;
4. capture payload privately;
5. compute fixity digest;
6. run privacy preflight;
7. create bounded summary;
8. review claim promotion;
9. review public change note.

No live provenance activity instances are created in rev0014. These are templates only.
