# Resilio escalation-lane entitlement, destination, and support-route ambiguity evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than `there is a support link somewhere`.
Current official docs are candid that **who may receive the package and by which lane** actually matters:

- the current `Collecting debug logs automatically` guide still says technical support is available exclusively for Resilio Sync Business customers, while Sync v3 users are directed to the community forum and Help Center for functionality help, and payments/licensing questions are sent to a web form
- that same automatic-log guide still tells the operator to open an in-app `Preferences (Settings) > Support > Contact support` form and send feedback with logs
- the current `Collecting debug logs manually` and current crash/core-dump guides still repeat the same Biz-only / Sync v3 self-serve / payments-web-form split
- the current `I still have questions, where can I get answers?` article still says users can look through the forum and also contact support, with `PRO users` first to get a response and `FREE users` answered to the extent possible
- the current `Licensing in Resilio Sync 3.0` article still says Resilio Sync Business licenses are not compatible with Sync v3 and that commercial users should continue using Sync v2 or explore business solutions
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`, including license-application UI work and earlier fixes for a non-clickable `Can't download file` status

That candor is useful.
Resilio is not pretending that every question goes to one identical destination.

The non-clone problem is still lane ownership.
One ordinary operator answer is still reconstructed too late:

> who is actually supposed to receive this package, what entitlement or product line makes that lane valid, and what outcome should the operator honestly expect after pressing send?

## What current official docs still get right

### 1) Different questions do belong to different lanes

Current docs still distinguish at least:

- forum / help-center self-service for many Sync v3 functionality questions
- direct technical-support lanes for Business customers
- payment / licensing web-form routes
- in-app feedback/send surfaces
- separate commercial-versus-non-commercial product lines

That is better than pretending every outbound action is just `contact support`.

### 2) Product line and entitlement are real facts

Current official docs still admit that:

- Sync v3 changed licensing and support posture
- Business and v3 are not one support/upgrade line
- commercial use and non-commercial use do not imply the same route
- edition and entitlement affect what recipient is actually plausible

That is good.
It acknowledges that route validity is not only a transport question.

### 3) Audience changes package meaning

A raw log packet sent to a private ticket, a licensing question sent through a web form, and a reproducible functional issue summarized for a public forum are not the same audience situation.
Current docs at least hint at this by separating forum/help-center guidance, Business-only support language, and payments/licensing web-form routing.

## Where the current contract still fails

### 1) The visible send surface still does not resolve the contradiction

The product/help surface can still show `Submit Customer Service Request`, `Contact support`, community links, and Biz-only support language at the same time.
The ordinary operator still has to reconcile:

- `direct technical support is not available` for Sync v3 functionality
- `Contact support` exists in-product
- `PRO users are first to get response` and `FREE users` may still be answered to the extent possible
- payments/licensing belong to a separate web form

That is too much interpretation for one send action.

### 2) Destination identity is still under-described

The product still does not leave one durable object saying:

- which exact lane is being used
- which recipient class that lane implies (`forum`, `private ticket`, `billing/licensing desk`, `local-only save`, `other`)
- which question classes the lane is fit for
- which response, privacy, or follow-up expectations are realistic

Without that object, operators confuse transport with destination.

### 3) Package fit is still not reviewed against the lane

A package that is sensible for a private business ticket may be too sensitive, too raw, or too context-poor for a public/self-serve lane.
Current docs still leave the operator to figure out whether the current package should be:

- kept local
- summarized first
- split before sharing
- redirected to another lane
- or held because entitlement/destination is mismatched

### 4) Delivery is still too easy to over-interpret

Even if an upload, feedback form, or request submission succeeds, the product still does not publish one durable receipt saying:

- why this lane was chosen
- which entitlement basis made it valid or provisional
- what audience received it
- whether any answer is actually owed
- what would force a redirect or re-export later

## What AnonSync should do instead

AnonSync should keep the candor and reject lane folklore.
The product should own four ordinary page families for this seam:

1. **Escalation lane page**
   - available lanes
   - entitlement basis
   - audience class
   - issue-fit contract

2. **Escalation review page**
   - compare candidate lanes
   - explain why one lane wins
   - show package-fit and privacy consequences
   - make mismatch explicit before send

3. **Destination confirmation page**
   - exact recipient class
   - purpose of this package in that lane
   - visibility/privacy posture
   - follow-up expectation

4. **Escalation lane receipt page**
   - chosen lane and entitlement basis
   - destination class and delivery state
   - response expectation ceiling
   - redirect / reopen boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that support lanes, entitlement, and audience really differ by product line and question class. But it is not worth cloning the way the ordinary operator still has to reconcile forum guidance, Biz-only support language, web-form routing, and in-product `Contact support` affordances without one product-owned lane contract.

## New replacement pages added in this revision

- `752` Escalation lane page
- `753` Escalation review page
- `754` Destination confirmation page
- `755` Escalation lane receipt page
