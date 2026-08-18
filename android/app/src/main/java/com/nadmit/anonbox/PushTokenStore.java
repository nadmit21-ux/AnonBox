package com.nadmit.anonbox;

import android.content.Context;
import android.content.SharedPreferences;

public final class PushTokenStore {
    private static final String PREFS = "anonbox_push";
    private static final String KEY_TOKEN = "fcm_token";

    private PushTokenStore() {}

    public static void save(Context context, String token) {
        if (token == null || token.trim().isEmpty()) return;
        prefs(context).edit().putString(KEY_TOKEN, token.trim()).apply();
    }

    public static String get(Context context) {
        return prefs(context).getString(KEY_TOKEN, "");
    }

    public static void clear(Context context) {
        prefs(context).edit().remove(KEY_TOKEN).apply();
    }

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }
}
