# Resilio discovery-bootstrap authority, catalog outage, and relay-inevitability fragmentation evaluation

## Why this pass exists

The archive already had route basis, helper-policy, ingress mutation, local-network-only posture, proxy notes, and ordinary connectivity repair language.
What it still did not own cleanly enough was one narrower but very ordinary operator seam:

> when peers do not connect, or when a seat is placed behind an egress-only proxy, who currently defines discovery infrastructure, what fallback envelope still remains, and for which peer pairs is relay merely possible versus already inevitable?

Current official Resilio docs still make that seam materially real.
They still say all of the following at once:

- peers in different networks may fail to connect simply because the client cannot reach `config.resilio.com/sync.conf`, the file from which Sync learns tracker and relay addresses
- once tracker and relay are learned, direct connectivity still separately depends on listening-port reachability and route possibility between peers
- if tracker use is not possible, the operator can fall back to `predefined hosts`
- `No tracker connection` is explicitly weaker than `no sync possible`, because LAN broadcasts, relay, or predefined hosts may still keep some peer discovery alive
- proxy servers prohibit incoming connections and allow only outgoing ones; when both peers are behind proxies they will be able to talk only via relay, while one proxied peer can still dial outward directly to a non-proxied peer
- relay is documented as slower than direct connection and only used when direct paths are not possible
- the core ports/protocols doc still splits the transport story across config-file fetch, tracker contact, direct peer dialing, relay transfer, LAN multicast, and UPnP/NAT-PMP mapping

That is good candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `what discovery authority still exists right now, and what connectivity envelope do I still have?` — still depends on combining:

- ports/protocols architecture notes
- connectivity troubleshooting
- preferences prose
- relay explainer text
- warning-page semantics

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Discovery bootstrap authority is first-class state.** The product must always know who currently defines tracker / relay / rendezvous infrastructure for a seat.
2. **Fallback envelope is explicit.** `No tracker connection` can never collapse into `broken` while relay, LAN discovery, cached endpoints, or manual hosts still preserve some reachability.
3. **Pairwise directness and relay inevitability are computed, not guessed.** A proxy-mediated or policy-narrowed seat cannot hide behind one generic `online` badge.
4. **Bootstrap freshness and route posture are separate truths.** A seat may still connect to old peers using cached or manual knowledge while new discovery is already narrowed or gone.
5. **Receipts must preserve dependency changes.** Authority source, freshness class, fallback envelope, and relay-bound pair deltas belong in one durable record.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Bootstrap dependence is admitted directly.** The current connectivity troubleshooting article still says Sync learns tracker and relay addresses from `config.resilio.com/sync.conf`.
- **Discovery lanes are admitted as distinct.** The same article and the ports/protocols doc still separate tracker, relay, direct dialing, LAN multicast, and predefined hosts.
- **Tracker loss is not overclaimed.** The current `Core warnings` page still says `No tracker connection` only prevents syncing when relay, LAN broadcasts, and predefined hosts are also unavailable.
- **Proxy asymmetry is candidly documented.** The current preferences page still says proxies prohibit incoming connections and that two proxied peers will talk only via relay, while one proxied peer may still connect directly outward to others.
- **Relay cost is admitted as real.** The relay article still says relayed transfers are slower than direct ones.
- **Manual fallback still exists.** The current troubleshooting article still says predefined hosts can be used when tracker use is impossible.

That is useful product honesty.
Resilio does not pretend that connectivity is one flat status.

## Where current Resilio still stays too article-shaped

### 1. Bootstrap authority still hides inside troubleshooting

The ordinary operator should not have to inspect a failure article just to learn that tracker and relay addresses come from a remote catalog and that catalog reachability is itself part of connectivity truth.
Yet that is still roughly how present-day Resilio explains it.

### 2. Fallback envelope still requires inference

Current official docs do say that tracker loss may still leave relay, LAN discovery, or predefined hosts available.
But they do not render one operator-owned answer such as:

- full discovery envelope retained
- existing peers only; new public discovery blocked
- manual-host direct only
- LAN-only discovery retained
- relay still possible but tracker-backed peer matching lost
- no ambient discovery remains

AnonSync should not clone a product where that answer remains a reconstruction.

### 3. Proxy posture still masquerades as one preference line

Current preferences prose is admirably blunt that proxies prohibit incoming connections and can make relay inevitable for some pairs.
But the operator still has to connect that statement to actual pairwise route outcomes, disclosure cost, and throughput expectation.
That is too weak for an ordinary interface.

### 4. Cached continuity versus fresh discovery remains underexplained

Current docs clearly allow the possibility that some peers may still connect via already learned or manually pinned knowledge even while the bootstrap source is unavailable.
That means `still syncing with one peer` and `bootstrap authority healthy` are different truths.
AnonSync should make the difference visible.

### 5. Warnings still do not own infrastructure dependency lineage

A core warning can say `No tracker connection`, but the durable operator question is broader:

- where did bootstrap authority come from before?
- what freshness state is it in now?
- which endpoint classes are still trusted?
- what pairings just became relay-bound or join-blocked?

Present-day Resilio still spreads that answer across several articles.

## The tighter non-clone decision

Borrow Resilio's candor that discovery depends on a remote catalog, that tracker / relay / LAN / manual hosts are distinct lanes, that proxy posture is asymmetric, and that relay is slower than direct connection.
Do **not** clone a product contract where operators still have to merge troubleshooting, preferences, relay explainers, warning pages, and ports/protocols notes to answer who currently defines endpoint authority, whether fallback discovery still exists, and for which peer pairs relay is already inevitable.

## What AnonSync should do instead

AnonSync should treat **discovery bootstrap authority and reachability asymmetry** as one first-class reviewed family.
Every serious bootstrap fetch, catalog outage, proxy adoption, private-infra pin, or route-posture change should answer five things in one place:

1. **authority source** — fetched public catalog, pinned private catalog, manual static endpoints, cached bootstrap residue, or none
2. **freshness state** — fresh, stale-but-usable, expired, absent, validation-failed, or unreachable
3. **fallback envelope** — what discovery and transport classes still remain right now
4. **pairwise route posture** — direct-capable, direct-asymmetric, relay-possible, relay-inevitable, or blocked
5. **safe language** — what the product may and may not say about `healthy connectivity`, `bootstrap outage`, and `proxy enabled`

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Bootstrap authority contract sheet**
- **Bootstrap outage review**
- **Egress-only reachability review**
- **Discovery fallback proof**
- **Bootstrap lineage receipt**

Those pages should sit beside route basis, helper policy, ingress mutation, and transfer-budget pages — not underneath troubleshooting alone.
