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

export interface FixtureCapture {
  adapter: string;
  url: string;
  title?: string;
  prompt: string | null;
  latest_output: string | null;
  selection: string | null;
  candidates: CandidateReport;
  html_samples?: {
    prompt?: string | null;
    latest_output?: string | null;
    submit?: string | null;
  };
  metadata?: Record<string, unknown>;
}

export interface AdapterCapabilities {
  read_prompt: boolean;
  write_prompt: boolean;
  submit_prompt: boolean;
  read_latest_output: boolean;
  read_selection: boolean;
  debug_candidates: boolean;
  fixture_capture: boolean;
}

export interface PageAdapter {
  name: string;
  origin_patterns: string[];
  capabilities: AdapterCapabilities;
  matches(url: string, document: Document): boolean;
  readPrompt(document: Document): string | null;
  writePrompt(document: Document, text: string): boolean;
  readLatestOutput(document: Document): string | null;
  readSelection(window: Window): string | null;
  debugCandidates(document: Document): CandidateReport;
  captureFixture?(document: Document, window: Window): FixtureCapture;
  submitPrompt?(document: Document): boolean;
}
