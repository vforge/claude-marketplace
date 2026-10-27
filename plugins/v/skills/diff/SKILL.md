---
name: diff
description: Open a scrollable side pane diffing two files, or one file against its timestamped sibling (name_YYYYMMDD-HHMMSS.ext). Use when asked to compare, diff, or see what changed between two versions of a file. Argument — OLD [NEW] [-f].
---

Call the `mcp__v__visual-diff` tool with the paths from the arguments.

- Two paths: `old` is the first, `new` is the second.
- One path: pass it as `old` alone. The tool pairs it with its neighbouring timestamped version (a stamped file with its predecessor, a base file with the newest stamped variant).
- `-f` in the arguments: set `full` to true to show whole files instead of 4 lines of context.

Relay the tool's one-line result. The diff itself appears in the pane.
