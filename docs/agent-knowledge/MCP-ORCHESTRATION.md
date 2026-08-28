# MCP Orchestration Playbook

> Attach with `@MCP-ORCHESTRATION.md` or run `/mcp-orchestration` when wiring agents to multiple APIs.

---

## What MCP gives you

**Model Context Protocol (MCP)** lets an agent discover and call tools exposed by servers — your bridge to ERP, Slack, databases, and custom microservices.

```
┌──────────┐     discover      ┌─────────────┐
│  Agent   │ ────────────────► │ MCP server  │
│ (Cursor) │ ◄──────────────── │ (tools)     │
└──────────┘     tool results  └──────┬──────┘
                                       │
                                       ▼
                                 External APIs
```

---

## When to use what

| Need | Start with | Build custom when |
|------|------------|-------------------|
| Slack, Notion, Google | Official / plugin MCP | — |
| Many SaaS apps | Composio MCP | single-app depth needed |
| Internal ERP API | Custom MCP or Composio action | no connector exists |
| SQL / warehouse | Database MCP | — |
| Cross-session memory | `@modelcontextprotocol/server-memory` | team wiki via Notion MCP |

---

## Agent workflow for MCP tasks

1. **Discover** — `GetDynamicTools` (or Cursor MCP panel) to list namespaces and schemas.
2. **Authenticate** — if `needsAuth`, complete OAuth in Cursor settings once.
3. **Call** — use tool with validated arguments; never guess parameter shapes.
4. **Compose** — chain tools: read ERP → transform → post Slack → log Notion.
5. **Capture** — update `SYSTEMS-AND-APIS.md` and `LEARNING-LOG.md`.

---

## Orchestration patterns (supply chain / quality)

### Pattern A: Human-in-the-loop approval

```
Agent reads data (MCP read tools)
→ Drafts action (email, ticket, report)
→ Posts to Slack with Approve / Reject buttons (or waits for Wong)
→ On approval only: MCP write tool executes
```

### Pattern B: Scheduled sync

```
Cron / Cloud Agent trigger
→ Pull master data (read MCP)
→ Transform in code
→ Write to staging table
→ Validation job → promote to prod
```

### Pattern C: Exception router

```
Webhook or poll for alert
→ Classify with rules + optional LLM
→ Route to correct MCP (create QMS NCR vs expedite PO)
→ Log outcome
```

---

## Custom MCP checklist

- [ ] Tool names are verb-noun (`get_purchase_order`, not `po`)
- [ ] Args validated with schemas (zod, JSON Schema)
- [ ] Secrets in env vars only
- [ ] Idempotent writes where possible
- [ ] Rate limiting and retries documented
- [ ] Audit log for regulated writes

---

## Example `.cursor/mcp.json` (template)

```json
{
  "mcpServers": {
    "slack": {
      "url": "https://mcp.slack.com/..."
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "/path/to/wong-memory.jsonl"
      }
    }
  }
}
```

Adjust per Cursor docs for your version. Store secrets outside the repo.

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Tools not listed | MCP server running; auth complete |
| `needsAuth` | Cursor Settings → MCP → authenticate |
| Wrong tool schema | Call `GetDynamicTools` before invoke |
| Cloud Agent missing MCP | Configure in environment or project `mcp.json` |

---

## References

- [Cursor MCP docs](https://cursor.com/docs/context/mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
- Building custom servers: `/building-mcp-server-on-cloudflare` skill (if using Workers)
