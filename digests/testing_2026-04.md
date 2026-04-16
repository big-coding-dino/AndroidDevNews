# Testing — April 2026 Digest
*Written by Claude · Source: Android Weekly*

---

### [Introducing Kensa: BDD for Kotlin and Java Without the Gherkin Tax](https://kensa.dev/blog/introducing-kensa)
**Kensa** is a BDD testing library for Kotlin and Java that eliminates the Gherkin layer entirely. Instead of maintaining feature files, step definitions, and glue code separately, you write Given-When-Then tests directly in Kotlin — Kensa parses your test source at runtime, extracts the sentence structure, and substitutes in actual captured values to generate living HTML documentation.

A test method like `` `address is serviceable by both suppliers` `` calls `given()`, `whenever()`, and `then()` with real objects and assertions. The resulting report shows those sentences with live values — fixture data like `fastestDownloadSpeed` and `fastestSupplier` appear in the report as they actually ran, not as placeholders.

Beyond readable test output, Kensa auto-generates **sequence diagrams** from interaction captures, provides inspectable request/response payloads per interaction, and ships with an IntelliJ plugin for navigating from report back to test. A Kotlin compiler plugin handles `@RenderedValue` and `@ExpandableSentence` annotations for capturing values in reports without extra boilerplate. Framework support covers **JUnit 5 & 6**, **Kotest**, and **TestNG**, with assertion library flexibility across Hamcrest, AssertJ, Kotest assertions, and HamKrest. The current release is `kensa-junit:0.6.6`, added via a single `testImplementation` dependency.

**Why it matters:** Cucumber's core promise — tests that non-technical stakeholders can read — breaks down when keeping Gherkin files and step definitions in sync becomes a maintenance burden that outweighs the benefit. Kensa bets that readable tests written in Kotlin are good enough for that purpose, and that generated sequence diagrams from real interactions are more valuable than hand-maintained specs. For teams already doing JVM development, it's a lower-friction path to documented, traceable behavior tests without a parallel file system to manage.