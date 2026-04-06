**Ep. 253 — logcat - a new look at logging with Piwai from Square**
*Fragmented Podcast · Kaushik · 40 min · 2024-12-10*

Pierre-Yves "Piwai" Ricau (LeakCanary, Square) joins to explain why he eventually built [Logcat](https://github.com/square/logcat) after years of resisting it, and what performance traps Timber quietly hides.

The core problem: Kotlin's string interpolation (`$value`) is so ergonomic that developers stopped using Timber's `%s`-style deferred formatting and started writing `Timber.d("value: $obj")` everywhere. The issue is that string interpolation compiles to eager concatenation — it runs even when the log is never emitted. Worse, interpolating a data class triggers its `toString()`, which recursively calls `toString()` on all its fields. That cascades into expensive object serialization on the main thread with zero benefit in production.

The second trap is Timber's `DebugTree`, which auto-tags logs with the calling class name by constructing a `Throwable` and reading its stack trace on every log call. It's labeled "debug" but it's so convenient that teams (including Square's) end up shipping it to production. Logcat solves both problems with two Kotlin features: an **inline lambda** wraps the log message so string building only runs if the log is actually needed, and **inline extension functions** give access to `this` at the call site, letting the library derive the class name at compile time rather than via stack trace.

For production logging, the recommended pattern pairs Logcat's lazy evaluation with server-side tag rules (control which lambdas fire remotely), an in-memory **ring buffer** (no disk writes unless the app is dying), and on-demand upload triggered by a push message. The result: near-zero cost until you actually need to investigate a device.

**Why it's worth your time:** If your team writes Kotlin and uses Timber, there's a real chance you have silent performance overhead from interpolated log strings and stack trace captures — this episode explains exactly why, and the fix is a drop-in library swap.