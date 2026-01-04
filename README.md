# 🚀 Work-O-Pilot

**AI-Powered Asset Management & Analytics Copilot**

An intelligent financial assistant that helps you track, analyze, and understand your investment portfolio across **stocks, cryptocurrencies, and commodities** using natural language conversations.

![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.8-blue.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Demo Queries](#-demo-queries)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)

---

## 🎯 Overview

Work-O-Pilot is an AI copilot for personal asset management. It combines:

- **Real-time market data** from Yahoo Finance
- **Time-series forecasting** with Meta's Prophet
- **Document Q&A** via RAG (Retrieval Augmented Generation)
- **Natural language interface** powered by Groq LLM

Ask questions in plain English like *"What is my portfolio allocation?"* or *"Forecast Bitcoin for 30 days"* and get instant insights with visualizations.

---

## ✨ Features

### 📊 Portfolio Analytics
- **Allocation breakdown** - See how your investments are distributed
- **Profit & Loss (P&L)** - Track unrealized gains/losses per asset
- **Performance ranking** - Identify top and bottom performers
- **Trend analysis** - Visualize price movements over time
- **Volatility metrics** - Understand risk exposure
- **Asset comparison** - Compare multiple assets side-by-side

### 🔮 Forecasting
- **AI-powered predictions** using Meta Prophet
- **Confidence intervals** for uncertainty visualization
- **Multi-horizon forecasts** (7 days to 6 months)
- **Trend direction analysis** (bullish/bearish/neutral)

### 🌐 Multi-Asset Support
| Asset Type | Examples | Data Source |
|------------|----------|-------------|
| Stocks | AAPL, TSLA, NVDA | Yahoo Finance |
| Crypto | Bitcoin, Ethereum, Solana | Yahoo Finance |
| Gold | GC=F, GLD | COMEX/Yahoo |
| Silver | SI=F, SLV | COMEX/Yahoo |
| Oil | CL=F, USO | NYMEX/Yahoo |

### 📄 Document Intelligence (RAG)
- **Upload notes and documents** (.txt, .md, .csv)
- **Ask questions** about your investment notes
- **Contextual retrieval** using vector embeddings
- **Per-user isolation** in Pinecone namespaces

### 📤 Export & Reports
- **Select specific messages** to export
- **Generate PDF reports** with charts and data
- **Include visualizations** in exports

---

## 💬 Demo Queries

```
Portfolio Queries:
• "What is my portfolio allocation?"
• "Show me my unrealized P&L"
• "What are my top 3 performers?"

Market Queries:
• "Show me AAPL trend for 6 months"
• "Compare Tesla and Nvidia"
• "What is the gold price?"
• "Show me Bitcoin trend for 1 month"

Forecasting:
• "Forecast Apple stock for 30 days"
• "Predict Bitcoin price for next week"
• "Forecast gold for 2 months"

Document Q&A:
• "What did I write about my investment strategy?"
• "What is my cost basis according to my notes?"
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
├─────────────────────────────────────────────────────────────────┤
│  Chat Interface    │  Asset Manager    │  Export Dialog         │
│  Visualizations    │  File Upload      │  Theme Switcher        │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/REST
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌─────────────────────────────────────┐    │
│  │   Router AI   │───▶│          Intent Classifier           │   │
│  │   (Groq LLM)  │    │  Determines: analytics/rag/forecast  │   │
│  └──────────────┘    └─────────────┬───────────────────────┘    │
│                                    │                             │
│         ┌──────────────────────────┼──────────────────────┐     │
│         ▼                          ▼                      ▼     │
│  ┌─────────────┐          ┌─────────────┐         ┌───────────┐ │
│  │  Analytics   │          │ Forecasting │         │    RAG    │ │
│  │  Pipeline    │          │  Pipeline   │         │  Pipeline │ │
│  └──────┬──────┘          └──────┬──────┘         └─────┬─────┘ │
│         │                        │                      │       │
│         ▼                        ▼                      ▼       │
│  ┌─────────────┐          ┌─────────────┐         ┌───────────┐ │
│  │   yfinance   │          │   Prophet   │         │  Pinecone │ │
│  │  Market Data │          │  ML Model   │         │ Vector DB │ │
│  └─────────────┘          └─────────────┘         └───────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Explanation AI (Groq)                     ││
│  │    Converts raw data → Natural language markdown response    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────┐
                        │     Supabase     │
                        │  (PostgreSQL DB) │
                        │  - Users/Assets  │
                        │  - Chat History  │
                        │  - File Storage  │
                        └──────────────────┘
```

### Pipeline Flow

1. **User Query** → Frontend sends message to `/chat/` endpoint
2. **Router AI** → Groq LLM classifies intent (analytics/rag/forecasting)
3. **Pipeline Execution**:
   - **Analytics**: Fetches market data via yfinance, runs calculations
   - **Forecasting**: Uses Prophet to predict future prices
   - **RAG**: Searches user documents in Pinecone vector DB
4. **Explanation AI** → Groq generates human-readable markdown response
5. **Chart Generation** → Matplotlib creates visualizations (base64 PNG)
6. **Response** → JSON with text, data, visualization, and sources

---

## 🛠 Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| TypeScript | Type Safety |
| Vite | Build Tool |
| TailwindCSS | Styling |
| Shadcn/UI | Component Library |
| Recharts | Interactive Charts |
| React Query | Data Fetching |
| React Router | Navigation |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | API Framework |
| Python 3.10+ | Runtime |
| Groq (Llama 3.3 70B) | LLM for NLU & Generation |
| yfinance | Market Data |
| Meta Prophet | Time-Series Forecasting |
| Pinecone | Vector Database (RAG) |
| Sentence Transformers | Text Embeddings |
| Matplotlib | Chart Generation |
| Supabase | Database & Auth |

---

## 📁 Project Structure

```
work-o-pilot/
├── src/                          # Frontend source
│   ├── components/
│   │   ├── chat/                 # Chat UI components
│   │   │   ├── ChatHeader.tsx
│   │   │   ├── ChatMessages.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatVisualization.tsx
│   │   │   ├── ExportDialog.tsx
│   │   │   └── MarkdownRenderer.tsx
│   │   ├── assets/               # Asset management
│   │   │   ├── AssetForm.tsx
│   │   │   └── AssetSidebar.tsx
│   │   └── ui/                   # Shadcn components
│   ├── hooks/                    # Custom React hooks
│   ├── lib/                      # API client, utilities
│   ├── pages/                    # Route pages
│   └── types/                    # TypeScript types
│
├── work-o-pilot-backend/         # Backend source
│   ├── app/
│   │   ├── core/                 # Config & settings
│   │   ├── models/               # Pydantic schemas
│   │   ├── pipelines/
│   │   │   ├── analytics/        # Market data & calculations
│   │   │   ├── forecasting/      # Prophet ML pipeline
│   │   │   └── rag/              # Document ingestion & retrieval
│   │   ├── routers/              # API endpoints
│   │   │   ├── chat.py           # Main chat endpoint
│   │   │   ├── assets.py         # Asset CRUD
│   │   │   ├── documents.py      # Document ingestion
│   │   │   └── export.py         # Report generation
│   │   └── services/             # AI & external services
│   │       ├── groq_client.py    # LLM wrapper
│   │       ├── router_ai.py      # Intent classification
│   │       ├── explanation_ai.py # Response generation
│   │       └── chart_generator.py# Chart creation
│   └── requirements.txt
│
├── package.json                  # Frontend dependencies
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **Supabase** account (database)
- **Groq** API key (LLM)
- **Pinecone** account (vector DB, optional)

### Backend Setup

```bash
# 1. Navigate to backend
cd work-o-pilot-backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
PINECONE_API_KEY=your_pinecone_api_key  # Optional
PINECONE_INDEX=work-o-pilot-rag
EOF

# 5. Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

```bash
# 1. Navigate to frontend (root directory)
cd work-o-pilot

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

The app will be available at `http://localhost:8080`

---

## 📡 API Documentation

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/` | Main chat interface |
| GET | `/assets/{user_id}` | Get user's assets |
| POST | `/assets/` | Create new asset |
| DELETE | `/assets/{user_id}/{symbol}` | Delete asset |
| POST | `/documents/ingest` | Upload documents for RAG |
| POST | `/export/generate-summary` | Generate export report |

### Chat Request Example

```json
POST /chat/
{
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "user_query": "What is my portfolio allocation?"
}
```

### Chat Response Example

```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": {
    "text": "Your portfolio consists of...",
    "visualization": {
      "type": "pie_chart",
      "image_base64": "iVBORw0KGgo..."
    },
    "follow_up_question": "Would you like to see your P&L breakdown?"
  },
  "sources": [
    {"name": "Yahoo Finance - AAPL", "url": "https://finance.yahoo.com/quote/AAPL"}
  ]
}
```

---

## ⚙️ Configuration

### Environment Variables (Backend)

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ | Groq API key for LLM |
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_KEY` | ✅ | Supabase anon/service key |
| `PINECONE_API_KEY` | ❌ | Pinecone API key (for RAG) |
| `PINECONE_INDEX` | ❌ | Pinecone index name |

### Database Schema (Supabase)

```sql
-- Assets table
CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  quantity DECIMAL NOT NULL,
  avg_buy_price DECIMAL NOT NULL,
  purchase_date DATE,
  portfolio_name VARCHAR(100),
  currency VARCHAR(10) DEFAULT 'USD',
  broker VARCHAR(100),
  investment_type VARCHAR(50) DEFAULT 'Stock',
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference
- **Meta Prophet** - Time-series forecasting
- **Yahoo Finance** - Market data
- **Pinecone** - Vector database
- **Supabase** - Backend infrastructure
- **Shadcn/UI** - Beautiful UI components

---