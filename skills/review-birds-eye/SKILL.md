---
name: review-birds-eye
description: Reviews a change from a bird's-eye view, the way a senior engineer does. Reads from the code up to its design and judges whether the change is sound in design (carried through consistently in the related code) and in non-functional requirements (side effects such as slowdowns or unintended data changes, security as design). Use it for a design, architecture or big-picture review of a PR, branch, diff or design document, or to check a change for side effects. Triggers include "bird's-eye review", "review the design", 「俯瞰してレビューして」「設計レビューして」「シニア目線でレビューして」「副作用がないか見て」.
---

# Bird's-Eye Review

The purpose is to see whether a change is sound as design, not whether each line is correct. A senior engineer reads from the code up to the design, and from there looks at two things:

- **Design.** Is what the change sets out to do carried through consistently, in the related code as well as the changed code?
- **Non-functional requirements.** What does the change do besides what it is meant to do: slow something down, change data, break under failure?

How to go about it, what to read and how deep to go, is yours to judge from the change in front of you.

## Understand the change

What to review comes from the arguments: a PR number or URL, a branch, a commit range, a path, or a design document written before any code exists. With no argument, review the current branch against the default branch.

Read what the change is for from the PR description and the commits. If it is written nowhere and your reading of it would change the review, ask. Otherwise, state your reading and go on.

## State the design the code implies

You can only judge a design you can state. So read beyond the changed lines, into the code that calls them and the code they call, and put the design in words: the parts and what each is responsible for, the boundaries between them, how data flows, and what the code relies on. Use the names of the actual modules, functions and files.

If part of the design cannot be drawn from the code, say so rather than filling it in. That is itself something the author should know.

Size this to the change: a few lines for a small one, a sketch or a diagram for a large one.

## Trace what the change affects

Starting from the changed code, trace what it affects, according to the kind of change.

- The code that uses it, and the code it uses.
- Other entry points and paths that handle the same concept or data.
- Boundaries: APIs, the database, data formats, contracts.
- Tests, configuration, documentation, operational jobs.
- The related lifecycle: create, update, delete, retry, cancel.

Do not check all of these mechanically; choose the places where this change could break consistency.

## Look at it from two sides

These are the usual points, each with an example. Choose what this change deserves. Not every one fits every change, and something not listed here may matter more.

**Design: is the change carried through consistently?**

- **Consistency with related code.** Is what the change sets out to do reflected everywhere the same thing is handled: the other entry points (API, CLI, batch), the callers, the docs and tests? For example, the web form now validates the new field, but the nightly import writes the same table without the check.
- **Place.** Does the new code sit where it belongs, and use the mechanism that is already there? For example, a shared validator exists, but the new endpoint validates on its own.
- **Hidden assumptions.** Has the change added a condition that callers must keep and nothing enforces? For example, "call `init()` first" is true only by convention.
- **The next changes.** When the changes likely to come arrive, what breaks, and how many places must change? For example, adding a second payment provider means editing five files that each switch on the provider's name.

**Non-functional requirements: what does the change do besides what it is meant to do?**

- **Side effects.** Does it make something slower, or change data it was not meant to? For example, the list page now runs one query per row; a function that looks like a read now updates a timestamp.
- **Compatibility.** Does it still work with data written before the change, and with old callers? For example, the new required field is missing from every existing record.
- **Failure.** If it stops halfway, is a half-done state left behind? For example, a crash between the two writes leaves only one of them.
- **Concurrency.** Does it hold when two run at once? For example, another request slips in between the check and the write.
- **Operation.** When it goes wrong, will anyone notice and be able to trace it? For example, the failure is swallowed and never logged.
- **Security.** Look at the design, not at whether each line is correct: where does trust change (user input, content from outside, other tenants), where does the control live, and does the new path go around it? For example, the HTML export escapes everything in one helper, but the new CSV export writes cells as they come.

## Tell the author

Say what design you read from the code, then whether the change is sound from the two sides. Where it is sound, say so, and let the reason show in a line or two how far you traced: which ways in, paths and boundaries you followed. You chose where to look deeply, so without that the reader cannot see whether "sound" took in, say, the nightly import, and the author has to check it again themselves. A short review is a fine result.

The points above are for looking, not a form to fill in, so do not go through them one by one in the review. Write what you found; the points that turned out fine would only bury it. When nothing is wrong, a few lines on why the change holds are enough.

## Grounds and confidence

Keep the facts in the code apart from the judgments you draw from them.

When you point out a problem, show these as far as you can:

- Place: the file or function.
- Expectation: the behavior or contract that should hold.
- Condition: when the problem occurs.
- Impact: what actually happens.
- Grounds: what in the code makes you think so.
- Fix: how it can be resolved.

Let the reader tell, right where you say it, whether what you write was seen by running the code or judged by reading it. The reader uses this to decide what to take as given and what to check for themselves. Having the code at hand is something a document review lacks, so what you can run cheaply without touching real data (the tests, a few lines against a throwaway database) is worth running to see. For the rest, it is enough that the reader can tell you judged it from reading. Where the grounds are thin, do not assert; treat it as unconfirmed.

Judge how much a point matters by its impact on the system and its users, not by how the code looks or by preference.

Do not treat general improvements beyond the scope of the change, or matters of taste, as defects.
