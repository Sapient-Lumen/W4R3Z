# Structural audit rev0351

Base package: `Global-Warming-rev0350-2026.06.05.18.59-ghostfork-liveredteam-receiptgate-cleanfix-refactor.zip`.

Primary correction: rev0350 protected live-drop receipt gates under normal console assumptions; rev0351 adds an offline/blackout fallback so evidence capture can continue during console, network, identity-provider, shared-drive, timestamp-source, scanner, printer, or public-web failures.

Key integrity rules:

* Offline forms are custody/intake controls only.
* Paper receipts are not readiness evidence.
* Deferred hashes prove the hashed file at hash time, not the original capture time.
* Clock-skew repairs are mandatory before timeline-dependent evidence can enter adjudication.
* Rehydrated packets are candidates for adjudication, not closure.
* Loss caps remain active for all 60 must-capture packets until real/anonymized evidence is adjudicated and any CAP/retest/verifier gates pass.

No real/anonymized Beaver Valley evidence was imported.
