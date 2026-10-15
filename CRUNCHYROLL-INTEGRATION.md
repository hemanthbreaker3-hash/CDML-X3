# Crunchyroll bot commands

The bot supports direct Crunchyroll episode links with:

- `/crl https://www.crunchyroll.com/watch/...` — download the episode and leech it to Telegram (same upload behavior as `/ytdlleech`).
- `/crm https://www.crunchyroll.com/watch/...` — download the episode and send it through the normal mirror destination (same behavior as `/ytdl`).

When `CMD_SUFFIX` is configured, these commands receive the same suffix automatically as the other registered commands.

## Required setup

This feature uses `Crunchyroll-Downloader-main/LastPerson07.py`. The bot does not include account cookies or a Widevine device file. Install `ffmpeg`, `yt-dlp`, and `mp4decrypt` on the host, install the Python dependencies from `requirements.txt`, and provide credentials you are authorized to use:

- Put your own Widevine device file at `Crunchyroll-Downloader-main/LastPerson07/LastPerson07.wvd`, or set `CRUNCHYROLL_WVD` to its path.
- Users can reply to an authorized Netscape-format Crunchyroll cookie `.txt` file with `/crcookie` in a private chat. It is saved per-user under `cr_cookies/<telegram-user-id>.txt` with restricted file permissions and takes priority for that user. `/crcookie status` checks whether one is saved; `/crcookie delete` removes it.
- Alternatively, an administrator may provide `cr_cookies.txt` or `cookies.txt` in the project root, or set `CRUNCHYROLL_COOKIES` to a shared cookie file. The bot also checks the path selected by its existing yt-dlp cookie settings.

For deployment-specific locations, set `CRUNCHYROLL_WVD` and `CRUNCHYROLL_COOKIES` in the process environment. Credentials and device files should not be committed or included in shareable ZIPs.

Only direct `/watch/` episode links are accepted by the bot commands. Series links are rejected instead of silently downloading a season or entire show. The bot uses the highest available video resolution, the page's default audio, and no subtitles; the standalone CLI remains interactive when launched without `--bot-url`.

## Thumbnail fix

The HyperUP upload path now resolves the modern `THUMBNAIL_MODE` setting first and falls back to `AUTO_THUMBNAIL` for older configurations. IMDb/TMDb catalogue URLs are preserved in auto mode so their artwork resolver can inspect the page instead of trying to decode it as an image.
