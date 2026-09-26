# AI Newsletter Pipeline

An n8n workflow that runs your entire weekly newsletter on autopilot: it **fetches** fresh content from RSS feeds, **summarises** each item with AI, **rewrites** everything in your newsletter voice, and **sends** a polished HTML email on schedule. Import the JSON, add your credentials, and you're done.

## The problem

Founders, indie hackers, and creators all know a newsletter is one of the highest-leverage growth channels — and one of the most time-consuming. Reading dozens of articles, picking the ones that matter, writing summaries, formatting the email: it's 4–6 hours of editorial work every single week. Most people either burn out or quit.

This pipeline compresses that editorial process into a few minutes of human review (if you even want that) by automating the fetch → summarise → rewrite → send loop.

## How it works

```
 ┌─────────────────┐
 │ Weekly Schedule │  Every Monday, 9:00 AM
 └────────┬────────┘
          ├──────────────┬──────────────┐
          ▼              ▼              ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │ RSS Feed 1  │  │ RSS Feed 2  │  │ RSS Feed N  │
   │ (Tech)      │  │ (AI News)   │  │ (your niche)│
   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
          └──────────────┬────────────────┘
                         ▼
                ┌────────────────┐
                │  Merge Feeds   │  combine all items
                └───────┬────────┘
                        ▼
        ┌───────────────────────────────┐
        │ AI: Summarise Items           │  2-sentence summary
        │ (OpenAI, per item)            │  per article
        └──────────────┬────────────────┘
                       ▼
        ┌───────────────────────────────┐
        │ AI: Rewrite Newsletter        │  witty, grouped
        │ (OpenAI, newsletter voice)    │  by section
        └──────────────┬────────────────┘
                       ▼
                ┌──────────────┐
                │ Build HTML   │  Code node: HTML
                │ Email        │  template
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ Send         │  Gmail / SMTP
                │ Newsletter   │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ Log Success  │  audit trail
                └──────────────┘
```

1. **Schedule Trigger** — fires weekly (Monday 9:00 AM by default; change to daily/monthly in one click).
2. **RSS Read** — pulls the latest items from as many feeds as you add (duplicate the node for each feed).
3. **Merge** — combines every feed's items into a single stream.
4. **AI Summarise** — OpenAI condenses each article into a 2-sentence summary with title + link, output as clean JSON.
5. **AI Rewrite** — OpenAI takes the summaries and rewrites them in a consistent newsletter voice, grouped into sections (AI & Tech, Product & Startups, Deep Dive).
6. **HTML Template** — a Code node wraps the rewritten content in a clean, responsive email layout.
7. **Send** — delivers via Gmail OAuth or SMTP.
8. **Log Success** — records each send with a timestamp for your audit trail.

## Features

- 📥 Multi-feed RSS ingestion — add or remove feeds by duplicating a node
- 🤖 Two-stage AI pipeline: factual summarisation, then voice rewrite
- ✉️ Styled HTML email output (no manual formatting)
- ⏰ Fully scheduled — set it and forget it
- 🔐 Credentials referenced by name only; secrets stay in n8n's vault and env vars
- ⚙️ Env-var driven config (`OPENAI_MODEL`, `NEWSLETTER_TO`, ...) — no hardcoding

## Quickstart

1. Install [n8n](https://n8n.io) (self-hosted or cloud).
2. In n8n, go to **Workflows → Import from File**.
3. Select `workflows/ai-newsletter-pipeline.json` from this repo.
4. Add your credentials when prompted:
   - **OpenAI account** — for the two AI nodes (API key)
   - **Gmail account** — OAuth2 for the Send node (or swap the Gmail node for an SMTP node)
5. Set the environment variables (see `workflows/starter-config.env.example`) — at minimum `NEWSLETTER_TO`.
6. Activate the workflow. Your first issue goes out at the next scheduled time.

## Required credentials & env

| What | Where | Notes |
|---|---|---|
| OpenAI API key | n8n credential `OpenAI account` | Powers both AI nodes |
| Gmail OAuth2 (or SMTP) | n8n credential `Gmail account` | Sending |
| `NEWSLETTER_TO` | env var | Recipient address |
| `NEWSLETTER_FROM` | env var | Sender display name |
| `OPENAI_MODEL` | env var | Default `gpt-4o-mini` |
| `RSS_FEEDS` | env var | Comma-separated feed URLs (reference when adding feeds) |

See `workflows/starter-config.env.example` for a ready-to-copy template. Never commit real keys — they belong in n8n credentials and your local `.env`, never in the repo.

## Customization guide

- **Change schedule:** edit the `Weekly Schedule` node — daily, bi-weekly, or monthly in seconds.
- **Add feeds:** duplicate an `RSS Feed` node, paste the new URL, and wire it into `Merge Feeds`.
- **Change voice:** edit the system prompt in the `AI Rewrite Newsletter` node — formal, punchy, casual, whatever fits your brand.
- **Add sections:** ask for new sections in the rewrite prompt (e.g. "Funding Rounds", "Bihar Startup News").
- **Add a review step:** insert a manual-approval node (or an email-to-self draft) between rewrite and send for human sign-off.
- **Multiple audiences:** duplicate the send branch and route by tag to send segmented editions.
- **Swap the sender:** replace the Gmail node with `n8n-nodes-base.smtp` for any mail provider.

## Testing

```bash
python3 -m pytest tests/ -q
```

The test suite validates the workflow JSON: structure, node types, connections, credentials-by-name-only, and no hardcoded secrets.

## License

MIT — use it for client work freely.
