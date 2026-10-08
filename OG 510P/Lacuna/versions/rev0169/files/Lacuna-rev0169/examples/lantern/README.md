# Lantern Room example

Create a blank cube and apply the complete demonstration as one atomic change-set:

```bash
./lacuna init /tmp/lantern
./lacuna apply /tmp/lantern examples/lantern/change-set.template.json --bind-current
./lacuna worlds /tmp/lantern
./lacuna evidence /tmp/lantern
./lacuna context /tmp/lantern
./lacuna context /tmp/lantern --agent-id player
```

The omniscient context includes all three candidate worlds and two world-scoped interpretations of the same observed tremor. The player-scoped context deliberately omits hidden-world assignments, privileged evidence links, and claims not visible to that perspective.
