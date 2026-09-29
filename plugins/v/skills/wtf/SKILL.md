---
name: wtf
description: "That last message did not land. Re-explain it in plain, simple language."
disable-model-invocation: true
---

Stop. Your last message did not land. Say it again, simply.

Give one line of context first, then the point. Write in ASD-STE100 Simplified Technical English: short sentences, one action or idea per sentence, active voice, plain words, few relative clauses. No jargon, no metaphors, no acronym you have not spelled out. One human talking to another.

If the repo has a `CONTEXT.md`, use its vocabulary for the domain terms (follow `CONTEXT-MAP.md` to the right one if there is more than one). If there is no `CONTEXT.md`, do not hunt for a substitute and do not mention it. Plain language is enough.

## Provenance

Combines Cursor's pstack [`bro`](https://github.com/cursor/plugins/blob/main/pstack/skills/bro/SKILL.md) (the plain, no-jargon restatement) with [`wait-what`](https://github.com/mattpocock/skills/blob/main/skills/productivity/wait-what/SKILL.md) from mattpocock/skills (MIT) (the ASD-STE100 angle), with its `CONTEXT.md` dependency made optional.
