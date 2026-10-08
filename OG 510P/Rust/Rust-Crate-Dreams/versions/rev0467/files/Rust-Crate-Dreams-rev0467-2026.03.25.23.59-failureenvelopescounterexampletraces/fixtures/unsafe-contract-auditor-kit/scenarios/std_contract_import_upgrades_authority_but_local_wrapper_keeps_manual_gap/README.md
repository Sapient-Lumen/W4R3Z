# std contract import upgrades authority but local wrapper keeps manual gap

This scenario models a crate that imports stronger authority from future std-contract-style annotations, but still wraps the unsafe API in a local abstraction whose callback and aliasing conditions remain only partially mapped.

The point is to keep **authority upgrade** separate from **full local closure of the obligation**.
