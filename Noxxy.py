import discord
from discord.ext import commands
import os
import asyncio

# Configuration
TOKEN = os.getenv("MTU3NDMzOTQ1NTUzNDIzOTc4NA.GiLik1.ITtVaCIGV-JuEb7rtoLHJELjRKRRQzabLJaXSg")
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents
)

# État du bot
stay_enabled = False
saved_channel = None
reconnecting = False


@bot.event
async def on_ready():
    print(f"Bot connecté : {bot.user}")
    print(f"ID : {bot.user.id}")
    print("Bot prêt !")


@bot.command()
async def join(ctx):
    global saved_channel

    if not ctx.author.voice:
        return await ctx.send(
            "❌ Tu dois être dans un salon vocal !"
        )

    channel = ctx.author.voice.channel
    saved_channel = channel

    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(
            f"✅ Connecté au vocal : {channel.name}"
        )

    except Exception as error:
        await ctx.send(f"❌ Erreur : {error}")


@bot.command()
async def stay(ctx):
    global stay_enabled, saved_channel

    if not ctx.author.voice:
        return await ctx.send(
            "❌ Rejoins un salon vocal avant !"
        )

    saved_channel = ctx.author.voice.channel
    stay_enabled = True

    try:
        if ctx.voice_client:
            if ctx.voice_client.channel != saved_channel:
                await ctx.voice_client.move_to(saved_channel)
        else:
            await saved_channel.connect()

        await ctx.send(
            "🔒 Mode STAY activé ! Je reste dans le vocal."
        )

    except Exception as error:
        await ctx.send(f"❌ Erreur : {error}")


@bot.command()
async def unstay(ctx):
    global stay_enabled, saved_channel

    stay_enabled = False
    saved_channel = None

    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)

    await ctx.send(
        "🔓 Mode STAY désactivé. Je quitte le vocal."
    )


@bot.command()
async def status(ctx):
    if stay_enabled:
        message = "🔒 Mode STAY activé"
    else:
        message = "🔓 Mode STAY désactivé"

    if ctx.voice_client:
        message += "\n✅ Connecté au vocal"
    else:
        message += "\n❌ Pas connecté au vocal"

    await ctx.send(message)


@bot.command()
async def helpbot(ctx):
    message = """
**COMMANDES DU BOT**

`!join` → Rejoindre ton vocal
`!stay` → Rester dans le vocal
`!unstay` → Quitter le vocal
`!status` → Voir le statut du bot
`!helpbot` → Afficher les commandes
"""
    await ctx.send(message)


@bot.event
async def on_voice_state_update(member, before, after):
    global reconnecting

    if bot.user is None:
        return

    if member.id != bot.user.id:
        return

    # Le bot a été déconnecté du vocal
    if before.channel is not None and after.channel is None:
        if stay_enabled and saved_channel and not reconnecting:
            reconnecting = True

            async def reconnect():
                global reconnecting

                try:
                    await asyncio.sleep(5)

                    if stay_enabled and not bot.voice_clients:
                        await saved_channel.connect()
                        print("Reconnexion au vocal réussie.")

                except Exception as error:
                    print(f"Erreur de reconnexion : {error}")

                finally:
                    reconnecting = False

            asyncio.create_task(reconnect())


if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN est absent des variables d'environnement."
    )
