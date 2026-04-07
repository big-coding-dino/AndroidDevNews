# build-apk

Build the anews debug APK and serve it over HTTP for sideloading.

## Steps

1. Build the debug APK:
```
cd /root/anews/kmp && ./gradlew assembleDebug
```
If the build fails, read the error output and fix compilation issues before retrying.

2. Kill any existing process on port 9000:
```
fuser -k 9000/tcp 2>/dev/null; sleep 1
```

3. Serve the APK:
```
python3 -m http.server 9000 --directory /root/anews/kmp/composeApp/build/outputs/apk/debug &
```

4. Report the download URL to the user:
```
http://$(hostname -I | awk '{print $1}'):9000/composeApp-debug.apk
```
