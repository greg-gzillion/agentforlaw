#!/usr/bin/env python3
"""
agentforlaw - Agent that studies statutes, codes, regulations, and rules
Part of the claw ecosystem: rustypycraw, eagleclaw, crustyclaw, claw-coder, agentforlaw
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Shared memory path
SHARED_MEMORY_DIR = Path.home() / ".claw_memory"
SHARED_MEMORY_DIR.mkdir(exist_ok=True)
DB_PATH = SHARED_MEMORY_DIR / "shared_memory.db"

class SharedMemory:
    """Connect to shared memory across all agents"""
    
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

class AgentForLaw:
    """AgentForLaw - understands law as a system of rules across all jurisdictions"""
    
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        
        # FREE LAW RESOURCES
        self.free_law_resources = {
            "supreme_court": {
                "name": "US Supreme Court",
                "url": "https://www.supremecourt.gov/opinions/opinions.aspx",
                "cases": "https://www.oyez.org/"
            },
            "court_listener": {
                "name": "CourtListener - Free case law",
                "url": "https://www.courtlistener.com/",
                "search": "https://www.courtlistener.com/search/"
            },
            "google_scholar": {
                "name": "Google Scholar - Legal Opinions",
                "url": "https://scholar.google.com/scholar",
                "cases": "https://scholar.google.com/intl/en/scholar/legal.html"
            },
            "justia": {
                "name": "Justia - Free Law",
                "url": "https://law.justia.com/",
                "constitution": "https://law.justia.com/constitution/us/"
            },
            "cornell_law": {
                "name": "Cornell LII",
                "url": "https://www.law.cornell.edu/",
                "constitution": "https://www.law.cornell.edu/constitution"
            }
        }
        
        self.constitution_resources = {
            "archives": "https://www.archives.gov/founding-docs/constitution",
            "congress": "https://constitution.congress.gov/",
            "cornell": "https://www.law.cornell.edu/constitution",
            "justia": "https://law.justia.com/constitution/us/"
        }
        
        self.domains = {
            "constitutional": "Constitution, fundamental law, bill of rights",
            "statutory": "written laws passed by legislatures",
            "regulatory": "agency rules and regulations",
            "common_law": "judge-made law from precedent",
            "contract": "agreements and obligations",
            "criminal": "crimes and punishments",
            "international": "treaties and customary law"
        }
        
        self.constitutional_principles = {
            "due_process": "5th and 14th Amendments",
            "equal_protection": "14th Amendment",
            "free_speech": "1st Amendment",
            "separation_of_powers": "Legislative, Executive, Judicial branches"
        }
    
    def get_law_resources(self, category: str = None) -> Dict:
        if category == "cases":
            return self.free_law_resources
        elif category == "constitution":
            return self.constitution_resources
        else:
            return {"cases": self.free_law_resources, "constitution": self.constitution_resources}
    
    def search_case_law(self, query: str) -> List[Dict]:
        return [
            {"source": "CourtListener", "url": f"https://www.courtlistener.com/search/?q={query.replace(' ', '+')}"},
            {"source": "Google Scholar", "url": f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"},
            {"source": "Justia", "url": f"https://law.justia.com/cases/?q={query.replace(' ', '+')}"}
        ]
    
    def get_constitution(self) -> Dict:
        return self.constitution_resources
    
    def get_constitutional_principle(self, principle: str) -> Dict:
        if principle in self.constitutional_principles:
            return {"principle": principle, "description": self.constitutional_principles[principle]}
        return {"error": f"Principle '{principle}' not found"}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw - Studies law")
    parser.add_argument("--domains", action="store_true", help="List law domains")
    parser.add_argument("--resources", help="Show law resources (cases, constitution)")
    parser.add_argument("--search-cases", help="Search case law")
    parser.add_argument("--constitution", action="store_true", help="Get constitution resources")
    parser.add_argument("--principle", help="Get constitutional principle")
    parser.add_argument("--recall", help="Recall memories from all agents")
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store a memory")
    parser.add_argument("--agents", action="store_true", help="Show other agents")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    if args.domains:
        print("\nLaw Domains:")
        for d, desc in agent.domains.items():
            print(f"  {d}: {desc}")
    elif args.resources:
        result = agent.get_law_resources(args.resources)
        print(json.dumps(result, indent=2))
    elif args.search_cases:
        results = agent.search_case_law(args.search_cases)
        print(json.dumps(results, indent=2))
    elif args.constitution:
        result = agent.get_constitution()
        print(json.dumps(result, indent=2))
    elif args.principle:
        result = agent.get_constitutional_principle(args.principle)
        print(json.dumps(result, indent=2))
    elif args.agents:
        agents = agent.shared.get_other_agents()
        print("\n🦞 Other Agents in Ecosystem:")
        for name, caps in agents:
            print(f"  {name}: {caps[:60]}...")
    elif args.recall:
        results = agent.shared.recall(args.recall)
        if results:
            print(f"\n📖 Memories matching '{args.recall}':")
            for ag, key, value, tags in results:
                print(f"\n🦞 {ag}: {key}")
                print(f"   {value[:200]}...")
        else:
            print(f"No memories found for '{args.recall}'")
    elif args.remember:
        agent.shared.remember(args.remember[0], args.remember[1])
        print(f"✅ Memory stored: {args.remember[0]} = {args.remember[1]}")
    else:
        parser.print_help()
    
    agent.shared.close()

if __name__ == "__main__":
    main()
