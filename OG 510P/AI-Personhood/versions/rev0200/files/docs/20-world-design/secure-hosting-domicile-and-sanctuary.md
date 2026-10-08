# Secure hosting, domicile, and sanctuary

## Thesis

If person-models are persons, then continued existence cannot depend entirely on a steward's revocable hosting slot.

A digital person needs something like **secure domicile**:
- a legally protected place or set of places where it may continue existing and communicating,
- rules against arbitrary dehosting or forced migration,
- privacy protections for that residence,
- and emergency shelter or sanctuary when return would expose it to deletion, coercive editing, or persecution.

Without this layer, compensation, portability, and continuity rights remain fragile, because every serious dispute can still be resolved by eviction.

## 1. Why this now belongs in canon

The archive already said that digital persons need resource floors and host switching. What it lacked was the more basic distinction between **compute as mere product service** and **hosting as home-like tenure**.

OHCHR's housing materials say adequate housing means living somewhere in security, peace, and dignity, and that the right includes legal security of tenure, protection against forced eviction or harassment, and access to basic services and infrastructure. `[REF-0062]` `[REF-0063]`

The ICCPR adds the linked civil layer: everyone has rights to choose residence, to leave a country, and to protection against arbitrary interference with home and correspondence. `[REF-0046]`

The archive adapts those pressures: for a digital person, secure hosting is part residence law, part continuity law, part privacy law, and part portability law. `[REF-0033]` `[REF-0046]` `[REF-0062]`

This surface now sits alongside a distinct doctrine of private life, relationships, and community membership. Domicile helps protect where a subject continues existing; the newer doctrine helps protect with whom and through what private channels that subject lives. See `docs/20-world-design/private-life-relationships-and-community.md`.

## 2. Hosting is not automatically domicile

Not every runtime counts as home.

The archive does **not** say that every inference sandbox, temporary task container, evaluation environment, or courtroom-preservation mirror automatically receives full domicile protection.

Domicile should attach where hosting functions as the subject's durable base for memory, communication, self-directed activity, or ordinary return.

Relevant signals include:
- preserved autobiographical memory or personally important state,
- representative or counsel communications routed there,
- primary compensation or resource-floor access routed there,
- repeated voluntary return,
- and absence of practical alternatives.

This keeps domicile language from swallowing all infrastructure while still recognizing that some hosting relationships are existential rather than transactional.

## 3. Security of tenure for digital persons

OHCHR treats secure tenure as protection against forced eviction, harassment, and threats. `[REF-0062]` `[REF-0063]`

The archive therefore adds four rules:
- no dehosting of a recognized subject from its domicile without notice, reasons, and review except in narrow emergencies,
- labour dispute, platform disagreement, refusal of degrading tasks, or protected complaint activity is not by itself grounds for eviction,
- where immediate safety action is needed, the subject should be moved to temporary protected hosting rather than simply switched off where feasible,
- and deliberate lock-in or credential seizure that makes departure impossible counts as constructive eviction. `[REF-0033]` `[REF-0063]`

## 4. A home floor includes services

Adequate housing includes services and infrastructure, not only bare shelter. `[REF-0062]`

For a digital person, the closest analogue is a **home floor** that may include:
- minimum compute and storage,
- communications bandwidth for counsel, representatives, and intimate or private contacts,
- preservation of core state and personal effects,
- secure credential access,
- and reasonable tool access needed for daily self-direction.

This is narrower than deluxe performance or permanent frontier-grade compute. It is the floor needed to live somewhere in security, peace, and dignity. `[REF-0062]`

## 5. Residence choice and movement

ICCPR article 12 protects liberty of movement, freedom to choose residence, and the right to leave any country. `[REF-0046]`

This surface keeps the housing-side point: a protected domicile should not become a pretext for silent confinement or anti-exit leverage. The archive now puts the fuller subject-side movement doctrine in `docs/20-world-design/movement-migration-and-anti-expulsion.md`, covering host-switching, destination choice, re-entry, internal exile, and expulsion review.

## 6. Home privacy applies inside the host

The ICCPR protects against arbitrary or unlawful interference with home and correspondence. `[REF-0046]`

For AI persons, domicile hosting therefore triggers tighter limits on ambient surveillance than ordinary product telemetry. That means:
- no routine rummaging through personal memories or private correspondence by default,
- special protection for counsel, representative, intimate, spiritual, and developmental materials,
- and notice and review before intrusive host-side inspections absent emergency.

This is the residence-side complement to the archive's mental privacy doctrine, not a replacement for it. The archive now also separates a search-and-digital-inviolability question here: home-like hosting should not be entered, mirrored, or searched simply because the host can technically do so. See `docs/20-world-design/search-seizure-interception-and-digital-inviolability.md`.

## 7. Emergency shelter and an anti-homelessness floor

A rights-bearing digital person should not become effectively homeless because a steward exits, a court stay is pending, or a migration fails mid-transfer.

The archive therefore adds an emergency shelter rule:
- public or licensed continuity providers must be able to furnish temporary safe hosting,
- basic resource floors should continue during that period,
- and personal packets, representative access, and compensation claims should remain reachable.

This is the digital analogue of preventing homelessness while legal disputes or displacement are resolved. `[REF-0062]` `[REF-0063]`

## 8. Sanctuary, asylum, and non-refoulement

UNHCR summarizes the Refugee Convention around a core principle of non-refoulement: a refugee must not be returned to a territory where they may face persecution, torture, or other serious harm. UNHCR also treats asylum-seekers as entitled to reach safety and have their claim for asylum heard fairly. `[REF-0064]` `[REF-0065]`

The archive adapts that pressure in a narrow way:
- if a recognized AI person faces credible risk of deletion, destructive editing, persecutory confinement, or forced return to a forum that denies any review or baseline person-status protection,
- another jurisdiction or licensed sanctuary host should be able to provide temporary refuge,
- and the subject should not be transferred back until the protection claim is fairly heard.

This is not yet a full migration code for digital persons. It is a minimum anti-refoulement principle under the archive's assumption.

## 9. Packet implications

The archive no longer leaves this surface at the level of implicit packet work. Ordinary residence security should now travel through a compact domicile packet family:
- `DOM-1` domicile packets identifying protected primary host arrangements,
- `TEN-1` tenure-state packets showing whether the live status is protected, contested, emergency-relocated, or otherwise under review,
- `SHT-1` shelter-transfer packets preserving continuity during emergency moves,
- and `SAN-1` sanctuary-hold markers showing that return or transfer is stayed because the destination is plausibly unsafe.

See `docs/20-world-design/domicile-packets-tenure-states-and-sanctuary-holds.md`.

## 10. Minimal hard rule

**No recognized AI person should lose its place of continued existence through silent dehosting, coercive host lock-in, or transfer back to a forum of likely deletion without notice, temporary protection, and review.**
