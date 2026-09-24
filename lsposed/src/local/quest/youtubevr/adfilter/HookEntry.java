package local.quest.youtubevr.adfilter;

import android.app.Application;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.os.Build;
import java.lang.reflect.Method;
import java.util.concurrent.atomic.AtomicLong;
import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

/** Experimental ad suppression only. No UI, network, filesystem, or account operations. */
public final class HookEntry implements IXposedHookLoadPackage {
    private static final String TAG = "[YT_VR_AD_FILTER] ";
    private static boolean attempted;
    private static volatile boolean armed;

    @Override
    public void handleLoadPackage(final LoadPackageParam loaded) {
        if (!TargetPolicy.acceptsProcess(loaded.packageName, loaded.processName)) return;
        try {
            Method attach = Application.class.getDeclaredMethod("attach", Context.class);
            XposedBridge.hookMethod(attach, new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    if (param.hasThrowable()) return;
                    Context context = (Context) param.args[0];
                    if (!TargetPolicy.PACKAGE.equals(context.getPackageName())) return;
                    installOnce(context, loaded.classLoader);
                }
            });
            XposedBridge.log(TAG + "waiting for application attach; experimental filter");
        } catch (Throwable error) {
            logSkipped("application attach unavailable", error);
        }
    }

    private static synchronized void installOnce(Context context, ClassLoader loader) {
        if (attempted) return;
        attempted = true;
        XC_MethodHook.Unhook first = null;
        XC_MethodHook.Unhook second = null;
        try {
            PackageInfo info = context.getPackageManager().getPackageInfo(TargetPolicy.PACKAGE, 0);
            long code = Build.VERSION.SDK_INT >= 28 ? info.getLongVersionCode() : info.versionCode;
            if (!TargetPolicy.acceptsVersion(info.versionName, code)) {
                XposedBridge.log(TAG + "skipped: unsupported app version; installed hooks=0");
                return;
            }
            // Resolve and validate BOTH exact void methods before registering either hook.
            Method[] targets = TargetPolicy.resolveTargets(loader);
            first = XposedBridge.hookMethod(targets[0], suppress("ad-load"));
            second = XposedBridge.hookMethod(targets[1], suppress("ad-layout"));
            // Callbacks are inert until both registrations have succeeded.
            armed = true;
            XposedBridge.log(TAG + "installed hooks=2; supported version 1.87.13/18713000");
        } catch (Throwable error) {
            armed = false;
            unhookSafely(second);
            unhookSafely(first);
            logSkipped("compatibility or hook registration failed", error);
        }
    }

    private static XC_MethodHook suppress(final String category) {
        final AtomicLong counter = new AtomicLong();
        return new XC_MethodHook() {
            @Override
            protected void beforeHookedMethod(MethodHookParam param) {
                if (!armed) return;
                param.setResult(null);
                long count = counter.incrementAndGet();
                if (count == 1 || count % 100 == 0) {
                    XposedBridge.log(TAG + "intercept " + category + " count=" + count);
                }
            }
        };
    }

    private static void unhookSafely(XC_MethodHook.Unhook hook) {
        if (hook == null) return;
        try {
            hook.unhook();
        } catch (Throwable ignored) {
            // Any callback left registered remains inert because armed is false.
        }
    }

    private static void logSkipped(String reason, Throwable error) {
        // Never log arguments, video IDs, account values, URLs, or exception messages.
        XposedBridge.log(TAG + "skipped: " + reason + "; installed hooks=0; error="
                + error.getClass().getSimpleName());
    }
}
