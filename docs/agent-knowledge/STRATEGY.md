# Agent Knowledge Base Strategy (for Wong)

This guide explains how to make Cursor agent workers behave like a close collaborator who remembers your style, domain, and workflows.

## The core idea

LLMs do not remember past chats by default. **Persistence is something you design**, not something you wait for. You build a layered system:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: WHO you are          → ABOUT-WONG.md + profile skill │
│  Layer 2: HOW you work         → rules (.mdc) + user rules     │
│  Layer 3: WHAT you automate    → domain skills + reference docs │
│  Layer 4: WHICH tools to use   → MCP config + orchestration skill │
│  Layer 5: WHAT we learned      → LEARNING-LOG.md + decision log  │
└─────────────────────────────────────────────────────────────┘
```

Each layer answers a different question. Together they make every new chat feel informed, not cold-started.

## Rules vs Skills vs Reference docs

| Artifact | When to use | Example |
|----------|-------------|---------|
| **Rule** (`.cursor/rules/*.mdc`) | Short, always-on constraints | "Prefer Python + pandas; explain trade-offs" |
| **Skill** (`.cursor/skills/*/SKILL.md`) | Multi-step workflows the agent should follow | "Run supplier risk check via MCP" |
| **Reference doc** (`docs/agent-knowledge/*.md`) | Long context you attach with `@` when needed | ERP field mappings, SOP glossary |
| **User Rules** (Cursor Settings) | Personal prefs across all repos | Communication style, role |

**Rule of thumb:** If it fits on one screen and should apply often → rule. If it is a procedure with steps → skill. If it is reference material → markdown doc you `@`-mention.

## Recommended folder layout

```
my-org-repo/                          # or a dedicated "agent-playbook" repo
├── .cursor/
│   ├── rules/
│   │   └── wong-working-style.mdc    # light, always-on preferences
│   ├── skills/
│   │   ├── wong-profile/SKILL.md     # loads your personal context
│   │   ├── supply-chain-orchestration/SKILL.md
│   │   ├── manufacturing-quality/SKILL.md
│   │   └── mcp-orchestration/SKILL.md
│   └── mcp.json                      # MCP server connections
└── docs/agent-knowledge/
    ├── ABOUT-WONG.md                 # your "friend profile"
    ├── DOMAIN-SUPPLY-CHAIN.md
    ├── DOMAIN-MANUFACTURING-QUALITY.md
    ├── MCP-ORCHESTRATION.md
    ├── SYSTEMS-AND-APIS.md           # your actual platforms
    └── LEARNING-LOG.md               # grows after each project
```

### Personal vs project vs org

| Location | Scope | Version control |
|----------|-------|-----------------|
| `~/.cursor/skills/` | You, all local projects | Your machine only |
| `.cursor/` in repo | Team + Cloud Agents | Git (recommended for work) |
| Cursor **User Rules** | You, all projects | Cursor account sync |

**Cloud Agents** do not see `~/.cursor/skills/` on your laptop. Put shared knowledge **in the repo** if Cloud Agents should use it.

## How to invoke in a new chat

### 1. Attach context with `@`

In any chat, type `@` and pick:

- `@ABOUT-WONG.md` — personal context
- `@supply-chain-orchestration` — skill folder
- `@wong-working-style` — a rule by name
- `@Chats` — prior conversation threads

### 2. Run a skill with `/`

```
/supply-chain-orchestration
```

Runs the workflow for that message.

### 3. Custom Mode (session-long skill)

Type `/mcp-orchestration` then **Option+Enter** (Alt+Enter on Windows). The skill stays active for the whole chat — good for long orchestration sessions.

### 4. Always-on rules

Rules with `alwaysApply: true` load automatically. Keep these **short** (under ~50 lines). Put depth in skills and reference docs.

### 5. User Rules (global)

**Cursor → Settings → Rules → User Rules**

Paste stable preferences that should apply everywhere (e.g. "I am a data scientist; prefer working in code").

## Parallel chats for topic management

Use **one chat per concern**, not one mega-thread:

| Chat branch | Purpose | Attach |
|-------------|---------|--------|
| **Profile & style** | Refine ABOUT-WONG, working preferences | `@ABOUT-WONG.md` |
| **Supply chain** | Planning, logistics, supplier workflows | `@DOMAIN-SUPPLY-CHAIN.md` + `/supply-chain-orchestration` |
| **Manufacturing / QA** | SPC, CAPA, inspection automation | `@DOMAIN-MANUFACTURING-QUALITY.md` |
| **MCP & integrations** | API wiring, auth, tool design | `@MCP-ORCHESTRATION.md` + `/mcp-orchestration` |
| **Project X** | One automation initiative | Project repo + relevant domain docs |

After a good session, ask the agent:

> "Capture what we learned into LEARNING-LOG.md and update the relevant domain doc."

That is how the system gets smarter over time.

## MCP orchestration strategy (supply chain context)

Your instinct is right: MCP is the **adapter layer** between the agent and your platforms (ERP, MES, QMS, WMS, Slack, email, spreadsheets).

```
Agent  →  MCP tool  →  API / database / file
         (discover)     (your systems)
```

### Recommended approach

1. **Start with existing MCP servers** (Slack, Notion, Google Drive, Composio, etc.) before building custom ones.
2. **One skill per integration pattern** — e.g. "pull PO status from ERP", not one giant skill.
3. **Document auth in `SYSTEMS-AND-APIS.md`** — never put secrets in markdown; reference env var names only.
4. **Build custom MCP** only when no server exists and the API is stable.

### Compliance note

For manufacturing/quality, log:

- Who triggered an action (human vs agent)
- What data was read/written
- Which system of record was updated

Add this to your orchestration skill when touching QMS or batch records.

## Growing memory over time

| Method | Best for |
|--------|----------|
| **LEARNING-LOG.md** | Decisions, gotchas, "we tried X, Y worked" |
| **Update domain docs** | Stable facts (glossary, field maps, SOP refs) |
| **Rules/skills** | Repeatable behavior the agent should automate |
| **MCP memory server** | Cross-repo facts (optional; `@modelcontextprotocol/server-memory`) |
| **Notion / wiki via MCP** | Team-visible knowledge (`knowledge-capture` skill) |

End each project with a **5-minute capture ritual**:

1. What did we automate?
2. What surprised us?
3. What should the next agent know?
4. Append to `LEARNING-LOG.md`.

## Next steps for Wong

1. Fill in `ABOUT-WONG.md` (start with the questionnaire section).
2. List your real systems in `SYSTEMS-AND-APIS.md`.
3. Enable 1–2 MCP servers you already use.
4. Run one pilot workflow with `/supply-chain-orchestration`.
5. After the pilot, update `LEARNING-LOG.md`.

## Quick invocation cheat sheet

```
@ABOUT-WONG.md                    # who you are
@DOMAIN-SUPPLY-CHAIN.md           # domain context
/supply-chain-orchestration       # run workflow once
/mcp-orchestration + Option+Enter # session-long integration mode
@LEARNING-LOG.md                  # what we learned before
```
