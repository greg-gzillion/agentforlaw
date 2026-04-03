#!/usr/bin/env python3
"""
agentforlaw - Agent that studies statutes, codes, regulations, and rules
Part of the claw ecosystem: rustypycraw, eagleclaw, crustyclaw, claw-coder, agentforlaw
"""

import json
import sqlite3
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Shared memory path
SHARED_MEMORY_DIR = Path.home() / ".claw_memory"
SHARED_MEMORY_DIR.mkdir(exist_ok=True)
DB_PATH = SHARED_MEMORY_DIR / "shared_memory.db"

class SharedMemory:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                tags TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_registry (
                agent_id TEXT PRIMARY KEY,
                name TEXT,
                repo TEXT,
                capabilities TEXT,
                last_seen TEXT
            )
        ''')
        self.conn.commit()
    
    def remember(self, key: str, value: str, tags: str = ""):
        self.cursor.execute(
            "INSERT INTO memories (agent, key, value, timestamp, tags) VALUES (?, ?, ?, ?, ?)",
            ("agentforlaw", key, value, datetime.now().isoformat(), tags)
        )
        self.conn.commit()
    
    def recall(self, key: str) -> list:
        self.cursor.execute(
            "SELECT agent, key, value, tags FROM memories WHERE key LIKE ? ORDER BY timestamp DESC LIMIT 10",
            (f"%{key}%",)
        )
        return self.cursor.fetchall()
    
    def register(self):
        self.cursor.execute(
            "INSERT OR REPLACE INTO agent_registry VALUES (?, ?, ?, ?, ?)",
            ("agentforlaw", "AgentForLaw", "https://github.com/greg-gzillion/agentforlaw", 
             "law study, case law, constitution, statutes, regulations", datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_other_agents(self) -> list:
        self.cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class LawRetriever:
    @staticmethod
    def get_case_text(case_name: str) -> Dict:
        try:
            url = f"https://www.courtlistener.com/api/rest/v3/opinions/?search={case_name.replace(' ', '+')}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    r = data['results'][0]
                    return {"case": case_name, "citation": r.get('citation', 'Unknown'), "url": r.get('absolute_url', '')}
            return {"error": "Not found", "url": f"https://www.courtlistener.com/?q={case_name.replace(' ', '+')}"}
        except:
            return {"error": "API error", "url": f"https://scholar.google.com/scholar?q={case_name.replace(' ', '+')}"}
    
    @staticmethod
    def get_statute(citation: str) -> Dict:
        parts = citation.upper().replace('USC', '').strip().split()
        if len(parts) >= 2:
            return {"citation": citation, "url": f"https://www.law.cornell.edu/uscode/text/{parts[0]}/{parts[1]}"}
        return {"error": "Invalid format. Example: 15 USC 78a"}
    
    @staticmethod
    def get_regulation(citation: str) -> Dict:
        parts = citation.upper().replace('CFR', '').strip().split()
        if len(parts) >= 2:
            return {"citation": citation, "url": f"https://www.ecfr.gov/current/title-{parts[0]}/section-{parts[1]}"}
        return {"error": "Invalid format. Example: 17 CFR 240.10b-5"}

class LegalReasoner:
    def __init__(self):
        self.groq_available = False
        try:
            from groq import Groq
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                self.client = Groq(api_key=api_key)
                self.groq_available = True
        except:
            pass
    
    def analyze(self, question: str) -> str:
        if not self.groq_available:
            return "GROQ_API_KEY not set. Install groq for AI analysis."
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"As an agent of law, analyze: {question}"}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

class RealTimeMonitor:
    @staticmethod
    def get_recent_scotus():
        try:
            url = "https://www.courtlistener.com/api/rest/v3/opinions/?court=scotus&order_by=date_filed&limit=5"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [{"case": r.get('case_name', 'Unknown'), "date": r.get('date_filed', '')} for r in data.get('results', [])]
            return []
        except:
            return []

class AgentForLaw:
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        self.reasoner = LegalReasoner()
        
        self.regulatory_agencies = {
            "sec": {"name": "Securities and Exchange Commission", "url": "https://www.sec.gov/"},
            "cftc": {"name": "Commodity Futures Trading Commission", "url": "https://www.cftc.gov/"},
            "finra": {"name": "FINRA", "url": "https://www.finra.org/"},
            "fincen": {"name": "FinCEN", "url": "https://www.fincen.gov/"},
            "ofac": {"name": "OFAC", "url": "https://ofac.treasury.gov/"}
        }
        
        self.domains = {
            "constitutional": "Constitution, fundamental law",
            "statutory": "Written laws", "regulatory": "Agency rules",
            "securities": "SEC, FINRA rules", "aml": "FinCEN, FATF"
        }
    
    def get_agency(self, name: str) -> Dict:
        return self.regulatory_agencies.get(name.lower(), {"error": "Not found"})
    
    def get_all_agencies(self) -> List[str]:
        return list(self.regulatory_agencies.keys())

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw")
    parser.add_argument("--agencies", action="store_true", help="List agencies")
    parser.add_argument("--agency", help="Get agency info")
    parser.add_argument("--domains", action="store_true", help="List domains")
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store memory")
    parser.add_argument("--recall", help="Recall memory")
    parser.add_argument("--agents", action="store_true", help="Show other agents")
    parser.add_argument("--case-text", help="Get case text")
    parser.add_argument("--statute", help="Get statute (e.g., '15 USC 78a')")
    parser.add_argument("--regulation", help="Get regulation (e.g., '17 CFR 240.10b-5')")
    parser.add_argument("--analyze", help="Analyze legal question")
    parser.add_argument("--recent", choices=["scotus"], help="Recent updates")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    if args.agencies:
        print("\nRegulatory Agencies:")
        for a in agent.get_all_agencies():
            print(f"  {a.upper()}")
    elif args.agency:
        print(json.dumps(agent.get_agency(args.agency), indent=2))
    elif args.domains:
        print("\nLaw Domains:")
        for d, desc in agent.domains.items():
            print(f"  {d}: {desc}")
    elif args.remember:
        agent.shared.remember(args.remember[0], args.remember[1])
        print(f"✅ Memory stored: {args.remember[0]}")
    elif args.recall:
        results = agent.shared.recall(args.recall)
        if results:
            for r in results:
                print(f"\n🦞 {r[0]}: {r[1]}\n   {r[2][:200]}...")
        else:
            print("No memories found")
    elif args.agents:
        others = agent.shared.get_other_agents()
        print("\nOther Agents:")
        for name, caps in others:
            print(f"  {name}: {caps[:60]}...")
    elif args.case_text:
        print(json.dumps(LawRetriever.get_case_text(args.case_text), indent=2))
    elif args.statute:
        print(json.dumps(LawRetriever.get_statute(args.statute), indent=2))
    elif args.regulation:
        print(json.dumps(LawRetriever.get_regulation(args.regulation), indent=2))
    elif args.analyze:
        print(f"\n🤖 Analysis:\n{agent.reasoner.analyze(args.analyze)}\n")
    elif args.recent:
        if args.recent == "scotus":
            print(json.dumps(RealTimeMonitor.get_recent_scotus(), indent=2))
    else:
        parser.print_help()
    
    agent.shared.close()

if __name__ == "__main__":
    main()
