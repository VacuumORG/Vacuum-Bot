import shutil

from discord import File
from discord.ext import commands
from discord.ext.commands import Context


class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(name='reload')
    async def _reload(self, ctx: Context, *, module: str):
        """Reloads a module."""
        await ctx.send(f'Try to reload {module}')
        try:
            await self.bot.reload_extension('cogs.' + module)
        except Exception as e:
            await ctx.send("Cannot reload the module. Exception raised:")
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    async def sync(self, ctx: Context) -> None:
        """Sync the app commands tree with Discord."""
        try:
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            synced_str = ",".join([sync_command.name for sync_command in synced])
            await ctx.send(f"Synced {synced_str} commands!")
        except Exception as e:
            await ctx.send(f"Cannot sync commands. Exception:\n{e}")

    @commands.command()
    async def get_log(self, ctx: Context) -> None:
        """Get log files."""
        try:
            logs_file_path = shutil.make_archive('logs', 'zip', 'log')
            discord_file = File(logs_file_path)
            await ctx.send(f"Logs file!", file=discord_file)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(Admin(bot))
