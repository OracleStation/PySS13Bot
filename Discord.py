import discord
import Topic
import math
import pymysql
import yaml
from urllib.parse import parse_qs

with open("config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    eye = "\U0001F441"

    if message.content.startswith(eye) == False:
        return

    explode = message.content.split(' ')

    if explode[0] == "\U0001F441status":
        await client.send_typing(message.channel)
        try:
            topic = Topic.Topic()
            response = parse_qs(topic.send_topic("status"))

            outmsg = "**Gamemode:** " + response["mode"][0] + "\n"
            states = ["Starting Up", "Lobby", "Setting Up", "In Progress", "Finished"]
            outmsg += "**State:** " + states[int(response["gamestate"][0])] + "\n"
            outmsg += "**Admins:** " + response["admins"][0] + "\n"
            outmsg += "**Players:** " + response["active_players"][0] + "\n"

            roundseconds = int(response["round_duration"][0])
            roundhours = 12 + int(math.floor(roundseconds / 3600))
            roundseconds %= 3600
            roundminutes = int(math.floor(roundseconds / 60))
            roundseconds %= 60
            outmsg += "**Time:** {h:02d}:{m:02d}:{s:02d}".format(h=roundhours, m=roundminutes, s=roundseconds)
        except ConnectionError as e:
            outmsg = "Server appears to be down!"

        await client.send_message(message.channel, outmsg)

    if explode[0] == "\U0001F441bwoink" and message.server.id == cfg['discord']['staffserverID']:
        await client.send_typing(message.channel)
        try:
            topic = Topic.Topic()
            outmsg = topic.send_topic("adminmsg=" + explode[1] + "&msg=" + explode[2] + "&sender=" + message.author.name)
        except ConnectionError as e:
            outmsg = "Server appears to be down!"

        await client.send_message(message.channel, outmsg)

    if explode[0] == "\U0001F441notes" and message.server.id == cfg['discord']['staffserverID']: # Check it's in the correct server
        output = ""
        ckey = ""
        if len(explode) == 2:
            ckey = explode[1]
        elif len(explode) > 2:
            ckey = " ".join(explode[1:])
        else:
            output = "No argument specified."
            await client.send_message(message.channel, output)
            return

        db = pymysql.connect(cfg["mysql"]["host"], cfg["mysql"]["user"], cfg["mysql"]["passwd"], cfg["mysql"]["db"])
        try:
            with db.cursor() as cursor:
                query = "SELECT `text`, `timestamp`, `adminckey`, `lasteditor` FROM messages WHERE targetckey LIKE \'" + ckey + "\'"
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    output = "Notes for player " + ckey + "\n\n"
                    for line in result:
                        newnote = "``` " + line[0] + "\n"
                        newnote += "added at " + str(line[1]) + " by " + line[2] + "\n\n"
                        newnote += "```"

                        if len(output + newnote) > 2000:
                            """If the message would be over 2000 characters then output the message and then reset"""
                            await client.send_message(message.channel, output)
                            output = newnote
                        else:
                            output = output + newnote

                else:
                    output = "No results found for " + ckey

        finally:
            await client.send_message(message.channel, output)
            del(cursor)
            db.close()


@client.event
async def on_ready():
    print('SS13 BOT ONLINE')

client.run(cfg["botclient"]["token"])
