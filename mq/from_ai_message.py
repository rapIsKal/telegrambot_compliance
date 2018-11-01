import json


def from_ai_message(payload):
    return json.loads(payload)
"""

{
  "messageId": "2548",
  "uuid":
  {
    "userChannel": "SBERBANK_MESSENGER",
    "userId": "2548",
    "chatId": "2548"
  },
  "ai_version": "02.007.00",
  "messages": [
    {
      "message_name": "OPEN_CHAT",
      "payload":
      {
        "answer": "2018-10-24 00:06:18 : incoming : если я оформлю молодежную карту, она будет именной?",
        "device":
        {
          "client_type": "RETAIL",
          "channel": "MESSENGER_IOS",
          "channel_version": "1",
          "platform_name": "browser",
          "platform_version": "windows"
        },
        "csa_profile_id": 2548
      }
    }
  ]
}


"""