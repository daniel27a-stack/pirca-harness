---
name: pirca-java
description: How pirca writes Java, covering style, responsibilities and encapsulation, design patterns and errors. Not preloaded, read it when the repository profile lists it in its Skills section. It grows with each library.
---

# pirca Java

How code is written in pirca's Java repositories (Java 25, Spring Boot 4). The architecture —
artifact types, layers, packages, build — is in `pirca-conventions`; this skill is about the code
inside. Where the two disagree, `pirca-conventions` wins. It grows with each library; what belongs to
one concern has its own skill, such as `pirca-errors`.

## General
- Dependency injection by constructor, never by field.
- Immutable data carriers are `record`s.
- Composition before inheritance; small interfaces.
- A library is technical only: no business logic.

## Style
- **Lombok: not by default.** Records cover data carriers, and a constructor is a few lines. Lombok
  adds a build dependency and an annotation processor that must follow every Java version, and hides
  code from the quality tools. Adopting it would be a template decision with its own card.
- **Lambdas: yes, short ones.** If a lambda passes about three lines or needs a comment, extract it
  to a named method. Use method references when they are enough.
- **Streams: yes to transform collections** (`map`, `filter`, `toList()`); a `for` loop when it is
  clearer. Never for side effects, and not nested.
- **`parallelStream`: not by default.** Only for CPU-bound work over large collections, where each
  element is independent, nothing depends on the thread context (tenant, MDC, security,
  transaction), and it was measured to be faster. To wait for several things at once, use virtual
  threads.

## Responsibilities and encapsulation
- **One responsibility per method**, at one level of detail. If its name needs an "and", or comments
  separate sections inside it, split it. The same for classes: one reason to change. The layers
  (`controller`, `service`, `repository`, `client`) already divide the work this way.
- **Encapsulation**: fields `private`, `final` when possible; expose behavior, not state. No public
  mutable fields. Internal collections are returned immutable or as copies. A class that is not part
  of the public API has no access modifier (visible only in its package). In a library, `public` is
  the API every service inherits: keep it minimal.

## Design patterns
Problem first, pattern after. A pattern is used when it removes an `if/else` that keeps growing or
real duplication, and the one that Spring or the JDK already provides is preferred. No layers for a
hypothetical extension, and no pattern for one or two cases that show no sign of growing.

Signals that call for a pattern:

| Signal | Consider |
|---|---|
| An `if/else` or `switch` on a kind that chooses behavior, 3 or more branches, likely to grow | Strategy (a small interface, or a lambda); if the set of cases is closed, `sealed` types and an exhaustive `switch` |
| A sequence of steps or validations where each can stop or enrich the process | A chain or pipeline (the framework's, when it has one) |
| Behavior that depends on a state, with transitions | State (or an enum of states) |
| A constructor with many optional parameters | Builder |
| Several external systems with different shapes | Adapter (the `acl` type) |
| Cross-cutting concerns: logging, audit, retries | AOP |

Never by hand what Spring gives: a singleton is a bean.

When the card has logic with one of these signals, the architect writes one line of design in
`implementation.md`: *pattern: X, because Y*, or *none, because Z*. Patterns inside a class or a
package are the architect's to decide. A pattern that changes the architecture of an artifact
(for example hexagonal ports and adapters, left as a future option for a `flow` with rich business
rules in `pirca-conventions`) is the user's decision: ask.

**Adapter.** Use it to isolate what is not yours (an external API, a legacy system, a third-party
SDK): its types do not leave the `client`. The class is named `*Client`, as the layer naming rule
of `archTest` requires. No interfaces or wrappers over your own code, or over Spring or the JDK
pieces you will not replace.
