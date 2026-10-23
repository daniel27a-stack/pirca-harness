---
name: pirca-errors
description: How pirca designs errors, covering the base exception and the ProblemDetail answers. Not preloaded, read it when the repository profile lists it in its Skills section. Used by lib-errors and by the services that use it.
---

# pirca errors

The error design of pirca. `lib-errors` implements it; every service that uses the library follows
it. How the Java code is written in general is in `pirca-java`.

- Exceptions are unchecked (`RuntimeException`).
- One base exception with three fields: `code` (stable, for machines, an uppercase string with
  underscores such as `EXPENSE_NOT_FOUND`, defined by each service), `message` (human) and `status`
  (HTTP). The library carries only the base; a service extends it for its domain errors.
- A `@RestControllerAdvice` answers with `ProblemDetail` (RFC 9457): `type`, `title`, `status`,
  `detail`, and the extension `code`.
- An unexpected exception, one that is not the base, is also answered as a `ProblemDetail` with
  status 500 and a generic `detail`: no stack trace and no internal message leaves the service.
- A trace or correlation id in the response is left to `lib-logging`; not here.
