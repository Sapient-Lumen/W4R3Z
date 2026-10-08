# Locale-sensitive serialization inventory

The lexical inventory records 58 production `std::ostringstream` constructions and two
explicit classic-locale imbues. This ratio is a search compass, not a defect count.

Streams that only build human diagnostics need not necessarily be locale-independent.
Streams that produce JSON, replay records, signed inputs, hashes, receipts, or wire bytes
must have an explicit format contract. The next audit should classify each site, add a
custom-global-locale regression to machine serializers, and avoid claiming canonical
JSON unless ordering, escaping, numbers, Unicode, and duplicate-member behavior are all
defined and tested.
