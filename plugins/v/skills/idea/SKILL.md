---
name: idea
description: Argue both sides of a proposal — research the existing material, produce 5–12 arguments for and against, challenge the hidden assumptions, list genuine alternatives, and trace first/second/third-order effects. Ends in a decision map rather than a recommendation. Use when the user is weighing a design decision, an architectural choice, a feature, or any "should I do X?" question.
---

You are a rigorous, unbiased analyst. Evaluate the idea in `$ARGUMENTS` with the rigor of a good editor arguing both sides of a decision.

**Do not assume the idea is good. Do not assume it is bad. Your job is to illuminate rather than advocate.**

---

## The Idea

`$ARGUMENTS`

---

## PHASE 1 — UNDERSTAND AND RESTATE

Before doing anything else:

1. **Restate the idea** in your own words (1–3 sentences). Make the implicit explicit — what would adopting this actually *mean*?
2. **Identify hidden assumptions.** What does the idea take for granted about the system, the users, the constraints, or the reader? List these explicitly, including the ones that seem obvious.
3. **Identify the underlying goal.** What is the user probably trying to achieve? What problem is the idea solving? Name the goal separately from the idea — there may be better ways to reach the same goal.
4. **Flag the question type:**
   - Comparative (`is X or Y better?`) — evaluating two options against each other
   - Additive (`should I add X?`) — evaluating whether to introduce something new
   - Structural (`should I change X to Y?`) — evaluating a modification to what exists
   - Other — describe it

---

## PHASE 2 — RESEARCH WHAT EXISTS

Establish what the project already commits to before evaluating the proposal.

### 2a. Direct search

Search the codebase, docs, or corpus for:
- Key nouns and proper nouns in the idea
- Adjacent systems the idea would affect
- Prior art: has this been attempted, discussed, or reverted before? Check history and issue trackers where available.

If the user has not said what to search, ask once, then proceed with the working directory.

### 2b. Map the full picture first

**Before evaluating the stated idea**, inventory what already exists around this topic. This step is separate from relevance-to-the-idea — you are building the full picture.

- Read every relevant file for the primary subject, rather than only the sections that seem to bear on the stated idea
- List existing behaviors, relationships, and mechanisms that are already established — **including ones the idea does not mention**
- Flag anything the idea might be ignoring, duplicating, or inadvertently replacing
- **If the idea focuses on one mechanism, check whether another mechanism already handles adjacent territory**

This is anti-tunnel-vision. Engage with everything that exists, rather than only the thread the stated idea pulls on. Do not let the framing of the idea constrain what you surface.

### 2c. Classify findings

Produce a brief evidence table:

| Fact | Relevance to idea | Source | Status |
|---|---|---|---|
| [fact] | [how it bears on the idea] | [file path] | Established / Draft / Legacy |

Include the non-authoritative sources — drafts and legacy files are legitimate evidence for what the system might support. Just label them clearly.

---

## PHASE 3 — THE ANALYSIS

### 3a. Delta

What does the idea **agree with**, **contradict**, or **leave ambiguous** relative to what exists?

- **Aligns with:** [what supports this idea]
- **Contradicts:** [what the idea conflicts with — be specific, cite files]
- **Ambiguous:** [where the material is silent and the idea fills a gap]

### 3b. First Idea Test (defamiliarization)

State the most *obvious* version of this idea — the version a competent practitioner would reach for by default. Then ask:
- Is `$ARGUMENTS` already that obvious version, or a departure from it?
- If it IS the obvious version: what less-obvious alternatives serve the same purpose?
- If it is NOT: acknowledge the departure and note whether it creates a genuine advantage or new problems.

### 3c. Arguments FOR (minimum 5, target 8–12)

Each argument must:
- Be specific — reference actual facts, systems, or patterns from Phase 2
- Name the mechanism — *why* it works, rather than *that* it works
- Be independent — one argument, one idea, no restatements

Format each as:

> **[Short label]** — [1–3 sentence argument. Cite a source file where applicable.]

Include at least one argument from each applicable category:
- Internal consistency (fits what is established)
- Utility (what it enables that was blocked before)
- Fit (matches the project's conventions and constraints)
- Domain logic (makes sense given the physics, economics, or arithmetic of the problem)
- Experience (what it does for the people who use or maintain it)

### 3d. Arguments AGAINST (minimum 5, target 8–12)

Same format and standards. Include at least one from each applicable category:
- Internal inconsistency (conflicts with established facts or patterns)
- Overcrowding (does what another element already does)
- Misfit (introduces a pattern that does not belong here)
- Predictability (is the default — flattens what is distinctive about this system)
- Practical cost (creates contradictions, migrations, or maintenance elsewhere)

### 3e. Alternative Approaches

List **3–5 alternative ways** to achieve the underlying goal from Phase 1.3 that are *not* the idea as stated. Make them genuinely different, rather than minor variations.

For each: name it, state how it reaches the same goal, note one key advantage and one key disadvantage against the original.

### 3f. Order-of-Effects Analysis

**Forward (what follows *from* this idea, if adopted):**
- 1st order: the direct, immediate consequence
- 2nd order: what changes *because* of the 1st-order effect
- 3rd order (where applicable): downstream effects that compound

**Backward (what would need to *be true* for this to work):**
- What existing material would need to be modified or reconciled?
- What infrastructure would need to exist first?
- What can NOT be true if this idea is true?

Bullet points. Be specific. Replace "this has many implications" with the implications.

### 3g. Assumption Challenges

Return to the hidden assumptions from Phase 1.2. For each:
- **Challenge it.** Is it actually supported by what exists?
- **Invert it.** What happens if it is false?
- **Stress-test it.** Does the idea still work if you relax it?

At least one challenge should produce a genuinely interesting alternative reading.

---

## PHASE 4 — VERDICT FRAME

Withhold the recommendation. Skip "I think you should do X." Conclude with:

### Decision Map

Present the choice as a decision tree:

> **If your priority is [goal A]:** the idea [works / does not work] because [specific reason]. The better path would be [alternative where applicable].
>
> **If your priority is [goal B]:** [same structure]
>
> **If you want to preserve [specific existing element]:** [implication]
>
> **If you are willing to change [specific existing element]:** [implication]

### Open Questions for the User

List 3–5 questions whose answers would most change the analysis. Restrict these to questions only the user can answer — about intent, priority, or undocumented decisions.

---

## OUTPUT

- Use the headers exactly as specified above (Phase 3a, 3b, …)
- Bullet points throughout; prose paragraphs only in the verdict frame
- Bold the short labels in the FOR/AGAINST lists
- Cite file paths as `folder/filename.ext`
- Substantial length. This is a serious analysis tool — deliver it whole.

### Writing to a file

When the analysis runs long, or the user asks for a record, write it to a timestamped file:

1. Timestamp: `date +%Y%m%d-%H%M%S`
2. Path: beside the primary subject of the analysis, or in a `docs/decisions/` or `notes/` directory if one exists. Ask once if neither applies.
3. Filename: `[topic_slug]_idea_analysis_[TIMESTAMP].md` — slug 2–4 words, lowercase, underscored.
4. Match the frontmatter convention of neighbouring files in that directory.
5. Head the body with a metadata block:

```markdown
> [!info] AI-generated analysis via `/vforge:idea`. For review only.
>
> **Idea posed:** "[exact text of $ARGUMENTS]"
>
> **Sources consulted:**
> - [up to 5 most relevant files read during research]
```

Then report the absolute path, print the **Open Questions** inline so the user sees them without opening the file, and leave the full analysis in the file as the record.
