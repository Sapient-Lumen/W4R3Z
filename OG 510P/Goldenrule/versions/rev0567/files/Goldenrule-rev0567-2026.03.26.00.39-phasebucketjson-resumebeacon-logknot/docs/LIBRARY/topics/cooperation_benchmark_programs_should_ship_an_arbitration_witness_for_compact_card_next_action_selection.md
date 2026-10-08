# Cooperation benchmark programs should ship an arbitration witness for compact-card next-action selection

Once a benchmark archive emits one preferred next action, a new risk appears: the chosen command can look more authoritative than the evidence that selected it.

That risk is avoidable.
A tiny arbitration witness can preserve:
- the live candidate family,
- the winning priority bucket,
- the tie set at that bucket,
- and the stable selector used to choose the final representative.

This keeps the next-action layer honest.
The archive still offers one practical first command, but it also preserves whether that command was uniquely forced or only the stable representative of a live tie.
