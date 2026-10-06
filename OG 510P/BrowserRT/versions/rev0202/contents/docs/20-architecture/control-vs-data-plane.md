# Control plane versus data plane

BrowserRT has two planes.

## Control plane

The control plane carries small messages:

- task ids;
- priority;
- deadlines;
- cancellation;
- lane selection;
- dependency edges;
- payload references;
- trace ids.

## Data plane

The data plane carries bytes:

- transferred ArrayBuffers;
- shared-memory slabs;
- streams;
- OPFS block refs;
- GPU buffers;
- compressed block payloads.

## Rule

Do not send giant object graphs through control-plane messages. A worker message
may describe bytes; it should not usually contain the bytes unless they are small.

## Review question

When reviewing a new API, ask: does this move data as bytes with ownership, or
as accidental JavaScript shape? If it is the latter, stop and redesign.
