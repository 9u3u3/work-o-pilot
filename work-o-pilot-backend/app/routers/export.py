"""
Export Router
Generates structured summaries of chat conversations for document export
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.services.groq_client import groq_client

router = APIRouter(prefix="/export", tags=["export"])


class ChatMessage(BaseModel):
    """A single chat message for export"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None
    has_visualization: bool = False
    visualization_type: Optional[str] = None
    image_base64: Optional[str] = None  # If there's a chart image


class ExportRequest(BaseModel):
    """Request to generate export summary"""
    user_id: UUID
    messages: List[ChatMessage]
    export_format: str = "markdown"  # "markdown", "html", "text"
    include_visualizations: bool = True
    title: Optional[str] = None


class ExportResponse(BaseModel):
    """Generated export document"""
    title: str
    summary: str
    structured_content: str  # Full formatted document
    sections: List[Dict[str, Any]]  # Broken down sections
    visualizations: List[Dict[str, str]]  # List of images with captions
    generated_at: str


EXPORT_SYSTEM_PROMPT = """You are a financial report generator. Your job is to:
1. Take a conversation between a user and a stock analytics AI
2. Create a well-structured, professional summary document

Output format (markdown):

# [Title based on conversation topic]

## Executive Summary
[2-3 sentence overview of the key findings]

## Key Insights
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

## Detailed Analysis
[Structured breakdown of the data discussed]

### [Section 1 Title]
[Content]

### [Section 2 Title]  
[Content]

## Data Sources
[List the sources mentioned]

## Recommendations
[If any actionable insights were discussed]

---
*Report generated from AI analytics conversation*

Rules:
- Be professional and concise
- Use proper markdown formatting
- Include specific numbers and percentages from the conversation
- Group related information together
- Make it suitable for export to PDF/Word
"""


@router.post("/generate-summary", response_model=ExportResponse)
async def generate_export_summary(request: ExportRequest):
    """
    Generate a structured summary document from selected chat messages.
    
    Takes selected messages from a conversation and creates a 
    professional, exportable summary document.
    """
    from datetime import datetime
    
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided for export"
        )
    
    # Format messages for AI
    conversation_text = _format_messages_for_ai(request.messages)
    
    # Collect visualizations
    visualizations = []
    for i, msg in enumerate(request.messages):
        if msg.image_base64:
            visualizations.append({
                "caption": f"Chart {i+1}: {msg.visualization_type or 'Analytics Chart'}",
                "image_base64": msg.image_base64
            })
    
    # Generate summary using AI
    if groq_client.is_available():
        summary_content = await _generate_ai_summary(conversation_text)
    else:
        summary_content = _generate_fallback_summary(request.messages)
    
    # Parse into sections
    sections = _parse_sections(summary_content)
    
    # Extract title
    title = request.title or _extract_title(summary_content) or "Stock Analytics Report"
    
    # Extract executive summary
    exec_summary = _extract_executive_summary(summary_content)
    
    return ExportResponse(
        title=title,
        summary=exec_summary,
        structured_content=summary_content,
        sections=sections,
        visualizations=visualizations,
        generated_at=datetime.now().isoformat()
    )


def _format_messages_for_ai(messages: List[ChatMessage]) -> str:
    """Format chat messages into a conversation string."""
    parts = []
    for msg in messages:
        role = "User" if msg.role == "user" else "Assistant"
        content = msg.content
        
        if msg.has_visualization:
            content += f"\n[Visualization: {msg.visualization_type}]"
        
        parts.append(f"{role}: {content}")
    
    return "\n\n".join(parts)


async def _generate_ai_summary(conversation: str) -> str:
    """Generate summary using AI."""
    messages = [
        {"role": "system", "content": EXPORT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Generate a professional export document from this conversation:\n\n{conversation}"}
    ]
    
    try:
        response = groq_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )
        return response.strip()
    except Exception as e:
        print(f"AI summary error: {e}")
        return _generate_fallback_summary([])


def _generate_fallback_summary(messages: List[ChatMessage]) -> str:
    """Generate basic summary when AI is unavailable."""
    parts = ["# Stock Analytics Report\n"]
    parts.append("## Conversation Summary\n")
    
    for msg in messages:
        if msg.role == "assistant":
            parts.append(msg.content + "\n")
    
    parts.append("\n---\n*Report generated from AI analytics conversation*")
    return "\n".join(parts)


def _parse_sections(content: str) -> List[Dict[str, Any]]:
    """Parse markdown content into sections."""
    sections = []
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections.append({
                    "title": current_section,
                    "content": '\n'.join(current_content).strip(),
                    "level": 2
                })
            current_section = line[3:].strip()
            current_content = []
        elif line.startswith('### '):
            if current_section:
                sections.append({
                    "title": current_section,
                    "content": '\n'.join(current_content).strip(),
                    "level": 2
                })
            current_section = line[4:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections.append({
            "title": current_section,
            "content": '\n'.join(current_content).strip(),
            "level": 2
        })
    
    return sections


def _extract_title(content: str) -> Optional[str]:
    """Extract title from markdown content."""
    for line in content.split('\n'):
        if line.startswith('# ') and not line.startswith('## '):
            return line[2:].strip()
    return None


def _extract_executive_summary(content: str) -> str:
    """Extract executive summary section."""
    in_summary = False
    summary_lines = []
    
    for line in content.split('\n'):
        if '## Executive Summary' in line or '## Summary' in line:
            in_summary = True
            continue
        elif in_summary and line.startswith('##'):
            break
        elif in_summary and line.strip():
            summary_lines.append(line)
    
    return ' '.join(summary_lines).strip() or "Stock analytics conversation summary."
