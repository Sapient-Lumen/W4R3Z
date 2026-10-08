# Resilio interface affinity, multi-NIC ambiguity, fall-forward, and service all-NIC exposure fragmentation evaluation

## Why this pass exists

The archive already had broad reachability, transport, and helper-budget doctrine.
What it still lacked was one tighter current Resilio pass about a narrower operator question:

> when I pick or imply one network interface, what do I actually constrain, what can still silently switch, and what exposure delta appears when the runtime class changes?

Current official Resilio docs are unusually useful here because they are candid about the real behavior while still leaving the operator to reconstruct it across power-user settings, troubleshooting, performance tables, and still-published changelog history.

Today those docs still show that:

- `bind_interface` names one interface, but if that interface is unavailable Sync can switch to the **next active interface** unless `use_only_bind_interface` is also enabled.
- `Peers aren't connecting` still treats multiple NICs as a first-class cause of wrong routing and even suggests switching to another NIC in LAN cases.
- the performance table still shows the currently established protocol, RTT, and speeds, but it does not by itself prove that the intended NIC or route-affinity contract held for the whole incident window.
- the still-published change log preserves several truths that matter to product design: historical allowance to **select NIC for data transfer instead of binding to all interfaces**, a fix for `"No Network"` when only a bridge interface existed, and a service-era change that allowed Sync to **listen all NICs when installed as service**.

That is a very good operator-truth corpus.
It is also a strong reason not to clone the exact page contract.

## What current Resilio still gets right

### 1) It admits that interface choice and effective route are different truths

The current power-user docs are explicit that the interface selection can fail over to the next active interface.
That honesty is worth keeping.

### 2) It admits that multi-NIC ambiguity is a real path problem

The troubleshooting docs still say multiple NICs can be the reason peers fail to connect.
That is materially better than pretending the host has one obvious network identity.

### 3) It leaves enough evidence to infer that runtime class changes interface audience

The still-published change-log trail matters here.
A product that at one point needed to call out `select NIC`, `listen all NICs when installed as service`, and `No Network` on bridge-only startup has already admitted that interface audience and startup viability are not one simple setting.

## Why AnonSync still should not clone it

### 1) Requested interface, effective interface, and hard cutoff are still too easy to confuse

Resilio's current docs still let an operator read `bind_interface` as stronger than it is.
The real contract depends on whether the interface exists now and whether `use_only_bind_interface` is enabled.

### 2) Current evidence is still weaker than continuity proof

A current performance row or a currently working connection does not prove that the chosen NIC stayed authoritative through the whole observation window.
AnonSync should not let one current witness impersonate a continuity claim.

### 3) Runtime class and audience widening still live partly in historical notes

The service all-NIC note is real product truth.
So is the bridge-only startup fix.
But today an operator still has to pull that meaning out of changelog archaeology rather than one stable page family.

### 4) The safe sentence depends on named interface identity, not only named route class

`direct`, `LAN`, or `connected` is weaker than `bound to this interface and did not fall forward`.
AnonSync should productize that weaker sentence instead of hiding it behind advanced settings.

## Hard decisions now locked for AnonSync

1. **Interface affinity is a first-class contract object, not an advanced footnote.**
2. **Requested interface, effective interface, listener audience, and fallback class are separate truths.**
3. **A named interface preference is weaker than a bind witness, and a bind witness is weaker than a continuity claim.**
4. **Service/runtime-class changes must review interface audience explicitly instead of laundering them through startup language.**
5. **Bridge-only or unusual-interface startup must be modeled as a host-network posture, not a generic `No network` surprise.**
6. **Receipts must preserve the strongest safe sentence and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Interface-affinity contract sheet**
- **Multi-NIC review**
- **Interface-fallback proof**
- **Service NIC-audience review**
- **Interface-affinity lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that chosen interface, effective interface, fallback, multi-NIC routing, and service listener audience are different truths. But it still makes one ordinary operator answer — `did this really stay on the interface I meant, and did service/runtime changes widen who could hear me?` — depend on power-user settings, troubleshooting prose, performance tables, and changelog archaeology. AnonSync should keep the candor and refuse the archaeology.
