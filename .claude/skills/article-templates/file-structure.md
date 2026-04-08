# KB Article File Structure

New KB articles live in `s/article/` with filenames in Title Case, hyphen-separated, no special characters (e.g., `Article-Title-Here.mdx`).

The file must follow this structure exactly. Only include sections that apply — omit any that don't (except Intro, Required Grants, and FAQ, which are always present).

```mdx
---
title: "Article Title Here"
---



## Intro

Brief overview of what this article covers and why it matters to the user. One to three sentences.

---



## Required Grants

List the grants a user needs to complete the tasks in this article. If none are required, write "No special grants are required."



## Accessing [Feature Name]

Step-by-step instructions for navigating to the feature. Use numbered steps.

1. In the navigation header, select **[Menu Item]**.
   The [result of the action].

2. Select **[Next Element]**.



## Creating [Something]

Step-by-step instructions. Follow the CRUD order (Create, Review, Update, Delete) — only include sections that apply.

1. First step. Include orienting language if needed.
   
   <Frame>![Alt text describing the screenshot](/images/kb/image-name.png)</Frame>

2. Second step. Always an action.

3. (Optional) Optional step.

4. (Conditional) Conditional step.



## FAQ


<AccordionGroup>

<Accordion title="Frequently asked question?">
Frequently asked answer.
</Accordion>

<Accordion title="Frequently asked question?">
Frequently asked answer.
</Accordion>

</AccordionGroup>
```
