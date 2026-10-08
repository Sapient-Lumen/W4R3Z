# PKT-002 — raw folder

Branch gate: ALERT-AUTH  
Purpose: original sensitive or unsanitized artifact  
Required: yes  
Redaction class: sensitive_security  
Loss cap if absent: blocks any alert-readiness claim

This folder is a capture target, not evidence. Evidence must arrive with packet ID, artifact ID, SHA-256 hash, owner, timestamp, custody event, source clock, redaction/surrogate status, counterevidence path, and adjudication-board disposition. Folder existence, this README, and a label never close readiness.
