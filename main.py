import asyncio
from secrets import bot_token, spotify_client_id, spotify_client_secret

import discord
import discord.ext.commands
import spotipy
import validators
import youtube_dl
from spotipy.oauth2 import SpotifyClientCredentials

import spotify_link_handler
import musicbot


class AgeRestrictedException(Exception):
    pass


if __name__ == "__main__":
    ccm = SpotifyClientCredentials(
        client_id=spotify_client_id, client_secret=spotify_client_secret
    )
    spotify_instance = spotipy.Spotify(client_credentials_manager=ccm)
    ytdl_options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "forceurl": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    bot = musicbot.MusicBot(None, [], None, None,  False, ytdl_options, spotify_instance, command_prefix="-")

    @bot.event
    async def on_ready():
        print(f"{bot.user} has connected to discord!")

    @bot.command(aliases=["j"])
    async def join(ctx, bot=bot):
        bot.voice_client = await ctx.message.author.voice.channel.connect(reconnect=True)
        print(f"Bot connected to voicechannel: \"{ctx.message.author.voice.channel.name}\"!")
        await ctx.message.add_reaction("👍")

    @bot.command(aliases=["bye"])
    async def leave(ctx, bot=bot):
        await bot.voice_client.disconnect()
        print("Bot disconnected!")
        await ctx.message.add_reaction("👍")

    @bot.command(aliases=["pp"])
    async def pause(ctx, bot=bot):
        bot.voice_client.pause()
        print("Music paused!")
        await ctx.message.add_reaction("👍")
        await ctx.channel.send("Paused!")

    @bot.command(aliases=["r"])
    async def resume(ctx, bot=bot):
        bot.voice_client.resume()
        print("Music resumed!")
        await ctx.message.add_reaction("👍")
        await ctx.channel.send("Resumed!")

    @bot.command(aliases=["l"])
    async def loop(ctx, bot=bot):
        if bot.looping:
            await ctx.channel.send("No longer looping!")
            print("Looping turned on!")
        else:
            await ctx.channel.send("You are now looping!")
            print("Looping turned off!")
        bot.looping = not bot.looping
        await ctx.message.add_reaction("👍")

    @bot.command(aliases=["s"])
    async def skip(ctx, bot=bot, silent=False):
        #error for no reason
        try:
            await bot.voice_client.stop()
        except TypeError:
            pass
        if silent is False:
            print("Song skipped!")
            await ctx.channel.send("Skipped!")
            await ctx.message.add_reaction("👍")
        playlist_handler(ctx)

    @bot.command(aliases=["np"])
    async def nowplaying(ctx, bot=bot):
        print("Sent current song!")
        await ctx.channel.send(f"Now playing: {bot.nowplaying}")

    @bot.command(aliases=["cp"])
    async def current_playlist(ctx, bot=bot):
        if len(bot.playlist) != 0:
            await ctx.channel.send(f"Current playlist: {bot.playlist}")
            print("Sent current playlist!")
        else:
            await ctx.channel.send("Playlist is empty!")
            print("Sent empty playlist!")

    @bot.command(aliases=["p"])
    async def play(ctx, *, song, bot=bot):
        if not bot.voice_client.is_playing():
            try:
                play_yt_song(song, bot.ytdl_options)
                await ctx.message.add_reaction("👍")
                await nowplaying(ctx)
                print(f"Now playing {bot.nowplaying}!")
            except AgeRestrictedException:
                await ctx.channel.send("This Video ist age restricted, sorry!")
                print("Age restricted Video skipped!")
                await skip(ctx, silent=True)    
        else:
            bot.playlist.append(song)
            await ctx.channel.send("Song added!")
            print(f"Added {song} to playlist!")
            await ctx.message.add_reaction("👍")

    def play_yt_song(song, ytdl_options, bot=bot):
        if "open.spotify.com" in song:
            print("Spotify Song detected!")
            song = spotify_link_handler.get_spotify_trackname(
                song, bot.spotify_instance)
        if not validators.url(song):
            if not song.startswith("ytsearch:"):
                song = "ytsearch:" + song

        with youtube_dl.YoutubeDL(bot.ytdl_options) as ydl:
            try:
                song_info = ydl.extract_info(song, download=False)
                if not validators.url(song):
                    song_url = song_info["entries"][0]["formats"][0]["url"]
                    song_title = song_info["entries"][0]["title"]
                else:
                    song_url = song_info["formats"][0]["url"]
                    song_title = song_info["title"]

                bot.voice_client.play(
                    discord.FFmpegPCMAudio(
                        song_url,
                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    ),
                    after=playlist_handler,
                )
                bot.lastplayed = song
                bot.nowplaying = song_title
            except youtube_dl.utils.DownloadError:
                raise AgeRestrictedException()

        

    def playlist_handler(error, bot=bot):

        if not bot.looping:
            if len(bot.playlist) != 0:
                play_yt_song(bot.playlist.pop(0), bot.ytdl_options)
        else:
            play_yt_song(bot.lastplayed, bot.ytdl_options)


    #######
    bot.run(bot_token)
