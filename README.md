# Vonnerco Automation Solutions

A portfolio of automation workflows, AI integrations, and freelance service deliverables built with **n8n**, third-party **APIs**, and **no-code / low-code** tools.

This repository is a working showcase of the automation work delivered through Vonnerco Consulting — each directory is a self-contained engagement, template, or reusable component.

---

## Purpose

Vonnerco Automation Solutions is the technical home for:

- **Client-facing deliverables** — automation systems shipped to or for customers.
- **Reusable templates** — workflow patterns that can be adapted across engagements.
- **AI integration experiments** — LLM-powered features, agents, and RAG prototypes.
- **Reference architecture** — patterns for orchestrating APIs, webhooks, and no-code tools.

The goal is to make every engagement reproducible: a new project or client should be able to clone, configure credentials, and run.

---

## Directory Structure

```
Vonnerco - Automation/
├── clients/              # Client-specific deliverables (one folder per engagement)
│   └── <client-name>/    # Isolated, scoped, with its own README
│
├── templates/            # Reusable workflow templates and starter kits
│   ├── n8n/              # Exportable n8n workflow JSON
│   ├── api-integrations/ # Reusable API connector patterns
│   └── no-code/          # Zapier, Make, and similar recipes
│
├── ai-integrations/      # LLM-powered automations and experiments
│   ├── agents/           # Agent definitions and tool configs
│   ├── rag/              # Retrieval-augmented generation prototypes
│   └── prompts/          # Versioned prompt library
│
├── tools/                # Scripts and utilities that support workflows
│
├── docs/                 # Architecture notes, decision records, runbooks
│
└── README.md             # You are here
```

### Directory conventions

- Every subdirectory has its own `README.md` with setup, configuration, and usage notes.
- Sensitive values (API keys, tokens) are **never** committed — use `.env` files listed in `.gitignore`.
- Each client engagement lives in `clients/<client-name>/` and is self-contained.

---

## Tech Stack

| Layer | Tools |
| --- | --- |
| **Workflow orchestration** | n8n (primary), Make, Zapier |
| **AI / LLMs** | Claude API, OpenAI, open-source models as needed |
| **Integrations** | REST and GraphQL APIs, webhooks, SaaS connectors |
| **No-code / low-code** | Airtable, Notion, Google Workspace, Bubble |
| **Supporting code** | Node.js, Python (for glue and custom nodes) |

---

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repo-url> "Vonnerco - Automation"
   cd "Vonnerco - Automation"
   ```

2. **Pick a directory** matching your use case (a client, a template, or an AI integration).

3. **Read its README** — every subdirectory documents its own prerequisites and setup steps.

4. **Configure credentials** — copy `.env.example` (where present) to `.env` and fill in keys.

5. **Run or import** the workflow into your tool of choice (e.g. import `*.json` into n8n).

---

## Contribution Notes

- Keep deliverables **scoped and documented** — every folder is a portfolio piece.
- Prefer **configuration over hard-coding** — externalize client names, IDs, and prompts.
- When adding a new client engagement, create `clients/<client-name>/` with its own README.
- Reusable patterns belong in `templates/` or `ai-integrations/`, not in client folders.

---

## About Vonnerco

Vonnerco Consulting helps small and mid-sized businesses adopt AI and automation — from workflow design through integration and ongoing support. This repository is a technical companion to that work: it shows, not just tells, what the engagements produce.

**For service inquiries, [book a free consultation at the Vonnerco portal](https://web-portal.corderio-vonner.workers.dev/).**
