---
name: review-birds-eye
description: Reviews a change from a bird's-eye view, the way a senior engineer does - looks at the whole design the code implies rather than line by line, and reports each finding concretely, with the file, a scenario and what happens. Judges the design (is the change carried through consistently in the related code, does it sit in the right place, will the next changes break it) and the non-functional requirements (side effects such as slowdowns or unintended data changes, compatibility, failure, concurrency, operation, security). Use it when the user asks for a design or architecture review, a senior-level or big-picture review of a PR, branch or diff, a security review of the design rather than the code, or wants to know whether a feature will hold up as the system grows. Triggers include "bird's-eye review", "review the design", "architecture review", 「俯瞰してレビューして」「設計レビューして」「アーキテクチャレビューして」「シニア目線でレビューして」「この機能、今後の拡張で壊れない？」「設計としてのセキュリティを見て」.
---

# Bird's-Eye Review

A line-level review asks whether the code does what it says. This review looks at the change from higher up, the way a senior engineer does, and asks two things the lines alone cannot answer:

- **Design.** Is the change carried through consistently in the code around it?
- **Non-functional requirements.** What does the change do besides what it is meant to do: slow something down, change data, break under failure?

The review goes in this order, because each part needs the one before: understand what the change is for, state the design the code implies, look at that design from the two sides above, turn what you see into concrete findings, and report. How deep to go in each part, and which questions to chase, is yours to judge from the change in front of you.

## Understand the change

What to review comes from the arguments: a PR number or URL, a branch, a commit range, a path, or a design document written before any code exists. With no argument, review the current branch against the default branch.

Read what the change is for from the PR description and the commits. The review judges the change against that purpose, so if it is written nowhere and your reading of it would change the findings, ask. Otherwise, state your reading and go on.

## State the design the code implies

You can only judge a design you can state. So read beyond the changed lines, into the code that calls them and the code they call, and put the design in words: the parts and what each is responsible for, the boundaries between them, how data flows, and the contracts and invariants the code relies on. Name the actual modules, functions and files rather than generic layers, and say where you read each piece.

If part of the design cannot be drawn from the code, say what is missing rather than filling it in. That the intent is not readable from the implementation is itself worth reporting.

Size this to the change: a few lines for a small one, a sketch or a diagram for a large one. For a design document, there is no code to read; take the design the document gives.

## Look at it from two sides

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

## Turn what you see into findings

Not everything you notice is a finding of this review. Two tests decide.

**It needs something outside the changed lines.** A finding here rests on how the rest of the system works, what the change is for, how it will be used, or what will change next. What the changed lines alone can show is better left to a line-level code review, by whatever tool or person does that where you work; mixed in, the many small points bury the few design ones. If you notice one anyway, a line pointing to it is enough.

**It is concrete.** A vague finding, such as "this coupling may hurt extensibility" or "consider a clearer separation of concerns", fits almost any code, cannot be shown wrong, and gives the author nothing to act on. Advice that would apply to any codebase (follow SOLID, add an abstraction layer, write more tests) is not a finding about this change. So write each finding with three things: the file and line where the problem sits, a specific input or change that sets it off, and what then happens. If you cannot say these, look further or leave it out.

The surest way to make a finding concrete is to run it: a minimal reproduction, a scenario put through the real code, a small check that a direction for a fix works. A reproduction turns "could" into "does", and authors act on that. Mark what you could not run as a hypothesis, so it is weighed as one. Keep reproductions in a scratch place, not in the repository.

Many design "problems" are tradeoffs the author chose, and the commit message may say so. Name the tradeoff and what it costs in a likely scenario, and leave the decision to the author. For the same reason, the review changes no code unless the user asks.

## Report

Start with the design as you stated it, briefly, so the author can see what the findings are judged against. Then the few findings that matter most, weighed by what happens in scenarios likely to occur, not by elegance. For each: the scenario, what happens, the evidence (`file:line`, the reproduction), whether it is reproduced or a hypothesis, and a direction for a fix (a direction, not necessarily a patch). Then what to keep, and what you did not look at, so the author knows where the review stops.

Read each finding back as the author: could they open the file, run the scenario and see it happen? If not, make it more concrete.

Keep it in proportion to the change. A small change gets a short review, and points that found nothing need not be reported one by one.

## An example

This shows the level to aim for, not a form to copy. It comes from the `semantic-structure` skill in saitofjp/skills (PR #39).

The tool turns a text into notes. Each note keeps the quote it rests on and the quote's character offsets in the text. The change added `resolve --base`: when the text is revised, a new draft is laid over the previous notes, and a quote that is no longer at its offsets is moved to its nearest occurrence. The commit message says a version without offsets was rejected because, when the same words are added earlier in the text, it silently points somewhere else.

- `semantic_structure.py` drops the previous text (`base.pop("sourceText")`) before the quotes are found again, so "nearest" is a guess. Revise 「…結論として原油価格の動向を注視する。」 by adding 「ただし原油価格は年内に下がるとの見方もある。」 just before it, and the concluding note now points at the new counter-view, with no error. The case the author said they rejected is still there. (Consistency with the author's words; reproduced. Mapping offsets through a diff of the old and new text puts the note back.)
- With `--base`, `merge_drafts` lays every draft over the one before. An update drafted in two files, as the docs recommend for long texts, loses the first file's quotes for a note the second file also touches; without `--base` they are combined. (Consistency with related code; reproduced.)
- An update can add and change notes but has no way to remove one. When a revision deletes the sentence a note rests on, the only error asks to restate a quote that no longer exists, and the way out is editing the JSON by hand or rebuilding. (An operation the design cannot do; reproduced.)

None of these can be argued from the changed lines alone, and each can be opened and run.
