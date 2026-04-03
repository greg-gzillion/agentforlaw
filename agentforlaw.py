#!/usr/bin/env python3
"""
agentforlaw - Agent that studies and works with law (statutes, codes, regulations, constitutions)
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
             "law study, statutes, codes, regulations, constitutions, document drafting", datetime.now().isoformat())
        )
        self.conn.commit()
    
    def get_other_agents(self) -> list:
        self.cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class LawDocumentDrafting:
    """Draft law documents: rules, statutes, codes, regulations, constitutions, notices, writs"""
    
    @staticmethod
    def draft(document_type: str, params: Dict) -> str:
        """Draft a law document based on type"""
        
        if document_type == "statute":
            return LawDocumentDrafting._draft_statute(params)
        elif document_type == "regulation":
            return LawDocumentDrafting._draft_regulation(params)
        elif document_type == "code_section":
            return LawDocumentDrafting._draft_code_section(params)
        elif document_type == "constitutional_article":
            return LawDocumentDrafting._draft_constitutional_article(params)
        elif document_type == "notice":
            return LawDocumentDrafting._draft_notice(params)
        elif document_type == "writ":
            return LawDocumentDrafting._draft_writ(params)
        elif document_type == "rule":
            return LawDocumentDrafting._draft_rule(params)
        elif document_type == "order":
            return LawDocumentDrafting._draft_order(params)
        elif document_type == "finding":
            return LawDocumentDrafting._draft_finding(params)
        else:
            return f"Unknown document type: {document_type}"
    
    @staticmethod
    def _draft_statute(params: Dict) -> str:
        """Draft a statute (written law passed by legislature)"""
        date = datetime.now().strftime("%Y")
        return f"""
[STATUTE]
Title: {params.get('title', 'An Act')}
Citation: {params.get('citation', 'Public Law ___')}
Enacted: {date}

Section 1. {params.get('section_1', 'Short title.')}
Section 2. {params.get('section_2', 'Findings and purpose.')}
Section 3. {params.get('section_3', 'Definitions.')}
Section 4. {params.get('section_4', 'Substantive provisions.')}
Section 5. {params.get('section_5', 'Enforcement.')}
Section 6. {params.get('section_6', 'Effective date.')}

Passed by the Legislature.
"""
    
    @staticmethod
    def _draft_regulation(params: Dict) -> str:
        """Draft a regulation (agency rule)"""
        return f"""
[REGULATION]
Agency: {params.get('agency', 'Agency Name')}
Citation: {params.get('citation', '___ CFR ___')}
Title: {params.get('title', 'Rule Title')}

§ {params.get('section', '1.0')} Purpose.
{params.get('purpose', 'This regulation establishes rules for...')}

§ {params.get('section', '2.0')} Definitions.
{params.get('definitions', 'Terms defined.')}

§ {params.get('section', '3.0')} Requirements.
{params.get('requirements', 'Persons subject to this regulation shall...')}

§ {params.get('section', '4.0')} Enforcement.
{params.get('enforcement', 'Violations subject to penalty.')}

Effective: {params.get('effective', '30 days after publication')}
"""
    
    @staticmethod
    def _draft_code_section(params: Dict) -> str:
        """Draft a code section"""
        return f"""
[CODE SECTION]
Code: {params.get('code', 'United States Code')}
Title: {params.get('title', '___')}
Section: {params.get('section', '§ ___')}

(a) {params.get('subsection_a', 'General rule.')}
(b) {params.get('subsection_b', 'Exceptions.')}
(c) {params.get('subsection_c', 'Penalties.')}
(d) {params.get('subsection_d', 'Definitions.')}
"""
    
    @staticmethod
    def _draft_constitutional_article(params: Dict) -> str:
        """Draft a constitutional article"""
        return f"""
[CONSTITUTION]
Article: {params.get('article', '___')}
Section: {params.get('section', '___')}

Clause 1. {params.get('clause_1', 'Text of clause.')}
Clause 2. {params.get('clause_2', 'Text of clause.')}
Clause 3. {params.get('clause_3', 'Text of clause.')}

Ratified: {params.get('ratified', 'Date of ratification')}
"""
    
    @staticmethod
    def _draft_notice(params: Dict) -> str:
        """Draft a notice (formal announcement)"""
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
[NOTICE]
Date: {date}
To: {params.get('to', 'All concerned parties')}
From: {params.get('from', 'Issuing authority')}
Subject: {params.get('subject', 'Notice of action')}

Notice is hereby given that:
{params.get('body', 'The following action is taken.')}

Effective: {params.get('effective', 'Upon publication')}
"""
    
    @staticmethod
    def _draft_writ(params: Dict) -> str:
        """Draft a writ (formal written order)"""
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
[WRIT]
Date: {date}
To: {params.get('to', 'Recipient')}
From: {params.get('from', 'Issuing authority')}
Case: {params.get('case', 'Case number')}

ORDERED: {params.get('order', 'The recipient shall take the following action.')}

Returnable by: {params.get('return_date', 'Date of return')}
"""
    
    @staticmethod
    def _draft_rule(params: Dict) -> str:
        """Draft a rule"""
        return f"""
[RULE]
Rule Number: {params.get('number', '___')}
Title: {params.get('title', 'Rule title')}

(a) {params.get('subpart_a', 'Rule text.')}
(b) {params.get('subpart_b', 'Rule text.')}
(c) {params.get('subpart_c', 'Rule text.')}

Effective: {params.get('effective', 'Date effective')}
"""
    
    @staticmethod
    def _draft_order(params: Dict) -> str:
        """Draft an order"""
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
[ORDER]
Date: {date}
Case: {params.get('case', 'Case number')}

ORDERED, ADJUDGED, AND DECREED that:
{params.get('decree', 'The following is ordered.')}

So ordered.
"""
    
    @staticmethod
    def _draft_finding(params: Dict) -> str:
        """Draft a finding of fact or law"""
        return f"""
[FINDING]
Case: {params.get('case', 'Case number')}
Finding: {params.get('finding_type', 'Finding of fact')}

The finder finds that:
{params.get('finding', 'The following facts are established.')}

Conclusion: {params.get('conclusion', 'Based on the findings, the following conclusion.')}
"""

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

class LawReasoner:
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
            return "GROQ_API_KEY not set. Install groq for law analysis."
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"As an agent of law, analyze this question about statutes, codes, or regulations: {question}"}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

class AgentForLaw:
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        self.reasoner = LawReasoner()
        
        self.regulatory_agencies = {
            "sec": {"name": "Securities and Exchange Commission", "url": "https://www.sec.gov/"},
            "cftc": {"name": "Commodity Futures Trading Commission", "url": "https://www.cftc.gov/"},
            "finra": {"name": "FINRA", "url": "https://www.finra.org/"},
            "fincen": {"name": "FinCEN", "url": "https://www.fincen.gov/"},
            "ofac": {"name": "OFAC", "url": "https://ofac.treasury.gov/"}
        }
        
        self.domains = {
            "constitutional": "Constitution, fundamental law",
            "statutory": "Written laws passed by legislatures",
            "regulatory": "Agency rules and regulations",
            "securities": "SEC, FINRA rules",
            "aml": "FinCEN, FATF rules"
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw - Agent of Law")
    
    # Info commands
    parser.add_argument("--agencies", action="store_true", help="List agencies")
    parser.add_argument("--agency", help="Get agency info")
    parser.add_argument("--domains", action="store_true", help="List law domains")
    
    # Memory commands
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store in shared memory")
    parser.add_argument("--recall", help="Recall from shared memory")
    parser.add_argument("--agents", action="store_true", help="Show other agents")
    
    # Research commands
    parser.add_argument("--case-text", help="Get case text")
    parser.add_argument("--statute", help="Get statute (e.g., '15 USC 78a')")
    parser.add_argument("--regulation", help="Get regulation (e.g., '17 CFR 240.10b-5')")
    parser.add_argument("--analyze", help="Analyze law question")
    parser.add_argument("--recent", choices=["scotus"], help="Recent cases")
    
    # Drafting commands
    parser.add_argument("--draft", choices=["statute", "regulation", "code_section", "constitutional_article", "notice", "writ", "rule", "order", "finding"], help="Draft a law document")
    parser.add_argument("--params", help="JSON parameters for drafting")
    
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
        print(f"\n📜 Analysis:\n{agent.reasoner.analyze(args.analyze)}\n")
    elif args.recent:
        if args.recent == "scotus":
            from LawRetriever import get_recent_scotus
            print(json.dumps(RealTimeMonitor.get_recent_scotus(), indent=2))
    elif args.draft:
        params = json.loads(args.params) if args.params else {}
        result = LawDocumentDrafting.draft(args.draft, params)
        print(result)
    else:
        parser.print_help()
    
    agent.shared.close()

if __name__ == "__main__":
    main()
