#!/usr/bin/env python3
"""
agentforlaw - Agent of Law
Studies and applies LAW (statutes, codes, regulations, constitutions, case law)
Drafts documents USING law (contracts, wills, trusts, estate documents)
Does NOT practice law. Does NOT give legal advice.
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
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, key TEXT, value TEXT, timestamp TEXT, tags TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS agent_registry (agent_id TEXT PRIMARY KEY, name TEXT, repo TEXT, capabilities TEXT, last_seen TEXT)''')
        self.conn.commit()
    
    def remember(self, key: str, value: str, tags: str = ""):
        self.cursor.execute("INSERT INTO memories (agent, key, value, timestamp, tags) VALUES (?, ?, ?, ?, ?)", ("agentforlaw", key, value, datetime.now().isoformat(), tags))
        self.conn.commit()
    
    def recall(self, key: str) -> list:
        self.cursor.execute("SELECT agent, key, value, tags FROM memories WHERE key LIKE ? ORDER BY timestamp DESC LIMIT 10", (f"%{key}%",))
        return self.cursor.fetchall()
    
    def register(self):
        self.cursor.execute("INSERT OR REPLACE INTO agent_registry VALUES (?, ?, ?, ?, ?)", ("agentforlaw", "AgentForLaw", "https://github.com/greg-gzillion/agentforlaw", "law study, statutes, codes, regulations, constitutions, case law, document drafting", datetime.now().isoformat()))
        self.conn.commit()
    
    def get_other_agents(self) -> list:
        self.cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class LawDocumentDrafting:
    """Draft documents USING law - contracts, wills, trusts, estates"""
    
    @staticmethod
    def draft_contract(contract_type: str, parties: Dict, terms: Dict) -> str:
        templates = {
            "service": {"title": "SERVICE CONTRACT", "clauses": ["PARTIES: {party_a} and {party_b}", "SERVICES: {services}", "PAYMENT: {payment}", "GOVERNING LAW: {governing_law}"]},
            "sale": {"title": "SALES CONTRACT", "clauses": ["SELLER: {seller} BUYER: {buyer}", "GOODS: {goods}", "PRICE: {price}", "GOVERNING LAW: UCC Article 2"]},
            "employment": {"title": "EMPLOYMENT CONTRACT", "clauses": ["EMPLOYER: {employer} EMPLOYEE: {employee}", "POSITION: {position}", "SALARY: {salary}", "GOVERNING LAW: {governing_law}"]},
            "lease": {"title": "LEASE CONTRACT", "clauses": ["LANDLORD: {landlord} TENANT: {tenant}", "PREMISES: {premises}", "RENT: {rent}", "TERM: {term}", "GOVERNING LAW: {governing_law}"]},
            "partnership": {"title": "PARTNERSHIP AGREEMENT", "clauses": ["PARTNERS: {partner_a} and {partner_b}", "PURPOSE: {purpose}", "PROFIT SHARING: {sharing}", "GOVERNING LAW: {governing_law}"]},
            "loan": {"title": "LOAN AGREEMENT", "clauses": ["LENDER: {lender} BORROWER: {borrower}", "PRINCIPAL: {principal}", "INTEREST: {interest}%", "REPAYMENT: {repayment}", "GOVERNING LAW: {governing_law}"]}
        }
        t = templates.get(contract_type, templates["service"])
        result = f"\n{'='*60}\n{t['title']}\n{'='*60}\n\n"
        for clause in t['clauses']:
            result += f"{clause.format(**parties, **terms)}\n\n"
        result += f"\nDate: {datetime.now().strftime('%B %d, %Y')}\n"
        result += f"{parties.get('party_a', 'First Party')}: ___________________\n"
        result += f"{parties.get('party_b', 'Second Party')}: ___________________\n{'='*60}\n"
        return result
    
    @staticmethod
    def draft_will(parties: Dict, provisions: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
{'='*60}
LAST WILL AND TESTAMENT OF {parties.get('name', '_________')}
{'='*60}

I, {parties.get('name', '_________')}, being of sound mind, declare this to be my Will.

ARTICLE I: EXECUTOR
I appoint {provisions.get('executor', '_________')} as Executor.

ARTICLE II: DISPOSITION
I give my entire estate to {provisions.get('beneficiary', '_________')}.

ARTICLE III: GOVERNING LAW
This Will is governed by the laws of {provisions.get('governing_state', '_________')}.

IN WITNESS WHEREOF, I sign this Will on {date}.

{parties.get('name', '_________')} (Testator)
Witness 1: _________    Witness 2: _________
{'='*60}"""
    
    @staticmethod
    def draft_trust(parties: Dict, provisions: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"""
{'='*60}
REVOCABLE LIVING TRUST OF {parties.get('name', '_________')}
{'='*60}

Settlor: {parties.get('name', '_________')}
Trustee: {provisions.get('trustee', '_________')}
Beneficiaries: {provisions.get('beneficiaries', '_________')}

The Settlor transfers property to the Trustee to hold for the beneficiaries.

Governing Law: {provisions.get('governing_state', '_________')}

IN WITNESS WHEREOF, executed on {date}.

{parties.get('name', '_________')} (Settlor)
{provisions.get('trustee', '_________')} (Trustee)
{'='*60}"""
    
    @staticmethod
    def draft_estate_document(doc_type: str, parties: Dict, provisions: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        if doc_type == "power_of_attorney":
            return f"""
{'='*60}
DURABLE POWER OF ATTORNEY
{'='*60}
I, {parties.get('principal', '_________')}, appoint {provisions.get('agent', '_________')} as my Attorney-in-Fact.
This Power of Attorney is durable and remains effective upon my disability.
Executed on {date}.
{parties.get('principal', '_________')} (Principal)
Notary: _________"""
        elif doc_type == "healthcare_directive":
            return f"""
{'='*60}
ADVANCE HEALTH CARE DIRECTIVE
{'='*60}
I, {parties.get('principal', '_________')}, appoint {provisions.get('agent', '_________')} as my Health Care Agent.
My Agent may make all health care decisions for me.
Executed on {date}.
{parties.get('principal', '_________')} (Principal)
Witness: _________"""
        elif doc_type == "living_will":
            return f"""
{'='*60}
LIVING WILL
{'='*60}
I, {parties.get('declarant', '_________')}, direct that life-sustaining treatment be withheld if I have a terminal condition.
Executed on {date}.
{parties.get('declarant', '_________')} (Declarant)
Witnesses: _________"""
        return "Unknown document type"

class USCourts:
    @staticmethod
    def get_federal_court(court_name: str) -> Dict:
        courts = {
            "supreme_court": {"name": "US Supreme Court", "url": "https://www.supremecourt.gov/"},
            "ninth_circuit": {"name": "9th Circuit", "url": "https://www.ca9.uscourts.gov/"},
            "second_circuit": {"name": "2nd Circuit", "url": "https://www.ca2.uscourts.gov/"}
        }
        return courts.get(court_name, {"error": "Not found"})
    
    @staticmethod
    def get_state_court(state: str, court_type: str = "supreme") -> Dict:
        return {"state": state, "court_type": court_type, "url": f"https://www.courts.{state}.gov/"}

class LawRetriever:
    @staticmethod
    def get_statute(citation: str) -> Dict:
        parts = citation.upper().replace('USC', '').strip().split()
        if len(parts) >= 2:
            return {"citation": citation, "url": f"https://www.law.cornell.edu/uscode/text/{parts[0]}/{parts[1]}"}
        return {"error": "Invalid format. Example: 15 USC 78a"}
    
    @staticmethod
    def get_case(case_name: str) -> Dict:
        return {"case": case_name, "url": f"https://www.courtlistener.com/?q={case_name.replace(' ', '+')}"}

class AgentForLaw:
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        self.agencies = {"sec": "Securities and Exchange Commission", "cftc": "CFTC", "finra": "FINRA"}
        self.domains = {"constitutional": "Constitution", "statutory": "Statutes", "regulatory": "Regulations", "case_law": "Case Law"}
    
    def get_agency(self, name: str) -> Dict:
        return {"name": self.agencies.get(name, "Not found")}
    
    def get_all_agencies(self) -> List[str]:
        return list(self.agencies.keys())

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
    parser.add_argument("--statute", help="Get statute URL")
    parser.add_argument("--case", help="Get case by name")
    
    # Drafting commands
    parser.add_argument("--draft-contract", choices=["service", "sale", "employment", "lease", "partnership", "loan"], help="Draft a contract")
    parser.add_argument("--draft-will", action="store_true", help="Draft a last will and testament")
    parser.add_argument("--draft-trust", action="store_true", help="Draft a revocable living trust")
    parser.add_argument("--draft-estate", choices=["power_of_attorney", "healthcare_directive", "living_will"], help="Draft an estate document")
    parser.add_argument("--parties", help="JSON string of party information")
    parser.add_argument("--provisions", help="JSON string of provisions")
    
    # Court commands
    parser.add_argument("--federal-court", help="Get federal court")
    parser.add_argument("--state-court", nargs=2, metavar=('STATE', 'TYPE'), help="Get state court")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    # Info commands
    if args.agencies:
        print("\nAgencies:")
        for a in agent.get_all_agencies():
            print(f"  {a.upper()}")
    elif args.agency:
        print(json.dumps(agent.get_agency(args.agency), indent=2))
    elif args.domains:
        print("\nLaw Domains:")
        for d, desc in agent.domains.items():
            print(f"  {d}: {desc}")
    
    # Memory commands
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
    
    # Research commands
    elif args.statute:
        print(json.dumps(LawRetriever.get_statute(args.statute), indent=2))
    elif args.case:
        print(json.dumps(LawRetriever.get_case(args.case), indent=2))
    
    # Drafting commands
    elif args.draft_contract:
        parties = json.loads(args.parties) if args.parties else {}
        provisions = json.loads(args.provisions) if args.provisions else {}
        print(LawDocumentDrafting.draft_contract(args.draft_contract, parties, provisions))
    elif args.draft_will:
        parties = json.loads(args.parties) if args.parties else {}
        provisions = json.loads(args.provisions) if args.provisions else {}
        print(LawDocumentDrafting.draft_will(parties, provisions))
    elif args.draft_trust:
        parties = json.loads(args.parties) if args.parties else {}
        provisions = json.loads(args.provisions) if args.provisions else {}
        print(LawDocumentDrafting.draft_trust(parties, provisions))
    elif args.draft_estate:
        parties = json.loads(args.parties) if args.parties else {}
        provisions = json.loads(args.provisions) if args.provisions else {}
        print(LawDocumentDrafting.draft_estate_document(args.draft_estate, parties, provisions))
    
    # Court commands
    elif args.federal_court:
        print(json.dumps(USCourts.get_federal_court(args.federal_court), indent=2))
    elif args.state_court:
        state, court_type = args.state_court
        print(json.dumps(USCourts.get_state_court(state, court_type), indent=2))
    
    else:
        parser.print_help()
    
    agent.shared.close()

if __name__ == "__main__":
    main()
