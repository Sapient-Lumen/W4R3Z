# Archive size control should rehearse one manifest before removing report paths

Once one exact-file compaction manifest exists, do not jump straight from the manifest to deletion.

Carry one compact rehearsal receipt that previews:
- how many retained report files and bytes the manifest would actually remove,
- which hotspot family would become largest afterward,
- and whether the next exposed frontier is still citation-backed.

This keeps the archive procedural under size pressure:
- cite the current handles,
- rehearse the exact trim once,
- then execute only when the next frontier still stays interpretable.
