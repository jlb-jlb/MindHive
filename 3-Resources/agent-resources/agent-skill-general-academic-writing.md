---
type: Resource
title: General Academic Writing Skill
description: Catalog entry for the reusable discipline-neutral academic writing skill.
tags: [resource, agents, skills, academic-writing, writing]
timestamp: 2026-07-06T00:00:00Z
resource: /3-Resources/agent-resources/agent-skills/general-academic-writing/SKILL.md
---

# Summary

`general-academic-writing` is a reusable agent skill for writing, revising,
restructuring, and reviewing academic prose across disciplines and document
formats.

The copy-pasteable skill folder is:

```text
3-Resources/agent-skills/general-academic-writing/
├── SKILL.md
└── agents/openai.yaml
```

Skill file: [SKILL.md](/3-Resources/agent-resources/agent-skills/general-academic-writing/SKILL.md)

# Trigger

Use the skill when an agent is asked to:

* Draft or revise academic prose.
* Improve academic style without adding unsupported claims.
* Polish a paragraph, section, abstract, caption, literature review, report, or
  reviewer response.
* Check whether claims are properly grounded.
* Reduce AI-sounding, inflated, promotional, or vague language.
* Preserve document conventions in Markdown, LaTeX, DOCX, or plain text.

# What The Skill Enforces

* Evidence-grounded claim construction.
* Clear separation between evidence, interpretation, and unresolved claims.
* Concise academic style with concrete nouns and plain verbs.
* Structural coherence at sentence, paragraph, and section level.
* Format-aware editing for LaTeX, Markdown, DOCX, and prose drafts.
* A self-review workflow before handing text back.

# Specialized Variants

This skill is intentionally discipline-neutral. If a future workspace needs
field-specific citation rules, file templates, or style constraints, create a
separate specialized skill rather than hard-coding those assumptions here.

# Research Basis

The skill keeps the general writing heuristics already used by the thesis-focused
skill:

* [Purdue OWL Academic Writing](https://owl.purdue.edu/owl/general_writing/academic_writing/index.html) - organization and sentence-level clarity.
* [Purdue OWL Concision](https://owl.purdue.edu/owl/general_writing/academic_writing/conciseness/index.html) - replacing vague wording with more specific wording.
* [UNC Writing Concisely](https://writingcenter.unc.edu/tips-and-tools/conciseness-handout/) - diagnosing wordiness at sentence and paragraph level.
* [UNC Word Choice](https://writingcenter.unc.edu/tips-and-tools/word-choice/) - improving clarity and audience fit.
* [UNC Flow](https://writingcenter.unc.edu/tips-and-tools/flow/) - coherence and cohesion between ideas.

# Maintenance Notes

Keep this skill discipline-neutral. If a future task needs field-specific citation
rules, file templates, or style constraints, create a separate specialized skill or
add a reference file rather than hard-coding those assumptions here.

# Related

* [Agent Skills Library](/3-Resources/agent-resources/agent-skills-library.md)
* [Agent Operating Protocol](/6-System/agent-operating-protocol.md)
