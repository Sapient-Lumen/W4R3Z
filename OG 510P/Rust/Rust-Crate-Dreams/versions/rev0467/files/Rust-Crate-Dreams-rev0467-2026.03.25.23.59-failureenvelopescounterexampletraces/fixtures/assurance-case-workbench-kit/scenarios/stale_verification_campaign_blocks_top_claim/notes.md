# stale_verification_campaign_blocks_top_claim

This scenario proves the workbench keeps freshness and change-impact first-class.

The imported verification campaign is still parseable, but it was produced under an older toolchain and campaign policy. The configured freshness policy says stale verification evidence blocks a green top-level result, so the expected status is **`blocked`** and the diff must explain why.
