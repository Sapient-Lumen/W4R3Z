# D006 zero-witness delta rewrite

`P0002-D005` was rejected because it was still a clean conceptual demonstration. `P0002-D006` compresses harder: the same high enters as `14.04` under MLLW and `11.27` under NAVD88, while station identity, timestamps, source table context, and API details move out of the poem body.

The refactor in this revision adds a `revision_delta_policy` to the external-material packet and validator. The point is to make the validator stop rewarding a successor draft that merely preserves source coverage while adding another datum line. D006 must reduce visible source burden relative to D005 and must not begin with station metadata.

No quality claim is made.
