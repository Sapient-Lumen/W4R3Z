# Sanitizer plan before native expansion

Native leaf candidates need evidence before they become routine.

`sanitizerplan.py` checks that a source audit passed, that the component is in the audited native set, that development builds carry address/undefined sanitizer intent, and that forbidden optimization flags do not smuggle undefined-behavior risk into a security boundary.

Release profiles may omit sanitizer flags, but only with prior development sanitizer evidence when native code is enabled.

needle: sanitizer plan
