## Lua Script (Roblox)
- Fetches banned user IDs from a GitHub raw file using HttpService:GetAsync.
- Parses the content of the fetched data into a list of numeric user IDs.
- Checks if a newly joined player (PlayerAdded) matches the banned IDs and kicks them with a custom message.

## Python Script (Discord Bot)
- Built using the [discord.py library.](https://discordpy.readthedocs.io/en/stable/)
- Manages bans and whitelisting for Roblox users through a GitHub repository.
- Uses GitHub API to fetch and update files containing banned/allowed user data.

# Commands:
- !ban / !unban / !unbanwave: Manage banned Roblox user IDs.
- !user <username>: Fetches Roblox User ID via Roblox API.
- !setadmin <role> / !whitelist <user> / !blacklist <user>: Manages admin roles for Discord users.
- !helpp: Lists available commands.
- Role management (setadmin, whitelist, blacklist) uses Discord's guild roles to control user permissions.

## setup

# discord bot
1. edit discord bot token, github token and repository info in discord.py.

2. in [discord.py](https://github.com/fentfeen/roblox-to-discord-/blob/main/src/bot.py) find the owner id part (line 28) and set it to the owners userid (this use can use all commands no matter what)

# roblox
1. in serverscriptstorage, paste the [provided script](https://github.com/fentfeen/roblox-to-discord-/blob/main/src/roblox.lua) in and change the github info.

2. save the game and enable "Allow http Requests".
