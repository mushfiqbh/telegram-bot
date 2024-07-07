import pandas as pd
import requests
import re

API_TOKEN = "6490263020:AAEF8s0e5Or12ykfibVRU9XWMpCQAiGpEX4"
base_url = "https://api.telegram.org/bot"+API_TOKEN


gsheet = "https://docs.google.com/spreadsheets/d/1SnpCguD2r9wx174A7uytZEJeWanzHwR6wIyonX9TWtw"


def convert_gsheet_to_tsv(url):
  pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
  def replacement(m):
    return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?" + \
    (f"gid={m.group(3)}&" if m.group(3) else "") + "format=tsv"
  return re.sub(pattern, replacement, url)

 
def fetch_gsheet(question,  column):
  url = convert_gsheet_to_tsv(gsheet)
  df = pd.read_csv(url, sep="\t")

  answer = df.loc[df[column].astype(str).str.lower().str.contains(question.lower())]
  if not answer.empty:
    res = []
    for col_index in answer.columns:
      res.append(answer.iloc[0][col_index])

    return res


def adressing(reply, props):
  repl = {
    "%uid": f"{props['user_id']}",
    "%un": f"{props['username']}",
    "%fn": f"{props['first_name']}",
    "%ln": f"{props['last_name']}"
  }
  if "%" in reply:
    for key, value in repl.items():
      if key in reply:
        reply = reply.replace(key, value)
  return reply


def auto_reply(reply, props):
  reply = adressing(reply, props)
  
  data = {
    "chat_id": props["chat_id"],
    "text": reply
  }
  
  requests.get(base_url + "/sendMessage", data)


def start(props):
  reply = "\n".join([f"Welcome {props['first_name']} {props['last_name']}🤗",\
"You can message me anything, I will be try to do follow up conversation.","",\
"Type /help to see the list of commands"])
  auto_reply(reply, props)


def help(props):
  reply = "\n".join(["Available commands:", "/start - Start the bot", "/help - Show the\
 list of commands", "/echo - Repeat the message", "/docs - Get your info by ID"])
  auto_reply(reply, props)


def chatbot(message, props):
  res = fetch_gsheet(message,  'Question')
  reply = res[1] if res else "Sorry, I could not understand you."
  auto_reply(reply, props)


def terminal(command, props):
  if command.startswith("/"):
    if command == "/start":
      start(props)
    elif command == "/help":
      help(props)
    else:
      auto_reply("Unknown Command /help", props)
  else:
    chatbot(command, props)
  print(props['chat_id'])


def read_msg(offset):
  parameters = {"offset": offset}
  resp = requests.get(base_url + "/getUpdates", data=parameters)
  data = resp.json()
  
  for result in data["result"]:
    if "message" in result and "text" in result["message"]:
      
      text = result["message"]["text"]
      msg_id = result["message"]["message_id"]
      chat_id = result["message"]["chat"]["id"]
      fromProps = result["message"]["from"];
      user_id = fromProps.get("id", "")
      username = fromProps.get("username", "")
      first_name = fromProps.get("first_name", "")
      last_name = fromProps.get("last_name", "")
      props = {
        "msg_id": msg_id,
        "user_id": user_id,
        "chat_id": chat_id, 
        "username":username,
        "first_name": first_name, 
        "last_name": last_name
      }
 
      terminal(text, props)
    else:
      print("Message format is invalid or missing 'text' field.")
  
  if data["result"]:
    return data["result"][-1]["update_id"] + 1


offset = 0
while True:
  offset = read_msg(offset)

