import discord.ext.commands


class MusicBot(discord.ext.commands.Bot):
    def __init__(self, voice_client, playlist, nowplaying, lastplayed, looping, ytdl_options, spotify_instance, command_prefix="/", help_command=None, description=None):
        super().__init__(command_prefix, help_command, description)
        self.voice_client = voice_client
        self.playlist = playlist
        self.nowplaying = nowplaying
        self.lastplayed = lastplayed
        self.looping = looping
        self.ytdl_options = ytdl_options
        self.spotify_instance = spotify_instance

    