# Scenario: large heap value should be constructed in final allocation, not stack-bounced

A crate advertises in-place heap construction for a very large value. The receipt must say whether bytes were first assembled in a temporary stack place before being copied into the heap.
