# DOS NEGOCIOS — NUNCA MEZCLAR

| | FURNITURE CLEAN SERVICES | MAGNEX INTERNATIONAL |
|---|---|---|
| Tipo | Limpieza/fumigación, Panamá | Bróker commodities sin inventario |
| Email | jdelcid@furniturecleans.com (Jessica) | mgonzalez@magnexinternational.com (Mike) |
| WhatsApp | +507 6233-4632 | +507 6593-3059 |

## Mike (CEO)
- Miguel Angel González Remond | mgonzalezremond@gmail.com | mrzeush2o@gmail.com
- Directo, en español, sin repetir preguntas ya respondidas

## MAGNEX INTERNATIONAL

### Infraestructura ✅
- Dominio: magnexinternational.com (Namecheap)
- Email: mgonzalez@magnexinternational.com (Zoho Mail Lite $1/mes)
- SMTP: smtppro.zoho.com | IMAP: imappro.zoho.com | DNS: MX+SPF+DKIM+DMARC ✅

### Apollo.io Pro ($99/mes)
- Mailbox ID: 6a14d2271d3a61001c4d3b7d
- **Secuencia MAGNEX Pintura Industrial** (ID: 6a277369cff2870014970d16)
  - 3 pasos: Día 0 / Día 4 / Día 7 — Auto email
  - **38 contactos activos** | pendientes de cargar: resto
  - Variables: `{{first_name}}` y `{{company}}` (NO usar `{{organization.name}}`)
- **Secuencia Furniture Cleans B2B** (ID: 6a28cf473d9ce200200fd649)
  - **15 contactos activos**

### Productos (3 fases)
| Producto | Estado | Comisión | Plazo |
|---|---|---|---|
| Pintura Industrial | ✅ Secuencia activa | $800–$3,000 | 30 días |
| Aceite de Palma | ⏳ Fase 2 | $1,200–$6,000 | 60 días |
| Fertilizantes/Acero | ⏳ Fase 3 | $2,000–$8,000 | 90 días |

### Proveedores Pintura Industrial (Alibaba FOB)
- Foshan Brightsun: $2.00–2.60/kg, MOQ 10kg
- Foshan Nanhai Huaren: $8.99–9.99/kg, MOQ 20kg (astilleros)
- Shanghai Cloud: $15–45/kg, MOQ 2kg (premium)

### Protocolo de cierre
1. Calificar volumen/frecuencia → 2. Firmar NCNDA → 3. Proveedor Alibaba FOB
4. Sumar 3% comisión → 5. Emitir FCO → 6. Buyer abre LC irrevocable UCP 600

## FURNITURE CLEAN SERVICES
- Meta Ads: act_735269780152091 | Pixel: 885240155980714 | $7/día
- Make.com: escenario ID 5135275 → lead → email automático a Jessica c/15 min
- WhatsApp Business Premium: +507 6233-4632 ($18/mes)
- ❌ Buzón Apollo jdelcid@furniturecleans.com NO conectado aún

## Credenciales (en .env local — nunca en el repo)
```
APOLLO_API_KEY=...
ANTHROPIC_API_KEY=...
ZOHO_EMAIL=mgonzalez@magnexinternational.com
ZOHO_PASSWORD=...
```

## App Streamlit (este repo)
- `app.py` — Dashboard principal
- `pages/1_MAGNEX_B2B.py` — Cotizador B2B con FCO
- `pages/2_Furniture_Cleans.py` — Cotizador + WhatsApp
- `pages/3_CRM_Leads.py` — CRM + importación CSV Apollo
- `pages/4_Automatizacion.py` — Envío emails Zoho por lote
- `database.py` — SQLite unificado
- `email_sender.py` — SMTP smtppro.zoho.com

## Tareas Pendientes
- [ ] Cargar siguiente tanda de leads MAGNEX Pintura Industrial en Apollo
- [ ] Revisar actividad Apollo ambas secuencias (MAGNEX + Furniture Cleans)
- [ ] LinkedIn Mike como CEO + página empresa MAGNEX
- [ ] Meta Ads MAGNEX ($5/día → WhatsApp)
- [ ] Secuencias Aceite de Palma y Fertilizantes (fases 2 y 3)

## Completado
- [x] App desplegada: https://cotizador-ventas.streamlit.app/
- [x] Secuencia MAGNEX Pintura Industrial activa (38 contactos)
- [x] Secuencia Furniture Cleans B2B activa (15 contactos)
- [x] DNS magnexinternational.com OK (MX/SPF/DKIM/DMARC)
- [x] Cotizador B2B + CRM + Automatización Zoho + integración Apollo

## Reglas para Claude
- Siempre en español, directo, sin rodeos
- Ahorrar tokens — respuestas cortas
- No crear archivos innecesarios
- Commit y push después de cada cambio

---

# Ruflo — Claude Code Configuration

## Rules

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER create documentation files unless explicitly requested
- NEVER save working files or tests to root — use `/src`, `/tests`, `/docs`, `/config`, `/scripts`
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- NEVER add a `Co-Authored-By` trailer to user commits unless this project's `.claude/settings.json` has `attribution.commit` set (#2078). The Claude Code Bash tool may suggest one in its default commit-message template — ignore it. `Co-Authored-By` is semantic authorship attribution under git/GitHub convention; the tool is the facilitator, not a co-author.
- Keep files under 500 lines
- Validate input at system boundaries

## Agent Comms (SendMessage-First Coordination)

Named agents coordinate via `SendMessage`, not polling or shared state.

```
Lead (you) ←→ architect ←→ developer ←→ tester ←→ reviewer
              (named agents message each other directly)
```

### Spawning a Coordinated Team

```javascript
// ALL agents in ONE message, each knows WHO to message next
Agent({ prompt: "Research the codebase. SendMessage findings to 'architect'.",
  subagent_type: "researcher", name: "researcher", run_in_background: true })
Agent({ prompt: "Wait for 'researcher'. Design solution. SendMessage to 'coder'.",
  subagent_type: "system-architect", name: "architect", run_in_background: true })
Agent({ prompt: "Wait for 'architect'. Implement it. SendMessage to 'tester'.",
  subagent_type: "coder", name: "coder", run_in_background: true })
Agent({ prompt: "Wait for 'coder'. Write tests. SendMessage results to 'reviewer'.",
  subagent_type: "tester", name: "tester", run_in_background: true })
Agent({ prompt: "Wait for 'tester'. Review code quality and security.",
  subagent_type: "reviewer", name: "reviewer", run_in_background: true })

// Kick off the pipeline
SendMessage({ to: "researcher", summary: "Start", message: "[task context]" })
```

### Patterns

| Pattern | Flow | Use When |
|---------|------|----------|
| **Pipeline** | A → B → C → D | Sequential dependencies (feature dev) |
| **Fan-out** | Lead → A, B, C → Lead | Independent parallel work (research) |
| **Supervisor** | Lead ↔ workers | Ongoing coordination (complex refactor) |

### Rules

- ALWAYS name agents — `name: "role"` makes them addressable
- ALWAYS include comms instructions in prompts — who to message, what to send
- Spawn ALL agents in ONE message with `run_in_background: true`
- After spawning: STOP, tell user what's running, wait for results
- NEVER poll status — agents message back or complete automatically

## Swarm & Routing

### Config
- **Topology**: hierarchical-mesh (anti-drift)
- **Max Agents**: 15
- **Memory**: hybrid
- **HNSW**: Enabled
- **Neural**: Enabled

```bash
npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized
```

### Agent Routing

| Task | Agents | Topology |
|------|--------|----------|
| Bug Fix | researcher, coder, tester | hierarchical |
| Feature | architect, coder, tester, reviewer | hierarchical |
| Refactor | architect, coder, reviewer | hierarchical |
| Performance | perf-engineer, coder | hierarchical |
| Security | security-architect, auditor | hierarchical |

### When to Swarm
- **YES**: 3+ files, new features, cross-module refactoring, API changes, security, performance
- **NO**: single file edits, 1-2 line fixes, docs updates, config changes, questions

### 3-Tier Model Routing

| Tier | Handler | Use Cases |
|------|---------|-----------|
| 1 | Agent Booster (WASM) | Simple transforms — skip LLM, use Edit directly |
| 2 | Haiku | Simple tasks, low complexity |
| 3 | Sonnet/Opus | Architecture, security, complex reasoning |

## Memory & Learning

### Before Any Task
```bash
npx @claude-flow/cli@latest memory search --query "[task keywords]" --namespace patterns
npx @claude-flow/cli@latest hooks route --task "[task description]"
```

### After Success
```bash
npx @claude-flow/cli@latest memory store --namespace patterns --key "[name]" --value "[what worked]"
npx @claude-flow/cli@latest hooks post-task --task-id "[id]" --success true --store-results true
```

### MCP Tools (use `ToolSearch("keyword")` to discover)

| Category | Key Tools |
|----------|-----------|
| **Memory** | `memory_store`, `memory_search`, `memory_search_unified` |
| **Bridge** | `memory_import_claude`, `memory_bridge_status` |
| **Swarm** | `swarm_init`, `swarm_status`, `swarm_health` |
| **Agents** | `agent_spawn`, `agent_list`, `agent_status` |
| **Hooks** | `hooks_route`, `hooks_post-task`, `hooks_worker-dispatch` |
| **Security** | `aidefence_scan`, `aidefence_is_safe`, `aidefence_has_pii` |
| **Hive-Mind** | `hive-mind_init`, `hive-mind_consensus`, `hive-mind_spawn` |

### Background Workers

| Worker | When |
|--------|------|
| `audit` | After security changes |
| `optimize` | After performance work |
| `testgaps` | After adding features |
| `map` | Every 5+ file changes |
| `document` | After API changes |

```bash
npx @claude-flow/cli@latest hooks worker dispatch --trigger audit
```

## Agents

**Core**: `coder`, `reviewer`, `tester`, `planner`, `researcher`
**Architecture**: `system-architect`, `backend-dev`, `mobile-dev`
**Security**: `security-architect`, `security-auditor`
**Performance**: `performance-engineer`, `perf-analyzer`
**Coordination**: `hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`
**GitHub**: `pr-manager`, `code-review-swarm`, `issue-tracker`, `release-manager`

Any string works as a custom agent type.

## Build & Test

- ALWAYS run tests after code changes
- ALWAYS verify build succeeds before committing

```bash
npm run build && npm test
```

## CLI Quick Reference

```bash
npx @claude-flow/cli@latest init --wizard           # Setup
npx @claude-flow/cli@latest swarm init --v3-mode     # Start swarm
npx @claude-flow/cli@latest memory search --query "" # Vector search
npx @claude-flow/cli@latest hooks route --task ""    # Route to agent
npx @claude-flow/cli@latest doctor --fix             # Diagnostics
npx @claude-flow/cli@latest security scan            # Security scan
npx @claude-flow/cli@latest performance benchmark    # Benchmarks
```

26 commands, 140+ subcommands. Use `--help` on any command for details.

## Setup

```bash
claude mcp add claude-flow -- npx -y @claude-flow/cli@latest
npx @claude-flow/cli@latest daemon start
npx @claude-flow/cli@latest doctor --fix
```

**Agent tool** handles execution (agents, files, code, git). **MCP tools** handle coordination (swarm, memory, hooks). **CLI** is the same via Bash.
