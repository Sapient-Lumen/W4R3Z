# Session review — rev0866

This revision turned existing patch content into real canonical material: **81 missing indexed files (546,423 bytes)** are now restored exactly, including **12 source payloads**. The result is measurable rather than procedural—exact coverage rose from 19 to 100 files and missing paths fell by 81.

The recovery path is reusable but intentionally narrow. It reconstructs only complete new-side streams, requires exact canonical size and SHA-256, writes only to a separate tree with the same index, refuses clobbering, and blocks symlink traversal. Five later-revision paths were preserved rather than rolled back to their baseline candidate bytes.

The refactor closes another integrity gap: the primary overlay gate now derives representation coverage live and refuses stale manifest numbers. A separate Makefile audit confirms that the canonical build surface is still incomplete here: 42 referenced scripts are absent.

Rights remain the highest non-byte blocker. Recovered historical rights drafts are not grants, all components remain `NOASSERTION`, and publication is still blocked. The next substantive input is a fuller tree/new byte source or an owner rights decision—not another registry layer.
