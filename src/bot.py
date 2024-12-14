import discord
from discord.ext import commands
import requests
import base64
import os
import asyncio

TOKEN = 'BOT-TOKEN'
GITHUB_TOKEN = 'GITHUB-TOKEN'
GITHUB_REPO = 'OWNER-NAME/REPOSITORY'
BANS_FILE = 'FILE-TO-STORE-BANNED-USERS'
ALLOWED_USERS_FILE = 'FILE-TO-STORE-ADMINS'
BRANCH = 'main'
ROBLOX_API_URL = 'https://users.roblox.com/v1/usernames/users'

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

OWNER_ID = '891904178815918101'
admin_role_id = None

def get_file_contents(file_path):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}?ref={BRANCH}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()['content']
        return base64.b64decode(content).decode('utf-8').splitlines()
    else:
        raise Exception(f"Error fetching {file_path}: {response.status_code}")

def update_file(file_path, content, message):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
    else:
        raise Exception(f"Error fetching {file_path}: {response.status_code}")

    content_encoded = base64.b64encode(content.encode('utf-8')).decode()
    payload = {
        'message': message,
        'content': content_encoded,
        'sha': sha,
        'branch': BRANCH,
    }

    update_response = requests.put(url, json=payload, headers=headers)
    if update_response.status_code != 200:
        raise Exception(f"Error updating {file_path}: {update_response.status_code}, {update_response.text}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

async def is_allowed_user(ctx):
    return str(ctx.author.id) == OWNER_ID

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.invoke(ctx)

@bot.command()
async def helpp(ctx):
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    embed.add_field(name="!help", value="Shows this help message.", inline=False)
    embed.add_field(name="!ban <userid>", value="Ban a user by their ID.", inline=False)
    embed.add_field(name="!unban <userid>", value="Unban a user by their ID.", inline=False)
    embed.add_field(name="!unbanwave", value="Clear all banned users.", inline=False)
    embed.add_field(name="!user <roblox_username>", value="Get the Roblox User ID from the username.", inline=False)
    embed.add_field(name="!setadmin <role>", value="Set the admin role for whitelisted users.", inline=False)
    embed.add_field(name="!whitelist <user>", value="Whitelist a user by mentioning them.", inline=False)
    embed.add_field(name="!blacklist <user>", value="Blacklist a user by mentioning them.", inline=False)
    embed.add_field(name="!discord <user>", value="Get the Discord User ID of a mentioned user.", inline=False)
    embed.add_field(name="!nuke", value="Nuke the server (delete all channels).", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ban(ctx, userid: str):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    banned_users = get_file_contents(BANS_FILE)
    if userid in banned_users:
        await ctx.send(f"User {userid} is already banned.")
        return

    banned_users.append(userid)
    update_file(BANS_FILE, '\n'.join(banned_users), f"Ban user {userid}")
    await ctx.send(f"User {userid} has been banned.")

@bot.command()
async def unban(ctx, userid: str):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    banned_users = get_file_contents(BANS_FILE)
    if userid not in banned_users:
        await ctx.send(f"User {userid} is not in the ban list.")
        return

    banned_users.remove(userid)
    update_file(BANS_FILE, '\n'.join(banned_users), f"Unban user {userid}")
    await ctx.send(f"User {userid} has been unbanned.")

@bot.command(name='UnbanWave', aliases=['unbanwave'])
async def unban_wave(ctx):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    update_file(BANS_FILE, '', "Clear all banned users")
    await ctx.send("All users have been unbanned.")

@bot.command()
async def user(ctx, roblox_username: str):
    payload = {
        "usernames": [roblox_username]
    }
    response = requests.post(ROBLOX_API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            user_info = data["data"][0]
            user_id = user_info["id"]
            await ctx.send(f"{user_id}.")
        else:
            await ctx.send(f"No user found with the username {roblox_username}.")
    else:
        await ctx.send(f"Failed to fetch user ID for {roblox_username}. Error: {response.status_code}")

@bot.command()
async def setadmin(ctx, role: discord.Role):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    global admin_role_id
    admin_role_id = role.id
    await ctx.send(f"Admin role has been set to {role.name}.")

@bot.command()
async def whitelist(ctx, user: discord.User):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    allowed_users = get_file_contents(ALLOWED_USERS_FILE)
    discord_userid = str(user.id)

    if discord_userid in allowed_users:
        await ctx.send(f"User {user.mention} is already an admin.")
        return

    allowed_users.append(discord_userid)
    update_file(ALLOWED_USERS_FILE, '\n'.join(allowed_users), f"Whitelist user {discord_userid}")
    
    if admin_role_id is not None:
        guild = ctx.guild
        member = guild.get_member(user.id)
        if member is not None:
            role = guild.get_role(admin_role_id)
            if role is not None:
                await member.add_roles(role)
                await ctx.send(f"{user.mention} is now an admin.")
            else:
                await ctx.send("Admin role not found.")
        else:
            await ctx.send("Member not found in the guild.")
    else:
        await ctx.send(f"User {user.mention} has been whitelisted without an admin role.")

@bot.command()
async def wl(ctx, user: discord.User):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    allowed_users = get_file_contents(ALLOWED_USERS_FILE)
    discord_userid = str(user.id)

    if discord_userid in allowed_users:
        await ctx.send(f"User {user.mention} is already an admin.")
        return

    allowed_users.append(discord_userid)
    update_file(ALLOWED_USERS_FILE, '\n'.join(allowed_users), f"Whitelist user {discord_userid}")
    
    if admin_role_id is not None:
        guild = ctx.guild
        member = guild.get_member(user.id)
        if member is not None:
            role = guild.get_role(admin_role_id)
            if role is not None:
                await member.add_roles(role)
                await ctx.send(f"{user.mention} is now an admin.")
            else:
                await ctx.send("Admin role not found.")
        else:
            await ctx.send("Member not found in the guild.")
    else:
        await ctx.send(f"User {user.mention} has been whitelisted without an admin role.")

@bot.command()
async def blacklist(ctx, user: discord.User):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    allowed_users = get_file_contents(ALLOWED_USERS_FILE)
    discord_userid = str(user.id)

    if discord_userid not in allowed_users:
        await ctx.send(f"{user.mention} is not an admin.")
        return

    if discord_userid == OWNER_ID:
        await ctx.send(f"{user.mention} is superior, you can't do that.")
        return

    allowed_users.remove(discord_userid)
    update_file(ALLOWED_USERS_FILE, '\n'.join(allowed_users), f"Blacklist user {discord_userid}")

    if admin_role_id is not None:
        guild = ctx.guild
        member = guild.get_member(user.id)
        if member is not None:
            role = guild.get_role(admin_role_id)
            if role is not None:
                await member.remove_roles(role) 
                await ctx.send(f"{user.mention} is no longer an admin")
            else:
                await ctx.send("Admin role not found.")
        else:
            await ctx.send("Member not found in the guild.")
    else:
        await ctx.send(f"{user.mention} has been blacklisted without an admin role.")

@bot.command()
async def bl(ctx, user: discord.User):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
        return

    allowed_users = get_file_contents(ALLOWED_USERS_FILE)
    discord_userid = str(user.id)

    if discord_userid not in allowed_users:
        await ctx.send(f"{user.mention} is not an admin.")
        return

    if discord_userid == OWNER_ID:
        await ctx.send(f"{user.mention} is superior, you can't do that.")
        return

    allowed_users.remove(discord_userid)
    update_file(ALLOWED_USERS_FILE, '\n'.join(allowed_users), f"Blacklist user {discord_userid}")

    if admin_role_id is not None:
        guild = ctx.guild
        member = guild.get_member(user.id)
        if member is not None:
            role = guild.get_role(admin_role_id)
            if role is not None:
                await member.remove_roles(role)
                await ctx.send(f"{user.mention} is no longer an admin")
            else:
                await ctx.send("Admin role not found.")
        else:
            await ctx.send("Member not found in the guild.")
    else:
        await ctx.send(f"{user.mention} has been blacklisted without an admin role.")


@bot.command()
async def discord(ctx, user: discord.User):
    await ctx.send(f"The Discord User ID for {user.mention} is {user.id}.")

@bot.command()
async def purge(ctx):
    if not await is_allowed_user(ctx):
        await ctx.send("You are not authorized to use this command.")
    await ctx.channel.purge()

bot.run(TOKEN)
