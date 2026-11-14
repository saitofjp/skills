---
name: design-architecture-review
description: Reviews a change the way a senior engineer does, from above rather than line by line. Recovers the design the code implies, then judges the change against it - whether it achieves the intent its author stated, its non-functional requirements (the architecture), security as a matter of design (where trust changes and where the controls live), and how easily the next changes will break it. Use it when the user asks for a design or architecture review, a senior-level or big-picture review of a PR, branch or diff, a security review of the design rather than the code, or wants to know whether a feature will hold up as the system grows. Triggers include "review the design", "architecture review", 「設計レビューして」「アーキテクチャレビューして」「シニア目線でレビューして」「この機能、今後の拡張で壊れない？」「設計としてのセキュリティを見て」.
---

# Design Architecture Review

A line-level review asks whether the code does what it says. This review asks whether what it says has the right shape: whether the design carries the feature's intent and its non-functional requirements, whether its security is designed in rather than patched on, and whether it will survive the changes that are coming. A senior engineer reads a change from above, with the whole system and its future in view. This review takes that view.

This file says what the review is for and what a good one looks like. How to get there (what to read first, which questions to chase, how deep to go) is yours to judge from the change in front of you.

## What counts as a design finding

A design finding cannot be argued from the changed lines alone. It needs something outside the diff: how the rest of the system works, what the change is meant to do, how it will be used, what will change next.

This boundary keeps the review from turning into a second line-level review. Anything the changed lines alone can show is better left to `/code-review` or `/security-review`; mixed in, the many small findings bury the few design ones. When you notice one anyway, a line pointing to it is enough.

## Start from the design the code implies

You can only judge a design you can state. So before judging, recover it: the parts and what each is responsible for, the boundaries between them, how data flows, the contracts and invariants the code relies on, and the intent the author gave (PR description, commit messages, docs, design records). Say where you read each piece.

Often, stating the design is the review. Where the code and the stated intent disagree, for example the author says they rejected an approach and the code still behaves that way in some case, that tends to be the most important finding.

If part of the design cannot be drawn from the code, that is a finding too: the intent is not readable from the implementation. Say what is missing rather than filling it in.

Size the recovery to the change: a few lines for a small one, a sketch or a diagram for a large one.

## Where a senior engineer looks

These are the usual directions. Choose what this change deserves. Not every one fits every change, and something not listed here may matter more.

- **Intent and design.** Does the implementation achieve what the author said they chose, and avoid what they said they rejected?
- **Non-functional requirements.** What does the feature depend on besides being correct: integrity of data, performance, availability, operability, cost, compatibility? Put each as a concrete scenario (when this happens, it should do that) and see whether the design gets there. The idea comes from the quality-attribute scenarios of ATAM; the ceremony is not needed.
- **The next changes.** Imagine the changes that are likely to come, and follow what breaks or how many places must change. Two places deserve a hard look: how the new feature combines with the ones already there, and the operations the design cannot do (it can add and change but not remove; it can write but not migrate).
- **Security as design.** Find where trust changes: user input, content from outside, other tenants, logs, anything that gets published. For each crossing, ask where the control lives, whether it sits in one place or is scattered, and whether the new path goes around it. A control that exists only as prose an agent is asked to follow is weaker than one the code enforces; say which kind each is. Whether a given line escapes correctly is code review's question.
- **What to keep.** Parts that are well designed and that a future change could easily undo. Naming them protects them.

## Check before you claim

A design finding is an argument about what can happen, so make it concrete where you can: a minimal reproduction, a scenario run through the real code, a small check that a direction for a fix works. A reproduction turns "could" into "does", and authors act on that. Mark what you could not check as a hypothesis, so it is weighed as one.

Keep reproductions in a scratch place, not in the repository. The review changes no code unless the user asks, because what to do about a design finding is the author's call.

## The author's tradeoffs

Many design "problems" are tradeoffs the author chose, and the commit message may say so. Name the tradeoff and what it costs in a likely scenario, and leave the decision to the author. Weigh findings by what happens in scenarios that are likely to happen, not by elegance.

## Input

What to review comes from the arguments: a PR number or URL, a branch, a commit range, a path, or a design document written before any code exists (then there is no code to recover the design from; review the design the document gives). With no argument, review the current branch against the default branch.

The design is judged against the intent of the change, so the intent matters. Read it from the PR and the commits. If it is written nowhere and your reading of it would change the findings, ask. Otherwise, state your reading and go on.

## Report

Lead with the few findings that matter most. For each, give the part of the design it is about, the scenario, what happens, the evidence (`file:line`, the reproduction), whether it is reproduced or a hypothesis, and a direction for a fix (a direction, not necessarily a patch). Then what to keep. Then what you did not look at, so the author knows where the review stops.

Keep it in proportion to the change. A small change gets a short review, and directions that found nothing need not be reported one by one.

## An example

This shows the level to aim for, not a form to copy.

The update feature of the `semantic-structure` skill in this repository (`resolve --base`, PR #39) lays a new draft over the previous model and finds quotes that have moved again by their nearest occurrence. Its commit message says a version without positions was rejected because, when the same words are added earlier in the text, it silently points somewhere else. Recovering the design and following likely changes found:

- The previous source text is dropped before the quotes are found again, so "nearest" is a guess. When a revision adds a sentence with the same words just before the old place, a chunk silently moves to that new sentence, with no error. The case the author said they rejected is still there. (Intent and design; reproduced; mapping offsets through a diff of the old and new text puts the chunk back.)
- With `--base`, an update drafted in parts, which the skill recommends for long texts, lets the second part replace the first part's spans instead of adding to them. (How the feature combines with an existing one; reproduced.)
- An update can add and change chunks but cannot remove a chunk whose text was deleted. (An operation the design cannot do; reproduced.)

None of these can be argued from the changed lines alone.
