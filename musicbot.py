import discord.ext.commands


class MusicBot(discord.ext.commands.Bot):
    def __init__(self, state, ytdl_options, spotify_instance, command_prefix="/", help_command=None, description=None):
        super().__init__(command_prefix, help_command, description)
        self.state = state
        self.YTDL_OPTIONS = ytdl_options
        self.SPOTIFY_INSTANCE = spotify_instance

    