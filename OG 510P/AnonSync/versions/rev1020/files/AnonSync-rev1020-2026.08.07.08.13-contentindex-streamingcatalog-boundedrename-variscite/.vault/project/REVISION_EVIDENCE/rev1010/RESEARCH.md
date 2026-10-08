# Rev1010 research note

The scale decision remains intentionally conservative: persist one bounded
source projection for restart recovery rather than introducing a global or
multi-source chunk index without measurements. The 8,192-chunk protocol frontier
is sufficient for the existing 4 TiB payload ceiling at the maximum 512 MiB
chunk size. Completed manifests remain O(chunk count), so target-scale RSS,
restart loss, write amplification, and disk latency still require measurement.
