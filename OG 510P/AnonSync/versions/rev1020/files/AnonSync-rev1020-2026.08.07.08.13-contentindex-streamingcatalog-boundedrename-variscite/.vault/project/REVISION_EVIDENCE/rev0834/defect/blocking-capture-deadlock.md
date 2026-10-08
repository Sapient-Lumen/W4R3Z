# Defect: blocking output collection could deadlock before child exit

## Parent behavior

The rev0833 allocator-fault bridge connected a worker stream to a pipe and then
assembled output and exit evidence through local blocking choreography. A worker
that exceeded pipe capacity, left a writer open, or stopped before exit could
prevent the parent from reaching the corresponding wait or cleanup path.

## Correction

Rev0834 drains stdout and stderr concurrently while the process is live. The
executable oracle queries the real pipe capacity and writes capacity plus 4096
bytes to each stream. Completion requires exact bytes, both EOFs, and a reaped
leader under one deadline.

## Remaining boundary

This proves the reviewed test helper topology, not arbitrary hostile child
behavior or kernel/resource exhaustion.
