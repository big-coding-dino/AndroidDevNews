# Performance — April 2026 Digest
*Written by Claude · Source: Android Weekly*

---

### [ImNotOkay, a GC experiment for Android CI builds](https://dev.to/cdsap/imnotokay-a-gc-experiment-for-android-ci-builds-489o)
An April Fools joke turned serious experiment: the author forked **JDK 23** and built a custom **G1-based GC policy** called `ImNotOkayGC`, designed specifically for the workload shape of Android CI builds. The hypothesis is that ephemeral Gradle builds — with their well-defined phases of startup, rising memory pressure, heavy execution, and termination — are fundamentally different from long-running JVM services, yet we use the same general-purpose collectors for both.

The experiment was rigorous. A baseline was established using standard G1 in both Gradle and Kotlin daemons, then an iterative loop was run across real projects (`android-nowinandeland`, `CatchUp`, and generated projects at small/medium/large scale): capture **JFR recordings** and GC logs, profile allocation patterns, modify the JDK, rerun, compare. Each scenario (`assembleDebug` / `assembleRelease`, warm vs. nonwarm) was executed 10 times for statistical reliability. **Codex** was used throughout to accelerate the mechanical work — modifying JDK internals, wiring CI runs, parsing profiling output.

The `ImNotOkayGC` policy tweaks G1 in three phases: stay hands-off for the first ~60 seconds (configuration phase), then cap young generation growth when memory pressure builds, then gradually relax constraints to recover throughput if pressure persists. The full diff is on GitHub at `cdsap/jdk`, branch `im-not-okay`.

The results were a clear failure by the author's own assessment. GC p95 pause times went up in most scenarios (e.g. `+21.51%` for nowinandroid release nonwarm, `+12.89%` for CatchUp release warm). Build durations were mixed — some marginal gains, some regressions — with no consistent pattern across project sizes or warm/nonwarm modes. The experiment was closed early.

The custom JDK is still usable via `-XX:+UnlockExperimentalVMOptions -XX:+UseImNotOkayGC` if you download the artifact from the `cdsap/im-not-ok-metrics` GitHub Actions run.

**Why it matters:** The result is negative, but the methodology is worth stealing. Most Gradle performance work stops at flag tuning (`-Xmx`, `-XX:G1HeapRegionSize`, etc.) because iterating on JDK internals is prohibitively slow. This experiment shows that JFR-driven profiling + Codex-assisted JDK modification makes that loop practical for a single developer. It also raises a question worth revisiting: if Android Gradle builds really do have a distinct, predictable memory profile, a purpose-tuned GC policy should theoretically be possible — this attempt just didn't find the right levers yet.