# Wake-from-amnesia rev0073

Start here:

1. `docs/768-rev0073-summarypublish-redactionwitness-importpruneaudit.md`
2. `tests/test_rev0073_summarypublish_redactionwitness_importpruneaudit.py`
3. `src/i2p_dht_lab/summarypublish.py`
4. `src/i2p_dht_lab/redactionwitness.py`
5. `src/i2p_dht_lab/importpruneaudit.py`
6. `src/i2p_dht_lab/summarypublishfold.py`

Mental model: rev0072 made redacted-summary receipt/archive/prune local memory. rev0073 asks whether that memory can safely become publication-ready, whether redaction was witnessed, and whether import-prune state still agrees after joining the new public edge.
