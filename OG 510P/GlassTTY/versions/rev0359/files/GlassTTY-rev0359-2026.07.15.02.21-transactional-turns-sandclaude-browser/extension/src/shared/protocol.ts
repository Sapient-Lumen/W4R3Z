export type MessageType =
  | 'health.ping'
  | 'bridge.status'
  | 'bridge.contexts'
  | 'bridge.trace'
  | 'bridge.probe'
  | 'bridge.content_script_experiment'
  | 'bridge.set_content_script_experiment'
  | 'bridge.clear_content_script_experiment'
  | 'bridge.offscreen_dom'
  | 'bridge.offscreen_fixture'
  | 'bridge.set_target_tab'
  | 'bridge.clear_target_tab'
  | 'bridge.set_receiver_override'
  | 'bridge.clear_receiver_override'
  | 'state.snapshot'
  | 'fixture.capture'
  | 'prompt.read'
  | 'prompt.write'
  | 'prompt.submit'
  | 'prompt.continue'
  | 'generation.state'
  | 'surface.probe'
  | 'surface.overrides.set'
  | 'surface.overrides.get'
  | 'attach.begin'
  | 'attach.chunk'
  | 'attach.commit'
  | 'attach.abort'
  | 'attach.status'
  | 'attach.clear'
  | 'prompt.stop'
  | 'chat.new'
  | 'proof.surface_screenshot'
  | 'proof.operator_readiness'
  | 'transcript.latest'
  | 'selection.read'
  | 'debug.dom_candidates'
  | 'transcript.delta'
  | 'adapter.detected'
  | 'error.report'
  | 'bridge.forward_to_active_tab'
  | 'offscreen.document_ready'
  | 'offscreen.document_ack'
  | 'offscreen.document_ping'
  | 'offscreen.document_pong'
  | 'offscreen.document_parse_html'
  | 'offscreen.document_parse_html_result'
  | 'offscreen.document_capture_fixture'
  | 'offscreen.document_capture_fixture_result';

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
