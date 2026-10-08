# Refusal schedule join

A useful refusal should help future scheduling, not launder a failure into success.

`refusalschedule.py` joins two already-tested surfaces:

- `refusalloop.py`: repeated useful-refusal and refusal-only loop memory;
- `schedjoin.py`: capability/admission success crossing into queue scheduling.

The join emits local pressure only:

```text
keep schedule
watch and throttle bulk
back off refusal-heavy families
quarantine refusal-loop laundering
quarantine scheduler starvation
```

The report is not global reputation. It is a local rule for not spending the next scheduling window as if repeated overload were healthy service.
