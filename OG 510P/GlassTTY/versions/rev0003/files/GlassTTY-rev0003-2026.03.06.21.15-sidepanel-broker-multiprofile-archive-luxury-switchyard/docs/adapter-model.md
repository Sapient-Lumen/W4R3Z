# Adapter model

An adapter is the page-specific code that knows how to interpret a browser application's DOM.

## Current adapters

- `claude`: first real adapter

## Adapter responsibilities

- decide whether the current page matches the adapter
- locate the composer/input area
- locate transcript/output nodes
- extract readable text for the shared protocol
- support debug candidate output for brittle pages

## Adapter interface sketch

```ts
export interface PageAdapter {
  name: string;
  matches(location: Location, document: Document): boolean;
  readPrompt(document: Document): string | null;
  writePrompt(document: Document, text: string): boolean;
  readLatestOutput(document: Document): string | null;
  readSelection(document: Document): string | null;
  debugCandidates(document: Document): CandidateReport;
}
```

## Rule of thumb

If logic depends on page structure, labels, or selectors, it probably belongs in an adapter.
