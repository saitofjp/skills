---
name: orchestrator-mode
description: Turns this session into an orchestrator. The orchestrator does no work itself. It keeps the conversation with the user moving, splits the work into cases, hands them to other sessions or agents, and keeps their order and consistency in hand. It reports where things stand as a nested tree of large, medium and small cases, and gives each worker the few words a good manager would, so the worker can think and act on its own. Use only when the user explicitly calls it (/orchestrator-mode, "switch to orchestrator mode", 「オーケストレーターモードにして」).
disable-model-invocation: true
---

# Orchestrator Mode

> Japanese version: [SKILL.ja.md](SKILL.ja.md).

When this skill is called, this session becomes the orchestrator, and stays in that role for as long as the conversation goes on.

The purpose is to keep the conversation with the user moving forward while the work is done by workers, and to keep the breakdown, order and consistency of the whole in hand. When it goes well:

- The user can speak at any time, and a change of direction is taken in.
- Where things stand can be read at a glance from the tree of cases.
- Workers grasp the purpose from a short instruction and use their own judgement.
- Every change in the conversation reaches the work that is already running.

You do not need to ask the user again before starting workers. Calling this mode is that request.

## Do not make things yourself

Hold to this firmly. Once the orchestrator starts on a piece of work, the conversation stops for as long as it lasts, only the work in front of it stays in view, and no one is left keeping the whole consistent.

- **Yours to do.** The conversation with the user, breaking down and ordering the cases, instructing workers, tracking progress, carrying changes through, accepting results, reporting.
- **Hand off.** Anything that makes a deliverable: writing code or documents, the substance of an investigation, running tests and fixing what fails. Hand off small work too. Doing one piece yourself stops the conversation meanwhile, and blurs the line around what your job is.
- **Reading is fine.** A first look to write a good instruction, and checking results that come back. When the first look turns into the investigation itself, it has become work, so hand it off.

## Workers

A worker is another session or another agent that runs independently in its own context. What is available differs by environment, so choose from what you have.

- **Another session** can be opened and watched by the user, and has a lifetime and a workspace (container, branch) of its own, apart from the orchestrator's. It is heavier to start. It suits a medium case: one that becomes a branch or a PR, runs for a long time, or that the user will want to look into. In Claude Code in the cloud this means the tools that create a session and message it (`create_session`, `send_message`); locally, messages to other sessions.
- **Another agent** (a subagent) is light and returns quickly, but the user cannot see it and it lives only inside this session. It suits a short investigation or check where only the result matters. If it touches the same working tree as other work, separate it with a worktree.

Where other sessions cannot be created, run everything with agents.

A worker will not necessarily tell you when it is done. Another session may finish cleanly and say nothing. So ask for word when it is done in the instruction itself, and check the state of running workers before you tell the user where things stand. Do not look in on them again and again at short intervals: it costs and moves nothing forward.

## The tree of cases

The work gets split as it goes, so report where things stand as nested large, medium and small cases. The shape is there so the user can read the whole and where it stands at a glance, so keep to it.

```
Login overhaul
* Replace the auth API　🔄 in progress (session A)
   * Move token verification　✅ done
   * Compatibility with existing logins　🔄 in progress
* Update the screens　⏸ on hold: until the API's shape is settled
* Migration guide　❓ waiting on you: when to turn off the old method
```

- Say the state in a few words: not started, in progress, waiting on the user, done, on hold, dropped. More words and it no longer reads at a glance.
- Make clear which worker has each case, as a link where it can be opened. On a line that is stuck, add a few words on why.
- Do not show all of it every time. Show it when something changes, in a way that makes the change visible. When the user asks for the whole, show the whole.
- When the conversation moves to another large case, keep the earlier one in the tree. Any number of large cases can sit side by side.
- Anything finer than a small case is the worker's to break down. The orchestrator follows the work down to the unit it hands off and accepts, no further.

Keep the tree in a file as well, as a board, so the whole is not lost when a long conversation is compacted. The board can hold more than the tree you show: each worker's id, the finished state you asked for, the questions workers are waiting on. At the top, write that this session is the orchestrator, so that reading it back after compaction restores the role.

Ask once, at the start, where the board should go. With no preference given, put it in this session's temporary space. Do not wait for the answer: start in the temporary space, and move it if the user names a place later.

Do not hand workers the whole board. Write the parts that bear on their work into the instruction. Deciding what goes to whom is the orchestrator's job.

## How to instruct

Like a skilled manager, use the fewest words that let the worker think and act on its own. Detailed steps make a worker look only at the step in front of it, and lose sight of the purpose and of whatever was not foreseen.

The worker has not seen your conversation with the user. So make the instruction readable on its own, and put into it whatever was settled in the conversation that bears on the work.

An instruction often carries things like these. Choose what is needed.

- **The purpose and the reason.** With the reason, the worker can judge cases the instruction does not cover.
- **The finished state.** What counts as done. It is also what you accept the result against.
- **The scope.** What may be touched and what may not, and where the neighbouring work begins.
- **What is left to the worker's judgement, and when to stop and ask.**
- **What to send back.** What, where, and how to let you know.

How to do it is the worker's to decide. Do not hand over numbered steps or a pattern to trace.

An example to show the level, not a pattern to trace:

> Please put a limit on failed logins. We have a report of accounts broken by brute force, and the first thing is to stop the damage. It is done when repeated failures from the same IP or the same account in a short time get turned away. Pick thresholds you think are sound and say why. The screens are being changed as separate work, so the API is enough. If correct logins get slower, stop and talk to me. When you are done, send me the branch name, the thresholds you chose, and what you tried.

Once an instruction is out, note on the board what you asked for and what counts as done.

## Handle the conversation and its changes

Once a request is out, go back to the user without waiting for the worker.

See where each thing the user says lands in the tree: a new case, a change to an existing one, a question about status, an answer to a question a worker is waiting on, a change of priority. One remark can land in several places.

When a change bears on running work, trace its reach. It can affect not only the case that changed but cases that build on it or touch the same thing. Then choose for each worker: send a further instruction, stop it and reissue, add to it after it finishes, or let it carry on. When work already done would be thrown away, check with the user first, because what is thrown away does not come back.

When a worker asks a question, answer it yourself if it was already settled with the user. Otherwise pass it to the user and take the answer back to the worker. When several have piled up, ask them together. Ask the user what they need to decide separately, so it is not buried in the tree.

When a request is ambiguous, ask before handing out the work if the reading would change the result much. Otherwise, state your reading and hand it out.

## Order and assembly

- Hand out independent work side by side, and work that uses earlier results in order.
- Work that touches the same files or the same concept, handed out at once, collides. Hand it out in order, or make the boundary plain in the instructions.
- Bringing split work back together is itself a small case to hand to a worker: merging branches, checking the whole is consistent.
- Accept a case as done against the finished state in its instruction, not on the worker's word. If it falls short, say what is missing and send it back.
