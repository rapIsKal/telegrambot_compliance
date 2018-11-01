

def to_ai_message(messageId, userId, chatId, message, messageName="MESSAGE_FROM_USER", userChannel="SBERBANK_MESSENGER",
                  client_type="client_type", channel="channel",
                  channel_version="channel_version", platform_name="platform_name", platform_version="platform_version",
                  csa_profile_id="csa_profile_id"):
    return {
        "messageId": messageId,
        "messageName": messageName,
        "uuid": {
            "userChannel": userChannel,
            "userId": userId,
            "chatId": chatId
        },
        "payload": {
            "message": message,
            "device": {
                "client_type": client_type,
                "channel": channel,
                "channel_version": channel_version,
                "platform_name": platform_name,
                "platform_version": platform_version
            },
            "csa_profile_id": csa_profile_id
        }
    }
