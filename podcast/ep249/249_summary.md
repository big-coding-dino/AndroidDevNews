I need permission to write files. Please approve the write to `podcast/ep249/249_summary.md`, then I'll also save it to the DB.

Here's the summary I've prepared:

---

**Ep. 249 — Java and the JDK: Powering the Android Landscape with Michael Bailey**
*Fragmented Podcast · Don Felker & Kaushik Gopal · 55 min · Jul 10, 2023*

Michael Bailey (Distinguished Engineer at American Express) demystifies the full Java/JDK stack as it applies to Android — from distribution basics through Gradle toolchains, bytecode targeting, and the three Android SDK version settings that every developer touches but few fully understand.

**JDK vs JRE and distributions.** The JRE is a runtime-only subset of the JDK; Android developers need the JDK for the compiler and tooling. Modern apps bundle their own JRE via `jpackage`. All major distributions — Temurin (Eclipse Foundation), Zulu, and others — compile from the same OpenJDK/JDK GitHub repo, which contains the HotSpot JVM, standard library implementations, and the Java compiler. Distributions differ in platform support and patches, analogous to Linux distros vs the kernel. Zulu is notable for offering ARM JDK 8 builds for Mac. The Foojay project provides APIs for querying and automating JDK discovery and installation across distributions.

**Multiple JDKs in one Android build.** Android Studio ships its own bundled JDK. Gradle (itself a JVM app) runs on a separate JDK. Gradle spawns additional daemon processes that may each need a JDK. Mismatched JDKs between IDE and CLI cause multiple Gradle daemons to spin up — wasting memory locally and on CI. The `JAVA_HOME` / `JDK_HOME` env vars control the CLI JDK; Android Studio's Gradle settings let you point it to the same installation. The "Show Gradle Daemons" action in Android Studio lets you check whether multiple are running.

**LTS versions, Gradle toolchains, and bytecode targeting.** JDK LTS releases are 8, 11, 17, and the upcoming 21. AGP 8.x requires JDK 17. Gradle toolchains let you decouple the JDK Gradle runs on from the one used to compile your code — Gradle auto-downloads the declared toolchain version if not found locally. `sourceCompatibility`/`targetCompatibility` in Java control input language features and output bytecode version respectively, but they miss a third dimension: which JDK APIs are accessible at runtime. The `--release` flag bundles all three, preventing accidental use of APIs unavailable on older runtimes. Kotlin's `jvmTarget` controls output bytecode independently of the toolchain running the Kotlin daemon. Android's compile options DSL still uses `sourceCompatibility`/`targetCompatibility` rather than `--release`.

**Core library desugaring.** Java 8's `java.time` APIs weren't available on Android until API 26. Core library desugaring (an AGP feature) injects OpenJDK library code directly into the APK, backporting those APIs to older Android versions — similar to how AndroidX ships its own copies of platform components.

**minSdk, compileSdk, targetSdk.** These three settings are distinct: `minSdk` is an install-time gate and primarily a product decision based on your user demographics (easier to maintain a low `minSdk` today thanks to AndroidX and desugaring). `compileSdk` is compile-time only — always upgrade to the latest as soon as it hits platform stability, since it has zero runtime impact and gives better nullability annotations. `targetSdk` changes runtime behavior on newer Android versions; Google Play mandates yearly upgrades, and testing must happen on the actual new OS version — bumping the number without testing on the new platform is a common mistake. Check the behavior changes docs on developer.android.com for each release.

**SDK Extensions / Project Mainline.** Newer Android APIs are being back-ported to older devices via Mainline module updates, requiring runtime SDK extension checks on top of the standard `minSdk` check. AndroidX abstracts these internally (the photo picker being one example), but understanding the mechanism matters when debugging failures on old-but-updated devices.

**Why it's worth your time:** If you've ever cargo-culted those `sourceCompatibility`, `targetCompatibility`, and SDK version settings without fully understanding what each one controls — or wondered why multiple Gradle daemons were eating your RAM — this episode gives a clean, end-to-end mental model. Bailey connects OpenJDK distributions, Gradle toolchains, bytecode versioning, and Android SDK levels into a single coherent picture that makes the configuration choices in any Android project immediately legible.