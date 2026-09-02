---
name: mcp-orchestration
description: |
  Design and implement multi-system agent workflows using MCP: discover tools, authenticate,
  chain API calls, and document integrations. Use when Wong mentions MCP, Model Context Protocol,
  API orchestration, connecting agents to ERP/MES/QMS/Slack, or building tool adapters.
---

# MCP Orchestration

## Prerequisites

- `@MCP-ORCHESTRATION.md` and `@SYSTEMS-AND-APIS.md` in context
- `.cursor/mcp.json` or global MCP config reviewed

## Workflow

### 1. Inventory

1. List required systems for the workflow
2. `GetDynamicTools` — catalog available MCP namespaces
3. Map each system → MCP tool or gap (needs custom server)

### 2. Auth

- If namespace status is `needsAuth`, stop and guide Wong through Cursor MCP authentication
- Never embed secrets in skills or markdown — env vars only

### 3. Design the orchestration

Choose a pattern from `MCP-ORCHESTRATION.md`:

- Human-in-the-loop approval (default for writes in regulated domains)
- Scheduled sync (staging → validate → promote)
- Exception router (classify → route to correct tool)

Document as:

```
Trigger → Tool A (read) → Transform → [Approval?] → Tool B (write) → Notify
```

### 4. Implement

1. Read full tool schema before each `CallDynamicTool`
2. Prefer small, composable tools over one mega-call
3. Add error handling: retries for transient failures; clear messages for auth/validation errors
4. Log tool names and args (redact secrets) for audit

### 5. Custom MCP (only if needed)

If no server exists:

1. Confirm API stability and auth model
2. Use `building-mcp-server-on-cloudflare` skill or org standard
3. Register in `SYSTEMS-AND-APIS.md`
4. Add compliance notes for quality/manufacturing writes

### 6. Test plan

- [ ] Happy path with sandbox/staging credentials
- [ ] Auth failure handling
- [ ] Rate limit behavior
- [ ] Idempotent retry on write tools
- [ ] Human approval gate for prod writes

### 7. Capture

Update `SYSTEMS-AND-APIS.md` and `LEARNING-LOG.md` with endpoints, quirks, and env var names.

## Invocation tip for Wong

For long integration sessions: run `/mcp-orchestration` then **Option+Enter** (Custom Mode) to keep this skill active throughout the chat.
