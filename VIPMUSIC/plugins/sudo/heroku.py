#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
import math
import os
import shutil
import socket
from datetime import datetime

import dotenv
import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

import config
from strings import get_command
from VIPMUSIC import app
from VIPMUSIC.misc import HAPP, SUDOERS, XCB
from VIPMUSIC.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from VIPMUSIC.utils.decorators.language import language
from VIPMUSIC.utils.pastebin import VIPbin

# Commands
GETLOG_COMMAND = get_command("GETLOG_COMMAND")
GETVAR_COMMAND = get_command("GETVAR_COMMAND")
DELVAR_COMMAND = get_command("DELVAR_COMMAND")
SETVAR_COMMAND = get_command("SETVAR_COMMAND")
USAGE_COMMAND = get_command("USAGE_COMMAND")
UPDATE_COMMAND = get_command("UPDATE_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


async def paste_neko(code: str):
    return await VIPbin(code)


@app.on_message(
    filters.command(["log", "logs", "get_log", "getlog", "get_logs", "getlogs"])
    & SUDOERS
)
@language
async def log_(client, message, _):
    try:
        if await is_heroku():
            if HAPP is None:
                return await message.reply_text(_["heroku_1"])
            data = HAPP.get_log()
            link = await VIPbin(data)
            return await message.reply_text(link)
        else:
            if os.path.exists(config.LOG_FILE_NAME):
                log = open(config.LOG_FILE_NAME)
                lines = log.readlines()
                data = ""
                try:
                    NUMB = int(message.text.split(None, 1)[1])
                except:
                    NUMB = 100
                for x in lines[-NUMB:]:
                    data += x
                link = await paste_neko(data)
                return await message.reply_text(link)
            else:
                return await message.reply_text(_["heroku_2"])
    except Exception as e:
        print(e)
        await message.reply_text(_["heroku_2"])


@app.on_message(filters.command(GETVAR_COMMAND) & SUDOERS)
@language
async def varget_(client, message, _):
    usage = _["heroku_3"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            return await message.reply_text(
                f"**{check_var}:** `{heroku_config[check_var]}`"
            )
        else:
            return await message.reply_text(_["heroku_4"])
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(_["heroku_5"])
        output = dotenv.get_key(path, check_var)
        if not output:
            await message.reply_text(_["heroku_4"])
        else:
            return await message.reply_text(f"**{check_var}:** `{str(output)}`")


@app.on_message(filters.command(DELVAR_COMMAND) & SUDOERS)
@language
async def vardel_(client, message, _):
    usage = _["heroku_6"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            await message.reply_text(_["heroku_7"].format(check_var))
            del heroku_config[check_var]
        else:
            return await message.reply_text(_["heroku_4"])
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(_["heroku_5"])
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text(_["heroku_4"])
        else:
            await message.reply_text(_["heroku_7"].format(check_var))
            os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")


@app.on_message(filters.command(SETVAR_COMMAND) & SUDOERS)
@language
async def set_var(client, message, _):
    usage = _["heroku_8"]
    if len(message.command) < 3:
        return await message.reply_text(usage)
    to_set = message.text.split(None, 2)[1].strip()
    value = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
        heroku_config = HAPP.config()
        if to_set in heroku_config:
            await message.reply_text(_["heroku_9"].format(to_set))
        else:
            await message.reply_text(_["heroku_10"].format(to_set))
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(_["heroku_5"])
        dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            await message.reply_text(_["heroku_9"].format(to_set))
        else:
            await message.reply_text(_["heroku_10"].format(to_set))
        os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")


@app.on_message(filters.command(USAGE_COMMAND) & SUDOERS)
@language
async def usage_dynos(client, message, _):
    ### Credits CatUserbot
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
    else:
        return await message.reply_text(_["heroku_11"])
    dyno = await message.reply_text(_["heroku_12"])
    Heroku = heroku3.from_key(config.HEROKU_API_KEY)
    account_id = Heroku.account().id
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {config.HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + account_id + "/actions/get-quota"
    r = requests.get("https://api.heroku.com" + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("Unable to fetch.")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    text = f"""
**Dʏɴᴏ Usᴀɢᴇ**

<u>Usᴀɢᴇ:</u>
Tᴏᴛᴀʟ ᴜsᴇᴅ: `{AppHours}`**ʜ**  `{AppMinutes}`**ᴍ**  [`{AppPercentage}`**%**]

<u>Rᴇᴀᴍɪɴɪɴɢ ǫᴜᴏᴛᴀ:</u>
Tᴏᴛᴀʟ ʟᴇғᴛ: `{hours}`**ʜ**  `{minutes}`**ᴍ**  [`{percentage}`**%**]"""
    return await dyno.edit(text)


@app.on_message(filters.command(["update", "gitpull", "up"]) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
    response = await message.reply_text(_["heroku_13"])
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["heroku_14"])
    except InvalidGitRepositoryError:
        return await response.edit(_["heroku_15"])
    to_exc = f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]
    for checks in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("» ʙᴏᴛ ɪs ᴜᴘ-ᴛᴏ-ᴅᴀᴛᴇ.")
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    updates = "".join(
        f"<b>➣ #{info.count()}: <a href={REPO_}/commit/{info}>{info.summary}</a> ʙʏ -> {info.author}</b>\n\t\t\t\t<b>➥ ᴄᴏᴍᴍɪᴛᴇᴅ ᴏɴ :</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
        for info in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}")
    )
    _update_response_ = "**ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !**\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n__**ᴜᴩᴅᴀᴛᴇs:**__\n"
    _final_updates_ = f"{_update_response_} {updates}"

    if len(_final_updates_) > 4096:
        url = await VIPbin(updates)
        nrs = await response.edit(
            f"**ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !**\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n__**ᴜᴩᴅᴀᴛᴇs :**__\n\n[ᴄʜᴇᴄᴋ ᴜᴩᴅᴀᴛᴇs]({url})",
            disable_web_page_preview=True,
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")

    try:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(
                    chat_id=int(x),
                    text="{0} ɪs ᴜᴘᴅᴀᴛᴇᴅ ʜᴇʀsᴇʟғ\n\nʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.".format(
                        app.mention
                    ),
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(
            _final_updates_
            + f"» ʙᴏᴛ ᴜᴩᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ! ɴᴏᴡ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ ᴍɪɴᴜᴛᴇs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ ʀᴇsᴛᴀʀᴛs",
            disable_web_page_preview=True,
        )
    except:
        pass

    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\nsᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ, ᴩʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs."
            )
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text="ᴀɴ ᴇxᴄᴇᴩᴛɪᴏɴ ᴏᴄᴄᴜʀᴇᴅ ᴀᴛ #ᴜᴩᴅᴀᴛᴇʀ ᴅᴜᴇ ᴛᴏ : <code>{0}</code>".format(
                    err
                ),
            )
    else:
        os.system("pip3 install --no-cache-dir -U -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")
        exit()


@app.on_message(filters.command(["restart"]) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    ac_chats = await get_active_chats()
    for x in ac_chats:
        try:
            await app.send_message(
                chat_id=int(x),
                text=f"{app.mention} ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...\n\nʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except:
            pass

    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit_text(
        "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
    )
    os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")


import requests
from pyrogram import filters

import config
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS

# Heroku API base URL
HEROKU_API_URL = "https://api.heroku.com/apps"

# Set the headers for Heroku API
HEROKU_HEADERS = {
    "Authorization": f"Bearer {config.HEROKU_API_KEY}",
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
}


# Command to create a new Heroku app
@app.on_message(filters.command("newapp") & SUDOERS)
async def create_heroku_app(client, message):
    try:
        # Extract the app name from the command
        if len(message.command) < 2:
            return await message.reply_text(
                "Please provide an app name after the command. Example: `/newapp myappname`"
            )

        app_name = message.command[1].strip()

        # Prepare the payload for creating the Heroku app
        payload = {
            "name": app_name,
            "region": "us",  # You can change the region if needed
        }

        # Send a POST request to create the app
        response = requests.post(HEROKU_API_URL, headers=HEROKU_HEADERS, json=payload)

        # Check if the request was successful
        if response.status_code == 201:
            await message.reply_text(
                f"App '{app_name}' has been successfully created on Heroku!"
            )
        elif response.status_code == 422:
            await message.reply_text(
                f"App name '{app_name}' is already taken. Please try a different name."
            )
        else:
            await message.reply_text(
                f"Failed to create app. Error: {response.status_code}\n{response.json()}"
            )

    except Exception as e:
        print(e)
        await message.reply_text(f"An error occurred: {str(e)}")


# ====≠=========================================HEROKU CONTROLS============================================


import os
import socket

import requests
import urllib3
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from VIPMUSIC import app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEROKU_API_URL = "https://api.heroku.com"
HEROKU_API_KEY = os.getenv("HEROKU_API_KEY")


def make_heroku_request(endpoint, api_key, method="get", payload=None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.heroku+json; version=3",
        "Content-Type": "application/json",
    }
    url = f"{HEROKU_API_URL}/{endpoint}"
    response = getattr(requests, method)(url, headers=headers, json=payload)
    return response.status_code, (
        response.json() if response.status_code == 200 else None
    )


async def fetch_apps():
    status, apps = make_heroku_request("apps", HEROKU_API_KEY)
    return apps if status == 200 else None


async def get_owner_id(app_name):
    status, config_vars = make_heroku_request(
        f"apps/{app_name}/config-vars", HEROKU_API_KEY
    )
    if status == 200 and config_vars:
        return config_vars.get("OWNER_ID")
    return None


@app.on_message(filters.command("heroku") & SUDOERS)
async def list_apps(client, message):
    apps = await fetch_apps()

    if not apps:
        await message.reply_text("No apps found on Heroku.")
        return

    buttons = [
        [InlineKeyboardButton(app["name"], callback_data=f"app:{app['name']}")]
        for app in apps
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await message.reply_text("Select an app:", reply_markup=reply_markup)


@app.on_callback_query(filters.regex(r"^appm:(.+)"))
async def app_options(client, callback_query):
    app_name = callback_query.data.split(":")[1]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to access this app!", show_alert=True
        )
        return

    buttons = [
        [
            InlineKeyboardButton(
                "Edit Variables", callback_data=f"edit_varsm:{app_name}"
            )
        ],
        [InlineKeyboardButton("Get Logs", callback_data=f"get_logsm:{app_name}")],
        [
            InlineKeyboardButton(
                "Restart All Dynos", callback_data=f"restart_dynosm:{app_name}"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        f"Manage app: {app_name}", reply_markup=reply_markup
    )


@app.on_callback_query(filters.regex(r"^get_logsm:(.+)"))
async def get_logs(client, callback_query):
    app_name = callback_query.data.split(":")[1]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to access logs for this app!", show_alert=True
        )
        return

    status, logs = make_heroku_request(
        f"apps/{app_name}/log-sessions",
        HEROKU_API_KEY,
        method="post",
        payload={"lines": 100, "source": "app"},
    )

    if status == 201:
        await callback_query.message.reply_text(
            f"Logs for {app_name}: {logs['logplex_url']}"
        )
    else:
        await callback_query.message.reply_text(f"Failed to get logs for {app_name}")


@app.on_callback_query(filters.regex(r"^restart_dynosm:(.+)"))
async def restart_dynos(client, callback_query):
    app_name = callback_query.data.split(":")[1]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to restart dynos for this app!", show_alert=True
        )
        return

    status, result = make_heroku_request(
        f"apps/{app_name}/dynos", HEROKU_API_KEY, method="delete"
    )

    if status == 202:
        await callback_query.message.reply_text(
            f"Restarting all dynos for {app_name}..."
        )
    else:
        await callback_query.message.reply_text(
            f"Failed to restart dynos for {app_name}"
        )


@app.on_callback_query(filters.regex(r"^edit_varsm:(.+)"))
async def edit_vars(client, callback_query):
    app_name = callback_query.data.split(":")[1]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to edit variables for this app!", show_alert=True
        )
        return

    # Fetch environment variables
    status, config_vars = make_heroku_request(
        f"apps/{app_name}/config-vars", HEROKU_API_KEY
    )

    if status == 200 and config_vars:
        buttons = [
            [
                InlineKeyboardButton(
                    var_name, callback_data=f"edit_var:{app_name}:{var_name}"
                )
            ]
            for var_name in config_vars.keys()
        ]
        buttons.append(
            [
                InlineKeyboardButton(
                    "Add New Variable", callback_data=f"add_var:{app_name}"
                )
            ]
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await callback_query.message.edit_text(
            "Select a variable to edit:", reply_markup=reply_markup
        )
    else:
        await callback_query.message.reply_text(
            f"Failed to fetch variables for {app_name}"
        )


@app.on_callback_query(filters.regex(r"^edit_varm:(.+):(.+)"))
async def edit_var(client, callback_query):
    app_name, var_name = callback_query.data.split(":")[1:]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to edit variables for this app!", show_alert=True
        )
        return

    await callback_query.message.reply_text(
        f"Please send the new value for the variable `{var_name}`."
    )

    # Awaiting response with the new variable value
    @app.on_message(filters.text & filters.private)
    async def get_new_value(client, message):
        new_value = message.text

        status, response = make_heroku_request(
            f"apps/{app_name}/config-vars",
            HEROKU_API_KEY,
            method="patch",
            payload={var_name: new_value},
        )

        if status == 200:
            await message.reply_text(
                f"Updated `{var_name}` to `{new_value}` for {app_name}."
            )
        else:
            await message.reply_text(
                f"Failed to update variable `{var_name}` for {app_name}."
            )

        # Remove the listener for this message after receiving input
        app.remove_handler(get_new_value)


@app.on_callback_query(filters.regex(r"^add_varm:(.+)"))
async def add_var(client, callback_query):
    app_name = callback_query.data.split(":")[1]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to add variables to this app!", show_alert=True
        )
        return

    await callback_query.message.reply_text(
        f"Please send the new variable name and its value in this format: `NAME=value`."
    )

    # Awaiting response for the new variable
    @app.on_message(filters.text & filters.private)
    async def get_var_name_value(client, message):
        text = message.text
        if "=" not in text:
            await message.reply_text("Invalid format. Please use `NAME=value` format.")
            return

        var_name, var_value = text.split("=", 1)

        status, response = make_heroku_request(
            f"apps/{app_name}/config-vars",
            HEROKU_API_KEY,
            method="patch",
            payload={var_name: var_value},
        )

        if status == 200:
            await message.reply_text(
                f"Added new variable `{var_name}` with value `{var_value}` for {app_name}."
            )
        else:
            await message.reply_text(
                f"Failed to add variable `{var_name}` for {app_name}."
            )

        # Remove the listener for this message after receiving input
        app.remove_handler(get_var_name_value)


@app.on_callback_query(filters.regex(r"^delete_varm:(.+):(.+)"))
async def delete_var(client, callback_query):
    app_name, var_name = callback_query.data.split(":")[1:]
    user_id = str(callback_query.from_user.id)

    owner_id = await get_owner_id(app_name)

    if owner_id != user_id and int(user_id) not in SUDOERS:
        await callback_query.answer(
            "You are not authorized to delete variables from this app!", show_alert=True
        )
        return

    status, config_vars = make_heroku_request(
        f"apps/{app_name}/config-vars", HEROKU_API_KEY
    )

    if status == 200 and var_name in config_vars:
        config_vars.pop(var_name)

        status, response = make_heroku_request(
            f"apps/{app_name}/config-vars",
            HEROKU_API_KEY,
            method="patch",
            payload=config_vars,
        )

        if status == 200:
            await callback_query.message.reply_text(
                f"Deleted variable `{var_name}` from {app_name}."
            )
        else:
            await callback_query.message.reply_text(
                f"Failed to delete variable `{var_name}` from {app_name}."
            )
    else:
        await callback_query.message.reply_text(
            f"Variable `{var_name}` not found in {app_name}."
        )


@app.on_callback_query(filters.regex(r"^cancelm"))
async def cancel_action(client, callback_query):
    await callback_query.message.edit_text("Action canceled.")


# Other functions like add_var, edit_var, delete_var can be similarly implemented following the same access control logic
