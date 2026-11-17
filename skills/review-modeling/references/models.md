# Models for a Modeling Review

Each entry says when a document calls for the model, how to write it, where it typically fails to write (the gaps it finds), what to check once it is written, and what else it yields. Choose the ones the document calls for; this is not a list to go through, and a document may call for a model not listed here.

## Contents

- Behavior: [State transitions](#state-transitions), [Scenarios](#scenarios), [Screen flow](#screen-flow)
- Data: [Domain model and rules](#domain-model-and-rules), [Terms](#terms)
- Access and trust: [Permission matrix](#permission-matrix), [Data flow and trust boundaries](#data-flow-and-trust-boundaries)
- Running it: [Failure](#failure), [Concurrency and ordering](#concurrency-and-ordering), [Capacity](#capacity), [Operation](#operation)
- [Checks across models](#checks-across-models)

## State transitions

- **Signs.** Statuses, lifecycle words ("draft", "in progress", "expired", "cancelled"), anything that can be done "once" or "after".
- **Write it as.** A table with states as rows and events as columns, each cell the next state or "refused", plus a Mermaid `stateDiagram` when the reader needs the picture. Note the guard on a transition if there is one.
- **Fails to write when.** An event is allowed "at any time" but its effect is defined for only some states; there is no way out of a state (timeouts, abandonment); the start or end state is unnamed; two documents name the same state differently.
- **Check.** States that cannot be reached or cannot be left; events with no defined result in some state; transitions that skip a step another rule depends on (paid before confirmed).
- **Yields.** Tests that cover every transition and every refused event.

## Scenarios

- **Signs.** Use cases, user stories, "the user does X, then Y".
- **Write it as.** Given / When / Then, or a Mermaid `sequenceDiagram` when several parties are involved. One main flow, then the alternatives.
- **Fails to write when.** Only the happy path exists; the precondition is not stated; the result is described as a screen, not as what is now true.
- **Check.** Every alternative (invalid input, nothing found, no permission, the other party fails) has an outcome; the outcome agrees with the state transitions.
- **Yields.** Acceptance tests and end-to-end tests.

## Screen flow

- **Signs.** Screens, pages, wizards, steps, "back", "return to".
- **Write it as.** Screens as nodes, actions as edges (Mermaid `flowchart`), with where each error lands.
- **Fails to write when.** Errors, empty states or expired sessions have no screen; "back" is not defined after a submission.
- **Check.** Dead ends; screens that cannot be reached; a path that submits twice; a path that shows data the user should not see.
- **Yields.** End-to-end paths.

## Domain model and rules

- **Signs.** Nouns that are stored, counts, "must", "unique", "at most", "always", relationships between things.
- **Write it as.** Entities and their relationships with multiplicities (a table or a Mermaid `erDiagram`), then the rules (invariants) as short statements: "a candidate has at most one active attempt per exam".
- **Fails to write when.** Multiplicity is unstated (one or many?); what happens to children when a parent is deleted is unstated; history versus overwrite is unstated (retakes, edits); identity is unclear (what makes two records the same thing).
- **Check.** Does every operation that changes data keep every rule? Can two rules both hold? Does deletion leave orphans? Does existing data satisfy a new rule?
- **Yields.** Property-based tests, database constraints, migration checks. When Alloy is available, a model it can search for counterexamples.

## Terms

- **Signs.** The same word in several sections, or several words that seem to mean one thing.
- **Write it as.** A short glossary: term, meaning, where it is used.
- **Fails to write when.** One term carries two meanings ("user" as account and as candidate; "result" as score and as report); two terms cannot be told apart.
- **Check.** Each use matches the meaning; the other models use the same names.
- **Yields.** A glossary the team can keep.

## Permission matrix

- **Signs.** Roles, owners, admins, teams, sharing, "only", "visible to".
- **Write it as.** Roles (and relationships such as "owner of this resource", "member of this team") as rows, operations on each resource as columns, each cell allowed, refused or conditional.
- **Fails to write when.** A role is named but its rights on some resource are not; sharing is mentioned without saying what the receiver can do; what a former member keeps is unstated.
- **Check.** Too much (a role can read or change what it should not, across tenants); too little (an operation no role can perform); every operation in the matrix exists in the API and the reverse.
- **Yields.** Authorization tests over every cell.

## Data flow and trust boundaries

- **Signs.** Personal data, uploads, input from users or other services, data sent outside, logs.
- **Write it as.** Where data enters, where it goes, where it is stored, and the lines where trust changes (browser to server, tenant to tenant, own system to third party).
- **Fails to write when.** Where data is stored or how long it is kept is unstated; who receives data sent outside is unstated; where validation happens is unstated.
- **Check.** Each crossing of a trust line: what validates or controls it, and whether any path goes around it. STRIDE is a useful prompt for what could go wrong at each crossing.
- **Yields.** Security test cases and a threat list.

## Failure

- **Signs.** Other services, payment, email, background jobs, anything that takes several steps.
- **Write it as.** For each dependency and each step: what happens when it fails, times out, or succeeds twice. A table of dependency × failure → behavior.
- **Fails to write when.** Only success is described; retries are mentioned without saying whether the operation is safe to repeat; a step in the middle has no rollback or recovery.
- **Check.** Half-done states (charged but not recorded); retries that duplicate; timeouts that disagree between caller and callee; what the user sees while it is broken.
- **Yields.** Failure-injection tests and recovery procedures.

## Concurrency and ordering

- **Signs.** Several people on the same thing, resubmission, deadlines, "first come", queues, retries.
- **Write it as.** The steps of each actor and the shared state they touch, then the interleavings that matter. TLA+ when it is available and the protocol is worth it.
- **Fails to write when.** What happens when two act at once is unstated; the order of messages is assumed; the deadline is not defined at the boundary (submitted at the second it closes).
- **Check.** Lost updates; double execution; a check and the action that relies on it separated by a gap; behavior that depends on arrival order.
- **Yields.** Race tests; with TLA+, counterexamples from the model checker.

## Capacity

- **Signs.** "Instantly", "large", limits, user numbers, peaks (an exam opens at 9:00 for everyone).
- **Write it as.** The load the document implies (users, requests, data size, peaks) next to the targets it states (response time, limits), and the resources each request uses.
- **Fails to write when.** Targets exist without load, or load without targets; limits have no behavior when reached.
- **Check.** Whether the stated targets can hold under the implied peak; what happens at the limit; which part saturates first.
- **Yields.** Load test scenarios and SLOs.

## Operation

- **Signs.** SLOs, alerts, audits, support requests, "administrators can see".
- **Write it as.** For each thing that can go wrong or must be known: the signal (metric, log, audit record) and who acts on it.
- **Fails to write when.** A target exists without a way to measure it; support is expected to answer questions the system keeps no record for.
- **Check.** Each SLO has a measure; each failure in the failure model is noticed by someone.
- **Yields.** Monitoring and runbook items.

## Checks across models

A gap between two views is invisible from either one, so these are often where the important findings are.

- Events in the state transitions ↔ actions in the scenarios and the screen flow.
- Operations in the permission matrix ↔ operations in the API or design ↔ state-changing events.
- Every state-changing event ↔ the domain rules it must keep.
- Every external call in a sequence ↔ a row in the failure model.
- Every crossing of a trust line ↔ a control, and that control ↔ the permission matrix.
- Every entity and state ↔ the same name in the terms.
- Spec models ↔ design models, when both documents are given.
