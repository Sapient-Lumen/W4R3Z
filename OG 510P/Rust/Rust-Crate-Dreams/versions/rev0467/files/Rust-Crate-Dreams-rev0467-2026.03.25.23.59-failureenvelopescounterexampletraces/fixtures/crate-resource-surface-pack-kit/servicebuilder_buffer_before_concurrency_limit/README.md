# ServiceBuilder buffer before concurrency_limit scenario

Focus: Tower documents that `buffer` before `concurrency_limit` can allow buffered requests on top of the concurrency-limited requests already forwarded downstream.

Resource-surface reading: admission order is part of the support contract because it changes effective in-flight capacity and who owns backlog.
