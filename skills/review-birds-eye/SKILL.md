---
name: review-birds-eye
description: Reviews a change from a bird's-eye view, the way a senior engineer does - looks at the whole design the code implies rather than line by line, and reports each finding concretely, with the file, a scenario and what happens. Judges the design (is the change carried through consistently in the related code, does it sit in the right place, will the next changes break it) and the non-functional requirements (side effects such as slowdowns or unintended data changes, compatibility, failure, concurrency, operation, security). Use it when the user asks for a design or architecture review, a senior-level or big-picture review of a PR, branch or diff, a security review of the design rather than the code, or wants to know whether a feature will hold up as the system grows. Triggers include "bird's-eye review", "review the design", "architecture review", 「俯瞰してレビューして」「設計レビューして」「アーキテクチャレビューして」「シニア目線でレビューして」「この機能、今後の拡張で壊れない？」「設計としてのセキュリティを見て」.
---

# Bird's-Eye Review

A line-level review asks whether the code does what it says. This review asks whether what it says has the right shape: whether the change is carried through consistently in the code around it, and what it does besides what it is meant to do: slow something down, change data, break under failure or under the changes that are coming. A senior engineer looks at the whole to find such problems, and then reports them concretely enough that the author can see them in the code. This review does both.

This file says what the review is for and what a good one looks like. How to get there (what to read first, which questions to chase, how deep to go) is yours to judge from the change in front of you.

## What counts as a design finding

A design finding cannot be argued from the changed lines alone. It needs something outside the diff: how the rest of the system works, what the change is meant to do, how it will be used, what will change next.

This boundary keeps the review from turning into a second line-level review. Anything the changed lines alone can show is better left to a line-level code review, by whatever tool or person does that where you work; mixed in, the many small findings bury the few design ones. When you notice one anyway, a line pointing to it is enough.

## Make each finding concrete

Looking at the whole is how you find a design problem, but a finding written at that level is of little use. A vague finding, such as "this coupling may hurt extensibility" or "consider a clearer separation of concerns", fits almost any code, cannot be shown wrong, and gives the author nothing to act on. Advice that would apply to any codebase (follow SOLID, add an abstraction layer, write more tests) is not a finding about this change.

So write each finding with three things: the file and line where the problem sits, a specific input or change that sets it off, and what then happens. If you cannot say these, it is not a finding yet. Look further, or leave it out.

The surest way is to run it: a minimal reproduction, a scenario put through the real code, a small check that a direction for a fix works. A reproduction turns "could" into "does", and authors act on that. Mark what you could not run as a hypothesis, so it is weighed as one.

Keep reproductions in a scratch place, not in the repository. The review changes no code unless the user asks, because what to do about a design finding is the author's call.

## Start from the design the code implies

You can only judge a design you can state. So before judging, recover it: the parts and what each is responsible for, the boundaries between them, how data flows, the contracts and invariants the code relies on, and the intent the author gave (PR description, commit messages, docs, design records). Name the actual modules, functions and files rather than generic layers, and say where you read each piece.

Often, stating the design is the review. Where the code and the stated intent disagree, for example the author says they rejected an approach and the code still behaves that way in some case, that tends to be the most important finding.

If part of the design cannot be drawn from the code, that is a finding too: the intent is not readable from the implementation. Say what is missing rather than filling it in.

Size the recovery to the change: a few lines for a small one, a sketch or a diagram for a large one.

## What to look at

With the design stated, look at the change from two sides: the design, and the non-functional requirements. These are the usual points, each with the kind of finding it leads to. Choose what this change deserves. Not every one fits every change, and something not listed here may matter more.

**Design: is the change carried through consistently?**

- **Consistency with related code.** A change is more than its edited lines. Is what it sets out to do reflected everywhere the same thing is handled: the other entry points (API, CLI, batch), the callers, the docs and tests? For example, the web form now validates the new field, but the nightly import writes the same table without the check. This includes the author's own words: the commit says a retried request is safe to repeat, but the handler writes the row before it checks the request id.
- **Place.** Does the new code sit where it belongs, and use the mechanism that is already there rather than build a second one? For example, a shared validator exists, but the new endpoint validates on its own.
- **Hidden assumptions.** Has the change added a condition that callers must keep and nothing enforces? For example, "call `init()` first" is true only by convention.
- **The next changes.** Imagine the changes likely to come, and follow what breaks or how many places must change: adding a second payment provider means editing five files that each switch on the provider's name. Look also for operations the design cannot do (it can add and change but not remove; it can write but not migrate).

**Non-functional requirements: what does the change do besides what it is meant to do?**

- **Side effects.** Does it make something slower, or change data it was not meant to? For example, the list page now runs one query per row; a function that looks like a read now updates a timestamp.
- **Compatibility.** Does it still work with data written before the change, and with old callers? For example, the new required field is missing from every existing record.
- **Failure.** If it stops halfway, is a half-done state left behind? Can it be retried or rolled back? For example, a crash between the two writes leaves only one of them.
- **Concurrency.** Does it hold when two run at once? For example, another request slips in between the check and the write.
- **Operation.** When it goes wrong, will anyone notice and be able to trace it? For example, the failure is swallowed and never logged.
- **Security.** Find where trust changes (user input, content from outside, other tenants, anything published) and ask where the control lives and whether the new path goes around it. For example, the HTML export escapes everything in one helper, but the new CSV export writes cells as they come, so a cell starting with `=` runs as a formula in a spreadsheet. A control that exists only as prose an agent is asked to follow is weaker than one the code enforces. Whether a given line escapes correctly is the line-level review's question.

Putting a requirement as a scenario makes it checkable: when the table holds ten million rows, the page still opens in a second.

Note also **what to keep**: parts that are well designed and that a future change could easily undo, such as that one escaping helper. Naming them protects them.

## The author's tradeoffs

Many design "problems" are tradeoffs the author chose, and the commit message may say so. Name the tradeoff and what it costs in a likely scenario, and leave the decision to the author. Weigh findings by what happens in scenarios that are likely to happen, not by elegance.

## Input

What to review comes from the arguments: a PR number or URL, a branch, a commit range, a path, or a design document written before any code exists (then there is no code to recover the design from; review the design the document gives, and tie findings to the document's own words and examples). With no argument, review the current branch against the default branch.

The design is judged against the intent of the change, so the intent matters. Read it from the PR and the commits. If it is written nowhere and your reading of it would change the findings, ask. Otherwise, state your reading and go on.

## Report

Lead with the few findings that matter most. For each, give the part of the design it is about, the scenario, what happens, the evidence (`file:line`, the reproduction), whether it is reproduced or a hypothesis, and a direction for a fix (a direction, not necessarily a patch). Then what to keep. Then what you did not look at, so the author knows where the review stops.

Read each finding back as the author: could they open the file, run the scenario and see it happen? If not, make it more concrete.

Keep it in proportion to the change. A small change gets a short review, and directions that found nothing need not be reported one by one.

## An example

This shows the level to aim for, not a form to copy. It comes from the `semantic-structure` skill in saitofjp/skills (PR #39).

The tool turns a text into notes. Each note keeps the quote it rests on and the quote's character offsets in the text. The change added `resolve --base`: when the text is revised, a new draft is laid over the previous notes, and a quote that is no longer at its offsets is moved to its nearest occurrence. The commit message says a version without offsets was rejected because, when the same words are added earlier in the text, it silently points somewhere else.

- `semantic_structure.py` drops the previous text (`base.pop("sourceText")`) before the quotes are found again, so "nearest" is a guess. Revise 「…結論として原油価格の動向を注視する。」 by adding 「ただし原油価格は年内に下がるとの見方もある。」 just before it, and the concluding note now points at the new counter-view, with no error. The case the author said they rejected is still there. (Consistency with the author's words; reproduced. Mapping offsets through a diff of the old and new text puts the note back.)
- With `--base`, `merge_drafts` lays every draft over the one before. An update drafted in two files, as the docs recommend for long texts, loses the first file's quotes for a note the second file also touches; without `--base` they are combined. (Consistency with related code; reproduced.)
- An update can add and change notes but has no way to remove one. When a revision deletes the sentence a note rests on, the only error asks to restate a quote that no longer exists, and the way out is editing the JSON by hand or rebuilding. (An operation the design cannot do; reproduced.)

None of these can be argued from the changed lines alone, and each can be opened and run.
