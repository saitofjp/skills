---
name: review-modeling
description: Reviews a specification or design document by modeling it. Reads the document, decides which models it calls for (state transitions, permissions, domain rules, failure, concurrency, data flow and trust boundaries, capacity, screen flow and so on), tries to write each one, and reports what could not be written as gaps and what does not hold once written as contradictions and risks, each traced to the text and put as a question the author can answer. Use it to review a spec, requirements, PRD, design document or API design, or to find what a spec leaves out. Triggers include "review this spec", "review the design doc", "find gaps in the requirements", 「仕様をレビューして」「設計書をレビューして」「仕様の抜け漏れを見て」「モデル化してレビューして」.
---

# Modeling Review

The purpose is to find, before code is written, what a specification or design leaves undefined and what in it cannot all be true at once.

A reader can skim past a gap. A model cannot: a state table has a cell for every state and event, a permission matrix a cell for every role and operation. So write the document down as models. Where a model cannot be written from the text, the document has a gap. Where it can be written but does not hold together, inside one model or across two, the document has a contradiction or a risk.

The user only asks for a review. The models are how you look and the grounds for what you say, not what they asked for, so the review should read like a good spec review that happens to have its evidence attached.

How far to go, which models and in what depth, is yours to judge from the document in front of you.

## Choose the models the document calls for

Read the document and let what is in it decide which models to write. Some signs:

- States, statuses, "in progress", "cancelled", "expired" → state transitions
- Roles, "admin", "only the owner", teams, sharing → a permission matrix
- Entities, counts, "must", "unique", "at most" → a domain model with its rules (invariants)
- Other services, email, payment, background jobs → failure, and the sequence across them
- Simultaneous edits, resubmission, deadlines, retries → concurrency and ordering
- "Instantly", "large", limits, numbers of users → capacity
- Personal data, uploads, input from outside → data flow and trust boundaries
- Screens, steps, a flow the user walks through → screen flow and scenarios
- The same word used in several places → terms, and whether they mean the same thing

[references/models.md](references/models.md) has, for each model, how to write it, where it typically fails to write, what to check, and what it yields. It is a set of options, not a list to go through: a spec for a login form does not need a capacity model, and a document may call for a model that is not listed.

Say which models you wrote and which you considered and left out, and why, in a line each. "Every angle" is only believable when the reader can see which angles were taken.

## Write the models from the text

Write each model from what the document says, and point each element back to where it says it (a section, a heading, a quoted phrase). That link is what lets the author check you, and what turns an empty cell into a finding.

Where the text does not say, leave the cell empty and mark it. Do not fill it with what a reasonable system would do. A plausible default is exactly what hides the gap the review exists to find, and the author will read your model as their spec. When the answer seems implied but is not stated, write it as implied, so it can be confirmed rather than assumed.

Use forms that a person can read and a tool could check: tables, Mermaid diagrams, short lists of rules. Keep each model the size of what it shows.

## Check the models

Once written, look at each model in three ways, as far as the document gives you material.

- **Inside one model.** States that cannot be reached or cannot be left, an event with no defined result, a rule some operation breaks, a role that can do something nobody meant it to.
- **Across models.** This is where several views earn their keep, since a gap between two views is invisible from either. Does every event in the state transitions appear in some scenario? Does every operation in the permission matrix exist in the API? Does every operation that changes state keep the domain rules? Does every external call in the sequence have a failure case?
- **Against the design.** When both a spec and a design are given, model each and compare. Does the design handle every state transition the spec has? Does the design's API enforce the spec's permission rules?

When a check can be run rather than read, for example a concurrency protocol in TLA+ or a domain model in Alloy, and the tool is available, run it. Otherwise say that the check is a careful reading, not a proof.

## Tell the author

Lead with the findings, ordered by their impact on users and the system. Put each one as a question the author can answer, because most findings in a spec are decisions nobody has made yet, not mistakes.

For each finding, show as far as you can:

- Kind: a gap (the text does not say), a contradiction (two statements cannot both hold), or a risk (it holds as written but breaks under a condition).
- Where: the place in the document.
- The model excerpt that shows it: the empty cell, the two rules that clash, the path that breaks.
- When it matters: the condition, and what happens to whom.
- The question.

For example, at the level of detail that helps:

> **Gap: what happens to an exam cancelled while it is being graded?**
> §3.2 defines `grading → graded` and §3.4 lets a candidate cancel "at any time", but nothing says what cancel does in `grading`. In the state table the cell (`grading`, cancel) is empty. If grading finishes after the cancel, a result may be saved for an exam the candidate believes they withdrew from. Should cancel be refused once grading starts, or should it discard the result?

After the findings, the coverage: which models you wrote and which you left out. Then every model you wrote, as an appendix, including the ones that turned up nothing. A model the coverage names but the appendix does not show is a claim the reader cannot check, and a model with nothing wrong in it is still the evidence that this angle was looked at. The models are also useful to the author beyond this review, as a supplement to the spec and as the basis for tests. What you only glanced at without writing a model is not a model you wrote; say so in the coverage instead.

In the findings, do not walk through the cells that turned out fine; they would bury what you found. When the document holds up, say so in a few lines and say why.

## Offer a checklist

End the review by offering to turn the models into a checklist of what to confirm, and write it only when the user says yes. The review is already long and not every reader wants the list, but most of what the list needs is already in the models.

Each cell the text settles becomes one item: a statement that can be confirmed against the built system, with the section it comes from, such as `- [ ] A tentative reservation not paid within 30 minutes expires, and someone else can book its slot (§3.3)`. If every item holds, the system does what the document says, as far as the document says it. Group the items by model.

A cell the text leaves open does not become an item, since writing one would make the decision the author has not made, the same plausible default the models avoid. List it under its model as waiting on an answer, with the finding it waits on. That part shows what still stands between the document and an OK.

## Grounds and confidence

Keep what the text says apart from what you conclude from it, and stated apart from implied.

Judge a finding by its impact, not by how the document is written. Wording, structure and taste are not defects unless they make two readings possible; a term used with two meanings is a finding, a clumsy sentence is not.

Do not raise improvements beyond what the document sets out to do as defects. When a finding rests on an assumption about the system the document does not describe, say what the assumption is.

## Where this ends

This skill reviews documents. For a change in code, a PR or a branch, `review-birds-eye` reads from the code up to its design. When both a spec and the code exist, the models written here can be handed to that review, or turned into tests.
