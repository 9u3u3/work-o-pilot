# Stock Analytics AI Copilot - API Documentation

Base URL: `http://localhost:8001`

---

## Authentication

Currently using hardcoded user ID for development:
```
USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
```

---

## Endpoints

### 1. Chat (Main Copilot)

#### `POST /chat/`

Main endpoint for interacting with the AI copilot.

**Request:**
```json
{
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "conversation_id": "optional-uuid-for-continuing-conversation",
  "user_query": "What is my portfolio allocation?"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": {
    "text": "Your portfolio consists of **100 shares of AAPL** worth **$27,101**...",
    "data": {
      "allocation": {
        "allocations": [
          {"symbol": "AAPL", "value": 27101.0, "quantity": 100.0, "percentage": 100.0}
        ],
        "total_value": 27101.0
      }
    },
    "visualization": {
      "type": "pie_chart",
      "chart_data": {
        "type": "pie_chart",
        "labels": ["AAPL"],
        "values": [100.0]
      },
      "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
    },
    "follow_up_question": "Would you like to see your P&L breakdown?"
  },
  "sources": [
    {"name": "Yahoo Finance - AAPL", "url": "https://finance.yahoo.com/quote/AAPL", "type": "market_data"}
  ],
  "data_accessed": {
    "symbols": ["AAPL"],
    "time_range": null,
    "data_source": "Yahoo Finance",
    "records_fetched": 0
  }
}
```

**Follow-up Questions:**
The `follow_up_question` field contains an **AI-generated contextual question** based on the response content. Example questions:
- After allocation: "Would you like to see your P&L breakdown?"
- After forecast: "Would you like to compare this forecast with historical data?"
- After trend: "Should I compare this with another stock?"

Frontend can display this as a clickable suggestion button.

**RAG Responses:**
When the user asks about their documents/notes, the response also includes their portfolio data from the database in `data.user_portfolio`.

**Visualization Types:**
- `pie_chart` - for allocation
- `line_chart` - for trends, comparisons, forecasts
- `bar_chart` - for rankings, volatility
- `table` - for P&L
- `none` - no visualization

**Chart Data Structure:**
```json
{
  "type": "line_chart",
  "labels": ["AAPL"],
  "datasets": [
    {
      "label": "AAPL",
      "data": [{"x": "2025-01-01", "y": 150.5}, {"x": "2025-01-02", "y": 151.2}]
    }
  ]
}
```

**Forecasting Response Example:**
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "response": {
    "text": "## **AAPL 30-Day Forecast**\n\n**Trend Direction:** UPWARD\n**Average Daily Growth:** 0.15%\n**Volatility:** LOW\n**Model Confidence:** 90.5%\n\n### Price Prediction\n- **Start (2026-01-03):** $283.58\n- **End (2026-01-30):** $301.05\n- **Predicted Change:** $17.47 (+6.16%)\n\n> See the chart below for the full forecast with confidence intervals.",
    "data": {
      "forecast": [
        {"ds": "2026-01-03", "yhat": 283.58, "yhat_lower": 269.43, "yhat_upper": 298.49},
        {"ds": "2026-01-04", "yhat": 284.02, "yhat_lower": 269.33, "yhat_upper": 299.45}
      ],
      "metrics": {
        "trend": "upward",
        "avg_growth_rate": 0.0015,
        "volatility": "low",
        "volatility_value": 4.72,
        "uncertainty_width": 29.92,
        "confidence": 0.9075
      },
      "metadata": {
        "entity": "AAPL",
        "metric": "Close Price",
        "horizon_days": 30,
        "model": "prophet",
        "historical_records": 502,
        "forecast_records": 30
      }
    },
    "visualization": {
      "type": "line_chart",
      "chart_data": {
        "symbol": "AAPL",
        "data_points": [
          {"date": "2026-01-03", "close": 283.58, "lower": 269.43, "upper": 298.49}
        ],
        "is_forecast": true
      },
      "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  },
  "sources": [
    {"name": "Yahoo Finance - AAPL", "url": "https://finance.yahoo.com/quote/AAPL", "type": "market_data"},
    {"name": "Meta Prophet", "url": "https://facebook.github.io/prophet/", "type": "model"}
  ]
}
```

---

### 2. Assets

#### `GET /assets/{user_id}`

Get all assets for a user.

**Response:**
```json
{
  "user_id": "uuid",
  "count": 2,
  "assets": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "symbol": "AAPL",
      "quantity": 100.0,
      "avg_buy_price": 150.0,
      "purchase_date": "2024-01-15",
      "portfolio_name": "Main",
      "currency": "USD",
      "broker": "Robinhood"
    }
  ]
}
```

#### `GET /assets/{user_id}/{symbol}`

Get a specific asset by symbol.

#### `POST /assets/`

Create a new asset.

**Request (multipart/form-data):**
```
user_id: uuid (required)
symbol: string (required)
quantity: float (required)
avg_buy_price: float (required)
purchase_date: date (optional)
portfolio_name: string (optional)
currency: string (default: "USD")
broker: string (optional)
files[]: File[] (optional)
```

#### `DELETE /assets/{user_id}/{symbol}`

Delete an asset.

---

### 3. Documents (RAG)

#### `POST /documents/ingest`

Upload documents for RAG search.

**Request (multipart/form-data):**
```
user_id: uuid (required)
files[]: File[] (required) - txt, md, csv files
```

**Response:**
```json
{
  "success": true,
  "ingested": [{"file": "notes.txt", "chunks": 3, "status": "success"}],
  "errors": [],
  "total_files": 1,
  "successful": 1,
  "failed": 0
}
```

#### `POST /documents/ingest-text`

Ingest raw text.

**Request (form-data):**
```
user_id: uuid
text: string
source_name: string (default: "manual-input")
```

#### `GET /documents/status`

Check RAG service status.

#### `DELETE /documents/{user_id}`

Delete all user documents from vector DB.

---

### 4. Chat History

#### `GET /chat/history/{conversation_id}`

Get all messages in a conversation.

#### `GET /chat/conversations/{user_id}`

Get all conversations for a user.

---

### 5. Export

#### `POST /export/generate-summary`

Generate a structured summary document from selected chat messages.

**Request:**
```json
{
  "user_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "Forecast AAPL for 30 days",
      "timestamp": "2026-01-04T07:30:00Z",
      "has_visualization": false,
      "visualization_type": null,
      "image_base64": null
    },
    {
      "role": "assistant", 
      "content": "AAPL is predicted to rise 6% over the next 30 days...",
      "has_visualization": true,
      "visualization_type": "line_chart",
      "image_base64": "iVBORw0KGgo..."
    }
  ],
  "export_format": "markdown",
  "include_visualizations": true,
  "title": "AAPL Forecast Report"
}
```

**Response:**
```json
{
  "title": "Apple Inc. (AAPL) 30-Day Forecast",
  "summary": "Our analysis predicts Apple Inc. (AAPL) to experience a 6% increase...",
  "structured_content": "# Apple Inc. (AAPL) 30-Day Forecast\n\n## Executive Summary\n...",
  "sections": [
    {"title": "Executive Summary", "content": "...", "level": 2},
    {"title": "Key Insights", "content": "- Predicted increase: 6%\n- Volatility: Low", "level": 2},
    {"title": "Recommendations", "content": "...", "level": 2}
  ],
  "visualizations": [
    {"caption": "Chart 1: line_chart", "image_base64": "iVBORw0KGgo..."}
  ],
  "generated_at": "2026-01-04T07:35:00.000000"
}
```

---

## Supported Analytics Queries

| Query Type | Example | Pipeline |
|------------|---------|----------|
| Allocation | "What is my portfolio allocation?" | analytics |
| P&L | "What is my unrealized P&L?" | analytics |
| Trend | "Show me AAPL trend for 6 months" | analytics |
| Ranking | "What are my top 3 performers?" | analytics |
| Comparison | "Compare AAPL and NVDA" | analytics |
| Volatility | "What is the volatility of AAPL?" | analytics |
| Forecast | "Forecast AAPL for 30 days" | forecasting |
| Document Q&A | "What is my cost basis according to my notes?" | rag |

---

## Frontend Integration Notes

### Rendering Response Text

The `response.text` field is **markdown formatted**. Render using a markdown library.

### Rendering Charts

Check `response.visualization.type` and render appropriate chart.

**Option 1: Use Pre-generated Image (Recommended)**
If `response.visualization.image_base64` is present, simply display it:
```javascript
<img src={`data:image/png;base64,${response.visualization.image_base64}`} />
```

**Option 2: Render from Data**
Use `chart_data` to render interactive charts using a library like Chart.js or Recharts:

```javascript
if (response.visualization) {
  const { type, chart_data } = response.visualization;
  // ... rendering logic
}
```

### Sources

Display sources as clickable links:

```javascript
sources.forEach(source => {
  if (source.url) {
    // Market data source with link
    renderLink(source.name, source.url);
  } else {
    // Document source
    renderDocumentBadge(source.name);
  }
});
```

---

## Error Handling

All errors return JSON with `detail` field:

```json
{
  "detail": "Error message"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable
