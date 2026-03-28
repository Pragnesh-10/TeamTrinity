# Mutual Fund X-Ray: Intelligent Portfolio Diagnostics

**Institutional-Grade Portfolio Analytics for Retail Investors.**

Mutual Fund X-Ray is an AI-powered diagnostic platform that performs deep structural analysis of your mutual fund portfolio. It moves beyond simple tracking by identifying hidden overlaps, tax liabilities, and precise growth metrics using a professional-grade multi-agent orchestration.

---

## 🚀 Key Features

- **Professional-Grade XIRR**: Our custom engine (powered by `pyxirr`) correctly distinguishes between internal reinvestments and external cash flows, anchoring terminal values to the statement date for true-to-life accuracy.
- **Deep Overlap Detection**: Analyzes underlying stock holdings across funds to expose hidden concentration risks and redundancy.
- **Tax-Efficient Rebalancing**: AI agents suggest optimal exit strategies while calculating STCG/LTCG liabilities.
- **FIRE Trajectory Mapping**: Dynamically connects your current diagnostic health to your long-term Financial Independence (FIRE) goals.
- **Privacy-First Design**: Local parsing of CAS PDFs; no financial data is ever stored on our servers.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, PyXIRR, PDFPlumber.
- **Frontend**: React 18, Vite, TailwindCSS, Framer Motion, Lucide Icons.
- **AI Orchestration**: Specialized Multi-Agent Framework (Parser, Analysis, Finance, Recommendation, Compliance).

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```
*The backend will be available at: http://localhost:8000*

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```
*The frontend will be available at: http://localhost:5173 (or as shown in terminal)*

---

## 📂 Project Structure

```
├── backend/
│   ├── agents/          # Specialized AI Agents (Analysis, Finance, etc.)
│   ├── models/          # Pydantic data schemas
│   ├── pdf_parser.py    # Robust CAS PDF extraction logic
│   ├── xirr_engine.py   # High-precision financial engine wrapper
│   └── main.py          # FastAPI entry point
└── frontend/
    ├── src/
    │   ├── components/  # Reusable UI components (Charts, Gauges)
    │   ├── pages/       # Core views (Landing, Dashboard, Upload)
    │   └── App.jsx      # Main application flow
```

---

## 🏆 Hackathon Highlights: Why We Win

1. **The "Financial Analyst" Edge**: Our XIRR calculation isn't a simple CAGR. We handle dividend reinvestments and statement "as-of" dates exactly like a professional wealth manager.
2. **Structural Depth**: Most trackers show "returns". We show "overlap" at the individual stock level across multiple AMC houses.
3. **Agentic Reasoning**: Instead of hard-coded rules, we use a chain of specialized agents that provide readable "AI Reasoning Trace Logs" for every recommendation.

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.

*Built for the Economic Times Hackathon 2024.*
