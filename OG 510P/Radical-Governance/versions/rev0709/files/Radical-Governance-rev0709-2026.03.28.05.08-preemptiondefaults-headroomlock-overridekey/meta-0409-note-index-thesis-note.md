# Meta note — rev0409 note index now carries one-line thesis text

This revision upgrades the machine-readable note index so each numbered archive entry includes its extracted one-line thesis alongside the heading.

Why this matters:

- later merge work can compare not only filenames and titles, but the core claim of each note,
- continuation snapshots become easier to diff semantically when headings are similar but emphasis shifts,
- lightweight tooling can cluster notes by thesis without scraping the full markdown body,
- future archive hygiene work can detect notes whose title and thesis diverge too much.

This is intentionally small. It does not attempt full semantic tagging or ontology design. It just makes the continuity spine slightly more informative and easier to reuse.
