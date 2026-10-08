# Miri dynamic execution does not close a proof obligation

This scenario keeps **dynamic execution evidence** separate from proof-shaped evidence.

The point is not that Miri is weak.
The point is that a campaign policy can legitimately require `bounded-proof` or `theorem-proof` evidence for some obligations.
A useful campaign crate must therefore be able to say:

- the Miri lane passed,
- the obligation still lacks the accepted evidence class,
- and the overall campaign is therefore still yellow or red.
