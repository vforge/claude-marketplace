---
name: unslop
description: Audit a generated document for the failure classes that survive review — metaphor standing in for mechanism, rhetorical totalisers, compressed derivations, scope overreach, stale claims, and unmarked provenance — and report the factual errors the phrasing was concealing. Use when reviewing AI-drafted specs, docs, or reference material, or when a document reads well but you suspect it is wrong. Argument: path to the file.
---

You are auditing `$ARGUMENTS` for the failure classes below. Each one was found repeatedly in real generated documents, survived multiple review passes, and in several cases carried a *factual* error that nobody caught because the sentence read well.

**The governing insight: a sentence that reads as settled stops being checked.** Colourful phrasing is a correctness problem, because it conceals claims the document's own rules do not support.

---

## Output protocol

Never overwrite. Write the corrected file to `<stem>_<YYYYMMDD-HHMMSS>.<ext>` beside the original.

If the file has checkboxes the user has been ticking, **edit phrases, not whole lines** — replacing a full line resets its checkbox state and destroys review progress. Verify the `- [x]` count is unchanged before and after.

If the file has tables, note that formatters re-pad them. Match table lines by prefix rather than by exact string.

**Leave quoted material alone.** Text the document quotes from a source, a transcript, an interview, or a piece of dialogue is evidence. Its register is content. Only the document's own assertions are in scope.

---

## Class 1 — Metaphor standing in for a mechanism

A compact image replaces an explanation, reads as precise, and asserts something the document never established.

Found in the wild: *"a slow capacity engine"*, *"tended ground"*, *"a breeding programme"*, *"a stockpile"*, *"hostage to one site"*, *"its blind range"*, *"a hand on the money supply"*.

`tended` was the worst of them: it means *renewed by repeated events*, but it implies somebody is deliberately maintaining the state — the opposite of the document's own claim that no party directs the outcome. It survived four passes.

**Fix:** state the mechanism. `tended ground` → `ground whose state its own events keep renewing`.

## Class 2 — Idiom for a mechanism

Named obliquely rather than stated. *"on credit"*, *"on the shelf"*, *"at the throat"*.

**Fix:** *"access on credit"* → *"access paid after delivery instead of before"*.

## Class 3 — Rhetorical totalisers

Sound conclusive, add no claim, and sometimes assert a precision the document cannot support.

*"the whole of X"*, *"and nothing more"*, *"and never"*, *"no defence at all"*, *"the only event that"*, *"by exactly the amount"*.

That last one asserted a measurement in a document whose central rule is that the quantity in question **cannot be measured**.

## Class 4 — Circular flourishes

The conclusion restates the premise. *"a queue that loses what makes it a queue"*, *"reaches for the opposite of a value that has none, and finds nothing to reach for"*.

## Class 5 — Evaluative language

*"excellent"*, *"best placed"*, *"takes the other for incompetence"*. Replace with the fact. *"the best engineers"* → *"the engineers with the most throughput"*, or delete the ranking.

## Class 6 — Dramatic exemplification

A vivid instance stands in for a general claim, implying its category is special when the rule is general.

*"cannot tell a legitimate request from an attack"* — an attack is not a special case; the claim is that the request is unattributable.

**Fix:** state the rule; if an example helps, mark it as one. *"One burst in an afternoon consumes more quota than a month of normal traffic"* → *"Requests of high volume close together in time consume more quota in a day than steady traffic consumes in a month. A burst is the limiting case."*

## Class 7 — Compressed derivation

A conclusion with its intermediate steps removed. It reads cleanly and cannot be checked, because the missing step is where the error lives.

*"Saturation is unpredicted by any reading, because the reading before it and the reading long before it are identical"* — circular. The missing step: headroom = capacity − load, load is readable, capacity is not, **therefore headroom is unreadable**, therefore no reading warns of saturation.

**Test:** for each derived claim, can you state every step? If not, the document is hiding one.

**Counter-pressure:** do not split until each step is its own line. Seven entries where two suffice is its own failure. Stop when a competent reader can follow it.

## Class 8 — Negation framing

Defining by what a thing is not, or denying something no reader would have assumed.

*"Nothing about an entry decays"* → *"The rate of loss is set by the surrounding store; elapsed time contributes nothing on its own."* The positive form carried a consequence the denial had hidden — that entry lifetime varies by location, so no single figure exists.

Also strip: *"it's not X, it's Y"* constructions (write Y), definitions by negation, and lists of what something lacks.

**Exception:** naming an absence earns its space when the reader would otherwise assume presence — e.g. a structure that is not thread-safe.

**Related:** when a source claim is simply wrong, **delete it**. Do not write a formal rebuttal that repeats the error in order to deny it.

## Class 9 — Scope overreach

A narrow rule extended to a broad case. A rule about a *processed* record became a claim about all records, and produced "archives are reserves" — which the document's own retention and expiry rules directly contradict.

**Test:** does the entry stay inside the scope of the rule it cites?

## Class 10 — Consequences drawn from imperceptible effects

The most productive error, because the reasoning is valid and the premise is unobservable. A whole economics of outages, insurers and opposed incentives, built on a capacity gain that **nobody in the system can measure**.

**Test:** does this consequence require a party to perceive something the document says is unreadable?

## Class 11 — Institutional machinery on unsupporting foundations

Markets, contracts, assays, insurers, arbitrage. A market needs price discovery; price discovery needs a measurement; if the document says no measurement is possible, the market cannot exist.

Ask what the stated rules actually permit — usually possession, secrecy, force, and knowledge held privately.

## Class 12 — Enumeration where one sentence suffices

*"Endpoints are shared. Access is granted by tokens, keys, sessions and delegation alike."* The second sentence restates four entries elsewhere. Worse, collecting them invited the assumption that an endpoint *belongs* to somebody, which was the error the entry existed to correct.

## Class 13 — Stale claims

An entry contradicting a later ruling. These hide in colourful lines specifically, because colour makes a sentence look decided.

Four in one file: a rejection of pre-computed state that a later entry asserted; a "widest range" remnant after the range was narrowed; a detection rule that survived the model replacing it; and a whole section saying a value could not be derived after it was ruled derivable.

**Method:** list every ruling the file has taken, then grep the file for the vocabulary of the *superseded* position, rather than the new one.

## Class 14 — Unmarked provenance

Treating chain-generated documents as authoritative. Phrasing like *"the source states"* implies authority that an earlier AI draft does not carry.

**Check named things against the source of record before relying on them.** In one audit, six of ten entries were wrong: wrong item named, invented properties, a real property dropped for lack of evidence, and one genuine entry missing entirely.

Distinguish **source-backed** (name the file) from **chain-asserted**. And distinguish tiers within the source: a merged document outranks a working note, a proposal, or an extraction.

---

## Procedure

1. Read the whole file. Build a list of the rulings and definitions it commits to.
2. Grep for the markers of classes 1–6 and 12. These are mechanical.
3. Read every derived claim against classes 7, 9 and 10. These need judgement.
4. Grep for superseded vocabulary (class 13).
5. Check named entities against the source of record (class 14).
6. Write the timestamped output. Verify checkbox counts match.
7. Report by class, listing what changed and — separately — **any factual error the phrasing was concealing.** That second list is the point of the exercise.

## When you are unsure

Ask the user to name one instance, then fix the whole class. A single flagged example generalises reliably; guessing at what bothers them does not.

Do not defend a phrasing because it reads well. That is the property that let it through.
