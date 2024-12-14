local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local bannedUserIdsUrl = "https://raw.githubusercontent.com/fentfeen/rtd-recourses-/refs/heads/main/bans"

local function fetchBannedUserIds()
    local success, response = pcall(function()
        return HttpService:GetAsync(bannedUserIdsUrl)
    end)

    if success then
        local bannedUserIds = {}
        for _, line in ipairs(string.split(response, "\n")) do
            local userId = tonumber(line)
            if userId then
                table.insert(bannedUserIds, userId)
            end
        end
        return bannedUserIds
    else
        warn("Failed to fetch banned User IDs: " .. tostring(response))
        return {}
    end
end

local bannedUserIds = fetchBannedUserIds()

local function checkPlayer(player)
    if table.find(bannedUserIds, player.UserId) then
        player:Kick("BAN-MESSAGE")
    end
end

Players.PlayerAdded:Connect(checkPlayer)
