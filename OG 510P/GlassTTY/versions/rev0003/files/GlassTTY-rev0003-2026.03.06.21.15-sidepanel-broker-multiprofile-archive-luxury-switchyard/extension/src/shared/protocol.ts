export type MessageType =
  | 'health.ping'
  | 'bridge.status'
  | 'state.snapshot'
  | 'prompt.read'
  | 'prompt.write'
  | 'prompt.submit'
  | 'transcript.latest'
  | 'selection.read'
  | 'debug.dom_candidates'
  | 'transcript.delta'
  | 'adapter.detected'
  | 'error.report'
  | 'bridge.forward_to_active_tab';

export interface Envelope<T = unknown> {
  version: '0.1';
  request_id: string;
  type: MessageType;
  tab_id?: number;
  timestamp: string;
  payload: T;
}

export function makeEnvelope<T>(type: MessageType, payload: T, tab_id?: number): Envelope<T> {
  return {
    version: '0.1',
    request_id: crypto.randomUUID(),
    type,
    tab_id,
    timestamp: new Date().toISOString(),
    payload,
  };
}

export function replyTo<T>(request: Envelope, type: MessageType, payload: T, tab_id?: number): Envelope<T> {
  return {
    version: '0.1',
    request_id: request.request_id,
    type,
    tab_id: tab_id ?? request.tab_id,
    timestamp: new Date().toISOString(),
    payload,
  };
}
