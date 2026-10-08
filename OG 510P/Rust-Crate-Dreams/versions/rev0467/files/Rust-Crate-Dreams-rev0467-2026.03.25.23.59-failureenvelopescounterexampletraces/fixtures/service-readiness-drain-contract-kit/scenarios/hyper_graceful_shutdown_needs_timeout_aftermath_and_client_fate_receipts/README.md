# graceful shutdown still needs timeout-aftermath and client-fate truth

This scenario keeps **graceful drain intent** separate from **timeout aftermath** and **client-visible request fate**.
Even when a framework supports graceful shutdown, reviewers still need an explicit account of what happens when the grace budget expires.
