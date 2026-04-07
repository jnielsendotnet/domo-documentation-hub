# KB Article Style Rules

## Voice and tense
- Write in present tense: "This opens the panel" not "This will open the panel."
- Use active voice. Avoid passive voice unless who performs the action does not matter.
- Use "select" not "click."
- Contractions are acceptable unless you need to emphasize "not."
- Spell out numbers less than 10.
- Never use "utilize" — use "use."
- No exclamation points.
- Use the Oxford comma.
- Eliminate unnecessary words ("will," "you are able to," "that").
- Avoid Latin expressions (i.e., e.g., etc.) — use "such as," "as in," or a list.
- Use "allowlist" and "blocklist," never "whitelist" or "blacklist."

## Text emphasis
- **Bold** static UI elements (fields, menus, buttons, icons). For a series: **Admin** > **Security** > **Whitelist** (do not bold the >).
- *Italics* for variables the user fills in with their own data.
- "Quotation marks" for on-screen text not used as an interface element, and for DataSet column names and ETL actions.
- `Code style` for code snippets.

## Domo-specific terminology (capitalize exactly as shown)
- DataSet, DataFlow, DataFusion, Magic ETL, Beast Mode, AppDB
- Admin Settings (not bolded, not a UI element)
- Data Center, Alerts Center, Knowledge Base
- Dashboard (not Page), Dashboard Filters (not Page Filters)
- Grants (lowercase unless naming a specific grant, e.g., Manage All Users grant)
- "select" not "click"; "field" not "box"; "pill" for rounded non-button elements
- Do not use: Dojo (use Community Forums), KPI card (use Visualization Card), image card (use Doc Card), Domo story (use Dashboard), Drilldown (use Drill Path or "drill into"), Page/Page Filters

## Links
- Internal article links: `[link text](/s/article/Article-Title)`
- Section links: `[link text](/s/article/Article-Title#section-heading)`
- External links: `[link text](https://full-url.com)`

## Images
- Auto-sized screenshot wrapped in Frame: `<Frame>![alt text](/images/kb/image-name.png)</Frame>`
- Specifically sized: `<Frame><img alt="alt text" src="/images/kb/image-name.png" style={{width: 500, height: 500}}/></Frame>`
- Inline icon: `<img alt="alt text" src="/images/kb/icon-name.png" style={{width: 20, height: 20, display: 'inline', verticalAlign: 'start', margin: '0'}}/>`
- Screenshots should be taken in Modocorp or a demo instance, not the company instance.

## Callout components (always bold the label)
- `<Note>**Note:** Text here.</Note>`
- `<Warning>**Important:** Text here.</Warning>`
- `<Tip>**Tip:** Text here.</Tip>`

## Beta features
- Do not put "(Beta)" in the article title. A single article can cover a mix of GA and beta functionality, so beta status is marked at the section level, not the title level.
- Immediately below the heading for any beta section or feature, add:
  ```mdx
  <Note>
    **Note:** This feature is in beta. Contact your Domo account team to join.
  </Note>
  ```
- If the entire article covers only beta functionality, place this note at the top of the Intro section.

## FAQ
- Place at the bottom of the article, above Troubleshooting if it exists.
- Always use `<AccordionGroup>` containing `<Accordion title="Question?">` items.
