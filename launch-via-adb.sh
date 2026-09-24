#!/bin/sh
set -eu
# One USB headset connected, USB debugging authorized. No root commands.
adb -d shell am force-stop com.google.android.apps.youtube.vr.oculus
adb -d shell am start -n com.google.android.apps.youtube.vr.oculus/com.google.android.apps.youtube.vr.activities.YouTubeVrActivity
sleep 1
adb -d shell am start -n com.google.android.apps.youtube.vr.oculus/com.google.android.apps.youtube.vr.activities.YouTubeVrActivity
