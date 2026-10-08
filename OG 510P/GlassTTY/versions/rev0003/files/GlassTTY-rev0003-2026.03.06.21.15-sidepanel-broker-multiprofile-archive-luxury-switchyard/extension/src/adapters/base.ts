export interface CandidateInfo {
  selector_hint: string;
  score: number;
  text_length: number;
  visible: boolean;
}

export interface CandidateReport {
  inputs: CandidateInfo[];
  outputs: CandidateInfo[];
}

export interface PageAdapter {
  name: string;
  matches(url: string, document: Document): boolean;
  readPrompt(document: Document): string | null;
  writePrompt(document: Document, text: string): boolean;
  readLatestOutput(document: Document): string | null;
  readSelection(window: Window): string | null;
  debugCandidates(document: Document): CandidateReport;
  submitPrompt?(document: Document): boolean;
}
