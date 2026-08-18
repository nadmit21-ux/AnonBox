package com.nadmit.anonbox;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.net.Uri;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class AnonBoxMessagingService extends FirebaseMessagingService {

    @Override
    public void onNewToken(String token) {
        super.onNewToken(token);
        PushTokenStore.save(this, token);
    }

    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        NotificationHelper.createChannels(this);

        String title = "Nouveau message AnonBox";
        String body = "Tu as reçu un nouveau message.";
        String conversationId = remoteMessage.getData().get("conversation_id");

        if (remoteMessage.getNotification() != null) {
            if (remoteMessage.getNotification().getTitle() != null
                    && !remoteMessage.getNotification().getTitle().trim().isEmpty()) {
                title = remoteMessage.getNotification().getTitle();
            }
            if (remoteMessage.getNotification().getBody() != null
                    && !remoteMessage.getNotification().getBody().trim().isEmpty()) {
                body = remoteMessage.getNotification().getBody();
            }
        }
        if (remoteMessage.getData().get("body") != null
                && !remoteMessage.getData().get("body").trim().isEmpty()) {
            body = remoteMessage.getData().get("body");
        }

        String url = "https://nadmit21-ux.github.io/AnonBox/?app=1";
        if (conversationId != null && !conversationId.trim().isEmpty()) {
            url += "&chat=" + Uri.encode(conversationId.trim());
        }

        Intent openIntent = new Intent(this, MainActivity.class);
        openIntent.setAction(Intent.ACTION_VIEW);
        openIntent.setData(Uri.parse(url));
        openIntent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);

        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                conversationId == null ? 0 : conversationId.hashCode(),
                openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification notification = new Notification.Builder(this, NotificationHelper.CHANNEL_MESSAGES)
                .setSmallIcon(R.drawable.ic_launcher)
                .setContentTitle(title)
                .setContentText(body)
                .setStyle(new Notification.BigTextStyle().bigText(body))
                .setAutoCancel(true)
                .setContentIntent(pendingIntent)
                .build();

        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager != null) {
            int id = (conversationId == null || conversationId.isEmpty())
                    ? (int) (System.currentTimeMillis() & 0x7fffffff)
                    : conversationId.hashCode();
            manager.notify(id, notification);
        }
    }
}
