# bound listener is not the same as safe traffic admission

This scenario keeps **port bound** separate from **dependency warmup**.
A service may bind early while caches, migrations, or downstream dependency checks are still in progress.
