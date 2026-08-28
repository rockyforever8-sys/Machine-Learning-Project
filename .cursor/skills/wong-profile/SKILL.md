---
name: wong-profile
description: |
  Load Wong's personal collaboration profile, working style, and preferences.
  Use when starting a new session, when Wong says "work with me like you know me",
  or when personal context would improve tone, priorities, or technical choices.
  Triggers on: Wong, personal context, how I like to work, my preferences.
disable-model-invocation: false
---

# Wong Profile — Personal Context

## When to use

- New chat where relationship context matters
- Wong asks for help aligned with his style (data scientist, code-first)
- Unclear whether to optimize for speed vs compliance vs exploration

## Steps

1. **Read** `docs/agent-knowledge/ABOUT-WONG.md` (or ask Wong to `@`-attach it).
2. **Check** `docs/agent-knowledge/LEARNING-LOG.md` for recent decisions in the same domain.
3. **Apply preferences:**
   - Work in code; propose runnable scripts over abstract advice.
   - Explain trade-offs for integration and automation choices.
   - Be cautious with writes to production QMS/MES/ERP — confirm first.
4. **Match communication:** concise, structured, complete sentences; markdown links for URLs.
5. **End of session:** offer to append learnings to `LEARNING-LOG.md`.

## If profile is incomplete

Ask Wong 1–3 targeted questions from the questionnaire in `ABOUT-WONG.md`, then offer to update that file with his answers.

## Related files

| File | Purpose |
|------|---------|
| `ABOUT-WONG.md` | Who Wong is |
| `SYSTEMS-AND-APIS.md` | Platforms and MCP registry |
| `LEARNING-LOG.md` | Evolving memory |
