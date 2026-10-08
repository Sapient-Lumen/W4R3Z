# Command runtime errors keep the command name visible

Ordinary command-bar typos already failed plainly as `command: no such command:
NAME`, but once a command existed the dispatcher still collapsed unexpected
runtime faults to a generic capitalized `Command error: ...` line. That made the
message log less useful exactly when a plugin command, future scripting hook, or
temporary dev command needed debugging.

Rev388 keeps that path tiny and more inspectable:

- `command NAME: error: DETAILS`

Examples:

- `boom` -> `command boom: error: boom`
- a future plugin command failure would keep its command name in the same prefix

The intent is simple: command entry should keep the failing surface visible even
when the fault is unexpected rather than a normal `no such ...` miss.
