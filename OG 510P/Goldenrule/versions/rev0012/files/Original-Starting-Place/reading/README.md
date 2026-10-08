# Reading Pack (citation-first index)

This directory is meant to be *practical*: it’s the “why this test exists” shelf for the LLM and the human.
Most items below are indexed in `reading/links.yaml` and `reading/bibliography.bib`.
Local PDF blobs are intentionally omitted from the compact long-term archive; use the recorded URLs when a paper needs to be reacquired temporarily.

If you want a fast mental model: Concord is trying to **discover and stress-test norms** for:
- *when to cooperate*,
- *when / how to punish*,
- *when / how to forgive*,
- *how to update trust under noise and partial observability*,
- *how to resist exploitation without becoming a vampire*.

---

## 0. “Golden Rule” as a research object (ethics + formal analogues)

**Core ethical tensions to keep in mind**
- “Treat others as you’d like to be treated” presupposes **symmetry** of preferences and contexts.
- Real life breaks symmetry: different needs, power, roles, information, and *capacity*.
- In games: Golden-Rule-ish ideas show up as **universalisation**, **Kantian / team reasoning**, and
  **policies that recommend themselves under role reversal**.

**Links**
- Internet Encyclopedia of Philosophy — *The Golden Rule* (overview + critiques).  
  https://iep.utm.edu/goldrule/
- Tullberg (2012) “The Golden Rule of Ethics” (Golden vs Silver rules, etc.).  
  https://www.diva-portal.org/smash/get/diva2:546873/FULLTEXT01.pdf

---

## 1. Direct reciprocity: forgiveness, contrition, escalation, longer memory

### 1.1 “Fast to forgive” as an equilibrium technology
- **Fudenberg & Levine (2009)** *Slow to Anger and Fast to Forgive* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Nowak & Sigmund (2007)** *Tit-for-Tat or Win-Stay, Lose-Shift?* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**How this should shape the lab**
- Build “anger” (retaliation) and “forgiveness” as *separate dials*, not one dial.
- Include explicit tests for:
  - noisy miscoordination (implementation error / perception error),
  - apology/repair signals,
  - partial memory + recency weighting.

### 1.2 “Partner strategies” / “nice strategies” / longer memory
- **Glynatsi, Nowak & Hilbe (2024)** *Conditional cooperation with longer memory* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Akin (2012/2013)** *Good strategies and their dynamics* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Duersch, Oechssler & Schipper (2013)** *When is Tit-for-Tat unbeatable?* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**Lab implication**
- Add “partner”/“non-exploitability” probes: if opponent cooperates, your best response should be cooperate.
- Add “recency-weighted memory” candidate families (your ‘gradualize gradual’ direction).

### 1.3 Tournament design (beyond classic Axelrod)
- **Mathieu et al. (2017)** *New winning strategies for the IPD* (JASSS) (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Axelrod (2000)** *Six Advances in Cooperation Theory* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

---

## 2. Extortion, ZD strategies, and “vampire” threat models

These papers are important because they define a family of adversaries that can *look* cooperative while
systematically extracting advantage.

- **Press & Dyson (2012)** *Iterated Prisoner’s Dilemma contains strategies that dominate...* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Hilbe, Nowak & Sigmund (2013)** *The evolution of extortion...* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Stewart & Plotkin (2013)** *From extortion to generosity...* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Chen & Zinger (2014)** *The robustness of zero-determinant strategies...* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**Lab implication**
- Maintain a permanent “vampire suite”: extortion, conditional extortion, apology-faking, grudge-baiting,
  exploitation of unilateral forgiveness, and “smart always defect” policies.

---

## 3. Indirect reciprocity, reputation, and institutions

If Golden-Rule-ish behavior is meant to scale beyond dyads, you need reputation and norms.

- **Ohtsuki & Iwasa (2006)** *The leading eight: social norms that can maintain cooperation* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Hilbe et al. (2018)** *Indirect reciprocity with private, noisy, and incomplete information* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Schmid et al. (2021)** *A unified framework of direct and indirect reciprocity* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Santos et al. (2021)** *The complexity of human cooperation under indirect reciprocity* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Takács et al. (2021)** *Networks of reliable reputations and cooperation: a review* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**Lab implication**
- Create “possible worlds” where:
  - reputations are **private** and can diverge,
  - gossip is noisy/adversarial,
  - observers have bias or limited sampling,
  - institutions exist (courts, moderators, escrow, restitution channels).

---

## 4. Partner choice and “moral markets” (escaping dyads)

- **Noë & Hammerstein (1994)** *Biological markets* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Gräser et al. (2024)** *Partner choice in repeated games: fair cooperation...* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Hilbe et al. (2018)** *Partners and rivals in direct reciprocity* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**Lab implication**
- Add environments with:
  - leaving / switching partners,
  - competitive partner markets,
  - “exclusion” and re-entry (jubilee / repentance mechanisms).

---

## 5. Intentions, apologies, fairness, and “duty-like” cooperation

These help you model *why* a defection happened (noise vs malice) and why forgiveness might be rational.

- **Ho (2012)** *Apologies as Signals* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Rabin (1993)** *Incorporating fairness into game theory...* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Fehr & Schmidt (1999)** *A theory of fairness, competition, and cooperation* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Bolton & Ockenfels (2000)** *ERC: A theory of equity, reciprocity, and competition* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Falk & Fischbacher (2006)** *A theory of reciprocity* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**Lab implication**
- Provide “repair channels” and intention-signals; test if strategies exploit them.
- Explicitly model degrees of defection/cooperation (continuous actions, partial help, delayed help).

---

## 6. Universalisation / Kantian / “role reversal” solution concepts

These are the closest formal neighbors to Golden Rule I’ve found in the econ/game theory literature.

- **Alger & Weibull (2013)** *Homo Moralis* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Roemer (2011)** *Attaining efficiency through Kantian optimization* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Curry & Roemer (2012)** *Evolutionary stability of Kantian optimization* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Sher (2020)** *Normative aspects of Kantian equilibrium* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
- **Salonia (2024)** *A Foundation for Universalisation in Games* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).

**Lab implication**
- Implement candidate strategies that explicitly do “universalise the policy” calculations as one family.
- Evaluate them alongside reciprocity strategies to see if they collapse under vampires/noise or
  survive via robust institutional scaffolding.

---

## 7. Tooling references

- **Knight et al. (2016)** *Axelrod-Python library* (indexed in `links.yaml`; local PDF intentionally omitted from compact archive).
