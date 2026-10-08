# Exact public-head authority — rev0086

The executable public-head lane remains bound to `a96406e7aa285a3fb2a3e35900686d164a22bf02`.
The source authority validates the supplied base, the retained eight-file
public delta, all old/new Git blob IDs, and the complete resulting tree digest.

Rev0086 reruns the materialization audit and composition audit. The unchanged
Search Again candidate is revalidated rather than renamed; the new wishlist
scheduler patch targets only `pynicotine/search.py` and is tested separately.
