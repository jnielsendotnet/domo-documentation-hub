---
name: mintlify-preview-workflow
user-invocable: true
description: "work on the Mintlify preview deployment GitHub Action, debug mint-preview.yml, change which PRs get previews, update the Mintlify preview-trigger API call, modify preview-URL PR comments"
---

Engineer skill for `.github/workflows/mint-preview.yml` — the workflow that creates Mintlify preview deployments for PRs.

---

## What the action does

Two triggers, each with a distinct path:

| Event | Behavior |
|---|---|
| `pull_request` (any base branch; types: opened/synchronize/reopened/ready_for_review) | No API call. Mintlify's native GitHub App handles PR previews automatically; the workflow just writes a summary pointer to the Checks tab. Draft PRs are skipped. |
| `push` to `refs/heads/release/**` | POSTs to Mintlify's preview-trigger API using `github.ref_name` as the branch. Captures `previewUrl`/`statusId`, writes them to the step summary, and — if there's an open PR whose head is the release branch — attaches a sticky comment with the preview link. |

**Why this shape?** Release branches are long-lived and need previews whether or not a PR is currently attached. PR-scoped previews are already handled end-to-end by the Mintlify GitHub App. Keying the API call on `push` to release instead of "PR whose base is release" avoids gaps where a release branch exists without a PR open against it.

**Concurrency:** `mintlify-preview-<PR#ornref>` with `cancel-in-progress: true` — back-to-back pushes to the same branch cancel prior in-flight runs, keeping us under the 5 req/min Mintlify limit.

---

## Mintlify API specifics (validated against `https://www.mintlify.com/docs/api/preview/trigger.md`)

- **Endpoint:** `POST https://api.mintlify.com/v1/project/preview/{projectId}`
  (note the `{projectId}` path parameter — easy to miss; earlier versions of this workflow used a wrong URL and silently 404'd)
- **Auth:** `Authorization: Bearer <MINTLIFY_TOKEN>`
- **Request body:** `{"branch": "<git-branch-name>"}`
- **Success response:** HTTP **202** with JSON `{ "statusId": "...", "previewUrl": "..." }`
- **Errors to handle explicitly:**
  - `400` — bad request (usually missing/empty `branch`)
  - `401`/`403` — bad token, wrong project ID, or plan doesn't include preview deployments (Pro/Enterprise only)
  - `429` — rate limit (**5 req/min per org**)
- **Poll preview build status** with `GET /v1/project/update/status/{statusId}` (see `https://www.mintlify.com/docs/api/update/status.md`) — not wired in yet.

---

## Required secrets

| Repo secret | Source | Notes |
|---|---|---|
| `MINTLIFY_KEY` | [Mintlify dashboard → API keys](https://dashboard.mintlify.com/settings/organization/api-keys) | Must be an **admin API key**, prefixed `mint_`. Inside the workflow this is mapped to the `MINTLIFY_TOKEN` env var before the curl call. |
| `MINTLIFY_PROJECT_ID` | Same page | Distinct from the key. Used as the `{projectId}` path parameter in the API call. |

Both are validated at the top of the trigger step. A missing value fails the step; a token that doesn't start with `mint_` emits a `::warning::` (the call will likely 401 but we still try, in case Mintlify changes the prefix scheme).

---

## File map

| File | Role |
|---|---|
| `.github/workflows/mint-preview.yml` | The workflow itself. All logic lives here — no helper scripts. |

---

## Design decisions (with context for future edits)

1. **Why `push` to release/**, not `pull_request` with base `release/**`?** Release branches live independently of PRs. Gating on "PR base is release" misses the case where someone pushes directly to a release branch or opens a PR from the release branch itself. Keying on pushes to the release branch catches all updates.
2. **Why let the GH App handle all PRs instead of duplicating?** Mintlify's GitHub App already generates previews for every PR event out of the box. Calling the API ourselves on PRs would produce two competing previews or waste rate-limit budget.
3. **Why find the PR from a push event?** When a push to a release branch arrives, any open PR with that branch as `head` should still get the preview link on it. `gh pr list --head <branch>` fetches it; if none exists, we just skip the comment (no-op).
4. **Why sticky comment instead of new ones?** Each push re-triggers preview creation; a non-sticky comment would spam the PR. `marocchino/sticky-pull-request-comment@v2` updates one comment in place via the `header: mintlify-preview` key.
5. **Why cancel in-progress?** Back-to-back pushes shouldn't queue multiple preview triggers against the 5-req/min API. The latest push wins.
6. **Why `if: pull_request == null || pull_request.draft == false`?** Mintlify previews cost build minutes; don't burn them on drafts. Push events have no `draft` concept — the `pull_request == null` short-circuit keeps pushes unaffected.

---

## Playbook: common tasks

### "Previews aren't showing up on release PRs"
1. Open the workflow run's "Trigger Mintlify preview" step — check the HTTP status printed at the top of the response log.
2. 401/403 → confirm `MINTLIFY_TOKEN` and `MINTLIFY_PROJECT_ID` in repo secrets match the current dashboard values. Also verify the org plan includes preview deployments.
3. 404 → the URL path changed upstream, or `MINTLIFY_PROJECT_ID` is wrong.
4. 429 → another workflow burned the org's 5-req/min budget; wait and re-run.
5. 202 but no sticky comment → check the "Post sticky preview comment" step and its `marocchino` action output; the issue is usually `pull-requests: write` permission missing or a fork PR (where secrets aren't available).

### "Add previews for another base branch"
Add the new pattern to the `on.pull_request.branches` list **and** add a matching `if:` conditional on a step that decides whether to hit the API vs. rely on the GH App. Don't forget the step summary block.

### "Want to show build status, not just 'queued'"
Mintlify returns a `statusId` on 202. Add a follow-up step that polls `GET /v1/project/update/status/{statusId}` until it reports `success` or `failed`, then update the sticky comment accordingly. Keep the poll bounded (e.g. 2 min with 10s sleep).

### "Change the API trigger to include metadata (commit SHA, author, etc.)"
Re-check the current API schema — it only documents `branch` as a request body field. Extra fields are ignored (best case) or 400 (worst). Don't invent fields; use the PR comment body for human-readable metadata instead.

---

## Working rules for this skill

- **Don't call the preview API on every event.** Preserve the draft-filter + base-branch gates. Previews cost plan budget.
- **Keep secret names stable** — `MINTLIFY_KEY` and `MINTLIFY_PROJECT_ID`. Renaming breaks existing repo configuration silently. (The internal env var is `MINTLIFY_TOKEN`; don't conflate the two.)
- **Always use the sticky-comment pattern** for preview links. Non-sticky comments create PR timeline noise.
- **When adding new HTTP status handling**, write an explicit `::error::` annotation — debugging opaque curl failures in CI logs is miserable.
- **Rate limit respect:** if you add a poller for `statusId`, keep its inner sleep ≥ 15s so a busy release day doesn't eat the 5-req/min budget.
- **Don't add workflow triggers for `push`**. This is PR-scoped; pushes to branches should not fire previews on their own.
