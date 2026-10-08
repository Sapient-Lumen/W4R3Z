# Rev0980 research note

The revision follows a standard database-lineage principle: content equality and a local generation counter do not identify an independently created database. A random incarnation separates lineages; an explicit recovery epoch invalidates pre-recovery evidence after an operator-declared restore. Because both values reside in the database image, they are continuity metadata rather than external anti-rollback authority. A future destructive collector must pair them with an external monotonic or conservative recovery policy.
