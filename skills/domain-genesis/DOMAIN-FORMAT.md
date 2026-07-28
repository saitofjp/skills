# DOMAIN.md Format

## Structure

```md
# {Domain Name}

{One or two sentence description of the world this domain models and why it exists.}

## Vision

{Why this domain exists.}

## Core Domain

{What unique value this domain provides.}

## Concepts

### {Concept}

{One or two sentence definition.}

### {Concept}

{Definition.}

## Rules

- {Invariant that is always true.}
- {Business rule that defines the domain.}

## Structure

```text
{Concept}
   │
   ▼
{Concept}
 ├─ {Concept}
 └─ {Concept}
```
```

---

# Rules

## General

- **Describe the world, not the implementation.**
- **Keep every section implementation independent.**
- **If a statement would change because of a framework or architecture decision, it does not belong here.**

---

## Vision

- Explain **why the domain exists**, not why the software exists.
- One or two sentences.
- Avoid product features and technical goals.

---

## Core Domain

- Describe the unique value of the business.
- Exclude authentication, payments, notifications, administration, and other supporting concerns.
- Focus on what makes this domain worth building.

---

## Concepts

- Define only concepts that exist in the domain.
- Define what a concept **is**, not how it behaves internally.
- Do not describe database fields, APIs, UI elements, or classes.
- Prefer one canonical name for each concept.

---

## Rules

- Only include rules that are **always true**.
- Rules must remain valid regardless of implementation.
- Avoid lifecycle details that depend on state machines or APIs.
- Avoid validation rules caused by UI or persistence.

---

## Structure

- Show relationships between concepts.
- This is **not** an ER diagram.
- This is **not** a UML class diagram.
- Do not include IDs, foreign keys, multiplicity, inheritance, or implementation details.
- Keep the graph simple enough to understand the domain at a glance.

---

# Never Include

The following belong in other documents:

- APIs
- Database schema
- SQL
- Classes
- Services
- Repositories
- Controllers
- Events
- State machines
- UI
- Frameworks
- Libraries
- Infrastructure
- Directory structure

---

# Related Documents

| Document | Responsibility |
|----------|----------------|
| DOMAIN.md | Defines the domain itself |
| USE_CASES.md | Defines user goals and interactions |
| CONTEXT-MAP.md | Defines bounded contexts and their relationships |
| ADR | Records architectural decisions |
| API.md | Defines external interfaces |
| DATABASE.md | Defines persistence |

---

# Philosophy

DOMAIN.md is the source of truth for the domain.

It defines:

- why the domain exists,
- what concepts exist,
- what rules are always true,
- and how those concepts relate.

Everything else is an implementation detail.