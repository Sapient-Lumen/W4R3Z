# Denominator visibility fields

Future study/claim records should be able to attach the following typed links.

| field | meaning |
|---|---|
| `visibility_layer` | registry, preregistration, Registered Report, results posting, formal update, or post-publication critique |
| `visibility_object_id` | NCT number, registry DOI, OSF registration URL, AsPredicted ID, AEA registry DOI, article DOI, PubPeer publication identifier, RWDB record ID, etc. |
| `visibility_timing` | before recruitment, before analysis, after completion, after publication, after correction/retraction |
| `public_state` | public, embargoed, private, unavailable, withdrawn, dynamic/unknown |
| `result_visibility` | none, registry summary results, paper result, preprint result, press release, correction/retraction notice |
| `plan_adherence_state` | unknown, adherent, deviated-with-disclosure, deviated-without-disclosure, not applicable |
| `claim_status_effect` | none yet, supports, narrows, contradicts, flags for review, supersedes, retracts |
| `privacy_or_ethics_note` | sensitive population, living researchers, private/embargoed record, comment-risk, medical-advice warning |

Do not collapse these fields into a boolean. Denominator visibility is a graph, not a checkbox.
