# Transport-state factor refactor — rev0028

Rev0027 created a flight-deck state/human-factors overlay. Rev0028 adds a marine vessel-state overlay. The refactor decision is to factor both through shared questions while preserving domain-specific axes.

Shared questions: What was the system actually doing? What did people and instruments show? What state could not be seen? What team surface had to convert observations into action? What emergency/survivability surface existed? What investigation rail preserved the lesson? What would prove that the lesson entered practice?

Debt introduced: the cube now needs transport-state negative controls, near-miss controls beyond Viking Sky, and recommendation-closure/in-training records.
