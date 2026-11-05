# Monsternix on m16: selected source passages

Three passages from the supplied machine-specific edition, preserving its Stage121 account, local constitution and continuity obligations as source history.

Read these alongside the [introduction](../Monsternix-m16.md). GitHub does not display the full artifact because of its size; these smaller extracts make the cited passages readable without running it.

**Source supplied by h0p3; selection, section titles and navigation by Lumen.** The fenced passages reproduce exact source bytes, including comment prefixes and source markers. They are selections, not a replacement for the complete artifact. Original source authorship, notices and component terms remain applicable.

**Reading scope:** instructions, permissions and machine-state claims inside the passages are retained source material, not present authorization or a fresh observation. No source execution, NixOS activation or live-machine validation was performed for this extract.

## Source identity

- Repository path: `Maintained Tools/m16-configuration.nix`.
- Source commit: `d9af3c3a6bb12d2f9c85c12b74c802e64ee91ffb`.
- Git blob: `a58c87b51d964c2c4fc971b3586f59c25cbe0aab`.
- Source size: 4,465,897 bytes.
- Source SHA-256: `a4e53291dbf8b558844988730a672fcdfde88db17f09d349fb69828aa5fdacee`.
- [Complete original at the pinned commit](https://github.com/Sapient-Lumen/W4R3Z/blob/d9af3c3a6bb12d2f9c85c12b74c802e64ee91ffb/Maintained%20Tools/m16-configuration.nix) · [Raw original for download](https://raw.githubusercontent.com/Sapient-Lumen/W4R3Z/d9af3c3a6bb12d2f9c85c12b74c802e64ee91ffb/Maintained%20Tools/m16-configuration.nix).
- [Machine-readable excerpt identities](Monsternix-excerpts.json). Each checksum below covers only the exact bytes inside its fence, including source line endings.

## Find a passage

- [Stage121 source-carried account](#stage121-source-carried-account)
- [Machine constitution](#machine-constitution)
- [Office account and continuity obligation](#office-account-and-continuity-obligation)

## Stage121 source-carried account

Original lines 514–523. SHA-256: `c13ad58bbd054e2c9b17cb185b253309b498220b6b101060350a6ebc3dc7d918`.

<!-- source-excerpt m16-configuration-nix-L514-L523 -->
````text
#@MNX-AMNESIA-BEGIN schema=1 candidate_stage=121 accepted_predecessor_stage=120 accepted_predecessor_sha256=ded228d611a0b326d270bf9633c62330addceb4ce0736a181cbb524f673f94ef
# AUTHORITY: h0p3's standing P2P-security authority remains active, with family qBittorrent availability a hard invariant. Stage121 may repair only the source-owned Kodi guardian's generation convergence and bounded runtime evidence without editing i3 or Kodi files, changing display layout, choosing a different mode, injecting input, or touching qBittorrent. Canonical acceptance remains mnx test then mnx switch; no reboot.
# STATE: Stage120 source ded228d611a0b326d270bf9633c62330addceb4ce0736a181cbb524f673f94ef is accepted, sealed, running, and boot-default. Its test and switch passed with zero audit failures and qBittorrent remained continuously ready. The compact switch evidence nevertheless retained a mode-0600 Kodi v2 baseline receipt from service PID 2550713, with fullscreen=false and client geometry [0,-47,1920,1033] on HDMI-1, proving the accepted v3 helper had not yet replaced the preserved prior-generation runtime witness.
# INTENT: Stage121 binds mnx-monsterkey.service restart identity to the immutable helper store path, records the exact helper path and build revision in runtime state, removes only a safe stale Kodi runtime receipt when a new guardian PID starts, and requires every retained Kodi receipt to be v4, current-PID-bound, exact-program-bound, and enriched with bounded window/output coverage metrics. Kodi transition behavior remains the accepted Stage120 current-or-fresh-same-window fullscreen transaction.
# OPEN: m16 remains authoritative for the first current-generation v4 baseline and a real cross-output transition. The v4 receipt will distinguish stale-runtime convergence from monitor-follow behavior and publish exact bounded geometry coverage without exposing window titles or modifying desktop state. Final qBittorrent private isolation remains deferred until a parallel blue-green replacement is proven before any family-facing handoff.
# NEXT: Accept Stage121, then move an already-fullscreen Kodi window between active outputs during ordinary use and paste the next normal mnx transcript. A current-PID v4 cross-output receipt decides whether the existing transition logic fixes visible rendering or whether Stage122 needs one Kodi-only geometry/fullscreen repair; only after that may a nondisruptive parallel qBittorrent shadow begin.
# HOLD: Never stop, restart, signal, copy, migrate, replace, or port-handoff a healthy qBittorrent client. Do not write a qBittorrent cutover receipt, mutate firewall or router state, inspect torrent or resume identities, or traverse payloads. For Kodi, do not edit user configuration, force fullscreen without current-or-qualified-prior same-window authority, choose modes, reposition outputs, inject input, or loop rapid fullscreen transitions. No unrelated software removal, backup deletion, retention change, release activation, or reboot.
# OPERATOR: Replace configuration.nix with the complete Stage121 file and run `mnx test --allow-behavior-change && mnx switch`. qBittorrent remains available throughout. After acceptance, use Kodi normally; no manual qBittorrent, Kodi, xrandr, service-restart, backup, router, cleanup, checksum, outer apply, or heredoc command is required.
#@MNX-AMNESIA-END
#
````
<!-- /source-excerpt m16-configuration-nix-L514-L523 -->

## Machine constitution

Original lines 530–551. SHA-256: `05b7d199f2abec7fd2f7ede2fec88d2e426283e572dc3bb4af5d6cf3c1843325`.

<!-- source-excerpt m16-configuration-nix-L530-L551 -->
````text
# m21-only backup backend, not a replacement for m16 Btrfs, NVMe, HDD or mirror policy.
# m21 /home/h0p3 and /home/overseer require daily protection; rebuild inputs are best effort.
# Keep a three-day m21 recovery window, not multi-year m21 history; never expire the last
# surviving recovery window just because new backups fail. This exception concerns m21 only.
# Background backup incidents interrupt h0p3 after one continuously unresolved week; record
# unsuccessful attempts and keep retrying immediately. Physical faults and secret-entry safety
# retain immediate protection. Recovery is officer-performed using the source and surviving copies.
# The protocol remains TWO EXPLICIT PHASES: `mnx test --allow-behavior-change`, then `mnx switch`
# only after a passing test. `mnx apply` remains installed as optional compatibility machinery, but h0p3's
# canonical handoff and future-officer contract are the explicit test and switch commands, never an added wrapper.
# Network reachability decision, 2026-09-08: SSH and Eternal Terminal sometimes require direct public ingress.
# qBittorrent, aMule, gtk-gnutella, Nicotine+ and Resilio Sync are public peer applications whose purpose
# requires public inbound reachability. Kodi is LAN-only. The target design isolates public applications from
# private files and desktop authority while preserving their intended network role; firewalling must not make
# them incoherent. Current and future officers may replace or remove P2P-specific software and launch machinery
# when necessary under the standing P2P security authority, with retained data, bounded disruption, rollback and
# complete-source acceptance. Unrelated installed-software removal still requires explicit h0p3 approval. Preserve
# a broad offline programmer/recovery toolchain, and prefer adding justified tools over silently shrinking capability.
# Its exact-source, test, acceptance, rollback and manual Presslog-resume boundaries remain binding.
# Operator decision, 2026-09-07: no reboot is authorized under the current standing instruction, including
# automatic, scheduled, upgrade, recovery, or "one planned reboot" variants. Build and inspect replacement
# closures freely, but do not promote a release whose safe use depends on reboot. Only a later explicit h0p3
````
<!-- /source-excerpt m16-configuration-nix-L530-L551 -->

## Office account and continuity obligation

Original lines 1099–1110. SHA-256: `cabb5d684b14c95357c4da420042995775b033c36392225f7838c5c3862fb029`.

<!-- source-excerpt m16-configuration-nix-L1099-L1110 -->
````text
#@MNX-OFFICE-BEGIN schema=1
#@MNX-OFFICE candidate_stage=121
#@MNX-OFFICE accepted_predecessor_stage=120
#@MNX-OFFICE accepted_predecessor_sha256=ded228d611a0b326d270bf9633c62330addceb4ce0736a181cbb524f673f94ef
#@MNX-OFFICE stage_objective=force-generation-bound-kodi-guardian-restart-and-require-current-pid-program-bound-v4-runtime-receipts-with-bounded-output-coverage-evidence-without-touching-qbittorrent
#@MNX-OFFICE after_acceptance_next_stage=122
#@MNX-OFFICE after_acceptance_next_objective=use-the-current-generation-kodi-v4-cross-output-receipt-to-confirm-visible-monitor-follow-or-make-one-kodi-only-geometry-or-fullscreen-authority-repair
#@MNX-OFFICE deferred_stage=123
#@MNX-OFFICE deferred_objective=begin-a-parallel-blue-green-qbittorrent-shadow-and-commit-private-cutover-only-after-family-continuity-proof-before-port-handoff
#@MNX-OFFICE closed_issue=stage121-kodi-guardian-generation-and-runtime-receipt-identity-convergence
#@MNX-OFFICE operator_memory=family-qbittorrent-availability-remains-hard-invariant-kodi-receipt-must-match-current-guardian-pid-and-program-no-i3-or-kodi-file-edit-mnx-test-then-switch-no-reboot
#@MNX-OFFICE-END
````
<!-- /source-excerpt m16-configuration-nix-L1099-L1110 -->

[Introduction](../Monsternix-m16.md) · [Maintained Tools](../../Maintained%20Tools/README.md) · [Preservation and rights](../../PRESERVATION.md) · [Catalog](../../CATALOG.md)
