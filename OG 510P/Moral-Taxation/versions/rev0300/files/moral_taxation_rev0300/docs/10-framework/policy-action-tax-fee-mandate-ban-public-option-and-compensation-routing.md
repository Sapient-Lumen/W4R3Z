# Policy-action tax, fee, mandate, ban, public-option, and compensation routing

## Question in one sentence

When the cube identifies a burden or benefit, how do we decide whether the morally correct policy action is a tax, fee, surcharge, mandate, public option, duty, ban/no-go rule, compensation scheme, or release block rather than merely inheriting the instrument label used by the proposal?[S573][S662][S663][S664]

## Rule

The fiscal label is not the policy action. A proposal can call something a tax, fee, premium, contribution, assessment, mitigation payment, credit, mandate, fine, or public option while doing a different moral job. The cube must therefore classify the **policy action semantics** before approving the design.

Use these distinctions:

| Policy action | Legitimate job | Category mistake |
|---|---|---|
| tax / levy / surcharge | raise revenue, capture rent, price compensable harm, or fund public capacity through legislative choice | disguising a tax as a fee, using a tax to sell permission for non-compensable harm, or collecting from a protected floor without repair |
| user fee / service charge | recover cost or value for an identifiable special benefit while preserving essential access and waivers | using access to a public right as a tollgate for general revenue or agency-wide protection of the public |
| mandate / standard / duty | require behavior because price alone is insufficient or monitoring/cure is central | calling a mandate a tax to hide rights, labor, speech, privacy, or due-process consequences |
| public option / fallback | preserve public access where a private rail, app, bank, vendor, platform, insurer, or utility controls the channel | treating a private channel as the public right itself |
| ban / no-go / veto | block non-compensable harm, cumulative burden, corruption, or non-repairable risk | selling the forbidden activity back through a tax, offset, abatement, or mitigation fee |
| compensation / rebate / credit | repair the actual burden bearer, preserve floors, or return overcollection | paying the legal remitter while the real bearer absorbs price, delay, denial, or risk |
| release block / source refresh | stop an archive or administrative surface from shipping a false answer | treating a clean manifest or citation list as substantive correctness |

A user fee needs a cost/value/special-benefit nexus and review discipline. OMB Circular A-25 frames federal user charges around special benefits beyond those received by the general public, cost/value bases, and periodic review; National Cable illustrates why a charge imposed for general public regulatory protection cannot simply be called a fee.[S662][S663]

## Ordering rule

Run this pass after the initial tax/non-tax question and before rate, proceeds, remedy, or case-contract review. The pass asks: what institutional move is actually needed? A price instrument is weaker than a duty when the harm cannot be compensated; a fee is narrower than a tax when the charge funds general public functions; a rebate is incomplete when paid through the same failed private rail; and a public option is required when exit from the private channel is fictitious.

## Machine surface

The companion machine layer is [`../00-meta/policy-action-profiles.json`](../00-meta/policy-action-profiles.json), validated by [`../../tools/audit_policy_action_profiles.py`](../../tools/audit_policy_action_profiles.py). Each route record must state an action family, legitimate use, category error to block, required distinctions, and linkage to its remedy profile.

## Source IDs only

[S573][S662][S663][S664]

[S573]: ../../SOURCES.md#S573
[S662]: ../../SOURCES.md#S662
[S663]: ../../SOURCES.md#S663
[S664]: ../../SOURCES.md#S664
