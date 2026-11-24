# Additional primary-source checks

Checked on 24 November 2026 through fresh document reads. Reviewer: AI documentation audit. These checks are separate from the fixed 100-field sample; independent human review was not performed.

| App / field | Confirmed finding | Primary source |
|---|---|---|
| Attio / access | Scoped API keys are available on all plans and created by a workspace admin. | https://attio.com/help/reference/apps/generating-an-api-key |
| Freshdesk / access | The cited rate-limit table lists zero API calls on Free and 50 calls per minute during a trial. | https://support.freshdesk.com/support/solutions/articles/225439-what-are-the-rate-limits-for-the-api-calls-to-freshdesk |
| Help Scout / mcp | New MCP connections are read-only and require an API-enabled plan. Some earlier beta accounts retain write tools. | https://docs.helpscout.com/article/1779-help-scout-mcp-server |

The Help Scout beta exception is retained: a small set of older beta accounts may have write tools; newly created connections are read-only. No credential issuance or authenticated API/MCP execution was tested.
