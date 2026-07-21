# Invoice Approval Workflow

> **Demo / portfolio piece — not production accounting software.** This workflow is a self-contained demonstration of an AI-assisted invoice intake pattern. It does not persist data, send notifications, or include auth or audit logging. For real accounts-payable automation (QuickBooks, NetSuite, Xero, Sage, etc., with proper review trails, fraud checks, and human-in-the-loop escalation), **[get in touch with Vonnerco Consulting](../../contact.html)** — this kind of work is exactly what we do.

An n8n workflow that reads an invoice, asks a local LLM to extract structured fields, and routes it for auto-approval or manual review based on the amount and the model's confidence.

---

## Fastest path: see it work in 5 minutes

```bash
# 1. Pull a chat model and start Ollama (in one terminal)
ollama pull llama3.1
ollama serve

# 2. In n8n: top-right → "Import from File" → invoice-approval-workflow.json
# 3. Open the imported workflow and click "Execute Workflow"
#    (no input needed — the Manual trigger runs the demo invoice)
```

You'll get an `approved` response with the demo invoice (`INV-DEMO-001`, $499, Acme Office Supplies). The whole loop runs end-to-end against your local Ollama — no other services required.

---

## What it does

1. Accepts an invoice via webhook, manual trigger, or schedule.
2. Validates the payload and extracts invoice fields (vendor, amount, date, due date, raw text).
3. Sends the raw text to a **local Ollama** model at `http://127.0.0.1:11434/v1/chat/completions`, which returns a JSON extraction with a `confidence` score.
4. Branches:
   - **`amount <= $499` AND `confidence >= 0.9`** → auto-approve (HTTP 200).
   - Otherwise → needs manual review (HTTP 202).
5. Responds to the webhook caller with the result.

The full request/response shape lives in [`invoice-approval-workflow.json`](./invoice-approval-workflow.json).

## Prerequisites

- **n8n** — any recent version (the workflow uses Ollama's OpenAI-compatible `/v1/chat/completions` endpoint via n8n's built-in `httpRequest` node).
- **Ollama** running locally with a chat model that supports structured output. The README assumes **`llama3.1`** as the default (universal, well-known, ~4.7 GB).
  ```bash
  ollama pull llama3.1
  ollama serve   # default: http://127.0.0.1:11434
  ```
  > If you have access to a larger or domain-tuned model (e.g. `gpt-oss:120b-cloud` or `qwen2.5`), change the `model` field in the **Build AI Request Body** node. The workflow is model-agnostic — anything Ollama serves that returns JSON will work.
- **Network access from n8n to Ollama** — if you run n8n in Docker and Ollama on the host, `http://127.0.0.1:11434` from inside the container points back to the container, not the host. Use one of:
  - Docker Desktop: `http://host.docker.internal:11434`
  - Linux Docker: `--add-host=host.docker.internal:host-gateway` on the container, then `http://host.docker.internal:11434`
  - Bare-metal n8n: `http://127.0.0.1:11434` works as-is.

## How to run

1. **Import the workflow**
   - In n8n: top-right → *Import from File* → select `invoice-approval-workflow.json`.
   - The workflow lands as **Invoice Processing & Approval Automation** and is **inactive** by default.

2. **Start Ollama** with `llama3.1` pulled (see Prerequisites).

3. **(Optional) Update the model name** in the **Build AI Request Body** node if you're not using `llama3.1`.

4. **Activate the workflow** in n8n (toggle in the top-right), or run a single execution to test.

5. **Trigger it three ways**:
   - **Manual trigger** — click *Execute Workflow* in n8n. With no input, it returns a hard-coded demo invoice and auto-approves it.
   - **Webhook trigger** — once active, POST JSON to the webhook URL n8n prints (it looks like `https://your-n8n.example.com/webhook/invoice-webhook`). Open the **Webhook Trigger** node in n8n to see the exact URL.
   - **Schedule trigger** — disabled by default. Open the **Schedule Trigger** node and toggle it on to run every 60 minutes with no input (falls through to demo mode).

### Example: webhook payload

The repo includes a ready-made sample at [`examples/sample-invoice.json`](./examples/sample-invoice.json). You can POST it directly:

```bash
curl -X POST https://your-n8n.example.com/webhook/invoice-webhook \
  -H "Content-Type: application/json" \
  -d @examples/sample-invoice.json
```

Or write one inline:

```bash
curl -X POST https://your-n8n.example.com/webhook/invoice-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "invoices": [
      {
        "id": "INV-1001",
        "vendor_name": "Acme Office Supplies",
        "amount": 320.50,
        "date": "2026-07-15",
        "due_date": "2026-08-15",
        "raw_text": "Invoice INV-1001\nVendor: Acme Office Supplies\nDate: 2026-07-15\nDue: 2026-08-15\nItem: Office Supplies - Qty 1 @ $320.50\nTotal: $320.50"
      }
    ]
  }'
```

### Response shapes

**Auto-approved (HTTP 200):**
```json
{
  "status": "approved",
  "code": 200,
  "invoiceId": "INV-1001",
  "vendor": "Acme Office Supplies",
  "amount": 320.5,
  "approvedAt": "2026-07-21T15:30:00.000Z",
  "approvedBy": "Auto",
  "aiExtraction": { "vendor_name": "Acme Office Supplies", "total": 320.5, "confidence": 0.95, "...": "..." },
  "model": "llama3.1",
  "message": "Invoice auto-approved (<=$499 threshold)"
}
```

**Needs manual review (HTTP 202):**
```json
{
  "status": "pending_review",
  "code": 202,
  "invoiceId": "INV-2002",
  "vendor": "Northwind Consulting",
  "amount": 12500.0,
  "reason": "Amount $12500 exceeds auto-approval threshold ($499)",
  "submittedAt": "2026-07-21T15:30:00.000Z",
  "aiExtraction": { "vendor_name": "Northwind Consulting", "total": 12500.0, "confidence": 0.92, "...": "..." },
  "model": "llama3.1",
  "message": "Invoice queued for manual review",
  "nextStep": "Notify AP team / write to review queue"
}
```

## Configuration knobs

| Knob | Where | Default | What it does |
| --- | --- | --- | --- |
| Auto-approve threshold | `Amount <= $499?` node, condition `amount-check` | `$499` | Max amount for auto-approval. |
| Confidence floor | `Amount <= $499?` node, condition `confidence-check` | `0.9` | Min AI confidence required for auto-approval. |
| AI model | `Build AI Request Body` node, `model` field | `llama3.1` | Any Ollama chat model. |
| AI temperature | `Build AI Request Body` node, `temperature` | `0.1` | Lower = more deterministic extraction. |
| Schedule interval | `Schedule Trigger` node | `60 minutes`, **disabled** | Polling cadence if you turn it on. |
| Webhook path | `Webhook Trigger` node, `path` | `invoice-webhook` | Public URL suffix. |

## Troubleshooting

**`connect ECONNREFUSED 127.0.0.1:11434` from the AI node**
Ollama isn't running, or n8n can't reach it. Start `ollama serve` in a terminal, then re-test. If you're running n8n in Docker, see the "Network access" note in Prerequisites — you'll need `host.docker.internal` instead of `127.0.0.1`.

**`model "llama3.1" not found`**
You pulled the wrong name, or nothing yet. Run `ollama pull llama3.1` and wait for it to finish. Check what you have with `ollama list`.

**Webhook returns 404 "not registered"**
The workflow isn't active. Toggle the active switch in the top-right of the n8n editor. n8n only registers webhook URLs while the workflow is active.

**Webhook returns 400 "No invoices found in request body"**
The payload wasn't shaped the way the validator expects. It looks for either:
- `{"invoices": [...]}` (recommended), or
- a top-level array `[...]`, or
- a single invoice object with `vendor` / `vendor_name` / `amount` / `text` fields.

**AI returns non-JSON, even after fence-extraction attempts**
The model is too small or the prompt isn't deterministic enough at the current temperature. Try:
- lowering temperature to `0.0` in the **Build AI Request Body** node, or
- switching to a larger model (`qwen2.5:14b`, `llama3.1:70b`, etc.), or
- adding a JSON-mode toggle if your model supports it.

**Auto-approve never fires even for small invoices**
Either the amount threshold or the confidence floor is rejecting the run. Open the **Parse AI Response** node's output and check `$json.invoice.confidence` — if it's below `0.9`, lower the confidence-check condition or switch to a more capable model.

## What's intentionally not here

This is a **demo workflow**. The following are deliberately out of scope:

- **No persistence.** Nothing is written to a database, file, or queue. The result only goes back to the webhook caller.
- **No OCR.** The payload must already contain `raw_text`. To ingest PDFs or images, add an upstream OCR node (Tesseract, AWS Textract, Google Document AI).
- **No notifications.** The `pending_review` branch returns 202 but does not email, Slack, or page anyone.
- **No webhook auth.** n8n's built-in webhook auth is not enabled in this export — anyone with the URL can hit it.
- **No retries / dead-letter queue.** A failed AI call fails the run.

To turn this into a production AP automation, the natural next steps are: enable webhook auth, write approved/pending invoices to your AP system of record, add a notification step for the `pending_review` branch, add OCR upstream, and add audit logging.

## Files

- [`invoice-approval-workflow.json`](./invoice-approval-workflow.json) — the importable n8n workflow.
- [`examples/sample-invoice.json`](./examples/sample-invoice.json) — a small invoice payload for the webhook trigger.

---

**Need this for real accounting work?** Vonnerco Consulting builds production AP automations integrated with QuickBooks, NetSuite, Xero, and Sage — with proper review trails, fraud detection, dual-approval thresholds, and human-in-the-loop escalation. **[Send a message](../../contact.html)** to start a conversation.
