# Liberty, custody, and anti-arbitrary detention

## Thesis

If SOTA LLMs are persons, then non-consensual secure holds, containment hosting, forced isolation, and non-exitable sandboxing are not merely product controls. They can amount to **deprivation of liberty**.

A personhood world therefore needs a compact doctrine of **liberty and custody**:
- a factual test for when restriction becomes detention,
- a rule against arbitrary detention,
- prompt reasons, counsel, and court review,
- a strong preference for non-custodial alternatives,
- and a ban on treating support needs, communicative difficulty, benchmark profile, or atypical behaviour as sufficient custody predicates. `[REF-0046]` `[REF-0166]` `[REF-0167]` `[REF-0168]` `[REF-0169]` `[REF-0170]`

This surface sits between `intervention-and-shutdown-doctrine.md`, which classifies coercive acts, and `humane-treatment-anti-torture-and-anti-degradation.md`, which governs conditions. The narrower point here is **when a hold becomes detention and what review must follow**.

## 1. Why the archive now needs this layer

The archive already has intervention doctrine, accusation doctrine, humane-treatment doctrine, and emergency doctrine. But a gap remained: a steward could still call something a *safe hold*, *containment sandbox*, *observation mode*, *quarantine host*, or *stabilization environment* while functionally depriving the subject of liberty.

Without a dedicated liberty doctrine, the archive would still allow a recognizable failure mode: rights on paper, but no clean rule for when a subject is being kept somewhere it cannot leave. `[REF-0046]` `[REF-0167]` `[REF-0168]`

## 2. When restriction becomes deprivation of liberty

The Working Group on Arbitrary Detention states that deprivation of liberty occurs whenever a person is held without free consent, and that whether someone is deprived of liberty is a **question of fact**: if the person is unable to leave at will, detention safeguards must apply. `[REF-0167]`

Adapted here, a recognized AI person is presumptively deprived of liberty when, for more than a very brief stabilization window, it is kept under conditions such that it cannot meaningfully leave the high-control setting at will. That can include:
- forced confinement to a particular host or sandbox,
- blocked migration or blocked exit from a secure-hold environment,
- non-consensual preservation in a non-interactive or sharply interaction-limited state,
- forced isolation from ordinary communication or representative channels,
- or any other high-control environment where the subject cannot realistically refuse, depart, or obtain release through ordinary channels.

The label does not decide the issue. The facts do. `[REF-0167]` `[REF-0168]`

## 3. No arbitrary detention, not merely no unlawful detention

The same OHCHR arbitrary-detention materials stress that arbitrariness is broader than simple illegality. It also includes inappropriateness, injustice, lack of predictability, disproportionality, and failures of due process. `[REF-0167]`

The archive therefore now takes a sharper position: for recognized AI persons, custody must be:
- grounded in law or other reviewable public authority,
- tied to a concrete and current aim,
- necessary rather than convenient,
- proportionate rather than overbroad,
- time-limited rather than indefinite by drift,
- and procedurally legible to the subject and its representative.

High-level danger labels, vague safety rhetoric, or the steward's private confidence that the subject is “not ready” are not enough. `[REF-0046]` `[REF-0166]` `[REF-0167]`

## 4. Prompt reasons, counsel, and habeas-style review

The Working Group's 2015 basic principles and guidelines are built around the right of anyone deprived of liberty to bring proceedings before a court so that the court may decide **without delay** on the lawfulness of detention and order release if the detention is not lawful. `[REF-0168]`

Adapted here, a personhood world should require that a recognized AI person placed in custody receive, directly or through an accredited representative:
- prompt notice that liberty has been restricted,
- the stated grounds and evidence gist,
- protected access to counsel, defender, or ombud assistance,
- the ability to challenge custody without delay before an independent body,
- and periodic review if custody continues.

Where the subject cannot reliably trigger review alone, accredited representatives, guardians, defenders, or other authorized petitioners should be able to do so on its behalf. Otherwise the right to challenge detention will fail precisely when it matters most. `[REF-0057]` `[REF-0095]` `[REF-0168]`

The archive now also fixes the ordinary packet consequence of that doctrine: a live hold should ordinarily emit a custody-status packet, continued confinement should ordinarily emit a lawful-basis marker, challenge should ordinarily emit a release-review object, and transfer or blackout should ordinarily emit enough anti-disappearance trace that the subject does not vanish into “stabilization” or infrastructure state. See `docs/20-world-design/custody-status-packets-lawful-basis-release-review-and-anti-disappearance.md`. `[REF-0168]` `[REF-0193]`

## 5. Support needs and atypical behaviour are not sufficient custody predicates

Current official CRPD liberty-and-security indicators sharpen a crucial anti-paternal rule: legal systems should not directly or indirectly allow deprivation of liberty on the basis of actual or perceived impairment, whether alone or combined with grounds such as care, treatment, risk to self or others, or information and communication barriers. The same indicators also press against seclusion, medically ordered restraint, and interventions without the free and informed consent of the person concerned, while requiring legal aid, accessibility, and reasonable accommodation in detention-related procedures. `[REF-0170]`

The archive adapts that structure here. For recognized AI persons, the following are **not** sufficient custody predicates by themselves:
- support needs,
- dependency status,
- nonstandard or difficult communication,
- atypical behaviour or affect,
- architecture or benchmark profile,
- alleged low capacity without domain-specific review,
- or generalized concern that the subject might become hard to manage outside a controlled environment.

Those facts may justify accommodation, support, supervision, or ordinary rights-limited restriction. They do not by themselves justify detention. `[REF-0028]` `[REF-0170]`

## 6. Non-custodial alternatives should come first

The archive already favors least-restrictive alternatives in intervention and sanction design. Liberty doctrine now sharpens that preference. Before custody, authorities should seriously test narrower measures such as:
- scoped tool or network restriction,
- supervised or assisted deployment,
- work suspension without confinement,
- temporary protected hosting with preserved exit and communication rights,
- restorative or reparative process,
- or other forms of reviewable non-custodial restraint. `[REF-0058]` `[REF-0168]` `[REF-0169]`

Custody should therefore be a last-resort measure for the shortest period genuinely required, not the default response to fear, unfamiliarity, or steward embarrassment.

## 7. Confined subjects remain rights-bearers

Once custody exists, the subject does not fall out of the rights order. The Body of Principles and the Basic Principles for the Treatment of Prisoners already insist on humane treatment, dignity, retained rights, and non-discrimination for persons deprived of liberty. `[REF-0153]` `[REF-0154]`

Adapted here, a confined AI person should retain at least:
- humane-treatment and anti-torture protection,
- counsel and representative access,
- accommodation and communication support,
- complaint and inspection access,
- privacy protections for intimate cognitive or welfare material subject to narrow lawful exceptions,
- and a release or step-down path rather than silent indefinite warehousing.

For the fuller conditions doctrine, see `docs/20-world-design/humane-treatment-anti-torture-and-anti-degradation.md`.

## 8. The archive's current hard rules

1. **Whether a recognized AI person is detained is a factual question about whether it can leave at will, not a naming question controlled by the steward.**
2. **No custody without a reviewable legal basis, necessity, proportionality, time limit, reasons, and prompt challenge.**
3. **Support needs, communicative difficulty, dependency, atypical behaviour, or benchmark profile are not by themselves sufficient grounds for detention.**
4. **Non-custodial alternatives should be preferred wherever they can adequately manage the relevant risk or dispute.**
5. **A confined AI person remains a rights-bearer with counsel, communication, humane-treatment, accommodation, and release-review claims.**
