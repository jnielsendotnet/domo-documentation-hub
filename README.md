# Domo Documentation Hub

Domo's public documentation site — Getting Started guides, the Knowledge Base (~1,700 articles), API Reference, and topic pages. Content is authored in MDX, navigation is defined in `docs.json`, and the site is built and hosted by [Mintlify](https://mintlify.com).

## Repository layout

- `portal/` — Developer Portal, topic-organized content (Getting Started, API Reference, etc.)
- `s/article/`, `s/topic/` — Knowledge Base articles and topic grouping pages
- `de/`, `es/`, `fr/`, `ja/` — localized content mirroring `s/`
- `openapi/product/` — OpenAPI YAML specs that drive the interactive API reference
- `images/` — screenshots and diagrams
- `docs.json` — Mintlify navigation and configuration (Mintlify manifest)
- `.github/workflows/` — automation for OpenAPI sync and Mintlify preview deployments

## Preview changes locally

Uses the [`mintlify`](https://www.npmjs.com/package/mintlify) npm package for a local dev server against this repo's content.

```bash
npm i -g mintlify       # once per machine — see https://www.npmjs.com/package/mintlify
git checkout <branch>   # any branch with changes you want to preview
mintlify dev            # run from the repo root (where docs.json lives)
```

Open <http://localhost:3000>. Most edits hot-reload; `docs.json` schema changes may need a server restart.

## Deployment

- **`main`** — merges auto-deploy to production via the Mintlify GitHub App.
- **`release/**`** — pushes to release branches create a Mintlify preview via `.github/workflows/mint-preview.yml`. Preview URL is posted to any open PR whose head is the release branch.
- **Any PR** — Mintlify's GitHub App posts a preview link in the PR's Checks tab.

## Writing content

- `CLAUDE.md` — repo conventions and MDX style.
- `Domo-KB-Style-Guide.mdx` — full style standards.
- `New-Article-Template.mdx` — starting point for new KB articles.

## Useful Mintlify references

- [Mintlify docs](https://mintlify.com/docs) · [CLI](https://mintlify.com/docs/cli) · [`docs.json` schema](https://mintlify.com/docs/settings/global) · [Components](https://mintlify.com/docs/components/overview)
