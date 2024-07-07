const express = require("express");
const axios = require("axios");
const path = require("path");
const { Telegraf } = require("telegraf");
require("dotenv").config();

// Creating Server
const App = express();
const PORT = process.env.PORT || 3000;

App.use(express.static("static"));
App.use(express.json());
App.get("/", (req, res) => {
  res.sendFile(path.join(__dirname + "/index.html"));
});

// Bot Functions
const bot = new Telegraf(process.env.BOT_TOKEN);

bot.command("start", (ctx) => {
  console.log(ctx.from.id);
  const reply = "Welcome to LU Bot.\nFor all commands click /help.";
  bot.telegram.sendMessage(ctx.chat.id, reply, {});
});

bot.command("help", (ctx) => {
  //   axios.get(url).then((response) => {
  //     rate = response.data.ethereum;
  //   });
  const reply = `Hello, today the ethereum price`;
  bot.telegram.sendMessage(ctx.chat.id, reply, {});
});

// Start the server
// App.use(bot.webhookCallback('/secret-path'))
// bot.telegram.setWebhook('<YOUR_CAPSULE_URL>/secret-path')
bot.launch();
// App.listen(PORT, () => console.log(`Server is running on ${PORT}`));
