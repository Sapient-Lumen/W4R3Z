# Research notes — rev0969

A safe restore precondition must identify causal state, not merely bytes or timestamps. Distinct operations can carry identical payloads, and a conflict has more than one visible head. The exact sole current operation is therefore the minimum path-local validator for the ordinary restore command. It resembles a strong conditional update while preserving AnonSync's later replica projection and rooted publication fences.

The complete rev0968 pagination source cutpoint was considered and rejected for restore intent. It binds unrelated paths and the entire retained payload namespace, so it would create false conflicts and force broader observation than the selected path requires.

The process-oracle race reinforces a separate systems rule: a test must model the product's documented internal namespace exactly. Ignoring every dotfile would hide user state; following every enumerated internal temporary after rename would manufacture failures. The exact publication-temporary grammar is the smallest correct exclusion.

The next product edge remains deliberate version lifecycle policy: explicit pins, current/version/in-flight reachability, bytes/count/age limits, crash-safe mark/quarantine/revalidate/unlink collection, friendly ordering metadata, conflict copies, and restore UX measured against a named Resilio workflow.
