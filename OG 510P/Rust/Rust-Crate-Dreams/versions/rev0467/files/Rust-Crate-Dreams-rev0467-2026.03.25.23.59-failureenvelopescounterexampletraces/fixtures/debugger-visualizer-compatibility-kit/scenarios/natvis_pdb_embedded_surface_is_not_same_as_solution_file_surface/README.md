# Scenario — NatVis embedded `.pdb` surface is not the same as a solution-file surface

This scenario exists to keep a common Windows debugging confusion explicit.
Two observations can both say “NatVis worked” while still representing different support surfaces:

- one visualizer came from an embedded `.pdb` asset,
- another came from a solution/project `.natvis` file that Visual Studio can refresh live.

Current Microsoft NatVis docs make the difference concrete: Visual Studio can load `.natvis` from embedded `.pdb`, project/solution files, VSIX registration, and user/system visualizer directories with an explicit precedence order, and embedded `.pdb` NatVis cannot be updated live during a debugging session.

The point of this fixture is therefore not to prove one route is “better”.
It is to make the **probe surface** reviewable so bundle consumers do not over-read a green observation from one delivery route as proof of the other.
