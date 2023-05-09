from discord.ext import commands
from discord.ext.commands import Context


class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        user_roles = ctx.author.roles
        allowed_roles = ['ADM', 'Líderes']
        return any([role.name in allowed_roles for role in user_roles])

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
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            synced_str = ",".join([sync_command.name for sync_command in synced])
            await ctx.send(f"Synced {synced_str} commands!")
        except Exception as e:
            await ctx.send(f"Cannot sync commands. Exception:\n{e}")


async def setup(bot):
    await bot.add_cog(Admin(bot))
