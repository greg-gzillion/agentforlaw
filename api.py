#!/usr/bin/env python3
"""
AgentForLaw REST API
Run: python api.py
Endpoint: http://localhost:8000
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import subprocess
import json
import sqlite3
from datetime import datetime
from pathlib import Path

app = FastAPI(title="AgentForLaw API", description="Apply law via REST API")

SHARED_MEMORY_DIR = Path.home() / ".claw_memory"
DB_PATH = SHARED_MEMORY_DIR / "shared_memory.db"

class LawRequest(BaseModel):
    question: str

class StatuteRequest(BaseModel):
    citation: str

class ContractRequest(BaseModel):
    contract_type: str
    parties: dict
    provisions: dict

class MemoryRequest(BaseModel):
    key: str
    value: str

@app.get("/")
def root():
    return {"agent": "AgentForLaw", "status": "running", "endpoints": ["/analyze", "/statute", "/case", "/constitution", "/draft/contract", "/draft/will", "/memory/remember", "/memory/recall", "/memory/agents"]}

@app.post("/analyze")
def analyze(req: LawRequest):
    """Apply law to a question"""
    import os
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"State the law directly. No conversation. Question: {req.question}"}],
        max_tokens=500,
        temperature=0.0
    )
    return {"question": req.question, "answer": response.choices[0].message.content}

@app.post("/statute")
def statute(req: StatuteRequest):
    """Look up a statute"""
    parts = req.citation.upper().replace('USC', '').strip().split()
    if len(parts) >= 2:
        return {"citation": req.citation, "url": f"https://www.law.cornell.edu/uscode/text/{parts[0]}/{parts[1]}"}
    raise HTTPException(status_code=400, detail="Invalid citation format")

@app.get("/case/{case_name}")
def case(case_name: str):
    """Search case law"""
    return {"case": case_name, "url": f"https://www.courtlistener.com/?q={case_name.replace(' ', '+')}"}

@app.get("/constitution/article/{article}")
def constitution_article(article: int, section: Optional[int] = None):
    """Read Constitution article"""
    articles = {1: "Legislative Branch", 2: "Executive Branch", 3: "Judicial Branch"}
    if section:
        return {"article": article, "section": section, "url": f"https://www.law.cornell.edu/constitution/article{article}#section{section}"}
    return {"article": article, "title": articles.get(article, "Unknown"), "url": f"https://www.law.cornell.edu/constitution/article{article}"}

@app.get("/constitution/amendment/{number}")
def constitution_amendment(number: int):
    """Read Constitution amendment"""
    amendments = {1: "Free speech", 2: "Bear arms", 4: "Search and seizure", 5: "Due process", 14: "Equal protection"}
    return {"amendment": number, "summary": amendments.get(number, "Unknown"), "url": f"https://www.law.cornell.edu/constitution/amendment{number}"}

@app.post("/draft/contract")
def draft_contract(req: ContractRequest):
    """Draft a contract"""
    from agentforlaw import LawDocumentDrafting
    result = LawDocumentDrafting.draft_contract(req.contract_type, req.parties, req.provisions)
    return {"contract": result}

@app.post("/draft/will")
def draft_will(parties: dict, provisions: dict):
    """Draft a will"""
    from agentforlaw import LawDocumentDrafting
    result = LawDocumentDrafting.draft_will(parties, provisions)
    return {"will": result}

@app.post("/memory/remember")
def memory_remember(req: MemoryRequest):
    """Store in shared memory"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memories (agent, key, value, timestamp) VALUES (?, ?, ?, ?)", 
                   ("agentforlaw", req.key, req.value, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"stored": req.key, "value": req.value}

@app.get("/memory/recall/{key}")
def memory_recall(key: str):
    """Recall from shared memory"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT agent, key, value FROM memories WHERE key LIKE ? ORDER BY timestamp DESC LIMIT 5", (f"%{key}%",))
    results = [{"agent": r[0], "key": r[1], "value": r[2]} for r in cursor.fetchall()]
    conn.close()
    return {"recall": key, "results": results}

@app.get("/memory/agents")
def memory_agents():
    """List other claw agents"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
    results = [{"name": r[0], "capabilities": r[1]} for r in cursor.fetchall()]
    conn.close()
    return {"agents": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
