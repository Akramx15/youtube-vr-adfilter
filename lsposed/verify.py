#!/usr/bin/env python3
"""Contract, bytecode, manifest, and signature checks; no device interaction."""
from pathlib import Path
import os, subprocess, sys, zipfile
ROOT=Path(__file__).resolve().parent
TEST=ROOT/'build'/'checks'
TEST.mkdir(parents=True,exist_ok=True)
def run(args):
    print('+',' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True)
fixtures={
 'good':('public void m(java.util.List<?> x) {}','public void a(Object x) {}'),
 'bad_return':('public void m(java.util.List<?> x) {}','public int a(Object x) { return 0; }'),
 'bad_parameter':('public void m(String x) {}','public void a(Object x) {}'),
 'bad_static':('public static void m(java.util.List<?> x) {}','public void a(Object x) {}'),
}
for name,(m,a) in fixtures.items():
    folder=TEST/name; folder.mkdir(exist_ok=True)
    (folder/'mhp.java').write_text('public class mhp { '+m+' }')
    (folder/'mjz.java').write_text('public class mjz { '+a+' }')
    run(['javac','--release','8','-d',folder,folder/'mhp.java',folder/'mjz.java'])
(TEST/'PolicyTest.java').write_text('''
import java.net.URLClassLoader;
import java.io.File;
import java.lang.reflect.Method;
import local.quest.youtubevr.adfilter.TargetPolicy;
public class PolicyTest {
  private static void check(boolean ok, String message) {
    if (!ok) throw new AssertionError(message);
    System.out.println("PASS: " + message);
  }
  public static void main(String[] args) throws Exception {
    String p=TargetPolicy.PACKAGE;
    check(TargetPolicy.acceptsProcess(p,p), "exact package and main process accepted");
    check(!TargetPolicy.acceptsProcess("com.google.android.youtube",p), "ordinary YouTube rejected");
    check(!TargetPolicy.acceptsProcess(p,p+":service"), "secondary process rejected");
    check(!TargetPolicy.acceptsProcess(null,null), "missing package rejected");
    check(TargetPolicy.acceptsVersion("1.87.13",18713000L), "exact version accepted");
    check(!TargetPolicy.acceptsVersion("1.87.14",18713000L), "wrong version name rejected");
    check(!TargetPolicy.acceptsVersion("1.87.13",18713001L), "wrong version code rejected");
    check(!TargetPolicy.acceptsVersion(null,18713000L), "missing version rejected");
    for (String name: new String[] {"good","bad_return","bad_parameter","bad_static"}) {
      try (URLClassLoader loader = new URLClassLoader(new java.net.URL[] {new File(args[0], name).toURI().toURL()},null)) {
        boolean resolved=false;
        try {
          Method[] methods=TargetPolicy.resolveTargets(loader);
          resolved=methods.length==2 && methods[0].getReturnType()==Void.TYPE && methods[1].getReturnType()==Void.TYPE;
        } catch (ReflectiveOperationException expected) {}
        check(resolved == name.equals("good"), "reflection contract " + name);
      }
    }
  }
}
''')
run(['javac','--release','8','-classpath',ROOT/'build'/'classes','-d',TEST,TEST/'PolicyTest.java'])
run(['java','-classpath',str(TEST)+os.pathsep+str(ROOT/'build'/'classes'),'PolicyTest',TEST])
from loguru import logger
logger.remove()
from androguard.core.apk import APK
from androguard.core.dex import DEX
apkpath=ROOT/'build'/'youtube-vr-adfilter-test.apk'
apk=APK(str(apkpath)); ns='{http://schemas.android.com/apk/res/android}'
assert apk.get_package()=='local.quest.youtubevr.adfilter'
assert not apk.get_permissions(),apk.get_permissions()
assert not apk.get_activities() and not apk.get_services() and not apk.get_receivers() and not apk.get_providers()
print('PASS: package, no requested permissions, no app components')
manifest=apk.get_android_manifest_xml()
meta={e.get(ns+'name'):e for e in manifest.findall('.//meta-data')}
assert meta['xposedmodule'].get(ns+'value')=='true'
assert meta['xposedminversion'].get(ns+'value')=='82'
assert meta['xposedscope'].get(ns+'resource')
with zipfile.ZipFile(apkpath) as z:
    assert z.read('assets/xposed_init').decode().strip()=='local.quest.youtubevr.adfilter.HookEntry'
    d=DEX(z.read('classes.dex'))
    classes=[c.get_name() for c in d.get_classes()]
    assert len(classes)==4,classes
    assert all(c.startswith('Llocal/quest/youtubevr/adfilter/') for c in classes),classes
    assert not any(c.startswith('Lde/robv/android/xposed/') for c in classes)
print('PASS: Xposed init, scope metadata, four production classes, compile-only API not bundled')
sdk=Path(os.environ.get('ANDROID_HOME',str(Path.home() / 'Android' / 'Sdk')))/'build-tools'/'34.0.0'
resources=subprocess.check_output([str(sdk/'aapt2'),'dump','resources',str(apkpath)],text=True)
(TEST/'resources.txt').write_text(resources)
assert 'xposed_scope' in resources and 'com.google.android.apps.youtube.vr.oculus' in resources
print('PASS: compiled recommended scope contains only VR package (one-item source array)')
run([sdk/'apksigner','verify','--verbose',apkpath])
print('ALL STATIC CHECKS PASSED; runtime ad removal and 360 playback NOT tested by this script.')
