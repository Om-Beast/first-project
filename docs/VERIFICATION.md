# Verification protocol

The research question is documentation-based buildability. A successful documentation check does not establish a successful login, credential issuance or authenticated API operation.

## Fixed sample, chosen before field rechecks

| Category | Apps |
|---|---|
| CRM and Sales | HubSpot, Twenty |
| Support and Helpdesk | Pylon, Help Scout |
| Communications and Messaging | Pumble, WhatsApp Business |
| Marketing, Ads, Email and Social | Google Ads, Mailchimp |
| Ecommerce | Squarespace, Amazon Selling Partner |
| Data, SEO and Scraping | Ahrefs, Waterfall.io |
| Developer, Infra and Data platforms | Supabase, MongoDB Atlas |
| Productivity and Project Management | Airtable, Smartsheet |
| Finance and Fintech | Plaid, Xero |
| AI, Research and Media-native | NotebookLM, Fathom |

Selection was purposive, emphasizing ambiguous gates and multiple auth/API surfaces. Each app has five evaluated fields: auth, access, API, MCP, verdict. The denominator is exactly 100 fields, not all facts in the report and not 100 apps. Five opportunistic auth checks outside this sample are logged separately and excluded.

## Field-level rubric

- **Supported:** fresh primary docs support the original classification, including its qualifications. Scope wording may be refined without pretending there was a classification error.
- **Corrected:** a supported reviewed value replaces the first value. If the original was unknown, classify this as an unknown resolved, not an initial factual mistake.
- **Unresolved:** available evidence does not determine the field. Search silence never proves an API or MCP does not exist.
- **Verdict:** an analyst inference from the documented credential path and useful surface, not an authenticated execution outcome.

Access may be represented in audit logs as a composite of the normalized label, explanatory detail and production gate. A correction can concern that detail even when the high-level label remains unchanged. This applies to MongoDB Atlas's programmatic service-account path versus organization AI-client settings.

## Verification loops

1. Five discovery agents researched 20 apps each and saved their initial records.
2. Each batch audited a fixed four-app subset by reopening relevant primary pages or conducting fresh targeted searches.
3. Four different agents cross-reviewed other batches' subsets: 80 targeted field checks and one additional Intercom access check. This review was independent of the batch author, but shared the same overall AI system and public documentation.
4. Central adjudication addressed Pylon OAuth, Supabase GraphQL, NotebookLM trial licensing and Pumble's scoped MCP token. The final consistency pass also fixed known auth omissions outside the fixed sample.
5. Three additional primary-source checks confirm Attio admin-issued keys on all plans, Freshdesk Free/trial API limits, and Help Scout read-only MCP scope. These checks were performed by AI and are recorded separately from the fixed sample. Independent human review was not performed.

First-pass data, original audits and cross-review disagreements remain unmodified. `adjudications.json` records subsequent corrections; `verification.json` consolidates them for display. First-pass hashes are checked by the test suite.

## Interpreting the reported improvement

The first pass has 81 supported sample fields, 12 known-field corrections, three unknowns later resolved and four still unresolved. Remediation yields 96 supported fields on that same reviewed sample. The result measures agreement with the final documented interpretation. It is not an unbiased post-fix generalization estimate, independent gold-standard accuracy or a human benchmark.

Confidence is assigned by agents from evidence clarity. It is neither a percentage probability nor validated against a calibration set. Some unsampled rows may still have errors; the 80 apps outside the fixed sample do not inherit the sample's score.

## Evidence levels

| Evidence level | Performed in this work |
|---|---|
| Primary-source discovery, including indexed snippets | Yes |
| Fresh document audits on the fixed sample | Yes |
| Cross-agent challenge and source adjudication | Yes |
| Independent human checks | Not performed; three additional AI checks are recorded separately |
| Credential generation and authenticated API smoke tests | No |
| Production integration or MCP execution | No |
| Live Composio catalog snapshot | No; optional SDK adapter provided |

When a primary page failed to open, its evidence is marked `search`; no successful browser read is implied. The known stale Twenty localized CLI URL was replaced with readable first-party source documentation. Vendor conflicts and announced/beta/read-only MCP scope are retained in app notes.
