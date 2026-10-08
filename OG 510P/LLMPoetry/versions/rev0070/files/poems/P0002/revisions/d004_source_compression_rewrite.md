# D004 source-compression rewrite note — rev0028

P0002-D003 failed in a useful way: the source layer became literal enough that the poem read like a verified NOAA table with commentary. The riskiest fix is not another registry. It is to let the source packet carry the full datum stack while the poem carries a smaller set of reading anchors.

D004 therefore keeps station, staff, office, MLLW, extrema, trend, and no-live-reading disclosure on the surface, while moving most datum-stack facts into `source_material_packet_004.json` as packet-context facts. The validator refactor must still require receipts/snapshots for those context facts so compression does not become source evasion.
