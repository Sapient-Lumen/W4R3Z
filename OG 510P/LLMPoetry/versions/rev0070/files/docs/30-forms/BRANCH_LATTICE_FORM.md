# Branch lattice rendered form

Form ID: `FORM-branch-lattice-rendered`

A branch lattice poem stores candidates in a packet, renders one selected path, retains a counterpath assembled from rejected options, and exposes the full lattice. The markdown draft is not the sole poem; it is a reproducible face of a machine-readable packet.

Optional high-risk feature: unselected candidates may carry a mechanically verifiable shadow sentence through their final words. This is useful only when the rejected branches change the reading of the selected path.

Minimum requirements:

- branch packet names the prompt, layers, candidates, selected path, and candidate count;
- exactly one candidate is selected per layer;
- selected line initials match the packet claim;
- every candidate appears in the rendered draft when `all_candidates_must_appear_in_draft` is true;
- any claimed unselected-final-word sentence is mechanically verified;
- selector map records exact selected lines and character positions;
- render receipt records packet, draft, and script hashes;
- same-turn quality judgment of a newly drafted rendering is prohibited.

Failure modes:

- the apparatus becomes self-congratulation;
- rejected branches become footnotes rather than pressure;
- the selected path is weaker than a rejected path;
- the shadow sentence is better than the poem and exposes it;
- disclosure appears as slogan rather than runtime condition.

Current use: `P0001-D002`.
