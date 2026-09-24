First release of the ad filter for YouTube VR 1.87.13 on Meta Quest (ARM64).

There are two downloads to choose from:

- **Standalone APK** — the patch is built into the app, so it does not need the LSPosed module. Uninstall the official YouTube VR app first, since the signatures are different. This clears its local data, so you may need to sign in again.
- **LSPosed/Vector module** — use this with the official YouTube VR app if your headset is rooted. It only supports version 1.87.13.

The standalone APK is working on a Quest 3: it opens straight from the headset library, and no ads showed up during use. That headset is rooted, but the module was removed for this test. It still needs testing on a headset without root, and 360° playback has not been checked separately yet.

Source for the module, public signing certificates, and SHA-256 checksums are included below. See the [README](https://github.com/Akramx15/youtube-vr-adfilter#readme) for setup instructions and how to switch back to the official app.
