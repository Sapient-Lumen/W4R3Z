# tower `poll_ready` is not the whole readiness story

This scenario keeps **admission readiness** separate from **external readiness** and **startup activation**.
A Tower service may correctly report `poll_ready`, while the broader service still has no exported readiness endpoint and may still be warming dependencies.
