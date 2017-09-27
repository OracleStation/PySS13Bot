import discord
import Topic
import math
from urllib.parse import parse_qs

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    eye = "\U0001F441"

    if message.content.startswith(eye) == False:
        return

    explode = message.content.split(' ', 2)

    if explode[0] == "\U0001F441status":
        await client.send_typing(message.channel)
        try:
            topic = Topic.Topic()
            response = parse_qs(topic.send_topic("status"))

            outmsg = "**Version:** " + response["version"][0] + "\n"
            outmsg += "**Gamemode:** " + response["mode"][0] + "\n"
            states = ["Starting Up", "Lobby", "Setting Up", "In Progress", "Finished"]
            outmsg += "**State:** " + states[int(response["gamestate"][0])] + "\n"
            outmsg += "**Players:** " + response["admins"][0] + "\n"
            outmsg += "**Admins:** " + response["active_players"][0] + "\n"

            roundseconds = int(response["round_duration"][0])
            roundhours = 12 + int(math.floor(roundseconds / 3600))
            roundseconds %= 3600
            roundminutes = int(math.floor(roundseconds / 60))
            roundseconds %= 60
            outmsg += "**Time:** {h:02d}:{m:02d}:{s:02d}".format(h=roundhours, m=roundminutes, s=roundseconds)
        except ConnectionError as e:
            outmsg = "Server appears to be down!"

        await client.send_message(message.channel, outmsg)

    if explode[0] == "\U0001F441bwoink":
        await client.send_typing(message.channel)
        try:
            topic = Topic.Topic()
            outmsg = topic.send_topic("adminmsg=" + explode[1] + "&msg=" + explode[2] + "&sender=" + message.author.name)
        except ConnectionError as e:
            outmsg = "Server appears to be down!"

        await client.send_message(message.channel, outmsg)

@client.event
async def on_ready():
    print('SS13 BOT ONLINE')

client.run('')
