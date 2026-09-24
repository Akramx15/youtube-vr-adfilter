# YouTube VR Ad Filter — Experimental

Two experimental options for YouTube VR **1.87.13 / 18713000** on Meta Quest ARM64. Choose one method.

## Downloads

Download the files from [Releases](https://github.com/Akramx15/youtube-vr-adfilter/releases):

- **YouTubeVR-1.87.13-rootless-experimental.apk**: the modified app; the patch itself does not require root or a module.
- **youtube-vr-adfilter-test.apk**: an LSPosed/Vector module for the official app on a rooted headset.
- **youtube-vr-adfilter-source.zip**: module source, build script, and verification script.
- **rootless-certificate.pem** and **lsposed-certificate.pem**: public signing certificates.
- **SHA256SUMS.txt**: file checksums for integrity verification.

## Standalone APK

Uninstall the official app before installing this APK because their signatures differ. Uninstalling deletes local app data and may require signing in again. Try launching directly from the headset library. The tester reported that direct launching works and that no ads appeared.

If a **Restore App** prompt prevents launching, the optional `launch-via-adb.sh` script starts the activity twice, one second apart, from a computer with an authorized ADB connection. Do not select Restore if you want to keep the modified app. This workaround does not guarantee that the prompt will stay away permanently.

The standalone APK was tested on a rooted Quest 3 after removing the ad-filter module. It has **not yet been tested on an actually unrooted headset**. Sign-in continuity and 360° playback were not separately confirmed in the recorded test.

To return to the official app, uninstall the modified APK and reinstall YouTube VR from the official store. Uninstalling removes local app data.

## LSPosed / Vector module

Install the official app version listed above, install the module, enable it in LSPosed/Vector, and select only **com.google.android.apps.youtube.vr.oculus** in its scope. Fully close YouTube VR and reopen it. The module refuses to apply hooks to other versions. The attached APK is our module, not the LSPosed framework installer.

## Signing and building

Private signing keys are not published. The public PEM certificates cannot be used to sign on behalf of the developer. Verify the files with `sha256sum -c SHA256SUMS.txt` and `apksigner verify --print-certs FILE.apk`.

Module source is in `lsposed/`. Set `ANDROID_HOME` to an Android SDK containing platform 34 and build-tools 34.0.0, then run `python build.py` from that directory. The script creates a local signing key and password inside `build/`; keep both private. Running `python verify.py` requires Java and the Python packages `androguard` and `loguru`. A fresh build has a different signature from the published release APKs.

## Testing limits and references

The patch skips two ad-related methods in this specific app version. Blocking every ad path or supporting future versions is not guaranteed. This is an unofficial project with no affiliation with Google, YouTube, or Meta. Rights to the original app belong to their respective owners. Published files contain no account data or private backups.

Ad-path fingerprints from [NexAlloy](https://github.com/NexAlloy/NexAlloy/tree/be1b44336330ac14431cfc4b7755dd97b3da313a/app/src/main/java/io/github/nexalloy/morphe/youtube/ad) were used as a comparison reference; the full module is not included. The fallback launch method comes from [QuestPatcher](https://github.com/Lauriethefish/QuestPatcher/commit/572bf49b27fc783f9d6dfcbbcdcacbf2eedda895), adapted to use the YouTube VR activity instead of the Unity activity.
