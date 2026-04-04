#!/usr/bin/env python3
"""AgentForLaw - Agent of Law"""

import json
import sqlite3
import re
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Shared memory setup
SHARED_MEMORY_DIR = Path.home() / ".claw_memory"
SHARED_MEMORY_DIR.mkdir(exist_ok=True)
DB_PATH = SHARED_MEMORY_DIR / "shared_memory.db"

class SharedMemory:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, key TEXT, value TEXT, timestamp TEXT, tags TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS agent_registry (agent_id TEXT PRIMARY KEY, name TEXT, repo TEXT, capabilities TEXT, last_seen TEXT)''')
        self.conn.commit()
    
    def remember(self, key: str, value: str):
        self.cursor.execute("INSERT INTO memories (agent, key, value, timestamp) VALUES (?, ?, ?, ?)", 
                           ("agentforlaw", key, value, datetime.now().isoformat()))
        self.conn.commit()
    
    def recall(self, key: str):
        self.cursor.execute("SELECT agent, key, value FROM memories WHERE key LIKE ? ORDER BY timestamp DESC LIMIT 10", (f"%{key}%",))
        return self.cursor.fetchall()
    
    def get_agents(self):
        self.cursor.execute("SELECT name, capabilities FROM agent_registry")
        return self.cursor.fetchall()
    
    def register(self):
        self.cursor.execute("INSERT OR REPLACE INTO agent_registry VALUES (?, ?, ?, ?, ?)", 
                           ("agentforlaw", "AgentForLaw", "", "Law agent: statutes, constitution, contracts, wills", datetime.now().isoformat()))
        self.conn.commit()
    
    def close(self):
        self.conn.close()

class ConstitutionAccess:
    @staticmethod
    def get_amendment(number: int) -> Dict:
        amendments = {1: "Free speech, religion, press, assembly", 2: "Right to bear arms", 
                      4: "Search and seizure", 5: "Due process", 6: "Speedy trial",
                      8: "No cruel punishment", 10: "States' powers", 13: "Abolish slavery",
                      14: "Equal protection", 19: "Women's vote"}
        return {"amendment": number, "summary": amendments.get(number, "Text not in library"), 
                "url": f"https://www.law.cornell.edu/constitution/amendment{number}"}
    
    @staticmethod
    def get_article(article: int, section: int = None) -> Dict:
        articles = {1: "Legislative Branch", 2: "Executive Branch", 3: "Judicial Branch",
                    4: "States' Powers", 5: "Amendment Process", 6: "Federal Supremacy", 7: "Ratification"}
        result = {"article": article, "title": articles.get(article, "Unknown")}
        if section:
            result["section"] = section
            result["url"] = f"https://www.law.cornell.edu/constitution/article{article}#section{section}"
        else:
            result["url"] = f"https://www.law.cornell.edu/constitution/article{article}"
        return result

class LawRetriever:
    @staticmethod
    def get_statute(citation: str) -> Dict:
        parts = citation.upper().replace('USC', '').strip().split()
        if len(parts) >= 2:
            return {"citation": citation, "url": f"https://www.law.cornell.edu/uscode/text/{parts[0]}/{parts[1]}"}
        return {"error": "Invalid format"}
    
    @staticmethod
    def get_cfr(citation: str) -> Dict:
        match = re.search(r'(\d+)\s+CFR\s+([\d\.]+)', citation, re.IGNORECASE)
        if match:
            return {"citation": citation, "url": f"https://www.ecfr.gov/current/title-{match.group(1)}/section-{match.group(2)}"}
        return {"error": "Invalid format"}

class LegalDefinitions:
    DEFINITIONS = {
        "consideration": "Something of value given in exchange for a promise in a contract.",
        "due_process": "Constitutional requirement that the government respect all legal rights.",
        "tort": "A civil wrong causing harm, giving the right to sue for damages.",
        "contract": "A legally enforceable agreement between two or more parties."
    }
    
    @staticmethod
    def define(term: str) -> Dict:
        return {"term": term, "definition": LegalDefinitions.DEFINITIONS.get(term.lower(), "Definition not found")}
    
    @staticmethod
    def list_terms() -> List[str]:
        return list(LegalDefinitions.DEFINITIONS.keys())

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AgentForLaw - Applies LAW")
    
    parser.add_argument("--analyze", help="Analyze a law question")
    parser.add_argument("--statute", help="Look up US Code")
    parser.add_argument("--case", help="Search case law")
    parser.add_argument("--cfr", help="Look up regulation")
    parser.add_argument("--constitution", action="store_true")
    parser.add_argument("--article", type=int)
    parser.add_argument("--section", type=int)
    parser.add_argument("--amendment", type=int)
    parser.add_argument("--draft-contract", choices=["service", "sale", "employment", "lease", "partnership", "loan"])
    parser.add_argument("--draft-will", action="store_true")
    parser.add_argument("--draft-trust", action="store_true")
    parser.add_argument("--draft-estate", choices=["power_of_attorney", "healthcare_directive", "living_will"])
    parser.add_argument("--parties", help="JSON string of parties")
    parser.add_argument("--provisions", help="JSON string of provisions")
    parser.add_argument("--list-clauses", action="store_true")
    parser.add_argument("--clause", help="Get contract clause")
    parser.add_argument("--define", help="Define a legal term")
    parser.add_argument("--list-terms", action="store_true")
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store in shared memory")
    parser.add_argument("--recall", help="Recall from shared memory")
    parser.add_argument("--agents", action="store_true", help="List all agents")
    parser.add_argument("--agencies", action="store_true")
    parser.add_argument("--domains", action="store_true")
    
    args = parser.parse_args()
    
    # Shared memory
    mem = SharedMemory()
    mem.register()
    
    if args.agencies:
        print("SEC, CFTC, FINRA")
    elif args.domains:
        print("Constitutional, Statutory, Regulatory, Case Law")
    elif args.remember:
        mem.remember(args.remember[0], args.remember[1])
        print(f"✅ Stored: {args.remember[0]}")
    elif args.recall:
        results = mem.recall(args.recall)
        for agent, key, value in results:
            print(f"📥 {agent}: {key} = {value[:100]}")
    elif args.agents:
        agents = mem.get_agents()
        for name, caps in agents:
            print(f"  {name}: {caps[:50]}...")
    elif args.statute:
        print(json.dumps(LawRetriever.get_statute(args.statute), indent=2))
    elif args.cfr:
        print(json.dumps(LawRetriever.get_cfr(args.cfr), indent=2))
    elif args.constitution:
        if args.amendment:
            print(json.dumps(ConstitutionAccess.get_amendment(args.amendment), indent=2))
        elif args.article:
            print(json.dumps(ConstitutionAccess.get_article(args.article, args.section), indent=2))
    elif args.list_terms:
        for term in LegalDefinitions.list_terms():
            print(f"  • {term}")
    elif args.define:
        print(json.dumps(LegalDefinitions.define(args.define), indent=2))
    elif args.draft_will:
        parties = json.loads(args.parties) if args.parties else {}
        provisions = json.loads(args.provisions) if args.provisions else {}
        name = parties.get('name', '_________')
        executor = provisions.get('executor', '_________')
        beneficiary = provisions.get('beneficiary', '_________')
        print(f"""
============================================================
LAST WILL AND TESTAMENT OF {name}
============================================================

I, {name}, declare this to be my Will.

ARTICLE I: EXECUTOR
I appoint {executor} as Executor.

ARTICLE II: DISPOSITION
I give my estate to {beneficiary}.

IN WITNESS WHEREOF on {datetime.now().strftime('%B %d, %Y')}.

{name} (Testator)
============================================================
""")
    elif args.draft_contract:
        parties = json.loads(args.parties) if args.parties else {}
        provisions = json.loads(args.provisions) if args.provisions else {}
        party_a = parties.get('party_a', 'Party A')
        party_b = parties.get('party_b', 'Party B')
        services = provisions.get('services', 'services')
        payment = provisions.get('payment', '$0')
        print(f"""
============================================================
{args.draft_contract.upper()} CONTRACT
============================================================

PARTIES: {party_a} and {party_b}

SERVICES: {services}

PAYMENT: {payment}

GOVERNING LAW: Delaware

Date: {datetime.now().strftime('%B %d, %Y')}
============================================================
""")
    elif args.analyze:
        print(f"\n📜 ANALYSIS of '{args.analyze}':")
        print("   (Run with GROQ_API_KEY or Ollama for AI analysis)")
    else:
        parser.print_help()
    
    mem.close()

if __name__ == "__main__":
    main()

# Add to argument parser (after other commands)
parser.add_argument("--teach", help="Teach AgentForLaw about a case (name, citation, holding)")
parser.add_argument("--find-case", help="Search for a case in the knowledge base")

# Add handlers
elif args.teach:
    from case_law_kb import CaseLawDatabase
    kb = CaseLawDatabase()
    
    # Parse input - format: "Case Name|citation|year|holding"
    parts = args.teach.split('|')
    case_data = {
        'name': parts[0] if len(parts) > 0 else "Unknown",
        'citation': parts[1] if len(parts) > 1 else "",
        'year': int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
        'holding': parts[3] if len(parts) > 3 else "",
        'court': parts[4] if len(parts) > 4 else "Supreme Court",
        'keywords': parts[5] if len(parts) > 5 else ""
    }
    
    case_id = kb.add_case(case_data)
    print(f"✅ Taught AgentForLaw about {case_data['name']}")
    print(f"   ID: {case_id}")
    print(f"   Citation: {case_data['citation']}")
    print(f"   Holding: {case_data['holding'][:100]}...")

elif args.find_case:
    from case_law_kb import CaseLawDatabase
    kb = CaseLawDatabase()
    results = kb.search_cases(args.find_case)
    
    if results:
        print(f"\n📚 CASES FOUND for '{args.find_case}':\n")
        for r in results:
            print(f"   • {r[0]} ({r[1]}) - {r[2]}")
            print(f"     Holding: {r[3][:100]}...")
            print(f"     Keywords: {r[4]}\n")
    else:
        print(f"No cases found for '{args.find_case}'")
        print("Try teaching me with: --teach 'Case Name|citation|year|holding'")
