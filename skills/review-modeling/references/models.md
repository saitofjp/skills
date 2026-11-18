# Models for a Modeling Review

Each entry says when a document calls for the model, how to write it, where it typically fails to write (the gaps it finds), what to check once it is written, and what else it yields. Choose the ones the document calls for; this is not a list to go through, and a document may call for a model not listed here.

## Contents

- Behavior: [State transitions](#state-transitions), [Scenarios](#scenarios), [Screen flow](#screen-flow)
- Data: [Domain model and rules](#domain-model-and-rules), [Terms](#terms)
- Access and trust: [Permission matrix](#permission-matrix), [Data flow and trust boundaries](#data-flow-and-trust-boundaries)
- Building it: [Structure](#structure), [Data ownership](#data-ownership), [Interface contracts](#interface-contracts), [Migration and compatibility](#migration-and-compatibility)
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

## Structure

- **Signs.** A section or diagram of the system's parts; services, apps, databases, queues, workers, batch jobs; "A calls B", "sends to"; other systems the system talks to.
- **Write it as.** The first two levels of the C4 model. The context: the people and outside systems around the system, and what passes between them. The containers: each part that runs or is deployed on its own, and each data store, with what it is responsible for. For each relationship, its direction, whether it is synchronous or asynchronous, and what it carries. Tables of parts and relationships, or a Mermaid `flowchart`. Go down to components only where the document does; the code level is too fine for a document review.
- **Fails to write when.** Something the document says the system does belongs to no part (who sends the reminder, where the nightly job runs); a part is named without what it does; which side starts a call is unstated; a part shows up in the processing sections but not in the structure; two diagrams at different levels disagree.
- **Check.** Each thing the system must do has exactly one part that owns it; calls that go round in a cycle; a chain of synchronous calls where one slow or stopped part stalls the rest; a part that two others rely on with nothing said about what happens when it is down.
- **Yields.** The map that the failure, trust and capacity models are laid on, and the places to put contract tests.

## Data ownership

- **Signs.** Several services, jobs or handlers that touch the same data; a shared database; copies, caches, search indexes, syncing, "reflect", "keep in step".
- **Write it as.** A CRUD matrix: the parts that act on data as rows (services, or, inside one service, API operations, jobs and handlers, whichever level the document is written at), the entities as columns, and a column of its own for any field that carries state, such as a status. Each cell C, R, U, D or blank. Then, for each entity, which part is its source of truth and where copies of it are kept.
- **Fails to write when.** Which part changes a piece of data is unstated; a copy exists without saying how it is kept in step or which side wins; nothing says how long data is kept or what deletes it.
- **Check.** Two or more writers to the same entity or field with nothing that puts them in order (each pair is a race or a lost update waiting to happen); an entity that nothing creates, or nothing deletes; a part that reads or writes another part's store directly; a copy that can fall behind its source while something relies on it being current.
- **Yields.** The source of truth for each entity, retention rules, and the race tests to write first.

## Interface contracts

- **Signs.** API tables, endpoints, events and messages, webhooks, files exchanged with other systems, "public API", versions.
- **Write it as.** One row per operation or message: who calls it, the input, the output, each error and how it reaches the caller, whether calling it twice is safe (idempotency), what authorization it checks, and how it can change without breaking its callers. For events and messages, add who publishes and who consumes, the order they arrive in, and how often they are delivered (at least once, at most once).
- **Fails to write when.** Only the success response is described; errors are not named, or are just "returns an error"; whether a retry is safe is unstated; who may call it is unstated, or rests on trusting the caller (a webhook that does not check who sent it); a list has no limit or paging; a change to an existing interface says nothing about its current callers.
- **Check.** Every operation the system needs has an interface, and every interface serves something the system needs; every error has an outcome for the caller and for the user; every state-changing call that something can retry (a client after a timeout, a queue, a webhook sender) is safe to repeat; the delivery guarantee of each message matches what its consumer can handle.
- **Yields.** Contract tests, and the error cases for the scenarios.

## Migration and compatibility

- **Signs.** A change to a system that is already running: "replace", "migrate", "switch over", "split", "deprecate", schema changes, new required fields or rules, a rollout plan, existing data or existing users.
- **Write it as.** The current state, the target, and the steps between, each with what runs during it (old, new, or both), where writes go, and how to go back. Then a compatibility table: the old and new versions of clients, servers, schemas and message formats that can meet during the rollout, each combination marked works, breaks or unstated.
- **Fails to write when.** Only the end state is described; how existing data gets into the new shape is unstated; how long old and new run side by side is unstated; a step has no way back, or going back after the new side has taken writes is unstated; what happens to requests in flight at the switch is unstated.
- **Check.** Every combination that can meet during the rollout works (a new client against an old server mid-release; an old reader on rows the new writer wrote); writes made during a step are not lost by the next one; existing data satisfies every new rule; each step can be undone, or the point of no return is named; a migration that fails halfway leaves something that can be resumed or reversed.
- **Yields.** The rollout and rollback plan, and migration tests on data shaped like the existing data.

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
- Operations in the permission matrix ↔ the interface contracts ↔ state-changing events.
- Every state-changing event ↔ the domain rules it must keep.
- Every external call in a sequence, and every relationship to another part in the structure ↔ a row in the failure model.
- Every crossing of a trust line ↔ a control, and that control ↔ the permission matrix and the authorization in the interface contracts.
- Every field with more than one writer in the data ownership ↔ the concurrency model.
- Every thing the spec asks the system to do ↔ a part in the structure that owns it.
- Every new rule in the domain model ↔ the existing data, when the document changes a running system.
- Every entity and state ↔ the same name in the terms.
- Spec models ↔ design models, when both documents are given.
