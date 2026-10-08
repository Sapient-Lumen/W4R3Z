# Cooperation benchmark programs should publish direct focus primary verify and refresh intent summaries for compact-card reentry

Once the compact-card stack already publishes direct focus verify / refresh commands, retained targets, and subject role codes, the first reentry move is almost locally legible but not quite.

Without one tiny intent gloss, inheritors still have to infer whether the first focus command is verifying a retained surface, refreshing one, or doing something subtler.

A good focus-lineage digest should therefore also publish `focus_primary_verify_intent_summary` and `focus_primary_refresh_intent_summary`.

Those fields should remain honest aliases of the retained focus-lineage handoff pack, so the global reentry surfaces keep saying “open this, then run this, for this reason” without inventing a second interpretation layer.
