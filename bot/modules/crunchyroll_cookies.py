"""Per-user Crunchyroll cookie file management."""
import os
from os import path as ospath

from ..helper.ext_utils.bot_utils import new_task
from ..helper.telegram_helper.message_utils import send_message


def _cookie_path(user_id):
    root = ospath.abspath(ospath.join(ospath.dirname(__file__), "..", ".."))
    folder = ospath.join(root, "cr_cookies")
    os.makedirs(folder, mode=0o700, exist_ok=True)
    return ospath.join(folder, f"{user_id}.txt")


@new_task
async def crcookie(client, message):
    user = message.from_user
    if not user:
        await send_message(message, "Please run this command from your own account.")
        return
    if not message.chat or message.chat.type.value != "private":
        await send_message(message, "🔒 Please use /crcookie in a private chat with the bot.")
        return

    parts = (message.text or "").split()
    action = parts[1].lower() if len(parts) > 1 else "save"
    path = _cookie_path(user.id)
    if action in {"delete", "remove", "clear"}:
        if ospath.isfile(path):
            os.remove(path)
            await send_message(message, "🗑 Your saved Crunchyroll cookie file was deleted.")
        else:
            await send_message(message, "No saved Crunchyroll cookie file was found.")
        return
    if action in {"status", "check"}:
        await send_message(message, "✅ A Crunchyroll cookie file is saved for you." if ospath.isfile(path) else "No Crunchyroll cookie file is saved. Reply to a cookie .txt file with /crcookie to save it.")
        return

    reply = message.reply_to_message
    doc = getattr(reply, "document", None) if reply else None
    if not doc:
        await send_message(message, "Reply to an authorized Crunchyroll Netscape-format cookie .txt file with /crcookie. Use /crcookie delete to remove it or /crcookie status to check it.")
        return
    filename = (doc.file_name or "").lower()
    if not filename.endswith((".txt", ".cookies", ".cookie")):
        await send_message(message, "Please reply with a .txt/.cookies file exported in Netscape cookie format.")
        return

    temp_path = f"{path}.tmp"
    try:
        downloaded = await client.download_media(reply, file_name=temp_path)
        if not downloaded or not ospath.isfile(downloaded):
            await send_message(message, "Could not download that cookie file. Please try again.")
            return
        with open(downloaded, "r", encoding="utf-8", errors="replace") as file:
            content = file.read(2_000_000)
        valid_header = "# Netscape HTTP Cookie File" in content or "# HTTP Cookie File" in content
        has_cr_cookie = any(line.strip() and not line.lstrip().startswith("#") and "crunchyroll.com" in line.lower() for line in content.splitlines())
        if not valid_header or not has_cr_cookie:
            await send_message(message, "That file doesn't look like a Netscape cookie export containing Crunchyroll cookies. Nothing was saved.")
            return
        os.replace(downloaded, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
        await send_message(message, "✅ Crunchyroll cookie file saved securely for your account. `/crm` and `/crl` will use it for your downloads. Use `/crcookie delete` to remove it.")
    except Exception as exc:
        await send_message(message, f"Could not save the cookie file: {exc}")
    finally:
        if ospath.isfile(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
