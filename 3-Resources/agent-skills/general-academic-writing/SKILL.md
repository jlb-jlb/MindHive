---
name: general-academic-writing
description: >
  Use when writing, drafting, revising, restructuring, or reviewing academic prose
  across disciplines and formats, including papers, essays, theses, reports,
  abstracts, captions, literature reviews, methods, results, discussion sections,
  grant text, peer-review responses, and supervisor-facing summaries. Applies
  evidence-grounded claim construction, precise academic style, citation discipline,
  structural coherence, concision, and format-aware integration for Markdown,
  LaTeX, DOCX, or plain text. Trigger when the user asks to improve academic style,
  polish prose, check claims, reduce AI-sounding language, strengthen argument flow,
  or turn notes and evidence into scholarly text.
---

# General Academic Writing

Use this skill to produce or revise academic prose that is clear, specific, and
grounded in evidence. The goal is not to make text sound more formal. The goal is
to make claims easier to trust, easier to follow, and harder to misread.

## Before Writing

1. **Classify the task.** Decide whether the user needs drafting, restructuring,
   line editing, evidence checking, citation integration, format conversion, or a
   review. If the request is broad, do the most useful safe subset and state what
   remains unchecked.
2. **Identify the source base.** Use only the materials the user provided, the
   repository or project files the user points to, and sources you can verify. If a
   claim needs evidence and no source is available, ask for the source or mark the
   claim as unresolved instead of inventing support.
3. **Read nearby context.** Before editing a section, inspect adjacent sections,
   headings, figures, tables, terminology, and existing style conventions. Match
   the document unless the user asks for a different voice.
4. **Preserve the user's argument.** Improve clarity and rigor without changing
   the conclusion, scope, or stance unless the evidence requires it. Call out any
   substantive change.
5. **Choose the output format.** Keep LaTeX as LaTeX, Markdown as Markdown, and
   prose as prose. Do not introduce formatting conventions that the document does
   not already use.

## Claim Construction

Every sentence should do at least one of these jobs:

1. State a specific claim.
2. Report evidence, a method detail, a result, or a cited finding.
3. Explain the inference that follows from evidence already introduced.
4. Connect two concrete points by naming the relationship between them.

Use this paragraph pattern by default:

1. State the local claim.
2. Provide the evidence, result, method detail, example, or citation.
3. Explain the supported inference.
4. Stop when the local point is complete.

Cut sentences that only decorate, praise, signal importance, or repeat the topic.
Do not end paragraphs with generic summary sentences. If the last sentence could
fit many unrelated paragraphs, remove it or replace it with the actual implication.

## Evidence Discipline

- Do not invent numbers, dates, quotations, sample sizes, effect sizes, methods,
  author positions, publication details, limitations, or conclusions.
- Treat quantitative claims as source-bound. If the number cannot be traced to a
  table, figure, result file, dataset, paper, or user-provided note, do not present
  it as fact.
- Treat literature claims as citation-bound. Name the source, cite it in the
  document's convention, or flag the claim as needing a citation.
- Distinguish evidence from interpretation. Use the result to support the
  inference, but do not upgrade an interpretation into a finding.
- Do not exaggerate consensus. One source is one source. Several sources with
  similar findings are still not universal agreement unless the sources establish
  that consensus.
- Flag uncertainty plainly. Use a comment, TODO, or short note to the user when
  evidence is missing, conflicting, or outside the checked material.

## Style Rules

Write in a precise academic voice.

- Prefer concrete nouns and plain verbs: "shows", "uses", "compares",
  "evaluates", "requires", "limits".
- Prefer verbs over nominalisations: "evaluated" instead of "conducted an
  evaluation of", "compared" instead of "made a comparison between".
- Replace vague abstractions with the actual mechanism, result, population,
  method, dataset, concept, or citation.
- Remove inflated language such as "pivotal", "crucial", "transformative",
  "groundbreaking", "rich", "dynamic", "robust" when the sentence works without
  it. Keep technical uses of these words when they are precise.
- Avoid promotional phrasing such as "showcasing", "fostering", "enhancing",
  "world-class", "powerful", or "seamless".
- Avoid vague attribution: "researchers note", "scholars argue", "many believe",
  "it is widely regarded". Name the source or cut the claim.
- Avoid formulaic contrast: "not only X but also Y", "more than just X",
  "while X, it also Y". State the actual contrast.
- Avoid decorative lists of three. Keep triples only when the three-part structure
  is analytically necessary.
- Avoid canned conclusions such as "despite these challenges, future work will..."
  unless the evidence and section purpose require that move.
- NEVER use em dashes. Do not use the Unicode em dash character, and do not use
  LaTeX `---` as an em dash. Rewrite with commas, parentheses, colons, semicolons,
  or separate sentences. En dashes for ranges may remain when the document's
  convention requires them.
- NEVER use chatbot meta-text: "Here is a draft", "based on the available
  information", "as of my last update", "this section will discuss", "in
  conclusion".
- Avoid placeholders in final prose. Use the document's visible TODO convention if
  a citation, number, or fact remains unresolved.

## Coherence And Structure

- Make the paragraph's first sentence do real work. It should orient the reader to
  the claim, not announce that a topic exists.
- Order information from known context to new claim when possible.
- Use transitions that name relationships: cause, contrast, limitation, method
  step, result, implication, example, or scope condition.
- Keep one main job per paragraph. Split paragraphs when evidence, inference, or
  topic changes.
- Keep headings informative and parallel with nearby headings. Do not add
  title-case headings inside running prose unless the format requires them.
- Preserve discipline-specific terms when they are accurate. Define them when the
  expected reader may not know them.

## Format-Aware Conventions

When editing an existing document, follow its conventions.

- **LaTeX:** preserve citation commands, labels, cross-references, acronyms,
  comments, and table syntax. Do not change bibliography style unless asked.
- **Markdown:** preserve heading levels, links, fenced code blocks, footnotes,
  tables, and frontmatter.
- **DOCX or prose drafts:** preserve section order, comments, tracked-change
  intent, and any style constraints the user states.
- **Reviewer responses:** separate what changed from why it changed. Keep tone
  factual, specific, and non-defensive.
- **Abstracts and summaries:** state problem, method, evidence, result, and
  implication in the user's requested length. Do not oversell.

## Revision Workflow

For line editing:

1. Fix unsupported or unclear claims before polishing wording.
2. Remove inflated, generic, or promotional language.
3. Replace vague referents such as "this", "it", "the approach", or "the system"
   when the reference could be unclear.
4. Tighten wordy constructions without deleting necessary nuance.
5. Check paragraph flow after sentence-level edits.

For drafting from notes:

1. Extract only claims supported by the notes or sources.
2. Group claims by logical relationship, not by source order.
3. Draft the shortest complete version first.
4. Add citations, TODOs, or uncertainty notes before handing back the text.

For review:

1. Separate style issues from evidence issues.
2. Prioritize claims that are unsupported, overstated, ambiguous, or structurally
   misplaced.
3. Give concrete rewrites for high-impact sentences.

## Self-Review Before Responding

Before treating the answer as finished:

1. Check that every factual claim is supported, cited, or explicitly marked as
   unchecked.
2. Remove em dashes, generic praise, AI-tell vocabulary, canned transitions, and
   decorative formatting.
3. Confirm that the output preserves the user's requested format.
4. Confirm that revisions did not change meaning without saying so.
5. Tell the user what evidence or conventions were not checked when relevant.
