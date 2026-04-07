---
name: new-kb-article
user-invocable: true
description: "write a new KB article, generate knowledge base article, draft a KB doc, create a new article, write documentation, create MDX article"
argument-hint: "article title or topic, or paste any source material"
---

Generate a new Domo Knowledge Base article as an MDX file.

The user will provide: $ARGUMENTS

---

## Step 1: Run the kb-intake skill

Before writing anything, invoke the `kb-intake` skill, passing `$ARGUMENTS` directly as the input. Let the Socratic intake conversation run to completion, ending with the Article Intake Summary.

Use the original source material and the Article Intake Summary as the authoritative source of truth for everything that follows — it defines the title, persona, structure, scope, and key details of the article. If there are conflicts between the original source material and the Article Intake Summary, the Article Intake Summary takes precedence. Be sure to call out any discrepancies and be clear to the user about which information is taken as the truth.

---

## Step 2: Gather release information

After the Article Intake Summary is confirmed, ask the following two questions before writing:

1. **Release status:** What is the release status of the feature(s) covered in this article? For each distinct feature or section, is it GA (generally available) or beta? If mixed, which parts are beta?
2. **Planned branch cut date:** What is the planned **branch cut date** for this release? This is the internal branch name (NOT the feature release date).

---

## Step 3: Write the article

Once the Article Intake Summary and release information are confirmed, create the MDX file. Do not ask for any information already answered.

Create a new MDX file in `s/article/` using the filename format `Article-Title-Here.mdx` (Title Case, hyphen-separated, no special characters).

Follow the file structure in `.claude/skills/article-templates/file-structure.md` and apply all style rules in `.claude/skills/article-templates/style-rules.md`. Read both files before writing.

---

## Output

1. Write the completed MDX file to `s/article/Article-Title-Here.mdx`.
2. Tell the user the file path and suggest running `/add-to-nav` to register it in `docs.json` navigation if they want it to appear on the site.
3. Note any sections left as placeholders (screenshots, specific grant names, etc.) that the user will need to fill in.
