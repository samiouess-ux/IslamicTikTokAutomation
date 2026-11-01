# Telegram on-demand Quran request bridge

This bridge is separate from the daily Quran workflow. It receives a text request
from the authorized Telegram chat, dispatches
`.github/workflows/telegram-quran-request.yml` on
`feature/telegram-review-notifications`, and acknowledges the request.

The workflow renders one **review-only** MP4 and sends it to Telegram. TikTok
publishing is not implemented and remains manual. A request must specify a
surah and an explicit range of 1–10 consecutive ayahs; the workflow rejects
whole-surah requests because a complete surah cannot reliably fit the 65-second
limit.

## Cloudflare Worker configuration

Deploy `cloudflare/telegram-bridge/worker.js` as a Cloudflare Worker. Bind a
Cloudflare KV namespace named `TELEGRAM_UPDATES` (see `wrangler.toml`).

Set these Worker variables/secrets:

- Secret `TELEGRAM_BOT_TOKEN`: the existing Telegram bot token.
- Secret `TELEGRAM_WEBHOOK_SECRET`: a random 32+ character secret used by Telegram's webhook header.
- Secret `GITHUB_TOKEN`: a fine-grained GitHub token limited to this repository with Actions: write permission.
- Variable `ALLOWED_TELEGRAM_CHAT_ID`: the one authorized Telegram chat ID.
- Variable `GITHUB_REPOSITORY`: `samiouess-ux/IslamicTikTokAutomation` (optional; this is the default).

Do not put tokens in this repository, source files, issues, or chat messages.

## Set the Telegram webhook

After deployment, set the webhook once using Telegram's `setWebhook` API.
Use the Worker HTTPS URL as `url`, and set `secret_token` to the exact
`TELEGRAM_WEBHOOK_SECRET` value. Restrict `allowed_updates` to
`message`. Keep the bot token and webhook secret private.

## GitHub requirements

The repository must already have Actions secrets `TG_BOT_TOKEN` and
`TELEGRAM_CHAT_ID` for the workflow to send the MP4. The Worker-side GitHub
token is separate and is used only to dispatch the on-demand workflow.

## Request format

Examples:

- `فيديو سورة الكهف` — automatically chooses an opening passage that fits 65 seconds.
- `فيديو سورة مريم الآية 5` — one ayah.
- `فيديو سورة البقرة الآيات 1-5` — exact range.

The parser also accepts Arabic-Indic digits. Ranges above ten ayahs, invalid
verse numbers, incomplete catalogs, or a single ayah longer than 65 seconds
fail closed and send a failure notice when Telegram credentials are available.

## Safety

- Only the configured Telegram chat is authorized.
- Telegram webhook requests require the configured secret header.
- Update IDs are stored in KV for seven days to reduce duplicate workflow runs.
- The generated MP4 is marked review-only; exact text, translation rights,
  recording reuse, and background review remain required.
- No TikTok publishing endpoint or automatic upload is present.
