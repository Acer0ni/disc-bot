import re
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()

W2G_TOKEN = os.getenv('W2G_TOKEN')
W2G_ROOM = os.getenv('W2G_ROOM')

class Watch2Gether(commands.Cog):
    """
    A suite of commands to help watch videos with friends.
    """
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name="create")
    async def W2G_create_room(self,ctx,args):
        """Creates a room at watch2gether.tv to watch videos with your friends."""
        with open('Data/W2G_Data.json') as json_file:
            data = json.load(json_file)
        share = args
        author = str(ctx.message.author)
        if author in data:
            await ctx.send(f"You already have a room created. Your url is https://w2g.tv/rooms/{data[author]} ")
            return
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "w2g_api_key": W2G_TOKEN,
            "share": share,
            "bg_color": "#00ff00",
            "bg_opacity": "50"
        }
        response = requests.post("https://w2g.tv/rooms/create.json",headers = headers,data=json.dumps(payload))
        if response.status_code == 200:
            content = json.loads(response.content)
            data[author] = content['streamkey']
            json_string = json.dumps(data)
            with open('Data/W2G_data.json','w') as outfile:
                outfile.write(json_string)
            await ctx.send(f"Here is your room! https://w2g.tv/rooms/{content['streamkey']}")
        else:
            await ctx.send("Something went wrong, please try again.")

    @commands.command(name='play')
    async def W2G_Play(self,ctx,url):
        """
        Plays a video immediately in your personal room, and will create one for you if you don't have one.
        !play  {video url}
        """
        with open('Data/W2G_Data.json') as json_file:
            data = json.load(json_file)
        author = str(ctx.message.author)
        if author not in data:
            await Watch2Gether.W2G_create_room(self,ctx,url)
            return
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "w2g_api_key": W2G_TOKEN,
            "item_url" : url
        }
        response = requests.post(f"https://w2g.tv/rooms/{data[author]}/sync_update",headers = headers,data=json.dumps(payload))
        if response.status_code == 200:
            await ctx.send("Your video is now playing.")
            await ctx.send(f"Here is your link! https://w2g.tv/rooms/{data[author]}")
        else:
            await ctx.send("Something went wrong, please try again.")

    #use *args to make titles optional
    @commands.command(name='add')
    async def W2G_add(self,ctx,url,title = "none"):
        """
        Add a video to the queue of your personal room. If you do not have a room,it creates one and plays the video for you.
        !add {video url} {title}(optional)
        """
        with open('Data/W2G_Data.json') as json_file:
            data = json.load(json_file)
        author = str(ctx.message.author)
        if author not in data:
            await Watch2Gether.W2G_create_room(self,ctx,url)
            return
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "w2g_api_key": W2G_TOKEN,
            "add_items": [{"url": url, "title": title}],
        }
        response = requests.post(f"https://w2g.tv/rooms/{data[author]}/playlists/current/playlist_items/sync_update",headers = headers,data=json.dumps(payload))
        if response.status_code == 200:
            await ctx.send("Your video is now queued.")
            await ctx.send(f"Here is your link! https://w2g.tv/rooms/{data[author]}")
        else:
            await ctx.send("Something went wrong, please try again.")

