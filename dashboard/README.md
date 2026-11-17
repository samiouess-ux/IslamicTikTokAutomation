# Quran Studio — Private Dashboard

A mobile-first, read-only dashboard for the existing Quran video automation repository.

## Isolation and safety

- This app lives entirely under `dashboard/` on the separate branch `dashboard/private-mobile-dashboard`.
- It does not modify or invoke the production renderer, external cron, Telegram sender, background rotation, or existing workflows.
- The dashboard only reads the delivery history, background catalog, and GitHub Actions run metadata.
- No database, billing, SaaS tenant system, or third-party analytics is used.
- GitHub credentials are used server-side only and are never sent to the browser.

## Deploy (Vercel)

Create a Vercel project connected to this repository and select **Root Directory: `dashboard`**. Do not deploy from the production branch until this dashboard branch has been reviewed and approved.

Configure these environment variables in Vercel:

| Variable | Value |
| --- | --- |
| `DASHBOARD_PASSWORD` | A long, unique password used for the private browser login |
| `GITHUB_READ_TOKEN` | Fine-grained GitHub token with read-only **Contents** and **Actions** access to this repository |
| `DASHBOARD_REPO_OWNER` | `samiouess-ux` |
| `DASHBOARD_REPO_NAME` | `IslamicTikTokAutomation` |
| `DASHBOARD_BRANCH` | `feature/telegram-review-notifications` |

Use a fine-grained token scoped to this single repository. Never add secrets to Git, source files, client-side variables, or screenshots. The token is consumed only by the server route.

The app uses HTTP Basic Authentication as a lightweight private gate. Use HTTPS hosting, keep the password unique, and do not share the URL or credentials. For stronger access control (for example GitHub OAuth or Cloudflare Access), add it before inviting any other viewer.

## Local development

From this directory:

```bash
npm install
DASHBOARD_PASSWORD='local-only-password' GITHUB_READ_TOKEN='read-only-token' npm run dev
```

Open `http://localhost:3000`. The browser will ask for the dashboard password.

## Data and refresh

The server reads:
- `data/quran_delivery_history.json`
- `data/background_candidates.json`
- GitHub Actions workflow runs for the configured branch

The client refreshes every 60 seconds and also offers a manual refresh. GitHub API usage is read-only and authenticated, subject to GitHub's rate limits.

## Known limits in this first version

- GitHub Actions runs are shown for the configured branch; an external cron service may not expose its own schedule details through GitHub.
- The repository stores delivery history and catalogs, not necessarily all rendered MP4 files. The dashboard therefore shows recorded deliveries and workflow links, not fabricated video previews.
- Hosting is not configured by this code commit. A Vercel account/project and the environment variables above are required before a private live URL can exist.
