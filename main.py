import pandas as pd
import time
from os import path
import json
import glob
import socket
import pyperclip
import subprocess
import os

def getAbsPath(relPath):
    basepath = path.dirname(__file__)
    fullPath = path.abspath(path.join(basepath, relPath))

    return fullPath


def getConfig():
    configFileName = getAbsPath("./config.json")
    with open(configFileName) as config:
        config = json.loads(config.read())

    return config


def getMsgText(message):
    msgTextFinal = ""
    if type(message["text"]) == list:
        for segment in message["text"]:
            if type(segment) == str:
                msgTextFinal += (" " + segment)
            elif type(segment) == dict and "text" in segment and segment["type"] == "link":
                msgTextFinal += (' <a href="' + segment["text"] + '" >' + segment["text"] + "</a> ")
    else:
        msgTextFinal = message["text"]
    return msgTextFinal

def createHtmlFromCSV(convo):
    html = """
    <html>
    <head>
    <style>
    </style>
    </head>
    <body>
    """
    for message in convo["messages"]:
        replyToText = ""
        msgText = getMsgText(message)
        
        if "reply_to_message_id" in message:
            replyToId = message["reply_to_message_id"]
            replyToMessage = getMsgText([m for m in convo["messages"] if m["id"] == replyToId][0])
            replyToText = "  [[Reply to:]] " + replyToMessage
        html += "<p>" + message["from"] + ": " + msgText + replyToText + "</p><br>"
    html += """
    </table>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    config = getConfig()
    inputDir, outputDir = config["inputDir"], config["outputDir"]
    chatExports = glob.glob(inputDir + "/ChatExport*/result.json")
    for jsonFilePath in chatExports:
        convo = json.loads(open(jsonFilePath).read())
        convoName = convo["name"] + str(convo["id"])
        htmlFilePath = outputDir + convoName + ".html"
        html = createHtmlFromCSV(convo)
        with open(htmlFilePath, "w") as f:
            f.write(html)
        if config["htmlFolderUrl"]:
            hostname = socket.gethostname()
            localIP = socket.gethostbyname(hostname)
            urlToOpen = config["htmlFolderUrl"].replace("localhost", localIP) + convoName + ".html"
            pyperclip.copy(urlToOpen)
        else:
            urlToOpen = htmlFilePath
        os.remove(jsonFilePath)
        subprocess.run(["xdg-open", urlToOpen])
        