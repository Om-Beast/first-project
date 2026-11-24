# Agent Access Atlas

**Om Kesharwani · Composio AI Product Ops take-home**

[Live case study](https://om-beast.github.io/first-project) · [Source repository](https://github.com/Om-Beast/first-project)

An evidence-backed access audit of the exact 100 apps in Composio's AI Product Ops assignment. It answers a practical question: **can a developer obtain credentials, reach useful API actions, and turn this app into an agent toolkit today?**

The public source browser includes every source file, a ZIP download and a read-only Git endpoint that can be cloned without an account. The case study is **one self-contained HTML page** at [`dist/index.html`](dist/index.html), with 100 searchable rows, expandable evidence, category comparisons, CSV/JSON exports, the agent workflow and an inspectable verification log.

## Reproduce in under a minute

Python 3.10 or later. The core project uses only the Python standard library. No package installation, API key or network is needed to rebuild the shipped report.

```bash
git clone https://github.com/Om-Beast/first-project.git agent-access-atlas
cd agent-access-atlas
python3 -m agent.research --replay
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. The HTML can also be opened directly; its table, charts, filters and app detail panels use embedded data. Relative download links work when served over HTTP.

## Findings

- **68/100** have a documented free or trial credential path. Self-hosted and local tools are counted separately.
- **52** are build-first prototype candidates; **32** have meaningful conditions; **11** need outreach; **3** remain investigations; **2** need a local wrapper.
- **70** document OAuth on an investigated API or native MCP surface. Auth methods overlap; these are not exclusive market shares.
- Developer and productivity platforms offer the clearest prototype access. Production entitlement and public-app distribution can still impose additional gates.
- The most common primary friction outside the build-first queue is production authorization, distribution or compliance: **18/48** cases. This is analyst coding, one primary category per app; secondary blockers remain visible.
- MCP presence alone is insufficient: Mailchimp's is documentation-only, new Help Scout connections are read-only, and Copper's is announced with a waitlist.
- Unknown does not mean partner-gated. Fanbasis and Paygent Connect remain unresolved; conflicting iPayX documentation is disclosed.

These are documentation findings as of **24 November 2026**, not successful authenticated API tests or confirmed gaps in Composio's catalog.

## What ran, and what is reproducible

Live discovery ran through hosted Codex agents using web search and page-open tools, split into five bounded research batches. Every app received a structured record. First-pass snapshots were saved before fresh source audits; another agent independently challenged 80 sampled fields, plus one extra Intercom access check. A final consistency review reconciled the remaining scope omissions.

The portable runner in [`agent/research.py`](agent/research.py) is an alternative fresh-execution route using OpenAI Responses web search and strict structured output. Its provider request, extraction, citation gate and retry behavior have offline tests. **A direct OpenAI API run was not performed in this workspace.** Offline replay regenerates the report from preserved research artifacts; it does not pretend to refresh the facts.

AI tooling was used for research, code and review. Three additional factual checks were completed through fresh primary-document reads and are recorded in `data/additional_doc_checks.json`. These are AI checks; independent human review was not performed. No time-spent claim, paid account, generated credential or successful vendor API call is invented.

## Fresh research

Set environment variables in your shell or secret manager. `.env.example` documents the names; the runner intentionally does not load a secret file.

```bash
export OPENAI_API_KEY='your-provider-key'
export OPENAI_MODEL='a-compatible-model-you-have-access-to'

# Small, reviewable run first
python3 -m agent.research --live --ids 1,2,3 --audit --resume

# Full set, after reviewing the small run and provider costs
python3 -m agent.research --live --ids all --audit --resume
```

Live provider use incurs the provider's normal charges. No cost estimate is presented as measured spend. Records are written per app to ignored `runs/latest/first/`; a fresh second pass goes to `runs/latest/audit/`. Source URLs, usage returned by the provider, input hashes and response IDs are checkpointed without logging API keys. Failed or unsupported records go to a review queue and cause a nonzero exit code. Nothing overwrites the shipped research.

The runner requests live web search with primary-domain hints, a strict JSON schema and complete consulted-source traces. It rejects an evidence URL that is absent from that trace. This prevents fabricated citations; it does **not** prove semantic entailment, so document review is still required. Live results require adjudication before replacing the canonical batch files.

The selected model must support the Responses API, web search and structured output together. See the official [web search guide](https://developers.openai.com/api/docs/guides/tools-web-search?api-mode=responses) and [structured output guide](https://developers.openai.com/api/docs/guides/structured-outputs).

## Verification, with the denominator shown

The fixed purposive sample is 20 apps across all ten categories, five fields per app: auth, access, API, MCP and verdict. Against the final reviewed document interpretation:

| Result | First pass | After remediation |
|---|---:|---:|
| Supported fields | 81/100 | 96/100 |
| Known-field corrections | 12 | Applied |
| Unknown fields resolved | 3 | Resolved |
| Still unresolved | 4 | 4 |

The final score includes corrections made against the same reviewed sources. It is **not a held-out accuracy result**, a human accuracy measurement, or an estimate of correctness across the entire population. Five extra opportunistic corrections are excluded from the 100-field denominator. The independent review's original disagreements remain visible, even after central adjudication corrected the data.

Examples include missing Supabase project auth/GraphQL, Plaid's separately scoped OAuth service, Pylon's native MCP OAuth, Mailchimp's Basic transport and NotebookLM Enterprise's trial license. Resolving previously unknown MCPs for WhatsApp, Squarespace and Xero is evidence enrichment, not an initial factual error.

## Research artifacts

| Path | Purpose |
|---|---|
| `data/apps.json` | Exact 100-app seed list and primary-domain discovery hints |
| `data/batch*.first.json` | Immutable first-pass records |
| `data/first_pass_manifest.json` | SHA-256 checksums for those snapshots |
| `data/batch*.final.json` | Reviewed canonical records |
| `data/audit*.json` | Original field audits, including explicitly excluded extra checks |
| `data/cross_review*.json` | Independent agent review, before adjudication |
| `data/adjudications.json` | Follow-up corrections with sources |
| `data/verification.json` | Consolidated sample log used by the page |
| `data/results.json` | Full final dataset with field-bound evidence |
| `data/evidence_index.json` | Source index and hashes of internal retrieval receipts |
| `tools/build.py`, `tools/page.html` | Deterministic validation, aggregation and one-page presentation |
| `tests/test_research.py` | Contract, citation, audit arithmetic and transport checks |
| `docs/VERIFICATION.md` | Sampling rubric, evidence levels and limits |

Full raw vendor-document extracts are kept out of the published repository. The concise field notes, links and retrieval digests retain provenance without redistributing full documentation pages.

## Optional Composio SDK check

```bash
python3 -m pip install composio
export COMPOSIO_API_KEY='your-project-key'
python3 -m agent.catalog
```

This adapter uses the official SDK's toolkit list and cursor pagination to create a project-specific catalog snapshot. It was **not run** here. Catalog presence is separate from an app's native/community MCP status. Join only on reviewed catalog identities and aliases, never guessed slugs. The report makes no net-new toolkit-gap claims. [Official toolkit SDK reference](https://docs.composio.dev/reference/sdk-reference/python/toolkits).

## Design decisions

- A buildless static page keeps review and hosting simple; no database or account is needed.
- The full dataset is embedded in the HTML and exported as ordinary JSON/CSV, so both people and agents can consume it.
- Free/trial, paid, approval, customer-only, local and unknown access are different labels. API surface, production gates and MCP maturity remain visible in each detail panel.
- Verdicts are explicit analyst judgments, not model confidence scores. Confidence is an evidence-quality flag and is not calibrated.
- Public API writes, destructive tools, live credentials and OAuth consent screens were outside this research-only scope.

## Publish the static source mirror

After rebuilding the report, `python3 -m tools.publish_source` creates the source browser, complete ZIP and read-only Git HTTP assets. It publishes an explicit file allowlist and excludes raw retrieval transcripts, real credentials and hosting metadata. The mirror is a generated snapshot; edits belong in the source checkout.
