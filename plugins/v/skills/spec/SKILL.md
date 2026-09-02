---
name: spec
description: Write a SPEC — a reference document in strict point form. One fact per line, no prose paragraphs, no fluff. Use whenever the user asks for a spec, a reference sheet, or asks that something be written as points rather than prose.
---

Write a spec for: `$ARGUMENTS`

A spec records facts. It explains nothing, introduces nothing, argues nothing, summarizes nothing.

---

## THE FORMAT

**One fact per line.**

- Max ~15 words per line. If a line needs more, it is two facts.
- No paragraphs. Anywhere. Not even one sentence long.
- Bullets and tables only. Tables when the facts share columns.
- No line may contain `because`, `which is why`, `so that`, `since`, or `and therefore`.

**Consequences get their own line, prefixed `→`.**

```
- Tokens expire 15 minutes after issue.
- → Long-running jobs must refresh mid-run. Batch imports are affected.
```

**Unresolved things are marked `⚠` and left unresolved.**

```
- ⚠ Retry limit unknown. Sources give 3 to 10.
- ⚠ Conflicts with the rate-limit doc. Not reconciled.
```

Never resolve a conflict in prose. Mark it and move on.

**Numbers, quantities and durations wherever they exist.** If unknown, write `⚠ unquantified` rather than an adjective.

**Structure**

- Heading → bullets. No preamble under a heading.
- Group by subject, rather than by narrative order.
- No opening paragraph. No closing paragraph. No summary. No recap.
- No changelog, no version history, no "what changed" section.

---

## BANNED

**Words:** delve · tapestry · testament · crucial · vital · robust · seamless · leverage · underscore · moreover · furthermore · nestled · boasts · realm of · rich · intricate · profound · stark · myriad · plethora · navigate · foster · holistic · comprehensive · ensure · facilitate · serve as · play a key role · stand as.

**Hedges:** somewhat · rather · fairly · perhaps · tends to · generally · often · typically · arguably · relatively.

**Intensifiers:** very · truly · deeply · simply · fundamentally · significant · substantial · essentially · notably · particularly.

**Throat-clearing:** It is worth noting · In many ways · It should be said · Of course · Importantly · Note that · This means that.

**Constructions:**

- Personification. Systems do not *want*, *remember*, *answer*, *seek*, or *refuse*. State the mechanical effect.
- Observer reactions as content. Not "and the caller knows it" — state the rule.
- Scene-painting. Not "an engineer at 3am staring at a dashboard" — state the property.
- Aphorisms and closing reversals. Any sentence whose job is to sound good.
- Rule of three. Three parallel clauses for rhythm.
- Em-dash asides carrying the actual content.
- Adjective stacking. One adjective, or none.

---

## TESTS BEFORE OUTPUT

Run each. Fix what fails.

1. **Line test.** Any line over ~15 words → split or cut.
2. **Paragraph test.** Any block of two consecutive sentences → convert to bullets.
3. **Deletion test.** Delete each line. If nothing is lost, leave it deleted.
4. **Retrieval test.** Can a reader find one fact by scanning, without reading? If not, restructure.
5. **Verb test.** Does any non-living subject take a living verb? Rewrite mechanically.
6. **Adjective test.** Every adjective must be checkable. "Dangerous" fails. "Kills the process in under a minute" passes.

---

## WHAT A SPEC IS

A lookup surface. Someone scans it for one fact and leaves.

Anything serving a different purpose belongs elsewhere: argument and persuasion in a proposal, atmosphere and example-as-story in prose, reasoning in an analysis document. If the user wants the reasoning, they will ask for `/vforge:idea`.

If a fact genuinely needs justification, it is two lines: the fact, and a `→` line.

---

## OUTPUT

Print the spec inline by default.

Write it to a file when the user asks, or when the spec is a revision of an existing file — in which case never overwrite: write `<stem>_<YYYYMMDD-HHMMSS>.<ext>` beside the original. Match the frontmatter convention already used by neighbouring files in that directory.

**Optional provenance**, only when the user asks for it: tag lines `[S]` sourced · `[P]` existing proposal · `[N]` new. Off by default — mixing sources is a different problem from the one the spec format solves.

---

## EXAMPLE

**Wrong:**

> **Silver, applied.** Worn on the body, silver resists workings directed at the wearer — curses, hostile seals and bindings take poorly. Silver ornament is protective equipment, and its status meaning derives from that function.

**Right:**

> **Silver**
> - Resists workings.
> - Workings in contact with it come apart.
> - Seals discharge on contact.
> - Spreading damage stops at a silver boundary.
> - → Worn silver blocks workings aimed at the wearer.
> - ⚠ Conflicts with the binding rules. Slave-seals are workings. Unresolved.
