from email import message
import os
import discord
from discord.ext import commands
import asyncio 
from datetime import datetime, timedelta
import re

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WHITELIST = [1469353569475100774,
             662596869221908480]

# Tracking
mention_tracker = {}
mod_actions = {}

TIME_WINDOW = timedelta(minutes=15)

# 🔍 Invite Regex
INVITE_REGEX = re.compile(r"(discord\.gg\/|discord\.com\/invite\/)")

# 🧹 Cleanup
def clean_old_entries(data_dict):
    now = datetime.utcnow()
    for user in list(data_dict.keys()):
        data_dict[user] = [t for t in data_dict[user] if now - t < TIME_WINDOW]
        if not data_dict[user]:
            del data_dict[user]

@bot.event
async def on_webhooks_update(channel):
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.user and webhook.user.id in WHITELIST:
            continue
        try:
            await webhook.delete(reason="Anti-Webhook")
        except:
            pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id in WHITELIST:
        return

    now = datetime.utcnow()

    if INVITE_REGEX.search(message.content):
        try:
            await message.delete()
            await message.author.timeout(timedelta(minutes=5), reason="Discord Invite gepostet")
            await message.channel.send(f"{message.author.mention} → Invite Links sind verboten!")
        except:
            pass
        return

    if message.mentions:
        user_id = message.author.id
        mention_tracker.setdefault(user_id, []).append(now)
        clean_old_entries(mention_tracker)

        if len(mention_tracker[user_id]) > 3:
            try:
                await message.author.timeout(timedelta(minutes=5), reason="Mention Spam")
                await message.channel.send(f"{message.author.mention} → Timeout wegen Mention Spam")
            except:
                pass


    if "@everyone" in message.content or "@here" in message.content:
        try:
            await message.author.timeout(timedelta(minutes=3), reason="@everyone missbraucht")
            await message.channel.send(f"{message.author.mention} → Timeout wegen @everyone")
        except:
            pass
    await bot.process_commands(message)

@bot.event
async def on_member_remove(member):
    guild = member.guild
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        user = entry.user

        if user.id in WHITELIST:
            return
        now = datetime.utcnow()
        mod_actions.setdefault(user.id, []).append(now)
        clean_old_entries(mod_actions)
        if len(mod_actions[user.id]) >= 3:
            try:
                await guild.ban(user, reason="Kick Spam")
            except:
                pass
@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        mod = entry.user

        if mod.id in WHITELIST:
            return
        now = datetime.utcnow()
        mod_actions.setdefault(mod.id, []).append(now)
        clean_old_entries(mod_actions)
        if len(mod_actions[mod.id]) >= 3:
            try:
                await guild.ban(mod, reason="Ban Spam")
            except:
                pass

@bot.event
async def on_member_update(before, after):
    # nur wenn Timeout gesetzt wurde
    if (
        before.timed_out_until == after.timed_out_until
        or after.timed_out_until is None
    ):
        return

    guild = after.guild

    await asyncio.sleep(1.5)

    async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.member_update):

        if entry.target.id != after.id:
            continue

        # check ob es wirklich ein timeout ist
        if not entry.after.timed_out_until:
            continue

        mod = entry.user

        if mod.id in WHITELIST:
            return

        now = datetime.utcnow()
        mod_actions.setdefault(mod.id, []).append(now)
        clean_old_entries(mod_actions)

        print(f"{mod} → Timeout #{len(mod_actions[mod.id])}")

        if len(mod_actions[mod.id]) >= 3:
            try:
                await guild.ban(mod, reason="Timeout Spam")
                print("🚨 MOD GEBANNT")
            except Exception as e:
                print(e)

        break


bot.run(os.getenv("TOKEN"))
