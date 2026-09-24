#!/usr/bin/env python3
"""Build locally using Android SDK tools and javac; no Gradle or global changes."""
from pathlib import Path
import hashlib, os, subprocess, urllib.request, zipfile, secrets
ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
DEPS = ROOT / 'deps'
SDK = Path(os.environ.get('ANDROID_HOME', str(Path.home() / 'Android' / 'Sdk')))
TOOLS = SDK / 'build-tools' / '34.0.0'
ANDROID = SDK / 'platforms' / 'android-34' / 'android.jar'
JAR = DEPS / 'xposed-api-82.jar'
JAR_URL = 'https://api.xposed.info/de/robv/android/xposed/api/82/api-82.jar'
JAR_SHA = 'f48c635f1c7469fdec0e00ad2ea0b7a6b2f5b55065784a35b7ca3a84615e8e25'
for folder in [BUILD, DEPS, BUILD/'classes', BUILD/'dex']: folder.mkdir(parents=True, exist_ok=True)
def run(args):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), check=True, cwd=ROOT)
if not JAR.exists(): urllib.request.urlretrieve(JAR_URL, JAR)
assert hashlib.sha256(JAR.read_bytes()).hexdigest() == JAR_SHA, 'Compile-only Xposed API hash mismatch'
run([TOOLS/'aapt2', 'compile', '--dir', ROOT/'res', '-o', BUILD/'resources.zip'])
run([TOOLS/'aapt2', 'link', '-o', BUILD/'unsigned.apk', '-I', ANDROID, '--manifest', ROOT/'AndroidManifest.xml', BUILD/'resources.zip', '-A', ROOT/'assets', '--min-sdk-version', '26', '--target-sdk-version', '34'])
run(['javac', '--release', '8', '-parameters', '-Xlint:deprecation', '-classpath', str(ANDROID)+os.pathsep+str(JAR), '-d', BUILD/'classes', *sorted((ROOT/'src').rglob('*.java'))])
run([TOOLS/'d8', '--min-api', '26', '--lib', ANDROID, '--classpath', JAR, '--output', BUILD/'dex', *sorted((BUILD/'classes').rglob('*.class'))])
with zipfile.ZipFile(BUILD/'unsigned.apk', 'a', zipfile.ZIP_DEFLATED) as apk:
    apk.write(BUILD/'dex'/'classes.dex', 'classes.dex')
run([TOOLS/'zipalign', '-f', '4', BUILD/'unsigned.apk', BUILD/'aligned.apk'])
KEY = BUILD/'test-signing.jks'
PASSWORD = BUILD/'signing-password.txt'
if not PASSWORD.exists():
    with PASSWORD.open('x') as f: f.write(secrets.token_urlsafe(32))
    PASSWORD.chmod(0o600)
if not KEY.exists():
    run(['keytool', '-genkeypair', '-keystore', KEY, '-storepass:file', PASSWORD, '-keypass:file', PASSWORD, '-alias', 'youtube-vr-test', '-dname', 'CN=Local YouTube VR Test', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '3650'])
run([TOOLS/'apksigner', 'sign', '--ks', KEY, '--ks-key-alias', 'youtube-vr-test', '--ks-pass', 'file:'+str(PASSWORD), '--out', BUILD/'youtube-vr-adfilter-test.apk', BUILD/'aligned.apk'])
run([TOOLS/'apksigner', 'verify', '--verbose', '--print-certs', BUILD/'youtube-vr-adfilter-test.apk'])
print('APK SHA256:', hashlib.sha256((BUILD/'youtube-vr-adfilter-test.apk').read_bytes()).hexdigest())
