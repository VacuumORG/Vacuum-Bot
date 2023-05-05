from discord.ext import commands
from discord.ext.commands import Context


class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_helper(self):
        help_text = """• /reload [cog_name] - Recarrega o cog especificado.
        • /sync - Sincroniza os App Commands do bot com o Discord.
        """
        group_name = "Administrador"
        return [group_name, help_text]

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
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context) -> None:
        """Sync the app commands tree with Discord."""
        try:
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            synced_str = ",".join([sync_command.name for sync_command in synced])
            await ctx.send(f"Synced {synced_str} commands!")
        except Exception as e:
            await ctx.send(f"Cannot sync commands. Exception:\n{e}")


async def setup(bot):
    await bot.add_cog(Admin(bot))
