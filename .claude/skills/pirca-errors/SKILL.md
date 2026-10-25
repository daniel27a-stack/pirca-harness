---
name: pirca-errors
description: The rules pirca follows to design errors. The exceptions and the answer format are the API of lib-errors and live in its README. Not preloaded, read it when the repository profile lists it in its Skills section. Used by lib-errors and by the services that use it.
---

# pirca errors

The rules for designing errors in pirca. `lib-errors` implements them; every service that uses the
library follows them. The list of exceptions, their constructors and the format of the answers are
the API of the library: they live in the README of `lib-errors`, which is read before using or
changing them. How the Java code is written in general is in `pirca-java`.

- Exceptions are unchecked (`RuntimeException`).
- Use the ready-made exceptions directly, giving the service's own code and message. Extend the base
  exception only for a case they do not cover.
- The `code` is stable and for machines: an uppercase string with underscores such as
  `EXPENSE_NOT_FOUND`, defined by each service. It is never a number.
- The `message` is written for the client and travels in the answer. It never carries internal data
  (stack traces, class names, queries, hosts).
- When wrapping another exception, pass it as the cause. The cause is only logged; it never leaves
  the service.
- An unexpected exception is answered as a generic 500: nothing internal leaves the service.
