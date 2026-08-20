package com.nadmit.anonbox;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import com.google.firebase.FirebaseApp;
import com.google.firebase.messaging.FirebaseMessaging;

import org.json.JSONObject;

public class MainActivity extends Activity {
    private static final String HOME_URL = "https://nadmit21-ux.github.io/AnonBox/?app=1";
    private static final String SUPABASE_URL = "https://ugyrgvbfwvmuhsjmjtue.supabase.co";
    private static final String SUPABASE_KEY = "sb_publishable_qHIobQFTgOOrzBttJazZQA_e5-MvmLK";
    private static final String SUPABASE_AUTH_KEY = "sb-ugyrgvbfwvmuhsjmjtue-auth-token";
    private static final String APP_VERSION = "1.2.5";
    private static final int FILE_CHOOSER_REQUEST = 1001;
    private static final int AUDIO_PERMISSION_REQUEST = 1002;

    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private PermissionRequest pendingAudioPermission;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        applyShellTheme("mix");

        NotificationHelper.createChannels(this);
        NotificationHelper.requestPermissionIfNeeded(this);

        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(202, 216, 216));
        webView.addJavascriptInterface(new ThemeBridge(), "AnonBoxThemeBridge");
        setContentView(webView);

        configureWebView();
        refreshFirebaseTokenIfConfigured();
        loadInitialUrl(getIntent());
    }

    private void applyShellTheme(String theme) {
        String selected = theme == null ? "mix" : theme;
        int color;
        boolean darkIcons = true;

        switch (selected) {
            case "blue": color = Color.rgb(200, 215, 229); break;
            case "green": color = Color.rgb(203, 220, 207); break;
            case "gray": color = Color.rgb(207, 212, 218); break;
            case "violet": color = Color.rgb(214, 208, 227); break;
            case "turquoise": color = Color.rgb(197, 220, 218); break;
            case "rose": color = Color.rgb(223, 207, 213); break;
            case "amber": color = Color.rgb(221, 210, 188); break;
            case "ocean": color = Color.rgb(191, 211, 220); break;
            case "forest": color = Color.rgb(197, 211, 197); break;
            case "sand": color = Color.rgb(216, 208, 195); break;
            case "bordeaux": color = Color.rgb(214, 198, 202); break;
            case "night":
                color = Color.rgb(28, 40, 48);
                darkIcons = false;
                break;
            case "mix":
            default:
                color = Color.rgb(202, 216, 216);
                break;
        }

        getWindow().setStatusBarColor(color);
        getWindow().setNavigationBarColor(color);
        getWindow().getDecorView().setSystemUiVisibility(
                darkIcons ? (View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR) : 0
        );
        if (webView != null) webView.setBackgroundColor(color);
    }

    private class ThemeBridge {
        @JavascriptInterface
        public void setTheme(final String theme) {
            runOnUiThread(() -> applyShellTheme(theme));
        }
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setSupportMultipleWindows(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setTextZoom(100);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setUserAgentString(settings.getUserAgentString() + " AnonBoxApp/1.2.5");

        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handleNavigation(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleNavigation(Uri.parse(url));
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                deliverPendingPushToken();
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> {
                    boolean asksAudio = false;
                    for (String resource : request.getResources()) {
                        if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(resource)) {
                            asksAudio = true;
                            break;
                        }
                    }
                    if (!asksAudio) {
                        request.deny();
                        return;
                    }
                    if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                    } else {
                        pendingAudioPermission = request;
                        requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, AUDIO_PERMISSION_REQUEST);
                    }
                });
            }

            @Override
            public void onPermissionRequestCanceled(PermissionRequest request) {
                if (pendingAudioPermission == request) pendingAudioPermission = null;
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallbackNew, FileChooserParams fileChooserParams) {
                if (filePathCallback != null) filePathCallback.onReceiveValue(null);
                filePathCallback = filePathCallbackNew;

                Intent intent;
                try {
                    intent = fileChooserParams.createIntent();
                } catch (Exception ignored) {
                    intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType("*/*");
                    intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, false);
                    intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{
                            "image/jpeg", "image/png", "image/webp", "image/gif",
                            "application/pdf", "text/plain", "application/zip",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            "audio/mpeg", "audio/mp4", "audio/webm", "audio/ogg", "video/mp4"
                    });
                }

                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (ActivityNotFoundException e) {
                    filePathCallback = null;
                    return false;
                }
            }
        });
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != AUDIO_PERMISSION_REQUEST || pendingAudioPermission == null) return;
        PermissionRequest request = pendingAudioPermission;
        pendingAudioPermission = null;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
        } else {
            request.deny();
        }
    }

    private void refreshFirebaseTokenIfConfigured() {
        try {
            if (FirebaseApp.getApps(this).isEmpty()) return;
            FirebaseMessaging.getInstance().getToken().addOnSuccessListener(token -> {
                if (token == null || token.trim().isEmpty()) return;
                PushTokenStore.save(this, token);
                deliverPendingPushToken();
            });
        } catch (Exception ignored) {
            // Firebase can be unavailable temporarily; the token will be retried later.
        }
    }

    private void deliverPendingPushToken() {
        if (webView == null) return;
        String token = PushTokenStore.get(this);
        if (token == null || token.isEmpty()) return;

        String androidId = Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
        if (androidId == null) androidId = "android";

        String script = "(function(){" +
                "if(window.__anonboxPushSyncStarted)return;window.__anonboxPushSyncStarted=true;" +
                "var token=" + JSONObject.quote(token) + ";" +
                "var deviceId=" + JSONObject.quote(androidId) + ";" +
                "var tries=0;" +
                "async function sync(){tries++;try{" +
                "var raw=localStorage.getItem(" + JSONObject.quote(SUPABASE_AUTH_KEY) + ");" +
                "if(!raw)return false;var s=JSON.parse(raw);" +
                "var access=(s&&s.access_token)||(s&&s.currentSession&&s.currentSession.access_token);" +
                "if(!access)return false;" +
                "var r=await fetch(" + JSONObject.quote(SUPABASE_URL + "/rest/v1/rpc/anonbox_register_push_token") + ",{method:'POST',headers:{'Content-Type':'application/json','apikey':" + JSONObject.quote(SUPABASE_KEY) + ",'Authorization':'Bearer '+access},body:JSON.stringify({p_token:token,p_device_id:deviceId,p_app_version:" + JSONObject.quote(APP_VERSION) + "})});" +
                "return r.ok;}catch(e){return false;}}" +
                "sync().then(function(ok){if(ok)return;var timer=setInterval(function(){sync().then(function(done){if(done||tries>=24)clearInterval(timer);});},5000);});" +
                "})();";
        webView.evaluateJavascript(script, null);
    }

    private boolean handleNavigation(Uri uri) {
        if (uri == null) return false;
        String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase();
        String host = uri.getHost() == null ? "" : uri.getHost().toLowerCase();
        String path = uri.getPath() == null ? "" : uri.getPath();

        if (("https".equals(scheme) || "http".equals(scheme))
                && "nadmit21-ux.github.io".equals(host)
                && path.startsWith("/AnonBox/")) return false;

        if ("about".equals(scheme) || "data".equals(scheme) || "blob".equals(scheme)) return false;

        Intent external = new Intent(Intent.ACTION_VIEW, uri);
        try {
            startActivity(external);
        } catch (ActivityNotFoundException ignored) {
            if ("intent".equals(scheme)) {
                try {
                    Intent fallback = Intent.parseUri(uri.toString(), Intent.URI_INTENT_SCHEME);
                    startActivity(fallback);
                } catch (Exception ignoredAgain) {
                    // No compatible external application.
                }
            }
        }
        return true;
    }

    private void loadInitialUrl(Intent intent) {
        Uri data = intent == null ? null : intent.getData();
        if (data != null
                && "https".equalsIgnoreCase(data.getScheme())
                && "nadmit21-ux.github.io".equalsIgnoreCase(data.getHost())
                && data.getPath() != null
                && data.getPath().startsWith("/AnonBox/")) {
            webView.loadUrl(data.toString());
        } else {
            webView.loadUrl(HOME_URL);
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        loadInitialUrl(intent);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != FILE_CHOOSER_REQUEST || filePathCallback == null) return;

        Uri[] results = null;
        if (resultCode == RESULT_OK && data != null) {
            if (data.getClipData() != null) {
                int count = data.getClipData().getItemCount();
                results = new Uri[count];
                for (int i = 0; i < count; i++) results[i] = data.getClipData().getItemAt(i).getUri();
            } else if (data.getData() != null) {
                results = new Uri[]{data.getData()};
            }
        }

        filePathCallback.onReceiveValue(results);
        filePathCallback = null;
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        if (pendingAudioPermission != null) {
            pendingAudioPermission.deny();
            pendingAudioPermission = null;
        }
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }
}
