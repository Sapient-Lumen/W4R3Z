# ADR 0187 — Native source audit before more C leaves

Accepted for rev0083.

C leaf sources must remain tiny and side-effect-free. Textual source audit is not sufficient for production, but it is enough to catch obvious drift while the cube is still a design lab.
