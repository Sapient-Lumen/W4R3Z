# Generated fuzz corpus

`fuzzwire.py` had fixed malformed fixtures. `generatorfuzz.py` grows that into a small deterministic corpus by mutating accepted seed cases into expected rejections.

Generated mutations include trailing parse data, duplicate keys, depth pressure, wire payload append/truncate, and shadow expected-digest drift. The value is not coverage bragging; the value is pinning parser/wire/shadow rejection behavior before live transport noise exists.
