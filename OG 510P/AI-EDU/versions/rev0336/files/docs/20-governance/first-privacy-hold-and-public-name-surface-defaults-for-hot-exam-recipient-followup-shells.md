# First privacy-hold and public-name-surface defaults for hot-exam recipient followup shells

The archive can now publish a very small post-conferral and post-publication grammar for the hottest
exam-like learner-request routes.

It can already say:

- what later standing, honors, aid/athletics, and conferral truth remains frozen rather than
  rewritten backward;
- what public-facing list, ceremony, program, newspaper, or web surface is merely tentative,
  historical, dynamic, or nonofficial;
- what transcript, diploma, or registrar-maintained record owns the final academic truth;
- and when later repair changes the live web surface, only the official record, or neither.

That is still not enough.

The archive still lacked the next tighter answer: **once a campus already admits that public
surfaces and official record truth do not always move together, what privacy or
directory-information control suppresses public visibility, what name surfaces can be chosen
separately, what happens if the learner misses the filing deadline, and which later name changes
stay prospective-only or replacement-only instead of rewriting every earlier public surface?**

This document adds one thing only:

- a **tiny privacy-hold / public-name-surface control field set** for those already named hot-exam
  recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether
the public list is tentative or historical**. It now asks **what public visibility can be blocked by
privacy settings, which name tokens travel separately across transcript, commencement, diploma, and
Dean's List surfaces, what defaults fire when a deadline is missed, and when later name repair
reaches only later official artifacts rather than earlier public surfaces**.

Current official signals support a deliberately narrow answer. The University of Washington
separates Student Record Name, Preferred Name, Commencement Program Name, Diploma Name, and Dean's
List Name; it says the student record name governs the official transcript and becomes the default
for commencement and diploma if no alternative is provided by the specified deadline, and it says
missed commencement and Dean's List name deadlines fall back to the student record name. UW–Madison
says FERPA restrictions ordinarily block Dean's List publication, but the graduation workflow can
also ask a learner to override the FERPA hold for commencement-program listing and let the learner
choose legal name or name-in-use for diploma and commencement materials. Penn says a
graduation-application deadline controls commencement-program printing, FERPA opt-out suppresses
program listing, and later diploma-name or legal-name updates do not rewrite the already submitted
graduation application. UNC says diploma-name changes can continue until degree conferral, but
commencement-program name changes have an earlier posted deadline; after the diploma order is
placed, the learner must buy a replacement diploma for the new name. Illinois says preferred first
name does not automatically change the diploma or commencement materials, and the legal name remains
the default unless a separate diploma name is specified. UAF says a directory hold suppresses Dean's
/ Chancellor's lists, commencement-program listing, and other university publications. College of
Staten Island says preferred name does not automatically carry into diploma or commencement
publications; the learner must set a separate diploma name, late submissions may miss commencement
publications, and the diploma name does not change the transcript or other official enrollment/aid
records. Together those signals support a tighter archive rule: **the next truthful portability gain
here is one tiny privacy-hold / public-name-surface control layer, but not one universal publicity
default, one universal FERPA-override rule, one universal preferred-name propagation rule, one
universal deadline, or one universal later-name-rewrite rule.** See `B235`.

## Small field set for privacy-hold and public-name-surface defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `PN0-NO-UNIVERSAL-PUBLICITY-DEFAULT-OR-NAME-PROPAGATION-RULE` | no one universal FERPA / directory-hold, preferred-name, diploma-name, commencement-program-name, or public-list rule governs all public surfaces the same way | keep publicity and name-surface publication route-bounded instead of implying `preferred or legal name must always flow everywhere` |
| `PN1-PUBLISH-PRIVACY-HOLD-SCOPE-AND-WHETHER-A-NAMED-OVERRIDE-EXISTS` | publish only whether directory-information restriction suppresses the public surface, whether that suppression reaches all university publications or only some, and whether a named override is offered for a specific surface such as commencement | distinguish privacy control from academic-record error |
| `PN2-PUBLISH-WHICH-PUBLIC-AND-OFFICIAL-NAME-SURFACES-ARE-SEPARATE` | publish only whether the route recognizes separate student-record, preferred/lived, commencement-program, diploma, or Dean's List name surfaces | distinguish one public name choice from full academic-record renaming |
| `PN3-PUBLISH-NON-AUTOMATIC-PROPAGATION-BETWEEN-NAME-SURFACES` | publish only whether preferred/lived or primary-name updates do not automatically carry into diploma, commencement, or other public surfaces unless a separate name token is filed | distinguish ordinary identity presentation from surface-specific publication choice |
| `PN4-PUBLISH-DEADLINE-FALLBACK-AND-LATER-CHANGE-BOUNDARIES` | publish only whether a deadline must be met for public listing, what name is used when the deadline is missed, and whether later correction is prospective-only, application/program-static, or replacement-diploma-only | distinguish missed-deadline defaults from later official-record or diploma repair |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `privacy_release_scope_token` — `directory hold suppresses all public surfaces`, `restriction
   suppresses Dean's List or named public list`, `commencement-only FERPA override available`,
   `public listing suppressed unless waived`, `none inherited`, or `not published`;
2. `public_name_surface_token` — `student-record name default`, `preferred/lived name separate from
   public surface`, `separate commencement-program name`, `separate diploma name`, `separate Dean's
   List/publication name`, `graduation workflow asks legal versus preferred/name-in-use choice`,
   `none inherited`, or `not published`;
3. `non_propagation_boundary_token` — `preferred name does not auto-change diploma`, `preferred name
   does not auto-change commencement/publications`, `primary/legal-name change does not auto-change
   diploma name`, `diploma name does not change transcript`, `none inherited`, or `not published`;
4. `deadline_default_token` — `missed deadline prints student-record/legal name`, `must apply by
   publication deadline for listing`, `late name filing may miss commencement publications`,
   `deadline posted separately from conferral date`, `none inherited`, or `not published`;
5. `late_change_effect_token` — `later application/program surface not rewritten`, `later
   diploma-name change remains prospective only`, `replacement diploma required after order`,
   `replacement transcript must be purchased after record-name change`, `public surface stays as
   published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish privacy-based omission from academic error,
separate name surfaces from global record renaming, non-automatic propagation from automatic
identity sync, missed-deadline fallback from later name repair, and replacement-only cleanup from
retroactive republication.

## First privacy-hold and public-name-surface assignments

| Route or family | Privacy / publicity control now admitted | Separate name-surface truth now admitted | Non-propagation / deadline / later-change truth now admitted | Why |
|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not published` | current ambiguity guidance still exposes reporting, correction, and recipient followup rather than privacy-controlled public-name surfaces |
| campuses with explicit directory-hold suppression across dean-list, commencement, or other university publications | `directory hold suppresses all public surfaces` or `restriction suppresses Dean's List or named public list` | `not published` or `student-record name default` | `public omission is intentional rather than academic-record error` | UAF and UW–Madison make it explicit that privacy restriction can suppress public listing without changing official record truth |
| campuses that separate student-record, preferred, commencement, diploma, and dean-list/publication names | `public listing may require opt-in or no opt-out` | `separate commencement-program name`, `separate diploma name`, `separate Dean's List/publication name` | `missed deadline prints student-record/legal name` or `replacement transcript must be purchased after record-name change` | UW shows the archive can publish a real multi-surface name grammar without pretending that one name token governs every surface |
| campuses where graduation workflow allows legal-vs-preferred/public-name choice and may also offer a commencement-specific FERPA override | `commencement-only FERPA override available` | `graduation workflow asks legal versus preferred/name-in-use choice` | `must apply by publication deadline for listing` | UW–Madison and UC show that a privacy hold can sometimes be overridden for commencement, but only through the named graduation flow |
| campuses where preferred or lived name does not automatically propagate to diploma / commencement / transcript surfaces | `not published` or `public listing suppressed unless waived` | `preferred/lived name separate from public surface` or `separate diploma name` | `preferred name does not auto-change diploma`, `preferred name does not auto-change commencement/publications`, `diploma name does not change transcript`, or `late name filing may miss commencement publications` | Illinois and CSI make the non-automatic propagation boundary explicit |
| campuses where program listing freezes earlier than diploma printing and later name repair becomes prospective-only or replacement-only | `public listing suppressed unless waived` | `separate diploma name` | `deadline posted separately from conferral date`, `later application/program surface not rewritten`, or `replacement diploma required after order` | Penn and UNC show that later name correction can still reach the diploma or later official artifact without rewriting the earlier program/application surface |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `PN0-PN4` layer whenever current offices
explicitly expose:

- whether privacy restriction suppresses public listing and whether any named override exists;
- whether public and official surfaces have separate name tokens;
- whether preferred/lived or legal-name updates fail to auto-propagate across those surfaces;
- whether missing the listing deadline falls back to student-record or legal name; and
- whether later name repair is prospective-only, replacement-only, or leaves an earlier
  public/application surface unchanged.

They still should **not** publish one universal FERPA-override workflow, one universal rule that
preferred name automatically changes diploma or commencement materials, one universal filing
deadline, or one universal duty to rewrite earlier public surfaces after later name correction.
