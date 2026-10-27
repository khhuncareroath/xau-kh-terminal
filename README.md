# XAU.KH

Put everything in the repo root, keeping `.github/workflows/signals.yml` at that exact path.

Repo secrets (Settings > Secrets and variables > Actions):
- TELEGRAM_TOKEN: your bot token
- TELEGRAM_CHAT_ID: the public alert channel, e.g. @yourchannel (best-setup alerts go here)
- TELEGRAM_OWNER_CHAT_ID: your private chat id (data-problem alerts go only here)
- NTFY_TOPIC: optional, a long random topic name for ntfy.sh push
Repo variable: SITE_URL (optional, link inside alerts)

Then Actions > Gold analysis > Run workflow once.
