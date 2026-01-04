# Work-o-Pilot Backend

Stock Analytics AI Copilot backend built with FastAPI and Supabase.

## Prerequisites

- Python 3.10+
- pip

## Setup

1.  **Clone and create venv**:
    ```bash
    cd work-o-pilot-backend
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Create a `.env` file:
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=asset-rag
```

## Running

```bash
uvicorn app.main:app --reload --port 8001
```

## API Endpoints

### Chat (Main Copilot)

*   **`POST /chat/`** - Main chat endpoint
    ```json
    {
      "user_id": "uuid",
      "conversation_id": "uuid (optional)",
      "user_query": "What is the trend for AAPL?"
    }
    ```

*   **`GET /chat/history/{conversation_id}`** - Get chat history
*   **`GET /chat/conversations/{user_id}`** - Get user's conversations

### Assets

*   **`POST /assets/`** - Create asset (multipart form)
    - `user_id`, `symbol`, `quantity`, `avg_buy_price`, `files[]`

### Health

*   **`GET /health`** - Health check

## Architecture

```
app/
├── core/config.py          # Environment config
├── routers/
│   ├── assets.py           # Asset CRUD
│   └── chat.py             # AI Copilot endpoint
├── services/
│   ├── supabase_client.py  # Supabase connection
│   ├── groq_client.py      # GROQ AI wrapper
│   ├── router_ai.py        # Intent classification
│   └── explanation_ai.py   # Result explanation
├── pipelines/
│   ├── dispatcher.py       # Pipeline routing
│   └── analytics/
│       ├── market_data.py  # yfinance wrapper
│       ├── calculators.py  # Deterministic analytics
│       └── executor.py     # Analytics orchestration
└── models/
    ├── schemas.py          # Pydantic models
    └── context.py          # Conversation context
```

## Supported Analytics

- Trend analysis
- Performance ranking (top/bottom N)
- P&L calculation
- Multi-asset comparison
- Volatility & drawdown
- Portfolio allocation
