# XAU.KH

Put everything in the repo root, except the two workflow files, which go in `.github/workflows/`:
`.github/workflows/signals.yml` and `.github/workflows/backtest.yml`.

## Secrets (Settings > Secrets and variables > Actions > Secrets)
- `TELEGRAM_TOKEN`: your bot token
- `TELEGRAM_CHAT_ID`: the public alert channel, e.g. @yourchannel
- `TELEGRAM_OWNER_CHAT_ID`: your private chat id (data-problem alerts go only here)
- `NTFY_TOPIC`: optional, ntfy.sh push
- `ANTHROPIC_API_KEY`: optional, turns on AI-written "Why" lines (a few cents a day at most)
- `TWELVEDATA_KEY`: optional, free key from twelvedata.com, adds the spot XAUUSD equivalent to alerts

## Variables (same page, Variables tab)
- `SITE_URL`: link inside alerts
- `XAU_RULES`: `current` (default) or `v2`. Switch only if backtest.json shows v2 doing better.
- `AI_LANG`: `en` (default) or `km` for English + Khmer
- `DISPLAY_TZ`: default `Asia/Phnom_Penh`

## First run
1. Actions > Daily backtest > Run workflow. Read `backtest.json`: the `verdict` lines say honestly whether the rules
   made money after costs and alert delay.
2. Actions > Gold analysis > Run workflow.

## What runs every 5 minutes
levels → ict → confluence → news → macro → quality → grade → spot → **track** (grades past alerts, replies with
the result) → **postnews** (after FOMC/CPI/NFP) → **notify** (one alert, only if it passes every gate).

## Files the site can read
`results.json` (live track record of every alert), `backtest.json` (historical test), `alerts_log.json`,
plus the existing ict/confluence/levels/news/macro/quality/grade/status files.
