# Agent Knowledge Base

Starter templates for Wong's supply chain / manufacturing / quality agent workflows.

## Quick start

1. Read the strategy: [`docs/agent-knowledge/STRATEGY.md`](docs/agent-knowledge/STRATEGY.md)
2. Fill in your profile: [`docs/agent-knowledge/ABOUT-WONG.md`](docs/agent-knowledge/ABOUT-WONG.md)
3. List your systems: [`docs/agent-knowledge/SYSTEMS-AND-APIS.md`](docs/agent-knowledge/SYSTEMS-AND-APIS.md)

## Invoke in a new chat

```
@ABOUT-WONG.md
/supply-chain-orchestration
```

For a full integration session:

```
/mcp-orchestration
```
then **Option+Enter** (Custom Mode).

## Structure

```
.cursor/
├── rules/wong-working-style.mdc    # always-on light preferences
└── skills/
    ├── wong-profile/
    ├── supply-chain-orchestration/
    ├── manufacturing-quality/
    └── mcp-orchestration/

docs/agent-knowledge/
├── STRATEGY.md
├── ABOUT-WONG.md
├── DOMAIN-*.md
├── MCP-ORCHESTRATION.md
├── SYSTEMS-AND-APIS.md
└── LEARNING-LOG.md
```

## Parallel chat topics

| Chat | Attach |
|------|--------|
| Personal profile | `@ABOUT-WONG.md` |
| Supply chain | `@DOMAIN-SUPPLY-CHAIN.md` |
| Quality / MES | `@DOMAIN-MANUFACTURING-QUALITY.md` |
| Integrations | `@MCP-ORCHESTRATION.md` |

End sessions with: *"Capture what we learned in LEARNING-LOG.md"*
