---
name: handoff
description: Write the current session's handoff into Atlas, or resume from the latest one — v:handoff's content and checks, stored under work/<ticket-or-slug>/ with note's naming, frontmatter and revision chain. Requires the v plugin.
disable-model-invocation: true
argument-hint: "[resume [path]]"
---

# handoff

`v:handoff` in an Atlas space: `v:handoff` (requires `v@vforge` alongside `atlas@vforge`) owns what goes in the file and how it's checked; this skill owns where it lives. No arguments → write. `resume` → read.

## Write

1. **Verify the vault** per `note` §0 — `$ATLAS_VAULT_ROOT` set and non-empty, or stop.
2. **Resolve the destination** per `note` §1–2: `work/<ticket-or-slug>/YYYY-MM-DD-handoff.md`, slug `handoff`. Filename match is exact — `YYYY-MM-DD-handoff[-vN].md` — so `sidequest`'s `-sidequest-handoff` files stay separate.
3. **Supersede** an earlier `status: open` handoff for the same ticket: new file gets the next `-vN` and `supersedes:`, old file flips to `status: superseded`. Read the old one first and carry its unresolved Dead ends, Traps and Open questions forward, tagged `[recalled]` unless re-checked.
4. **Run `v:handoff <that path>`.** It writes the body and its four frontmatter fields.
5. **Add `note`'s frontmatter** to the file: `type: scratch`, `repos:`, `ticket:`, `author: claude-code`, `supersedes:` when revising. Keep `v:handoff`'s `status: open`.
6. **Report** as `v:handoff` does, plus what it superseded, with the resume line as:

```
/atlas:handoff resume
```

## Resume

1. Verify the vault, as above.
2. **Find it:** `resume <path>` → that file. `resume` alone → ticket from the branch, newest `YYYY-MM-DD-handoff[-vN].md` with `status: open` in `work/<ticket>/`. No ticket or nothing found → list the five most recent open handoffs across `work/` and ask which.
3. **Run `v:handoff resume <path>`.** Its `status: resumed` flip is an administrative field — edit in place, no new `-vN`.
