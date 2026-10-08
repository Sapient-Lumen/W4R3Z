# 980 — Applied digital-administrative service-home case packet for GOV.UK One Login, HMRC, DWP, relying services, and no service home by shared account

## One-line thesis

GOV.UK One Login is not a service home merely because it gives people one account, one proofing route, one status page, or one future front door for government services; it becomes a credible digital-administrative service home only when GDS platform duties, relying-department duties, service-by-service configuration, assisted access, delegated access, incident fallback, migration receipts, support routing, and source-boundary limits are visible together.

## Why this matters

Rev0779 kept note `615` active because the service-home successor route still leaned too heavily on transport, water, and intermunicipal examples. Rev0780 added a social-service stress case through LAHSA. Rev0781 added an emergency-communications stress case through NG911. The remaining risk was administrative/digital: a central public-service platform can look like a service home because it is the common place where users arrive, prove themselves, receive tokens, store documents, or see a status page.

GOV.UK One Login is a good administrative/digital stress case because it is both narrower and more dangerous than the phrase "one account" suggests. It can reduce duplicate sign-ins and proofing routes, but it can also become the practical gate through which tax, company, licensing, benefits-adjacent, and future wallet/document services pass. A shared digital front door is not a service home unless the public can still see who owns each service promise and what happens when identity proofing, claims, delegation, session return, wallet/document state, or account recovery fails.

This note does not replace note `904`. Note `904` classifies GOV.UK One Login as a credential-access waist. This note asks the service-home question: whether the shared administrative/digital layer has enough public constitution to prevent a central account from hiding the service owner.

The governing repair phrase is **no service home by shared account**.

## Relationship to the service-home retirement work

This packet is the first administrative/digital service-home application added after the final preservation review for note `615`. It reduces the administrative/digital thinness blocker in `MP-003-615-to-974`, but it does not retire note `615`.

Use it with:

- `archive/615-service-homes-for-shared-territorial-power-service-authorities-operator-chains-commissioning-continuity-and-no-government-by-memorandum-network.md` for original service-home lineage;
- `archive/901-identity-credential-access-and-delegated-authority-dockets-assurance-levels-recovery-relying-party-boundaries-and-no-public-service-by-login.md` for credential-access doctrine;
- `archive/904-applied-credential-access-case-packet-for-govuk-one-login-central-government-front-door-identity-proofing-incidents-and-no-service-by-single-sign-on.md` for the existing One Login credential-access packet;
- `archive/974-service-home-successor-route-for-shared-territorial-services-service-map-operator-chain-continuity-and-no-service-government-by-case-example.md` for the successor service-home route; and
- `generated/SERVICE_HOME_TESTS.md` plus `generated/ROUTE_REDIRECT_LEDGER.md` for test and redirect parity.

## Pattern pack

### 1. Start with the service transaction, not the account

The shared account is not the service. A user may have a GOV.UK One Login account, prove identity, pass authentication, or see a digital document, yet still fail to complete the underlying tax, company, licence, benefit-adjacent, veteran, import/export, or local-government transaction.

A service-home packet must therefore name:

- the relying service;
- the transaction or decision at stake;
- whether One Login is sign-in only, identity proofing, wallet/document, or a combined route;
- the public body that owns the service promise;
- the proofing level and claims requested;
- the alternative route if proofing or account recovery fails;
- the support route for the central layer and for the underlying service; and
- the appeal, complaint, review, deadline, or case-protection route.

If the packet cannot name the relying-service owner, it cannot call the shared account a service home.

### 2. Split GDS, relying departments, issuers, support, and service owners

A digital-administrative service home has to keep hats separate.

| Role | Evidence needed | Thin or dishonest shortcut |
| --- | --- | --- |
| Platform / identity provider | GDS ownership, technical documentation, status page, privacy/data notice, service support route | service home by central platform |
| Relying service owner | department/service page, legal transaction, assurance requirement, fallback and appeal route | service by login success |
| Data / claim owner | requested scopes, claims, sector identifiers, confidence levels, correction and minimization rationale | data by token |
| Proofing-route owner | app, security questions, Post Office or alternative routes, abandonment/support metrics | identity by one journey |
| Digital-document issuer | issuing authority, expiry, revocation, correction, device/wallet rule | status by wallet display |
| Incident / support owner | status page, urgent incident lane, contact route, service-specific continuity action | remedy by status page |
| Representative / helper lane | parent, carer, agent, appointee, professional or corporate access route | access by personal account |

### 3. Treat the connected-service list as a service map, not coverage proof

A list of services that use One Login is a useful service map. It is not proof that those services have been safely absorbed into a common service home.

The list should trigger a per-service table:

- sign-in only or identity check;
- legal consequence of the transaction;
- service owner;
- proofing and authentication requirement;
- claim/data minimization;
- fallback and assisted route;
- representative route;
- incident/deadline rule; and
- user-support owner.

A shared digital service fails the home test when the only visible map is a service count.

### 4. Treat HMRC and DWP onboarding as transition receipts, not completion

The HMRC and DWP examples matter because they show the platform moving into high-volume, high-consequence administrative terrain. They are not completion proof.

For HMRC, a service-home packet should ask whether new-user rollout and future Government Gateway migration have:

- old/new account transition receipts;
- contact-centre and friction metrics;
- deadline protection if proofing or return links fail;
- agent/corporate/delegated access lanes;
- tax-record, payment, appeal, and notice boundaries; and
- service-specific fallback if the central account is unavailable.

For DWP, a service-home packet should ask whether new proofing questions using DWP-held information improve inclusion without turning one department's data into an unchallengeable gate for other services.

### 5. Make support and incident handoff part of the service constitution

The One Login support route is necessary but insufficient. When an identity-proofing incident or authentication error interrupts a consequential service, the user needs both central-account support and service-owner protection.

A credible packet should show:

- central support route;
- relying-service support route;
- urgent incident route for service teams;
- status-page incident classification;
- affected-service notification;
- deadline pause or protective filing rule;
- return-link/session recovery; and
- post-incident learning.

A status page can inform. It cannot by itself remedy.

### 6. Keep assisted, delegated, and non-digital access visible

One Login can improve inclusion by broadening proofing routes. It can also exclude people who lack documents, stable devices, email/SMS access, confidence with the app, or the ability to complete a proofing route unaided.

A service-home packet should therefore separate:

- helper access;
- formal representative access;
- parent/carer/appointee access;
- corporate or agent access;
- assisted digital;
- Post Office or face-to-face route;
- language and disability support;
- hard-to-proof users; and
- non-digital or service-specific fallback.

Do not let a personal central account become a silent ban on legitimate representation.

### 7. Treat wallet and digital documents as issuer-governance, not display proof

A wallet can carry convenient evidence. It does not itself prove that the issuing authority's record is current, correct, revoked, replaced, or accepted by every relying service.

The packet should require issuer, document, expiry, revocation, correction, device-loss, offline-use, privacy, and relying-service acceptance rules before any digital document becomes part of a service home.

### 8. Keep configuration and claims visible enough for public accountability

Technical documentation matters because it shows that relying services choose levels of authentication, levels of identity confidence, requested attributes, scopes, claims, sector identifiers, and production configuration. Those are not purely developer details when they govern access to public services.

A service-home packet should require an accountability route for each service configuration: who chose the level, why it fits the transaction, what data is requested, what happens when the user cannot satisfy it, and when it is reviewed.

### 9. Use shared infrastructure to strengthen, not erase, service ownership

The best reading of One Login is that it lets service owners avoid rebuilding identity plumbing and focus on their service. The archive should preserve that advantage. The risk is that service owners then disappear behind the common front door.

The service-home rule is therefore: GDS may own the platform, but the department still owns the service consequence.

### 10. Do not retire service-home lineage until digital service homes show real outcome joins

This packet reduces the digital/admin thinness blocker for note `615`, but it does not eliminate it. One Login sources show architecture, service lists, support, status, onboarding, and proofing expansion. They do not prove that every relying service has fallback, representative access, deadline protection, or incident remedy.

## Applied digital-administrative service-home ladder

1. **Classify the transaction.** Sign-in, identity proofing, digital document, wallet, credential recovery, account migration, or service return link.
2. **Name the service owner.** Department, agency, arm's-length body, issuer, local authority, or service team.
3. **Name the central-layer owner.** GDS platform, One Login support, status, technical integration, privacy/data owner, or urgent incident lane.
4. **Map the relying-service configuration.** Authentication level, identity confidence, claims/scopes, sector identifier, production config, and data minimization.
5. **Protect alternatives.** Assisted digital, Post Office or face-to-face, representative/agent/appointee/corporate lanes, non-digital fallback, and hard-to-proof route.
6. **Protect continuity.** Status incident, maintenance, failed proofing, broken return link, account recovery, deadline pause, protective filing, and service-specific remedy.
7. **Prove transition.** HMRC or other migration receipt, Government Gateway/legacy account cutover, user cohort, support load, friction metrics, and rollback/fallback.
8. **Prove learning.** Incident review, support/contact-centre trend, proofing abandonment, inclusion metric, service-owner configuration review, and public source-health refresh.

## Applied examples

### Connected-service list

Use the public services list as a service map and risk queue. It says which services currently use One Login and therefore where the shared account may affect access. It does not prove that each service has an adequate fallback, support route, representative route, or proofing fit.

### HMRC onboarding

Use the GDS/HMRC rollout account as a transition receipt: it records a February 2026 public beta go-live for new HMRC users, future expansion to more new users, and a future phase for existing Government Gateway users. Treat the monitoring measures named there — usage, proofing success/friction, and contact-centre call volumes — as necessary evidence requests, not as proof that migration is harmless.

### DWP proofing questions

Use the GDS/DWP material as inclusion evidence: it describes additional security questions based on DWP-held information for people who cannot use the app route. Then test whether cross-department use of DWP-held data creates correction, challenge, privacy, and fallback duties.

### Technical documentation

Use the technical documentation to locate configuration seams: authentication level, identity confidence, scopes, claims, sector identifier, production configuration, testing, and incident integration. Do not treat standards-compliant integration as proof of service accountability.

### User account guide and status page

Use the user guide and status page to find support, deletion, sign-in, and incident surfaces. They must be joined to relying-service consequences before the archive can claim continuity or remedy.

## Repair surfaces

- connected-service inventory with sign-in/identity/document classification;
- service-by-service owner, consequence, assurance, claims, and fallback map;
- GDS/relying-service support and urgent incident handoff;
- account recovery, proofing abandonment, failed-return-link, and contact-centre logs;
- HMRC/Government Gateway migration receipt and rollback/fallback plan;
- DWP-held-data proofing correction, challenge, and inclusion metrics;
- assisted digital, Post Office, representative, agent, corporate, parent/carer/appointee routes;
- wallet/document issuer, expiry, revocation, correction, device-loss, and relying-service acceptance rules;
- status incidents joined to service deadlines and remedies;
- privacy and claim-minimization review records.

## Anti-theater tests

- Do not cite one account as one service home.
- Do not cite a service count as access proof.
- Do not cite OIDC integration as public accountability.
- Do not cite identity-proofing success as service eligibility.
- Do not cite a status page as a remedy receipt.
- Do not cite HMRC rollout as harmless migration without old/new account, contact-centre, deadline, and representative-access evidence.
- Do not cite DWP-held-data proofing as inclusion without correction, privacy, fallback, and challenge routes.
- Do not cite a wallet document as legal status without issuer and relying-service rules.

## Source posture

This packet uses official GOV.UK, GDS, HMRC/DWP, One Login technical, status, privacy, and public-service-list materials. The sources prove service architecture, support routes, connected-service scope, rollout claims, monitoring categories, and proofing-expansion posture. They do not prove that any individual service was completed, that every user can prove identity, that account recovery protects deadlines, that representatives can act, that wallet documents are accepted, or that service owners kept legal accountability when the central layer failed.

## What this repairs in the service-home residue

Rev0779 kept note `615` active partly because administrative and digital service-home application was thin. Rev0782 partially repairs that blocker. The successor route now has infrastructure, social-service, emergency-communications, and administrative/digital identity applications. The remaining thinness is narrower: non-identity administrative shared-service families and local digital shared services still need applied packets, and even this packet needs service-specific outcome evidence before any deletion authorization can exist.

## rev0783 local digital companion

Rev0783 adds note `981` as a local digital administrative companion service-home packet for NYC MyCity. It is a separate applied example, not a replacement for this packet.
