---
name: handoff
description: Write the current session's handoff to a file — what was done, what Claude plans to do next, decisions, dead ends, open questions — so a fresh session can pick it up; or resume from one. Claims are re-checked against the repo before writing and tagged verified or recalled.
disable-model-invocation: true
argument-hint: "[path] | resume <path>"
---

A **handoff** carries one task across a session boundary: this session writes it, the next reads it and continues. `resume <path>` → read. Anything else → write, to `$ARGUMENTS` if given.

It gets written when context is fullest and memory least reliable, so the rule throughout: **a claim enters the file from a command or file read made during this run, or it carries a `[recalled]` tag.**

## Write

### 1. Destination

- Path in `$ARGUMENTS` → that file. Wrapper skills that own a storage layout pass one.
- Otherwise → `.claude/handoffs/YYYY-MM-DD-HHMM-<slug>.md` under the project root (`git rev-parse --show-toplevel`, or the current directory), `<slug>` a kebab-case name for the task. `mkdir -p` the directory.
- Destination already exists → stop and ask.

### 2. Verify

- **Git state:** `git status --short`, `git log --oneline -10`, `git diff --stat`, branch, HEAD sha. Reconstruct what changed from this output and compare it with what the conversation says changed. A mismatch is a finding — write the repo's version.
- **Files:** re-read every file the handoff will name. Line numbers and quoted code come from this read.
- **Ground truth:** run the project's test/build/lint command if one exists and finishes in a few minutes. "Tests pass" appears only with output from this run behind it.
- More than a third of claims `[recalled]` → open the file with a one-line warning telling the next session to verify aggressively.

### 3. Write

```yaml
---
created: 2026-08-18T14:32
branch: feature/x
head: <full sha>
status: open
---
```

Callers may add fields; keep these four. Body, in point form:

- **Goal** — the task in one line, and its done-criterion, stated so it can be checked.
- **Done** — what the user and Claude did this session, as outcomes: changed X in `file`, ran Y, confirmed Z. Uncommitted work called out. Each line tagged `[verified]` or `[recalled]`.
- **Next** — what Claude would do next, numbered, in order. Step 1 is concrete enough to start without reading anything else: a file, a command, a change. Mark any step that waits on the user.
- **Decisions** — choice → reason. The reason is what stops the next session relitigating it.
- **Dead ends** — approach → why it failed, with file or error text. The only record of what already failed.
- **Traps** — non-obvious behavior that cost time: a flaky test, a misleading name, an env var that has to be set.
- **Open questions** — what the user has to decide. The next session asks before guessing past these.
- **Files** — paths that matter, each with a few words on why.

Empty section → one line saying so ("none found"), so the reader can tell empty from forgotten.

Cap at ~150 lines. Over budget: cut Done prose first, then compress Decisions to one line each. Next, Dead ends, Traps and Open questions survive intact.

Quality gate, per line: would someone with only this line avoid the mistake or take the step? If not, add the file, the error text, or the reason — or delete the line.

Secrets, tokens and credentials stay out of the file.

### 4. Report

Path written, the `[verified]`/`[recalled]` count, and a line to paste into the next session:

```
/v:handoff resume <path>
```

## Resume

1. **Read** the whole file before acting.
2. **Re-check** it against the repo as it is now: `git log --oneline <head>..HEAD` and `git status --short` for what moved since; branch mismatch or `<head>` missing from history is drift. Re-check `[verified]` claims; resolve `[recalled]` ones where it's cheap. Re-run the ground-truth command if the handoff cited one.
3. **Brief the user:** Goal and Next, adjusted for whatever moved. Drift as "handoff said X, repo shows Y". Open questions listed.
4. Drift, open questions, or a failing check → stop and wait for the user. Clean → set `status: resumed` in the file and start Next step 1.
