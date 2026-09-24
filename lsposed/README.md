# YouTube VR Ad Filter (Test) — 0.1-test

An experimental local LSPosed module for the native YouTube VR app on Meta Quest. It attempts to block two video-ad creation paths while retaining the original app and player. Building the APK and passing static checks do not establish ad-blocking effectiveness or correct 360° playback; these require device testing.

- Module name: **YouTube VR Ad Filter (Test)**
- Module package: `local.quest.youtubevr.adfilter`
- Sole target: `com.google.android.apps.youtube.vr.oculus`
- Supported version only: `1.87.13`, version code `18713000`. Hooks are not applied if either value differs.
- No ads, network connections, Android permissions, UI activity, or account access. Does not modify the original APK.

## Enable and test

1. Install `youtube-vr-adfilter-test.apk` and enable the module in LSPosed.
2. Select only YouTube VR in the module scope. Do not select the system framework or other apps.
3. Fully close YouTube VR and reopen it. If LSPosed requests a reboot to apply the configuration, follow that prompt.
4. Test a regular video and a 360° video: playback, audio, head tracking, changing the viewing angle, seeking, and returning to the library. If playback fails, disable the module and reopen the app.
5. Module logs use the `[YT_VR_AD_FILTER]` prefix. Successful loading reports `installed hooks=2`. The first interception and every hundredth interception are reported as `intercept ad-load count=...` or `intercept ad-layout count=...`, without video titles, video identifiers, or account information. A counter alone does not prove that all ads are blocked.

## Rollback

Disable the module in LSPosed or uninstall **YouTube VR Ad Filter (Test)**, then fully close YouTube VR and reopen it. After disabling the module, you can use `adb shell am force-stop com.google.android.apps.youtube.vr.oculus`. To uninstall the module through ADB, run `adb uninstall local.quest.youtubevr.adfilter`. This does not remove YouTube VR data.

## Implementation and verification

The policy checks the app package, main process, and version, then verifies that both matching methods exist with the exact parameters and a `void` return type before installing any hooks:

- `mhp.m(java.util.List)`
- `mjz.a(java.lang.Object)`

Callbacks stay inactive until both hooks have been registered successfully. If registration fails, installed hooks are removed and any remaining callback stays inactive. The filter returns `null` before executing the two `void` methods, matching the corresponding video-ad path behavior in [NexAlloy](https://github.com/NexAlloy/NexAlloy/tree/be1b44336330ac14431cfc4b7755dd97b3da313a/app/src/main/java/io/github/nexalloy/morphe/youtube/ad). Method names for this app version were identified by matching fingerprint strings in the original APK. This does not install the full NexAlloy module or imply that NexAlloy supports VR.

The verification script covers 12 acceptance and rejection cases for package, process, version, and method signatures, and checks the compiled manifest, Xposed scope, and APK signature. The DEX contains only the module's four classes; the Xposed API library is not bundled. These checks do not run the headset or establish that playback is ad-free.

## Build locally

Source is available in `youtube-vr-adfilter-source.zip`. Requirements: Java, Android SDK platform 34 and build-tools 34.0.0, and Python 3. Set `ANDROID_HOME` if needed, then run `python build.py`. The script downloads Xposed API 82 from its official repository for compilation only and verifies its SHA-256 checksum. It generates a local test key and password inside `build/`; keep both private. Building in a fresh directory produces a different signature, so uninstall a previously signed module before installing that build. Private signing keys are not included in the source archive.

Run `python verify.py` to check the policy and APK. Install `androguard` and `loguru` in your local Python environment first.

This experimental module was built and signed locally. Other YouTube VR versions or different ad paths are not guaranteed to work.
