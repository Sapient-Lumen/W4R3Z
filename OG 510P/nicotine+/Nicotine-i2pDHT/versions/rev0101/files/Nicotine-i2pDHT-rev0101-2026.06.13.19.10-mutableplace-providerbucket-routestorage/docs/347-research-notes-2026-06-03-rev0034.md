# Research notes — rev0034

No new external claims were introduced in this revision.  The design continues earlier lines:

- I2P/SAM remains shadowed until local protocol boundaries stop moving.
- Garden nodes need operator feedback, but observability must be treated as a metadata surface.
- Branchlets should be folded with explicit supersession/audit surfaces instead of deleted.

The next concrete research/code seam is likely a no-network startup profile matrix: leaf, garden, bridge, and offline-design modes should each define exact launch quorum requirements before a live SAM harness exists.
