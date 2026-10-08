# Patch static compile / AST contract gate — rev0069

rev0069 continues from rev0068 and keeps the strict/front lane frozen at seven production-gated packets. It validates the selected rev0059 split patch series as post-apply Python source against the uploaded archived `Nicotine-source(1).zip` bundle.

```text
source bundle SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
patch apply rows: 12/12 pass
static compile rows: 30/30 pass
import delta rows: 15/15 pass
symbol continuity rows: 15/15 pass
constant contract rows: 6/6 pass
negative controls: 5/5 pass
```

The helper extracts the five strict/front touched source files for each archived lane, applies the four split filing-bundle patches, then checks Python syntax, dangerous AST nodes, unchanged imports, unchanged top-level class/function symbols, and AST literal parser-budget constants.

Touched files:

```text
pynicotine/downloads.py
pynicotine/transfers.py
pynicotine/slskproto.py
pynicotine/search.py
pynicotine/slskmessages.py
```

Boundary: this is archived-source static proof and does not replace the fresh current checkout/tarball requirement before live-current external filing.
