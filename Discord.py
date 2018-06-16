import discord
import Topic
import math
import pymysql
import yaml
from ipaddress import IPv4Address
from urllib.parse import parse_qs

with open("config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

client = discord.Client()

"""SQL Connection stuff"""

async def queryMySql(query):
    db = pymysql.connect(cfg["mysql"]["host"], cfg["mysql"]["user"], cfg["mysql"]["passwd"], cfg["mysql"]["db"])
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    finally:
        del(cursor)
        db.close()
        return result

async def staffServerCheck(id):
    if id == cfg['discord']['staffserverID']:
        return True
    else:
        return False

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

    if explode[0] == "\U0001F441notes" and await staffServerCheck(message.server.id):  # Check it's in the correct server
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

        query = "SELECT `text`, `timestamp`, `adminckey`, `lasteditor` FROM messages WHERE targetckey LIKE \'{0}\'".format(ckey)
        result = await queryMySql(query)
        if result:
            output = "Notes for player " + ckey + "\n\n"
            for line in result:
                newnote = "```" + line[0] + "\n"
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

        await client.send_message(message.channel, output)

    if explode[0] == "\U0001F441info" and await staffServerCheck(message.server.id):
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

        query = "SELECT `accountjoindate`, `firstseen`, `lastseen`, `computerid`, `ip` FROM player WHERE ckey LIKE \'{0}\';".format(ckey)
        result = await queryMySql(query)

        if result:
            output = "Player information for **{0}**:\n\n".format(ckey)
            for line in result:
                ip = IPv4Address(line[5])
                output += "```Join Date: {0}\nFirst Seen: {1}\nLast Seen: {2}\nComputer ID: {3}\nIP: {4} ({5})```".format(line[0], line[1], line[2], line[3], ip, line[4])
                return await client.send_message(message.channel, output)
        else:
            return await client.send_message(message.channel, "No result found for {0}".format(ckey))

    if explode[0] == "\U0001F441searchban" and await staffServerCheck(message.server.id):
        output = ""
        ckey = ""
        if len(explode) == 2:
            ckey = explode[1]
        elif len(explode) > 2:
            ckey = " ".join(explode[1:])
        else:
            output = "No argument specified."
            return await client.send_message(message.channel, output)

        query = "SELECT `bantype`, `bantime`, `expiration_time`, `computerid`, `ip`, `adminwho`,`unbanned`,`unbanned_datetime`, `duration`, `reason` FROM ban WHERE ckey LIKE \'{0}\';".format(ckey)
        result = await queryMySql(query)
        if result:
            output = "Ban information for **{0}**:\n\n".format(ckey)
            for line in result:
                if len(output) > 1500:
                    await client.send_message(message.channel, output)
                    output = ""
                output += "```Ban Type: {0} duration {1} minutes placed by {2} on {3}.\n".format(line[0], line[8], line[5], line[1])
                output += "Expiry Time: {0}\n".format(line[2])
                output += "Reason: {0}\n".format(line[9])
                output += "Unbanned: {0} {1}\n```".format("YES at" if str(line[6]) == "1" else "NO", line[7] if str(line[6]) == "1" else "")
            return await client.send_message(message.channel, output)


@client.event
async def on_ready():
    print('SS13 BOT ONLINE')

client.run(cfg["botclient"]["token"])
