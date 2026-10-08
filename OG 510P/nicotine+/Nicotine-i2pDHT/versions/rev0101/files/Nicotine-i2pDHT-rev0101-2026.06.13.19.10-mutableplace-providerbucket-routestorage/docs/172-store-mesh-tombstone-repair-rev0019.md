# Store mesh and tombstone repair — rev0019

`siblingcast.py` can prove that one round of selected siblings acknowledged one exact digest. `storemesh.py` asks the harder question: do several related store rounds fit together safely?

The risky case is a mutable head or provider record being replicated while the tombstone/deletion/revocation evidence that constrains it is weak or late. The rev0019 store mesh keeps these evidence types separate:

```text
tombstone repair round
mutable-head replication round
provider-record replication round
contact-lease storage round
useful refusal / timeout pressure
```

A mutable head with a linked tombstone should not outrun the tombstone repair. A provider record colliding with live tombstone evidence becomes resurrection pressure, not availability truth.
