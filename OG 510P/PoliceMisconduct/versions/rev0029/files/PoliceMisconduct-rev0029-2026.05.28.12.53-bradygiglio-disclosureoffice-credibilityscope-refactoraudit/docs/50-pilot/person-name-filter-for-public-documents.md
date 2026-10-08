# Person-name filter for public documents

Many public accountability documents contain people who should not become corpus entities merely because their names are present.

Rev0007 uses a simple rule: **no person extraction from DOJ pilot PDFs.**

This includes:

- judges and attorneys;
- monitors and consultants;
- agency officials;
- officers named in footnotes or narrative sections;
- civilians, witnesses, family members, public commenters, survivors, minors, and vulnerable-community members.

Future revisions may create separate citation-role metadata for judges or attorneys if necessary, but that is not officer/person entity resolution. Officer entity creation remains closed until weighted identifiers, correction routes, and display gates are ready.
