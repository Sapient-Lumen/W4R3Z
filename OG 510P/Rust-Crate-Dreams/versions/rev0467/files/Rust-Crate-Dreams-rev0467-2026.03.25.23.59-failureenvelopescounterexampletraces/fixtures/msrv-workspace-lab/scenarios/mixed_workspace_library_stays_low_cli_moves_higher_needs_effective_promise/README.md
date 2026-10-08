
# Mixed workspace library stays low while CLI moves higher

This scenario exists to show that a workspace support promise may need to split by member instead of pretending there is one honest number for the whole repo.

What should happen:
- the public library keeps the lower published promise,
- the CLI and examples are allowed to move higher,
- the manifest captures command-family expectations per member,
- and the bundle makes it obvious that lockfile authoring may still require a newer lane.

The point is not to make mixed-MSRV workspaces look uniform.
The point is to make the split portable and reviewable.
