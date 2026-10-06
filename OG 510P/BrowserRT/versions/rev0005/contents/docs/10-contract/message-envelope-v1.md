# Message envelope v1

BrowserRT uses a stable envelope to separate control-plane messages from
data-plane bytes.

## Envelope fields

```ts
type RtEnvelopeV1 = {
  magic: 'BRT1';
  id: string;
  parentId: string | null;
  traceId: string;
  op: string;
  version: 1;
  priority: RtPriority;
  deadlineMs: number | null;
  cancelToken: string | null;
  lane: RtLane;
  flags: string[];
  payloadRef: RtPayloadRef;
};
```

## Payload refs

```ts
type RtPayloadRef =
  | { kind: 'inline-json'; bytes: number }
  | { kind: 'transfer'; bufferId: string; bytes: number }
  | { kind: 'shared'; slabId: string; offset: number; length: number }
  | { kind: 'opfs'; path: string; offset: number; length: number }
  | { kind: 'stream'; streamId: string }
  | { kind: 'gpu'; bufferId: string; bytes: number };
```

## Rules

- `inline-json` is for small control data only.
- Large data must use a payload ref.
- Every envelope carries a trace id.
- Every fallback changes flags and emits a trace event.
- Future binary encoding may replace JSON, but the field meaning should survive.

## Why freeze this early

Worker pools can be refactored. A bad message ABI infects everything. The
BrowserRT envelope must be boring, versioned, and cheap to inspect.
