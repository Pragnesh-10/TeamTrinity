# MF Portfolio X-Ray — Vibe-Coding Agent Prompt

## What You Are Building

A **full-stack AI-powered Mutual Fund Portfolio X-Ray web application** for Indian retail investors.

The user uploads their CAMS or KFintech Consolidated Account Statement (PDF). The app autonomously runs a 5-step agentic pipeline and returns a rich, interactive portfolio analysis report — no manual inputs required beyond the PDF upload.

This is a **hackathon submission** for ET AI Hackathon 2026 (Track 9: AI Money Mentor). The judges will score on autonomy depth, specific quantitative outputs, and enterprise-grade reliability. Every output must show exact numbers — vague advice scores zero.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | React + Tailwind CSS + shadcn/ui |
| Backend | Python FastAPI |
| PDF parsing | pdfplumber |
| Financial math | scipy, numpy, pandas |
| LLM synthesis | Ollama (Llama 3 / Mistral / Mixtral - local inference) |
| Deployment | Single repo, `uvicorn` backend + Vite frontend |

The backend and frontend can be in the same repo. Use a `/api` prefix for all backend routes.

---

## Application Pages & Flow

### Page 1 — Upload Screen
- Clean drag-and-drop zone for CAMS/KFintech PDF
- Accepts `.pdf` only, max 10MB
- On upload: show animated 5-step progress tracker (see pipeline below)
- Show sample demo button that loads built-in demo data (for judges who don't have a CAMS PDF)

### Page 2 — Dashboard (main output)
Five collapsible sections, each rendered as a card:

#### Card 1: Portfolio Overview
- Total invested (₹), current value (₹), absolute gain (₹ and %)
- Portfolio XIRR badge — large, prominent number (e.g. "14.2% p.a.")
- Benchmark comparison: small text showing Nifty 50 historical XIRR (~13.5%) for context
- Fund count, date range of oldest transaction

#### Card 2: Per-Fund XIRR Breakdown
- Horizontal bar chart — one bar per fund
- Each bar shows: fund name, XIRR %, current value (₹), units held
- Color: green if XIRR > 12%, amber if 8–12%, red if < 8%
- Sort descending by XIRR

#### Card 3: Overlap Analysis
- Heatmap grid — funds on both axes, overlap % in each cell
- Cells above 40% highlighted in red/orange with warning icon
- Below the heatmap: "Top 5 most concentrated stocks across your portfolio" as a ranked list with effective portfolio weight %
- Concentration risk badge: LOW / MODERATE / HIGH based on HHI score

#### Card 4: Rebalancing Recommendations
- One action card per fund needing change
- Each card has: [SELL] or [BUY] badge, fund name, current % → target %, rupee amount to move
- For SELL actions: show STCG tax (₹), LTCG tax (₹), and recommendation text
- If STCG > tolerance: show "⏳ Wait X days until [date] to avoid ₹Y in STCG tax" suggestion
- Total tax triggered summary at bottom

#### Card 5: LLM Synthesis Report
- Markdown-rendered plain-English report from local LLM (Ollama)
- 5 sections: Returns, Overlap, Expense Ratio, Rebalancing, Next Steps
- Always ends with SEBI disclaimer in a distinct styled block

---

## Backend API Endpoints

### POST /api/upload
- Accepts multipart form with PDF file
- Returns job_id (UUID)

### GET /api/status/{job_id}
- Returns: `{ step: 1-5, label: "Computing XIRR...", progress: 40 }`
- Frontend polls this every 1 second to drive the progress tracker

### GET /api/result/{job_id}
- Returns full JSON result (see Data Contracts below)

### POST /api/demo
- Triggers pipeline on built-in demo data (no PDF needed)
- Returns job_id same as upload

---

## The 5-Step Agentic Pipeline (Backend)

The pipeline runs fully autonomously after PDF upload. No human input between steps.

```
Step 1: Parse PDF → extract transactions, fund names, NAV, date range
Step 2: Build FIFO lot ledger → per-fund positions with purchase lots
Step 3: Compute XIRR → per-fund + portfolio level using scipy brentq solver
Step 4: Overlap analysis → pairwise overlap % + portfolio HHI concentration
Step 5: STCG-aware rebalancing → FIFO tax calculation + LLM synthesis
```

This 5-step autonomous chain satisfies the hackathon's "3+ sequential steps without human input" requirement. Log each step to a job audit trail stored in memory (or Redis if available).

---

## Core Financial Logic — Implement Exactly As Described

### XIRR

XIRR solves for `r` in: `Σ [ CFᵢ / (1+r)^((dᵢ - d₀)/365) ] = 0`

- Investments (purchases) = **negative** cashflows
- Redemptions + current portfolio value (as of today) = **positive** cashflows
- Use `scipy.optimize.brentq` with bounds `(-0.999, 100.0)`, `xtol=1e-8`
- Compute per-fund and portfolio-level (deduplicate the "today's value" inflow)
- Handle edge cases: single transaction, all redemptions, NAV not available

```python
from scipy.optimize import brentq
from datetime import date

def xirr(cashflows):  # [(date, float), ...]
    t0 = min(d for d, _ in cashflows)
    def npv(r):
        return sum(cf / (1+r)**((d-t0).days/365) for d, cf in cashflows)
    return brentq(npv, -0.999, 100.0, xtol=1e-8)
```

### Overlap Score

Pairwise overlap between fund A and fund B:
```
overlap_pct = Σ min(w_A_i, w_B_i) × 100
```
where `w_i` = weight of stock `i` in that fund as a fraction (0 to 1).

This is the standard "portfolio overlap" metric from Value Research / Morningstar.

For concentration: compute **Herfindahl-Hirschman Index (HHI)**:
```
HHI = Σ (effective_weight_i)² × 10000
HHI > 1500 → HIGH, 800–1500 → MODERATE, < 800 → LOW
```

### STCG / LTCG Tax Rules (India FY 2025-26)

| Fund type | LTCG threshold | STCG rate | LTCG rate |
|---|---|---|---|
| Equity / hybrid-equity (≥65% equity) | 12 months | 20% | 12.5% on gains > ₹1.25L/yr |
| Debt / hybrid-debt | Any holding | Slab rate (30%) | Slab rate (30%) |

- Use **FIFO** (first in, first out) for lot accounting — India's default MF method
- For each sell action, calculate STCG gain and LTCG gain separately across lots
- If STCG tax > ₹5,000 tolerance: find next lot's LTCG date and suggest waiting
- Apply ₹1,25,000 LTCG annual exemption for equity funds

### Fund Holdings (for overlap)

Use a hardcoded `DEMO_HOLDINGS` dict for the hackathon demo (real funds with approximate SEBI-disclosed holdings). Include at least:
- Mirae Asset Large Cap
- Axis Bluechip Fund
- HDFC Flexi Cap
- SBI Large & Midcap
- Parag Parikh Flexi Cap
- ICICI Prudential Bluechip
- Kotak Flexicap

Each fund: `{ "Stock Name": weight_as_fraction }` where weights sum to ~0.6–0.8 (top holdings only).

In production, these would come from the AMFI monthly disclosure XML.

---

## Data Contracts (API Response Schema)

### GET /api/result/{job_id} — full response

```json
{
  "status": "complete",
  "portfolio": {
    "total_invested": 550000,
    "total_current_value": 718450,
    "absolute_gain": 168450,
    "absolute_return_pct": 30.6,
    "portfolio_xirr_pct": 14.2,
    "fund_count": 6,
    "date_range": { "from": "2022-01-15", "to": "2025-03-01" }
  },
  "per_fund": [
    {
      "fund_name": "Mirae Asset Large Cap",
      "xirr_pct": 16.4,
      "units_held": 397.88,
      "current_nav": 135.50,
      "current_value": 53913,
      "total_invested": 44826,
      "absolute_gain": 9087,
      "absolute_return_pct": 20.3
    }
  ],
  "overlap": {
    "pairwise": [
      {
        "fund_a": "Mirae Asset Large Cap",
        "fund_b": "HDFC Flexi Cap",
        "overlap_pct": 42.0,
        "top_shared": [
          { "stock": "Reliance Industries", "min_weight_pct": 9.2 },
          { "stock": "HDFC Bank", "min_weight_pct": 8.5 }
        ]
      }
    ],
    "portfolio_top_10": [
      { "stock": "Reliance Industries", "effective_pct": 8.6 }
    ],
    "concentration_risk": "moderate",
    "hhi": 940
  },
  "rebalancing": {
    "summary": "2 funds to reduce, 3 to increase. Total STCG triggered: ₹2,340.",
    "total_stcg_tax": 2340,
    "actions": [
      {
        "action": "SELL",
        "fund_name": "Mirae Asset Large Cap",
        "current_pct": 35.2,
        "target_pct": 20.0,
        "amount": 36800,
        "units_to_sell": 271.66,
        "stcg_gain": 4200,
        "ltcg_gain": 18600,
        "stcg_tax": 840,
        "ltcg_tax": 1500,
        "total_tax": 2340,
        "recommendation": "Sell 271 units. STCG tax ₹840 is within tolerance.",
        "wait_suggestion": null
      },
      {
        "action": "BUY",
        "fund_name": "Parag Parikh Flexi Cap",
        "current_pct": 8.1,
        "target_pct": 25.0,
        "amount": 121800,
        "recommendation": "Top-up ₹1,21,800 via lump sum or increase monthly SIP by ₹8,500."
      }
    ]
  },
  "llm_report": "## Portfolio X-Ray\n\n### 1. Returns...",
  "audit_trail": [
    { "step": 1, "label": "PDF parsed", "timestamp": "2025-03-26T10:22:01" },
    { "step": 2, "label": "FIFO ledger built", "timestamp": "2025-03-26T10:22:02" }
  ],
  "disclaimer": "This is AI-generated analysis for informational purposes only and does not constitute SEBI-registered investment advice. Please consult a SEBI-registered investment advisor before making investment decisions."
}
```

---

## LLM Synthesis Prompt (send to Ollama API)

```
You are an expert financial analyst. Analyse the following mutual fund portfolio data and write a clear Portfolio X-Ray report in markdown.

Structure your report in exactly 5 sections:
1. **Portfolio Returns** — compare XIRR to Nifty 50 (~13.5% historical). Call out underperformers.
2. **Overlap & Concentration** — name the specific over-concentrated stocks and which fund pairs share them.
3. **Expense Ratio Alert** — remind user to check if they are in direct plans vs regular plans (0.5–1% annual difference).
4. **Rebalancing Plan** — summarise specific sell/buy actions with rupee amounts and tax impact.
5. **Next Steps** — 3 concrete action items the user should do this week.

Rules:
- Be specific and quantitative. Use exact numbers from the data.
- Do NOT give generic advice like "diversify your portfolio."
- Do NOT recommend specific funds to buy — only rebalancing direction.
- Keep each section to 3–5 sentences.

End with exactly this disclaimer on its own line:
"⚠ This is AI-generated analysis for informational purposes only and does not constitute SEBI-registered investment advice. Please consult a SEBI-registered investment advisor before making investment decisions."

Portfolio data:
{json_data}
```

---

## UI Design Direction

**Aesthetic**: Financial terminal meets modern fintech. Dark-first. Data-dense but never cluttered.

- **Color palette**: Dark navy background (`#0a0f1e`), card surfaces (`#111827`), borders (`#1f2937`). Accent: electric teal (`#00d4aa`) for positive returns, amber (`#f59e0b`) for warnings, red (`#ef4444`) for overlaps/losses.
- **Typography**: `DM Mono` or `JetBrains Mono` for numbers and percentages (critical — financial data must feel precise). `Inter` or `DM Sans` for body text.
- **XIRR badge**: Large, bold, prominent — if portfolio XIRR > Nifty: teal glow; if below: amber.
- **Charts**: Use Recharts (already in React ecosystem). Bar charts for per-fund returns, custom heatmap for overlap.
- **Overlap heatmap**: CSS grid, cells colored from white (0%) → deep red (100%). Diagonal cells gray (same fund).
- **Upload screen**: Subtle animated border on drag-over. Show a skeleton of the dashboard loading in the background as a teaser.
- **Progress tracker**: 5 numbered circles connected by lines. Active step pulses. Completed steps turn teal.
- **Rebalancing cards**: Left border accent color-coded by action type (teal = BUY, amber = SELL).
- No light mode needed — judges will see dark mode.

---

## Evaluation Rubric (How Judges Score This)

Build every feature with these weights in mind:

### 1. Autonomy Depth — 30%
**What judges look for**: How many steps complete without human input? Does the agent recover from failures? Can it handle branching logic?

**How to satisfy this**:
- The pipeline must run all 5 steps after PDF upload with zero user interaction
- Show a live step-by-step progress tracker so judges can *see* the autonomy
- Handle errors gracefully: if XIRR fails for one fund (e.g. only one transaction), continue with the others and flag it — don't crash the whole pipeline
- If NAV is missing for a fund, use last known transaction NAV as fallback
- The `audit_trail` array in the response proves the agent completed each step independently

### 2. Multi-Agent Design — 20%
**What judges look for**: Are responsibilities split across agents? Clear orchestration pattern?

**How to satisfy this**:
- Structure the backend as 4 distinct modules with clean interfaces: `parser`, `xirr_engine`, `overlap_detector`, `rebalancer`
- The `orchestrator` calls each in sequence and passes results forward — make this visible in code structure
- In your architecture diagram (required for submission), label each module as a separate "agent"
- Log each agent's start/end time in the `audit_trail`

### 3. Technical Creativity — 20%
**What judges look for**: Interesting use of agentic patterns, domain-specific reasoning, cost-efficient architecture.

**How to satisfy this**:
- Use Ollama only for the synthesis step (Step 5) — all math is deterministic Python. This shows cost efficiency.
- The STCG "wait for LTCG" suggestion (computing the exact future date when a lot becomes tax-exempt) is a domain-specific insight that impresses judges
- The HHI concentration score shows knowledge of financial risk metrics beyond simple overlap %
- Show the LLM the structured JSON, not raw text — demonstrates good prompt engineering

### 4. Enterprise Readiness — 20%
**What judges look for**: Error handling, compliance guardrails, audit trails, graceful degradation.

**How to satisfy this**:
- SEBI disclaimer must appear on every output path — hardcode it, never skip it
- `audit_trail` in every response proves traceability
- All API endpoints must return structured error responses: `{ "error": "...", "step": 2, "recoverable": true }`
- If PDF parsing finds 0 transactions: return a helpful error, not a 500
- Log all LLM calls with prompt length, response length, and latency
- Add a `/api/health` endpoint that returns `{ "status": "ok", "model": "ollama-llama3" }`

### 5. Impact Quantification — 10%
**What judges look for**: Can the team show the math on business value?

**How to satisfy this**:
- Add a small "Impact" section at the bottom of the report: 
  - "Switching to direct plans saves you approximately ₹X/year" (calculated as 0.75% × portfolio value)
  - "Reducing overlap saves estimated ₹Y in duplicated exposure"
  - "Tax-optimised rebalancing saves ₹Z vs naive rebalancing"
- These are simple calculations — implement them

---

## Mandatory Scenario Pack (Judges Will Test These)

Your app must handle all three of these correctly:

### Scenario A: Overlap-heavy portfolio
6 funds uploaded, 3 of them are large-cap (Mirae, Axis Bluechip, HDFC Top 100).
Expected output:
- Pairwise overlap between all three > 35%
- Reliance, HDFC Bank, Infosys flagged as over-concentrated across all three
- Rebalancing suggests selling one of the three and routing to a distinct category (midcap or international)
- No STCG triggered if all lots are > 12 months old

### Scenario B: STCG trap scenario
User has Mirae Asset Large Cap purchased 8 months ago (still STCG territory) with significant gains.
Target rebalancing would require selling this fund.
Expected output:
- Agent detects the lot is within 12-month STCG window
- Shows STCG tax = 20% × gain
- Suggests: "Wait 4 months until [exact date]. Savings: ₹X in STCG tax."
- Shows both options: sell now (with tax cost) vs wait (with exact date)

### Scenario C: Single-fund portfolio
User has only one fund (HDFC Flexi Cap) with 3 years of SIPs.
Expected output:
- XIRR computed correctly
- Overlap section: "Only 1 fund — overlap analysis not applicable"
- Rebalancing: suggests diversification across 3-4 categories (without naming specific funds)
- Pipeline should not crash — this is a valid edge case

---

## Submission Checklist

Before you consider this done, verify:

- [ ] PDF upload + demo mode both work
- [ ] All 5 pipeline steps complete without errors on demo data
- [ ] XIRR displayed per-fund and portfolio level
- [ ] Overlap heatmap renders with correct values
- [ ] STCG calculation shows correct tax for at least one SELL action
- [ ] LLM report renders as markdown with SEBI disclaimer
- [ ] `audit_trail` populated in every result response
- [ ] `/api/health` endpoint returns 200
- [ ] All errors return structured JSON (no unhandled 500s)
- [ ] Demo mode works without a PDF (for judges without CAMS access)
- [ ] App loads and is usable on a 1080p screen
- [ ] README has setup instructions (pip install + npm install + how to run)

---

## File Structure to Scaffold

```
mf-xray/
├── backend/
│   ├── main.py                  # FastAPI app, routes
│   ├── orchestrator.py          # 5-step pipeline runner
│   ├── parser.py                # CAMS PDF parser (pdfplumber)
│   ├── xirr_engine.py           # XIRR computation
│   ├── overlap_detector.py      # Overlap + HHI
│   ├── rebalancer.py            # STCG-aware rebalancing
│   ├── llm_synthesiser.py       # Ollama local inference call
│   ├── demo_data.py             # Built-in demo transactions + holdings
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Upload.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── components/
│   │   │   ├── ProgressTracker.jsx
│   │   │   ├── XirrChart.jsx
│   │   │   ├── OverlapHeatmap.jsx
│   │   │   ├── RebalancingCard.jsx
│   │   │   └── LlmReport.jsx
│   │   └── lib/api.js           # fetch wrappers
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## SEBI Compliance Guardrail — Non-Negotiable

Every API response must include a `disclaimer` field. Every page of the frontend that shows financial data must render this text:

> ⚠ This is AI-generated analysis for informational purposes only and does not constitute SEBI-registered investment advice. Please consult a SEBI-registered investment advisor before making investment decisions.

The disclaimer must be visually distinct — use a bordered box with amber/yellow background, not just a footer footnote.

This is a hard requirement in the hackathon rubric under Enterprise Readiness. Missing it will cost points.
