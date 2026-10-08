# rev0104 to rev0105 migration map

rev0105 narrows FT-0090 by extracting signed profile-reference binding checks from the monolithic validator and making profile-reference binding coverage/time ordering executable.

| rev0104 | rev0105 |
|---|---|
| Local assessment temporal checks lived in `tools/assessment_temporal.py`. | That helper is retained unchanged. |
| `assessed_profile.binding` was schema-valid metadata but had little semantic validation. | `tools/profile_reference_binding.py` checks signed binding coverage and artifact-time ordering. |
| Digest-bearing profile references could carry a signed binding that omitted `digest` from `covers`. | Such references now fail semantic validation. |
| A profile-reference binding could be signed after the assessment/challenge that relied on it. | Such references now fail semantic validation for local assessments, evidence summaries, and authorized-verifier challenge targets. |
| 300 semantic vectors. | 303 semantic vectors. |

No TimeState core fields, profile maps, transport adapters, or evidence classes changed.
