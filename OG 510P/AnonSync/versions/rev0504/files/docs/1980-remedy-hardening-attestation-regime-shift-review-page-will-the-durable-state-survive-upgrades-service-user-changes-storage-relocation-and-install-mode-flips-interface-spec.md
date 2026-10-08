# Remedy-hardening-attestation regime-shift review page — will the durable state survive upgrades, service-user changes, storage relocation, and install-mode flips?

## Purpose

This page is the operator-facing review that answers the practical regime-shift question after durability is already good enough in the current world: given that the intended state stays true through ordinary churn, will it stay true after the named world transition without losing the governing identity, storage, topology, or control surface assumptions that supported the prior sentence?

## Primary review prompts

The review must answer these prompts in order:

1. **Which durable receipt is the starting basis for this transition review?**
2. **What exact regime shift is under review: upgrade, reinstall, service-account change, storage relocation, config-mode flip, product-family update, or topology migration?**
3. **Which continuity assumptions must remain true for the prior sentence to survive this transition?**
4. **Which parts of the transition are supported, conditional, blocked, or explicitly unsupported?**
5. **What witnesses show the state surviving after the transition rather than merely before it?**
6. **What is the strongest regime-shift sentence the product may honestly publish now?**

## Review sections

### 1. Durable basis board

Show:

- source postcondition-durability receipt
- target postcondition sentence
- governed slice
- current durable class before transition

### 2. Transition-class board

Show:

- transition class under review
- whether the path is supported, conditional, or blocked
- whether the path preserves the same user, principal, identity, storage root, and launch shape
- whether the path changes control surface or folder-class availability

### 3. World-continuity board

Show:

- principal or service-account continuity
- storage-root continuity
- launch-parameter continuity
- version-family continuity
- control-surface continuity
- whether any of those create a new world rather than continue the old one

### 4. Unsupported-shortcut board

Show:

- clone or image-copy exposure
- multi-instance collision exposure
- unsupported product-family transition exposure
- any requirement to re-share, reconnect, or rebind the slice

### 5. Transition sentence chooser

The review must output one and only one primary sentence class such as:

- durable in current world only, regime shift unreviewed
- upgrade-path conditional on same user, storage, and parameters
- service-account fork risk open
- config-mode or control-surface override risk open
- folder-class continuity blocked
- version-family transition blocked
- clone-derived transition unsupported
- named transition survived for named slice only
- named transition set survived for governed slice
- broader all-transition regime robustness blocked

## Hard rules

The review must never let an operator hide:

- an unsupported transition behind `probably similar enough`
- surviving bytes behind `same shares world survived`
- re-share or reconnect labor behind `migration succeeded`
- new storage auto-creation behind `same identity world`
- one successful transition class behind universal migration robustness
