import { Chat, Message } from "@/types/chat";

const now = new Date();
const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
const fiveDaysAgo = new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000);
const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

export const mockChats: Chat[] = [
  {
    id: "1",
    title: "Q4 Revenue Analysis",
    createdAt: now,
    updatedAt: now,
    messages: [
      {
        id: "1-1",
        role: "user",
        content: "Can you analyze our Q4 revenue data and identify the top performing products?",
        timestamp: new Date(now.getTime() - 30 * 60 * 1000),
      },
      {
        id: "1-2",
        role: "assistant",
        content: `## Q4 Revenue Analysis Summary

Based on the data provided, here are the key findings:

### Top 5 Performing Products

| Rank | Product | Revenue | Growth |
|------|---------|---------|--------|
| 1 | Enterprise Suite | $2.4M | +34% |
| 2 | Pro Analytics | $1.8M | +28% |
| 3 | Team Collaboration | $1.2M | +22% |
| 4 | Data Connector | $890K | +18% |
| 5 | API Access | $670K | +15% |

### Key Insights

- **Enterprise Suite** continues to lead with the strongest quarter-over-quarter growth
- The **Pro Analytics** tier saw significant adoption from mid-market companies
- **Team Collaboration** features drove upgrades from basic to premium tiers

\`\`\`sql
SELECT product_name, SUM(revenue) as total_revenue
FROM sales
WHERE quarter = 'Q4' AND year = 2024
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 5;
\`\`\`

Would you like me to dive deeper into any specific product category?`,
        timestamp: new Date(now.getTime() - 28 * 60 * 1000),
      },
      {
        id: "1-3",
        role: "user",
        content: "Yes, can you break down the Enterprise Suite revenue by region?",
        timestamp: new Date(now.getTime() - 25 * 60 * 1000),
      },
      {
        id: "1-4",
        role: "assistant",
        content: `## Enterprise Suite - Regional Breakdown

### Revenue by Region

| Region | Revenue | % of Total | YoY Change |
|--------|---------|------------|------------|
| North America | $1.2M | 50% | +42% |
| Europe | $720K | 30% | +28% |
| APAC | $360K | 15% | +35% |
| LATAM | $120K | 5% | +18% |

### Notable Trends

1. **North America** remains the largest market, driven by large enterprise deals
2. **APAC** showed the second-highest growth rate, particularly in Japan and Australia
3. **Europe** expansion is gaining momentum with GDPR-compliant features

The growth in APAC suggests opportunity for increased investment in that region.`,
        timestamp: new Date(now.getTime() - 22 * 60 * 1000),
      },
    ],
  },
  {
    id: "2",
    title: "Customer Churn Prediction",
    createdAt: yesterday,
    updatedAt: yesterday,
    messages: [
      {
        id: "2-1",
        role: "user",
        content: "I need help understanding our customer churn patterns",
        timestamp: yesterday,
      },
      {
        id: "2-2",
        role: "assistant",
        content: `## Churn Analysis Overview

I've analyzed your customer data and identified several key churn indicators:

### High-Risk Factors
- **Login frequency** drop > 50% in 30 days
- **Feature usage** decline in core workflows
- **Support tickets** increase without resolution
- **Contract renewal** approaching within 60 days

### Recommendations
1. Implement proactive outreach for accounts showing 2+ risk factors
2. Create automated health score dashboard
3. Set up early warning alerts for Customer Success team`,
        timestamp: yesterday,
      },
    ],
  },
  {
    id: "3",
    title: "Sales Pipeline Review",
    createdAt: threeDaysAgo,
    updatedAt: threeDaysAgo,
    messages: [
      {
        id: "3-1",
        role: "user",
        content: "Show me the current sales pipeline status",
        timestamp: threeDaysAgo,
      },
      {
        id: "3-2",
        role: "assistant",
        content: `## Sales Pipeline Status

### Pipeline Summary
- **Total Pipeline Value:** $8.2M
- **Weighted Value:** $4.1M
- **Expected Close (This Quarter):** $2.8M

### Stage Breakdown

| Stage | Deals | Value | Avg Days |
|-------|-------|-------|----------|
| Discovery | 24 | $2.4M | 12 |
| Qualification | 18 | $2.1M | 28 |
| Proposal | 12 | $1.8M | 45 |
| Negotiation | 8 | $1.2M | 62 |
| Closing | 5 | $700K | 78 |

The pipeline is healthy with good distribution across stages.`,
        timestamp: threeDaysAgo,
      },
    ],
  },
  {
    id: "4",
    title: "Marketing Campaign ROI",
    createdAt: fiveDaysAgo,
    updatedAt: fiveDaysAgo,
    messages: [
      {
        id: "4-1",
        role: "user",
        content: "What's the ROI on our recent marketing campaigns?",
        timestamp: fiveDaysAgo,
      },
      {
        id: "4-2",
        role: "assistant",
        content: `## Marketing Campaign ROI Analysis

### Campaign Performance

| Campaign | Spend | Revenue | ROI |
|----------|-------|---------|-----|
| LinkedIn Ads | $45K | $180K | 300% |
| Google Search | $32K | $96K | 200% |
| Content Marketing | $28K | $112K | 300% |
| Webinar Series | $15K | $75K | 400% |
| Trade Shows | $80K | $160K | 100% |

**Best Performer:** Webinar Series with 400% ROI
**Recommendation:** Increase investment in high-ROI digital channels`,
        timestamp: fiveDaysAgo,
      },
    ],
  },
  {
    id: "5",
    title: "Inventory Optimization",
    createdAt: twoWeeksAgo,
    updatedAt: twoWeeksAgo,
    messages: [
      {
        id: "5-1",
        role: "user",
        content: "Help me optimize our inventory levels",
        timestamp: twoWeeksAgo,
      },
      {
        id: "5-2",
        role: "assistant",
        content: `## Inventory Optimization Recommendations

Based on historical sales data and current stock levels:

### Overstocked Items (Reduce)
- Product A: 45 days excess inventory
- Product D: 38 days excess inventory

### Understocked Items (Increase)
- Product B: Only 8 days remaining
- Product E: Only 12 days remaining

### Action Items
1. Run promotion on overstocked items
2. Expedite orders for understocked items
3. Adjust reorder points based on seasonality`,
        timestamp: twoWeeksAgo,
      },
    ],
  },
];

export const mockAIResponses = [
  `## Analysis Complete

I've processed your data and here are the key findings:

### Summary
- Total records analyzed: **12,847**
- Time range: Last 90 days
- Key metrics identified: 8

### Recommendations
1. Focus on high-value segments
2. Optimize conversion funnel
3. Reduce customer acquisition cost

Would you like me to elaborate on any of these points?`,

  `## Data Insights

Based on the uploaded file, I can see several interesting patterns:

| Metric | Value | Trend |
|--------|-------|-------|
| Growth Rate | 23% | ↑ |
| Retention | 89% | → |
| NPS Score | 72 | ↑ |

### Next Steps
- Segment analysis by region
- Cohort comparison
- Predictive modeling

Let me know which direction you'd like to explore.`,

  `## Quick Summary

Here's what I found in your data:

\`\`\`python
# Key statistics
mean_value = 847.32
median_value = 792.00
std_deviation = 234.56
\`\`\`

The data shows a **positive trend** with some seasonal variation. The Q4 numbers are particularly strong.

Should I generate a detailed report or focus on specific segments?`,
];

export function getRandomMockResponse(): string {
  return mockAIResponses[Math.floor(Math.random() * mockAIResponses.length)];
}
