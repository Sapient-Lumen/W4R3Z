# Resilio external recipe provenance and postcondition proof evaluation

## Why this pass exists

The archive already had:

- diagnostic probe approval
- external guidance intake
- remediation recipe review
- escalation packet review
- bounded intervention receipts

Those were necessary, but another current Resilio pass shows a still-missing seam.
The problem is no longer only `should I do something external`.
It is now:

- what exact *kind* of outside-the-product step is this?
- what exact target tuple will it touch?
- what must already be stopped, paused, or closed?
- what counts only as a witness that the step executed?
- what product-side reread would actually prove success?
- what residue remains even if the immediate ritual appeared to work?

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still candid that some real support actions are not in-product clicks at all.

Examples the docs still openly recommend include:

- stopping Sync completely before running `iperf3`
- running explicit client/server terminal commands for network measurement
- enabling debug logging via settings *or* by placing `debug.txt` with `FFFFFFFF` in the storage folder and restarting
- collecting logs for a minimum evidence window rather than assuming instant proof
- editing or supplying `sync.conf` so config-defined behavior outranks WebUI behavior
- clearing HSTS, using the temporary browser bypass, or supplying a trusted certificate when the WebUI trust warning appears
- deleting `settings.dat` as one password-reset lane but preferring config-mode credentials when the operator wants to avoid duplicate-device rows and reset global preferences
- treating `.sync` loss or corruption as service-state loss rather than merely cosmetic file clutter

This is good evidence that Resilio is not pretending complicated products can be supported by one magical button.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many article types.

### 1. Recipe class is not stable enough

A current official article may tell the operator to:

- type something into the browser
- edit a config file
- create or remove local hidden files
- stop and restart the runtime
- run terminal commands
- inspect a hidden storage location

But the product does not give one stable answer to:

- is this observation-only?
- is this a temporary browser workaround?
- is this a restart-bearing config mutation?
- is this a destructive reset?
- is this continuity-preserving or continuity-recreating?

The operator has to infer that from prose.

### 2. Target scope is still too implicit

Resilio help text often names a folder, storage path, service user, or config file, but ordinary operators still have to reconstruct the exact target tuple:

- which seat
- which runtime
- which process identity
- which path
- which hidden state family
- which browser trust store or HSTS cache
- which config lane now has precedence

That is too much inference for high-consequence steps.

### 3. Witness and success are still too easy to confuse

Current docs often provide a ritual witness:

- the command ran
- the browser opened
- the log switch was enabled
- the config file was saved
- the service restarted

But the real operator question is harder:

- did the product truth actually change?
- did the intended state survive the restart?
- did this merely permit access or did it restore health?
- did this fix continuity, or only recreate successor state?

Those questions still require hopping back into other articles.

### 4. Postcondition proof is not centralized

Current docs usually explain *how to do the step* better than *what exact reread proves the step worked*.
That is the core page-contract gap.

The operator still lacks one stable answer to:

- what should I reread immediately after this step?
- what counts as partial success?
- what contradictory evidence should block closure?
- what residue still demands a follow-up review?

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.

The product should split this seam into four page families:

1. **External recipe**
   - what the recipe is
   - why this source is trusted enough to consider
   - what exact target tuple it touches
   - how invasive or reversible it is

2. **Command step**
   - when the next move is a literal command or file operation
   - what shell / runtime / path / process it addresses
   - what precondition proof is required before execution

3. **Off-product execution**
   - when the lane is browser, OS trust prompt, service manager, admin console, or support portal
   - what human witness proves the lane action happened
   - what that witness still does not prove

4. **Postcondition verification**
   - what product-side reread must happen afterward
   - what changed, what did not, and what remains risky
   - whether the step repaired continuity or only recreated a workable successor state

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that some repairs are outside the product, exact, and worth doing, but not for the way ordinary answers to `what step is this`, `what does it touch`, `what had to stop first`, and `what proves success afterward` still sprawl across support how-tos, browser-warning pages, config notes, and troubleshooting prose instead of one stable page family.

## New replacement pages added in this revision

- `442` External recipe
- `443` Command step
- `444` Off-product execution
- `445` Postcondition verification
