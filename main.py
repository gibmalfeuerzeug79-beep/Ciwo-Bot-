import discord
import os
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
from discord import Embed

TOKEN = os.getenv("TOKEN")

app = Flask('')

@app.route('/')
def home():
    return "Bot läuft!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()




intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"{len(synced)} commands synced")

def create_embed(title: object, description: object, user: object = None, color: object = discord.Color.blue()) -> Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1292435237653184554/1480994783458496562/pelangi.gif"
    )

    embed.set_footer(text="Made By Yuqii")



    if user:
        embed.set_thumbnail(url=user.display_avatar.url)

    embed.set_footer(text="Made By Yuqii")

    return embed



#Kick ---------------------------------------------------------------------



@bot.tree.command(name="kick", description="Kick a user from Server")
@app_commands.describe(member="User to kick", reason="reason")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No Reason"):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You dont have perms to do that.", ephemeral=True)
        return

    await member.kick(reason=reason)

    await interaction.response.send_message(
        f" {member.mention} was kicked.\nreason: {reason}"

    )

    now = datetime.now().strftime("%d.%m.%Y | %H:%M")


# Ban ---------------------------------------------------

@bot.tree.command(name="ban", description="Ban a user from Server")
@app_commands.describe(member="User to kick", reason="reason")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No Reason"):

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You dont have perms to do that.", ephemeral=True)
        return

    await member.ban(reason=reason)
#mit embed -----

    embed = create_embed(
      title="User banned",
      description=f"{member.mention} wurde gebannt.\nGrund: {reason}",
      color=0x000370
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

    now = datetime.now().strftime("%d.%m.%Y | %H:%M")

#TIMEOUT ------------------------------------------------------------

from datetime import timedelta

@bot.tree.command(name="timeout", description="Timeoute the User")
@app_commands.describe(member="Mitglied", minutes="Time in minutes", reason="Grund")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Kein Grund angegeben"):

    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("you dont have perms to do that", ephemeral=True)
        return

    await interaction.response.defer()

    duration = timedelta(minutes=minutes)

    await member.timeout(duration, reason=reason)

    embed = create_embed(
        title="User got Timeout!",
        description=f"{member.mention} wurde für **{minutes} Minuten** getimeoutet.\nGrund: {reason}",
        color=0x000370
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.followup.send(embed=embed)

    now = datetime.now().strftime("%d.%m.%Y | %H:%M")

    #timeout remove-------------------------------------------------------------------------------------


@bot.tree.command(name="untimeout", description="Untimeoute the User")
@app_commands.describe(member="User", reason="reason")
async def untimeout(interaction: discord.Interaction, member: discord.Member, reason: str = "No Reason"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("you dont have perms to do that!", ephemeral=True)
        return

    await interaction.response.defer()

    await member.timeout(None, reason=reason)

    now = datetime.now().strftime("%d.%m.%Y | %H:%M")

    embed = create_embed(
        title="Timeout removed",
        description=f"{member.mention} was untimeouted.\nReason: {reason}",
        user=member,
        color=0x000370
    )

    await interaction.followup.send(embed=embed)


#avatar-------------------------------------------------------------------------------------


@bot.tree.command(name="avatar", description="Show the User avatar")
@app_commands.describe(member="User whose avatar should be displayed")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    embed  = create_embed(
        title = "Avatar von {user}".format(user=member),
        description=f"[Avatar Herunterladen]({member.display_avatar.url})",
        user=member,
        color=0x000370

    )

    embed.set_image(url=member.display_avatar.url)


    await interaction.response.send_message(embed=embed)

#banner-------------------------------------------------------------------------------------

@bot.tree.command(name="banner", description="Show the User banner")
@app_commands.describe(member="User whose banner should be displayed")
async def banner(interaction: discord.Interaction, member: discord.Member = None):


    if member is None:
        member = interaction.user

    user = await bot.fetch_user(member.id)

    if user.banner is None:
        await interaction.response.send_message("This User has not Banner." ,ephemeral=True)
        return



    embed = create_embed(
         title="Banner von {user}".format(user=user),
         description=f"[Banner Herunterladen]({user.banner.url})",
         user=member,
         color=0x000370

    )

    embed.set_image(url=user.banner.url)

    await interaction.response.send_message(embed=embed)


# clear ----------------------------------------------------------------------------------

@bot.tree.command(name="clear", description="Clear number of messages")
@app_commands.describe(amount="User whose messages should be cleared")
async def clear(interaction: discord.Interaction, amount: int):

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Du dont have Permissions to do that!", ephemeral=True)
            return

        await interaction.response.defer()

        deleted = await interaction.channel.purge(limit=amount)

        embed = create_embed(
            title="Messages cleared",
            description=f"{len(deleted)} Messages were deleted.",
            user=interaction.user,
            color=0x000370
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


#invite look up-----------------------------------------------------------------------------


@bot.tree.command(name="invites", description="Zeigt alle Server Invites")
async def invites(interaction: discord.Interaction):

    await interaction.response.defer()

    invites = await interaction.guild.invites()

    if not invites:
        await interaction.followup.send("Keine Invites gefunden.")
        return

    embed = create_embed(
        title="Server Invite Übersicht",
        description="Alle aktiven Server Einladungen",
        color=0x000370
    )

    for invite in invites[:25]:
        inviter = invite.inviter.mention if invite.inviter else "Unbekannt"

        embed.add_field(
            name=f"Code: {invite.code}",
            value=f"Erstellt von: {inviter}\nUses: {invite.uses}",
            inline=False
        )

    await interaction.followup.send(embed=embed)




#help funktion-------------------------------------------------------------------------------------


@bot.tree.command(name="help", description="Function by Yuqii")
async def help(interaction: discord.Interaction):

    embed = create_embed(
        title="Yuqii Features",
        description="Hier findest du die Slash Commands und Funktionen von Yuqii",
        user=interaction.user,
        color=0x000370
    )

    embed.add_field(
        name="`/kick`",
        value="Kicking a User spezific on Server",
        inline=False
    )

    embed.add_field(
        name="`/ban`",
        value="Banning a User spezific on Server.",
        inline=False
    )

    embed.add_field(
        name="`/timeout`",
        value="Timeoutet a User on Server.",
        inline=False
    )

    embed.add_field(
        name="`/untimeout`",
        value="Remove the timeout from the User.",
        inline=False
    )

    embed.add_field(
        name="`/avatar`",
        value="Show the User avatar.",
        inline=False
    )

    embed.add_field(
        name="`/banner`",
        value="Show the User banner.",
        inline=False
    )

    embed.add_field(
        name="`/clear`",
        value="Delete a spezific message from the Server.",
        inline=False
    )

    embed.add_field(
        name="`/invites`",
        value="Look Up your Invite Stats",
        inline=False
    )


    await interaction.response.send_message(embed=embed)



# counting ---------------------------------------------------------------------


COUNT_CHANNEL_NAME = "🔢・counting"

current_number = 1
last_user_id = None
failures = {}  # user_id: fehler


def error_embed(user, text):
    embed = discord.Embed(
        title="mistake",
        description=f"{user.mention} {text}",
        color=0x000370
    )
    return embed


def reset_embed(user):
    embed = discord.Embed(
        title="Counter Reset",
        description=f"{user.mention} Made 3 mistakes!\nThe counter has been reset to **1**.",
        color=0x000370
    )
    return embed




@bot.event
async def on_message(message):
    global current_number, last_user_id, failures

    if message.author.bot:
        return

    if message.channel.name != COUNT_CHANNEL_NAME:
        await bot.process_commands(message)
        return

    user_id = message.author.id

    # Nur Zahlen erlauben
    try:
        user_number = int(message.content)
    except ValueError:
        return

    # ❗ Nicht zweimal hintereinander
    if last_user_id == user_id:
        await message.add_reaction("❌")
        await message.channel.send(
            embed=error_embed(message.author, "duplicated from same user is not allowed!")
        )
        return

    # ✅ Richtige Zahl
    if user_number == current_number:
        await message.add_reaction("✅")
        await message.channel.send(embed=success_embed(current_number, message.author))
        current_number += 1
        last_user_id = user_id
        return

    # ❌ Falsche Zahl
    failures[user_id] = failures.get(user_id, 0) + 1
    remaining = 3 - failures[user_id]

    await message.add_reaction("❌")

    if failures[user_id] >= 3:
        await message.channel.send(embed=reset_embed(message.author))
        current_number = 1
        last_user_id = None
        failures = {}
    else:
        await message.channel.send(
            embed=error_embed(
                message.author,
                f"Incorrect number! **{remaining} attempts** remaining."
            )
        )

    await bot.process_commands(message)

    




# bot start -------------------------------------------------------------------------------------

bot.run(os.getenv("TOKEN"))
