# Metric interpretation review page — window, sentence, and counterfactual interface spec

## Purpose

The archive already has receipts and review gates.
What it still lacked was one explicit review surface for the moment an operator clicks a row and asks:

> before I act on this number or timestamp, what does it mean, what does it not mean, and what nearby metric would tell a different story?

## Core decision

AnonSync must expose one first-class **Metric interpretation review** page whenever a metric can plausibly be over-read as stronger proof than it really provides.

## Fixed page order

1. **Current interpretation**
2. **Competing nearby interpretations**
3. **Counterfactual metric set**
4. **Action safety verdict**
5. **Receipt**

### 1) Current interpretation

Show:

- clicked metric label and value
- current window class
- strongest safe sentence
- confidence class

### 2) Competing nearby interpretations

Show the interpretations the product is actively rejecting, such as:

- live presence vs remembered inventory
- last change vs last landing
- current sufficiency vs historical activity
- connected-peers completeness vs all-known-peers completeness

### 3) Counterfactual metric set

Show:

- the next metric the operator would need for the stronger sentence
- whether that metric already exists nearby
- whether that metric would likely contradict the current over-read

### 4) Action safety verdict

Verdicts may include:

- `safe for observation only`
- `safe for routine action`
- `needs deeper proof before destructive action`
- `unsafe as currently interpreted`

### 5) Receipt

The receipt must preserve:

- metric reviewed
- over-read sentence rejected
- safe sentence adopted
- deeper proof page chosen next

## Public object

### Metric interpretation review page

Fields:

- `metric_interpretation_review_id`
- `metric_ref`
- `safe_sentence`
- `rejected_sentence`
- `counterfactual_metric_rows[]`
- `action_safety_verdict`
- `next_pages[]`
- `generated_at`
