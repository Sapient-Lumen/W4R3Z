# rev0028 experiment matrix additions

New axis:

```text
opening-branch policy = forced keep vs forced first mulligan
```

Controlled fields:

```text
same first seven-card look
same opponent pregame state
same deck shell
same gameplay agents
same starting life
same starting player
same transition seed
same agent seed
```

Measured fields:

```text
keep branch score
mulligan branch score
mulligan-minus-keep delta
branch mulligans taken
kept hand size
initial hand card counts
initial hand quality
terminal winner/loss reason
C++ transition parity
```

Future expansion:

```text
multiple rollouts per branch
more deck shells
constructor-generated decks
learned mulligan candidate policies
paired branch value model
```
