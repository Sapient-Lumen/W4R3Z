export interface CandidateInfo {
  selector_hint: string;
  score: number;
  text_length: number;
  visible: boolean;
  label_text?: string;
  labels?: string[];
  accessible_name?: string;
  accessible_names?: string[];
  description_text?: string;
  descriptions?: string[];
  fieldset_legend?: string;
  fieldset_legends?: string[];
  dialog_name?: string;
  dialog_role?: string;
  dialog_modal?: boolean;
  dialog_open?: boolean;
  control_kind?: string;
  form_name?: string;
  form_action?: string;
  form_method?: string;
  frame_selector?: string;
  frame_name?: string;
  frame_title?: string;
  frame_path?: string;
  frame_depth?: number;
  frame_path_selectors?: string[];
  frame_path_names?: string[];
  frame_path_titles?: string[];
  option_count?: number;
  option_labels?: string[];
  selected_options?: string[];
  required?: boolean;
  invalid?: boolean;
  checked_state?: string;
  disabled?: boolean;
  readonly?: boolean;
  multiple?: boolean;
  selected_count?: number;
  autocomplete?: string;
  input_mode?: string;
  constraint_hints?: string[];
  constraint_flags?: string[];
  choice_group?: string;
  placeholder?: string;
  name?: string;
  role?: string;
  text_sample?: string;
  submit_action?: string;
  submit_method?: string;
  submit_target?: string;
}

export interface CandidateReport {
  inputs: CandidateInfo[];
  outputs: CandidateInfo[];
}

export interface LatestOutputWitness {
  text: string | null;
  selector_hint?: string | null;
  selection_policy?: string;
  assistant_like?: boolean;
  author_role?: string | null;
  author_role_source?: string | null;
  node_tag?: string | null;
  candidate_score?: number;
  document_order_index?: number;
  frame_depth?: number;
  frame_path?: string;
}

export interface UserTurnWitness {
  text: string | null;
  selector_hint?: string | null;
  selection_policy?: string;
  user_like?: boolean;
  author_role?: string | null;
  author_role_source?: string | null;
  node_tag?: string | null;
  candidate_score?: number;
  document_order_index?: number;
  frame_depth?: number;
  frame_path?: string;
}

export interface FixtureCapture {
  adapter: string;
  url: string;
  title?: string;
  prompt: string | null;
  latest_output: string | null;
  latest_output_witness?: LatestOutputWitness;
  latest_user_turn_witness?: UserTurnWitness;
  selection: string | null;
  candidates: CandidateReport;
  html_samples?: {
    prompt?: string | null;
    latest_output?: string | null;
    submit?: string | null;
  };
  metadata?: Record<string, unknown>;
}

export type GenerationLifecycle = 'streaming-or-stoppable' | 'needs-continue' | 'settled-or-idle';

// Cheap, poll-friendly readout of whether the active turn is still generating.
// The conversation engine polls this to know when an answer has settled instead
// of guessing from transcript-text stability alone.
export interface GenerationSnapshot {
  state: GenerationLifecycle;
  stop_present: boolean;
  continue_present: boolean;
  stop_selector?: string | null;
  continue_selector?: string | null;
}

export interface AdapterCapabilities {
  read_prompt: boolean;
  write_prompt: boolean;
  submit_prompt: boolean;
  read_latest_output: boolean;
  read_selection: boolean;
  debug_candidates: boolean;
  fixture_capture: boolean;
  generation_state?: boolean;
  continue_generation?: boolean;
  surface_probe?: boolean;
  attach_files?: boolean;
}

export interface PageAdapter {
  name: string;
  origin_patterns: string[];
  capabilities: AdapterCapabilities;
  matches(url: string, document: Document): boolean;
  readPrompt(document: Document): string | null;
  writePrompt(document: Document, text: string): boolean;
  readLatestOutput(document: Document): string | null;
  readLatestOutputWitness?(document: Document): LatestOutputWitness;
  readLatestUserTurnWitness?(document: Document): UserTurnWitness;
  readSelection(window: Window): string | null;
  debugCandidates(document: Document): CandidateReport;
  captureFixture?(document: Document, window: Window): FixtureCapture;
  submitPrompt?(document: Document): boolean;
  // Poll-friendly generation lifecycle for the conversation engine.
  generationSnapshot?(document: Document, window: Window): GenerationSnapshot;
  // Click a visible "Continue generating" control if present. Returns whether
  // a control was found and clicked. Never submits a new prompt.
  continueGeneration?(document: Document, window: Window): boolean;
  // Read-only inventory of every control on the page, classified against a
  // known-role atlas, with anything unrecognised reported as an oddity.
  surfaceProbe?(document: Document, window: Window): unknown;
  attachmentReadiness?(document: Document): {
    ok: boolean; error?: string; input_selector?: string | null; authentication?: string;
  };
  attachFiles?(document: Document, files: Array<{ name: string; mime: string; bytes: Uint8Array }>): {
    ok: boolean; error?: string; input_selector?: string | null; files_before: number; files_after: number;
  };
  clearAttachments?(document: Document): {
    ok: boolean; error?: string; inputs_seen: number; files_before: number; files_after: number;
  };
  composerKeys?(document: Document): string[];
  attachmentWitness?(
    document: Document,
    keysBefore: string[],
    expectedName?: string,
    expectedNameVisibleBefore?: boolean,
  ): {
    input_files: number; added_keys: string[]; added_controls: unknown[];
    known_chip_keys: string[]; expected_name_visible: boolean;
    expected_name_newly_visible: boolean; chip_present: boolean;
  };
  stopGeneration?(document: Document, window: Window): boolean;
  newChat?(document: Document): boolean;
}
