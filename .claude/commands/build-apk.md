# build-apk

Build the anews debug APK and serve it over HTTP for sideloading.

## Steps

1. Build the debug APK:
```
cd ~/anews && ./gradlew :kmp:composeApp:assembleDebug
```
If the build fails, read the error output and fix compilation issues before retrying.

2. Kill any existing process on port 9000:
```
fuser -k 9000/tcp 2>/dev/null; sleep 1
```

3. Copy the APK as `a.apk` and serve it:
```
cp ~/anews/kmp/composeApp/build/outputs/apk/debug/composeApp-debug.apk ~/anews/kmp/composeApp/build/outputs/apk/debug/a.apk
python3 -m http.server 9000 --directory ~/anews/kmp/composeApp/build/outputs/apk/debug &
```

4. Report the download URL to the user:
```
http://$(hostname -I | awk '{print $1}'):9000/a.apk
```
