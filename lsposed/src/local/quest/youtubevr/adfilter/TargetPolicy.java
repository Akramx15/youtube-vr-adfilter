package local.quest.youtubevr.adfilter;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.List;

/** Narrow compatibility contract; never guess after a YouTube VR update. */
public final class TargetPolicy {
    public static final String PACKAGE = "com.google.android.apps.youtube.vr.oculus";
    public static final String VERSION_NAME = "1.87.13";
    public static final long VERSION_CODE = 18713000L;

    private TargetPolicy() {}

    public static boolean acceptsProcess(String packageName, String processName) {
        return PACKAGE.equals(packageName) && PACKAGE.equals(processName);
    }

    public static boolean acceptsVersion(String versionName, long versionCode) {
        return VERSION_NAME.equals(versionName) && versionCode == VERSION_CODE;
    }

    public static Method[] resolveTargets(ClassLoader loader) throws ReflectiveOperationException {
        Method loadAds = Class.forName("mhp", false, loader).getDeclaredMethod("m", List.class);
        Method adLayout = Class.forName("mjz", false, loader).getDeclaredMethod("a", Object.class);
        for (Method method : new Method[] {loadAds, adLayout}) {
            if (method.getReturnType() != Void.TYPE || Modifier.isStatic(method.getModifiers())) {
                throw new NoSuchMethodException("Unexpected ad hook signature");
            }
        }
        return new Method[] {loadAds, adLayout};
    }
}
