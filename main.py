import json
import requests
import time
import logging
import telebot

config = json.load(open("config.json", "r"))

logging.basicConfig(filename="all.log", level=logging.INFO)

youtubeApiKeys = config["youtube"]["apiKey"]
youtubeChannelId = config["youtube"]["channelId"]

telegramApiKey = config["telegram"]["apiKey"]
telegramChannelId = config["telegram"]["channelId"]

tgBot = telebot.TeleBot(telegramApiKey)

youtubeApiKey = youtubeApiKeys[0]
qoutaExceededFlag = False
timeoutFlag = True


def postVideoToTelegram(video):
    text = config["postTemplate"]
    text.replace("(%title%)", video["snippet"]["title"].split('|')[0])
    text.replace("(%description%)", video["snippet"]["description"])
    text.replace("(%videoURL%)",
                 "https://www.youtube.com/watch?v=" + video["id"]["videoId"])
    text.replace("(%thumbnailURL%)", video["snippet"]["thumbnails"]["high"])
    tgBot.send_message(chat_id=telegramChannelId, text=text)
    logging.info(
        str(json.dumps({"telegramChannelId": telegramChannelId, "text": text})))

print("Starting!")

while True:
    response = requests.get("https://www.googleapis.com/youtube/v3/search?key=" + youtubeApiKey +
                            "&channelId=" + youtubeChannelId + "&part=snippet,id&order=date&maxResults=2")
    print("https://www.googleapis.com/youtube/v3/search?key=" + youtubeApiKey +
          "&channelId=" + youtubeChannelId + "&part=snippet,id&order=date&maxResults=2")
    ytData = json.loads(response.content)
    if response.status_code == 200:
        video = ytData["items"][0]
        videoId = video["id"]["videoId"]
        lastProcessedVideoId = open('lastProcessedVideoId.txt', 'r').read()
        if video["snippet"]["description"].count('https://vk.me/club179935239') > 0 and lastProcessedVideoId != videoId:
            postVideoToTelegram(video=video)
            open('lastProcessedVideoId.txt', 'w').write(videoId)
            logging.info("New post!")
        timeoutFlag = True
    else:
        logging.error(ytData["error"]["code"])
        logging.error(ytData["error"]["message"])
        for error in ytData["error"]["errors"]:
            logging.error(error["domain"] + ', ' +
                          error["reason"] + ', ' + error["message"])
            if error["reason"] == "qoutaExceeded":
                qoutaExceededFlag = True
        if qoutaExceededFlag:
            logging.info("qoutaExceededFlag")
            if youtubeApiKeyCounter != len(youtubeApiKeys):
                youtubeApiKeyCounter += 1
            else:
                youtubeApiKeyCounter = 0
            youtubeApiKeys[youtubeApiKeyCounter]
            qoutaExceededFlag = False
            timeoutFlag = False
    if timeoutFlag:
        time.sleep(90)
        timeoutFlag = False
