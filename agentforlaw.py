#!/usr/bin/env python3
"""
agentforlaw - The Ultimate Agent of Law
Specialized in law, powered by ALL available LLM models
"""

import json
import sqlite3
import re
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import subprocess

# ============================================================
# SHARED MEMORY (Works with all claw agents)
# ============================================================

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
        self.cursor.execute("INSERT OR REPLACE INTO agent_registry VALUES (?, ?, ?, ?, ?)", 
                          ("agentforlaw", "AgentForLaw", "https://github.com/greg-gzillion/agentforlaw", 
                           "law, statutes, constitution, case law, contracts, wills, trusts, AI analysis", 
                           datetime.now().isoformat()))
        self.conn.commit()
    
    def get_other_agents(self) -> list:
        self.cursor.execute("SELECT name, capabilities FROM agent_registry WHERE agent_id != 'agentforlaw'")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

# ============================================================
# LLM MODEL CONNECTIVITY (Best of all worlds)
# ============================================================

class ModelRegistry:
    """Discover and manage all available LLM models"""
    
    @staticmethod
    def discover_all() -> Dict:
        """Discover all models from all providers"""
        models = {"groq": [], "ollama": [], "deepseek": [], "openai": [], "local": []}
        
        # Groq (fastest)
        if os.environ.get("GROQ_API_KEY"):
            models["groq"] = [
                {"name": "llama-3.3-70b-versatile", "speed": "fast", "best": "legal reasoning", "free": True},
                {"name": "llama-3.1-8b-instant", "speed": "fastest", "best": "quick definitions", "free": True},
                {"name": "mixtral-8x7b-32768", "speed": "fast", "best": "long documents", "free": True},
                {"name": "gemma2-9b-it", "speed": "fast", "best": "general analysis", "free": True}
            ]
        
        # Ollama (local, private)
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                for m in r.json().get("models", []):
                    models["ollama"].append({
                        "name": m["name"],
                        "speed": "slow" if "70b" in m["name"] else "medium",
                        "best": "privacy & offline",
                        "free": True
                    })
        except:
            pass
        
        # DeepSeek (cheap, powerful)
        if os.environ.get("DEEPSEEK_API_KEY"):
            models["deepseek"] = [
                {"name": "deepseek-chat", "speed": "fast", "best": "legal analysis", "free": False},
                {"name": "deepseek-coder", "speed": "fast", "best": "contract drafting", "free": False}
            ]
        
        # OpenAI (optional)
        if os.environ.get("OPENAI_API_KEY"):
            models["openai"] = [
                {"name": "gpt-4-turbo", "speed": "medium", "best": "complex legal", "free": False},
                {"name": "gpt-3.5-turbo", "speed": "fast", "best": "quick answers", "free": False}
            ]
        
        return models
    
    @staticmethod
    def get_best_for_task(task: str) -> Dict:
        """Get best model recommendation for a legal task"""
        recommendations = {
            "legal_analysis": ["groq/llama-3.3-70b-versatile", "deepseek/deepseek-chat", "ollama/codellama:7b"],
            "contract_drafting": ["deepseek/deepseek-coder", "groq/llama-3.1-8b-instant", "ollama/deepseek-coder:6.7b"],
            "quick_definition": ["groq/llama-3.1-8b-instant", "ollama/llama3.2:3b"],
            "private_analysis": ["ollama/codellama:7b", "ollama/mistral:7b", "ollama/llama3.2:3b"],
            "long_document": ["groq/mixtral-8x7b-32768", "deepseek/deepseek-chat", "ollama/codellama:13b"],
            "case_summary": ["groq/llama-3.3-70b-versatile", "deepseek/deepseek-chat", "ollama/mistral:7b"],
            "statute_interpretation": ["groq/llama-3.3-70b-versatile", "openai/gpt-4-turbo", "ollama/codellama:7b"]
        }
        return {"task": task, "recommended": recommendations.get(task, recommendations["legal_analysis"])}

class LegalAnalyzer:
    """Unified legal analysis using ANY model"""
    
    @staticmethod
    def analyze(question: str, model: str = None, provider: str = "auto", stream: bool = False) -> str:
        """Analyze legal question using best available model"""
        
        # Auto-select best model
        if provider == "auto" or not provider:
            if os.environ.get("GROQ_API_KEY"):
                provider = "groq"
                model = model or "llama-3.3-70b-versatile"
            elif os.environ.get("DEEPSEEK_API_KEY"):
                provider = "deepseek"
                model = model or "deepseek-chat"
            elif LegalAnalyzer._check_ollama():
                provider = "ollama"
                model = model or "codellama:7b"
            elif os.environ.get("OPENAI_API_KEY"):
                provider = "openai"
                model = model or "gpt-3.5-turbo"
            else:
                return self._local_analyze(question)
        
        # Route to provider
        if provider == "groq":
            return LegalAnalyzer._groq_analyze(question, model)
        elif provider == "ollama":
            return LegalAnalyzer._ollama_analyze(question, model)
        elif provider == "deepseek":
            return LegalAnalyzer._deepseek_analyze(question, model)
        elif provider == "openai":
            return LegalAnalyzer._openai_analyze(question, model)
        else:
            return f"Unknown provider: {provider}"
    
    @staticmethod
    def _groq_analyze(question: str, model: str) -> str:
        try:
            from groq import Groq
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are AgentForLaw, an expert in US law. Provide accurate, concise legal analysis based on statutes, regulations, and case law."},
                    {"role": "user", "content": question}
                ],
                max_tokens=800,
                temperature=0.3
            )
            return f"[Groq/{model}]\n{response.choices[0].message.content}"
        except Exception as e:
            return f"Groq error: {e}"
    
    @staticmethod
    def _ollama_analyze(question: str, model: str) -> str:
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": f"You are AgentForLaw, a legal expert. Answer: {question}",
                    "stream": False,
                    "options": {"num_predict": 800, "temperature": 0.3}
                },
                timeout=90
            )
            if response.status_code == 200:
                return f"[Ollama/{model}]\n{response.json().get('response', 'No response')}"
            return f"Ollama error: HTTP {response.status_code}"
        except Exception as e:
            return f"Ollama error: {e}"
    
    @staticmethod
    def _deepseek_analyze(question: str, model: str) -> str:
        try:
            import requests
            headers = {"Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY')}", "Content-Type": "application/json"}
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are AgentForLaw, a legal expert."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }
            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return f"[DeepSeek/{model}]\n{response.json()['choices'][0]['message']['content']}"
            return f"DeepSeek error: {response.status_code}"
        except Exception as e:
            return f"DeepSeek error: {e}"
    
    @staticmethod
    def _openai_analyze(question: str, model: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are AgentForLaw, a legal expert."},
                    {"role": "user", "content": question}
                ],
                max_tokens=800,
                temperature=0.3
            )
            return f"[OpenAI/{model}]\n{response.choices[0].message.content}"
        except Exception as e:
            return f"OpenAI error: {e}"
    
    @staticmethod
    def _check_ollama() -> bool:
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            return r.status_code == 200
        except:
            return False
    
    @staticmethod
    def _local_analyze(question: str) -> str:
        """Fallback when no AI is available"""
        return """No AI models available. Options:
1. Set GROQ_API_KEY (fastest, free) - Get from console.groq.com
2. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
3. Set DEEPSEEK_API_KEY (cheap, powerful)
4. Set OPENAI_API_KEY

Without AI, AgentForLaw can still:
- Look up statutes: --statute "15 USC 78a"
- Access Constitution: --constitution --article 1
- Draft contracts: --draft-contract service
- Draft wills: --draft-will
- Search case law: --case "Marbury v Madison"
"""

# ============================================================
# LEGAL DOCUMENT DRAFTING
# ============================================================

class LawDocumentDrafting:
    @staticmethod
    def draft_contract(contract_type: str, parties: Dict, terms: Dict) -> str:
        defaults = {'governing_law': 'Delaware', 'services': 'services', 'payment': '$0', 'goods': 'goods', 'price': '$0', 'position': 'position', 'salary': '$0', 'premises': 'premises', 'rent': '$0', 'term': 'one year', 'purpose': 'business', 'sharing': 'equal', 'principal': '$0', 'interest': '0', 'repayment': 'on demand'}
        for key, default in defaults.items():
            if key not in terms:
                terms[key] = default
        
        templates = {
            "service": {"title": "SERVICE CONTRACT", "clauses": ["PARTIES: {party_a} and {party_b}", "SERVICES: {services}", "PAYMENT: {payment}", "GOVERNING LAW: {governing_law}"]},
            "sale": {"title": "SALES CONTRACT", "clauses": ["SELLER: {seller} BUYER: {buyer}", "GOODS: {goods}", "PRICE: {price}", "GOVERNING LAW: {governing_law}"]},
            "employment": {"title": "EMPLOYMENT CONTRACT", "clauses": ["EMPLOYER: {employer} EMPLOYEE: {employee}", "POSITION: {position}", "SALARY: {salary}", "GOVERNING LAW: {governing_law}"]},
            "lease": {"title": "LEASE CONTRACT", "clauses": ["LANDLORD: {landlord} TENANT: {tenant}", "PREMISES: {premises}", "RENT: {rent}", "TERM: {term}", "GOVERNING LAW: {governing_law}"]},
            "partnership": {"title": "PARTNERSHIP AGREEMENT", "clauses": ["PARTNERS: {partner_a} and {partner_b}", "PURPOSE: {purpose}", "PROFIT SHARING: {sharing}", "GOVERNING LAW: {governing_law}"]},
            "loan": {"title": "LOAN AGREEMENT", "clauses": ["LENDER: {lender} BORROWER: {borrower}", "PRINCIPAL: {principal}", "INTEREST: {interest}%", "REPAYMENT: {repayment}", "GOVERNING LAW: {governing_law}"]}
        }
        
        t = templates.get(contract_type, templates["service"])
        result = f"\n{'='*60}\n{t['title']}\n{'='*60}\n\n"
        format_dict = {**parties, **terms}
        for clause in t['clauses']:
            try:
                result += f"{clause.format(**format_dict)}\n\n"
            except KeyError:
                result += f"{clause}\n\n"
        result += f"\nDate: {datetime.now().strftime('%B %d, %Y')}\n{'='*60}\n"
        return result
    
    @staticmethod
    def draft_will(parties: Dict, provisions: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"\n{'='*60}\nLAST WILL AND TESTAMENT OF {parties.get('name', '_________')}\n{'='*60}\n\nI, {parties.get('name', '_________')}, declare this to be my Will.\n\nARTICLE I: EXECUTOR\nI appoint {provisions.get('executor', '_________')} as Executor.\n\nARTICLE II: DISPOSITION\nI give my estate to {provisions.get('beneficiary', '_________')}.\n\nARTICLE III: GOVERNING LAW\nThis Will is governed by {provisions.get('governing_state', '_________')}.\n\nIN WITNESS WHEREOF on {date}.\n\n{parties.get('name', '_________')} (Testator)\nWitness 1: _________    Witness 2: _________\n{'='*60}"
    
    @staticmethod
    def draft_trust(parties: Dict, provisions: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        return f"\n{'='*60}\nREVOCABLE LIVING TRUST OF {parties.get('name', '_________')}\n{'='*60}\n\nSettlor: {parties.get('name', '_________')}\nTrustee: {provisions.get('trustee', '_________')}\nBeneficiaries: {provisions.get('beneficiaries', '_________')}\n\nGoverning Law: {provisions.get('governing_state', '_________')}\n\nExecuted on {date}.\n\n{parties.get('name', '_________')} (Settlor)\n{provisions.get('trustee', '_________')} (Trustee)\n{'='*60}"
    
    @staticmethod
    def draft_estate_document(doc_type: str, parties: Dict, provisions: Dict) -> str:
        date = datetime.now().strftime("%B %d, %Y")
        templates = {
            "power_of_attorney": f"\n{'='*60}\nDURABLE POWER OF ATTORNEY\n{'='*60}\n\nI, {parties.get('principal', '_________')}, appoint {provisions.get('agent', '_________')} as my Attorney-in-Fact.\n\nExecuted on {date}.\n\n{parties.get('principal', '_________')} (Principal)\n{'='*60}",
            "healthcare_directive": f"\n{'='*60}\nADVANCE HEALTH CARE DIRECTIVE\n{'='*60}\n\nI, {parties.get('principal', '_________')}, appoint {provisions.get('agent', '_________')} as my Health Care Agent.\n\nExecuted on {date}.\n\n{parties.get('principal', '_________')} (Principal)\n{'='*60}",
            "living_will": f"\n{'='*60}\nLIVING WILL\n{'='*60}\n\nI, {parties.get('declarant', '_________')}, direct that life-sustaining treatment be withheld if I have a terminal condition.\n\nExecuted on {date}.\n\n{parties.get('declarant', '_________')} (Declarant)\n{'='*60}"
        }
        return templates.get(doc_type, "Unknown document type")

# ============================================================
# LEGAL RESEARCH
# ============================================================

class ConstitutionAccess:
    @staticmethod
    def get_article(article: int, section: int = None) -> Dict:
        articles = {1: "Legislative Branch", 2: "Executive Branch", 3: "Judicial Branch", 4: "States' Powers", 5: "Amendment Process", 6: "Federal Supremacy", 7: "Ratification"}
        result = {"article": article, "title": articles.get(article, "Unknown")}
        if section:
            result["section"] = section
            result["url"] = f"https://www.law.cornell.edu/constitution/article{article}#section{section}"
        else:
            result["url"] = f"https://www.law.cornell.edu/constitution/article{article}"
        return result
    
    @staticmethod
    def get_amendment(number: int) -> Dict:
        amendments = {1: "Free speech, religion, press, assembly", 2: "Right to bear arms", 4: "Search and seizure", 5: "Due process, self-incrimination", 6: "Speedy trial", 8: "No cruel punishment", 10: "States' powers", 13: "Abolish slavery", 14: "Equal protection, due process", 19: "Women's suffrage"}
        return {"amendment": number, "summary": amendments.get(number, "Text not in library"), "url": f"https://www.law.cornell.edu/constitution/amendment{number}"}

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
    
    @staticmethod
    def get_cfr(citation: str) -> Dict:
        match = re.search(r'(\d+)\s+CFR\s+([\d\.]+)', citation, re.IGNORECASE)
        if match:
            return {"citation": citation, "url": f"https://www.ecfr.gov/current/title-{match.group(1)}/section-{match.group(2)}"}
        return {"error": "Invalid format. Example: 17 CFR 240.10b-5"}

class ClauseLibrary:
    CLAUSES = {
        "indemnification": "The indemnifying party shall defend, indemnify, and hold harmless the indemnified party from any and all claims arising out of this Agreement.",
        "confidentiality": "The receiving party shall not disclose confidential information to any third party without written consent.",
        "termination": "Either party may terminate this Agreement upon 30 days written notice.",
        "governing_law": "This Agreement shall be governed by the laws of the State of Delaware.",
        "arbitration": "Any dispute shall be resolved by binding arbitration in accordance with AAA rules.",
        "force_majeure": "Neither party shall be liable for delays caused by circumstances beyond reasonable control.",
        "entire_agreement": "This Agreement constitutes the entire agreement between the parties."
    }
    
    @staticmethod
    def get_clause(name: str) -> str:
        return ClauseLibrary.CLAUSES.get(name, f"Clause '{name}' not found")
    
    @staticmethod
    def list_clauses() -> List[str]:
        return list(ClauseLibrary.CLAUSES.keys())

class LegalDefinitions:
    DEFINITIONS = {
        "consideration": "Something of value given in exchange for a promise in a contract. Essential for contract enforceability.",
        "due_process": "Constitutional requirement that government respect all legal rights. Fifth and Fourteenth Amendments.",
        "tort": "A civil wrong causing harm, giving the right to sue for damages. Includes negligence, intentional torts, strict liability.",
        "contract": "A legally enforceable agreement between two or more parties with offer, acceptance, and consideration.",
        "negligence": "Failure to exercise reasonable care, resulting in harm to another person.",
        "strict_liability": "Liability without fault for inherently dangerous activities or defective products.",
        "jurisdiction": "The authority of a court to hear and decide a case.",
        "precedent": "A legal decision that serves as an example for future similar cases (stare decisis)."
    }
    
    @staticmethod
    def define(term: str) -> Dict:
        return {"term": term, "definition": LegalDefinitions.DEFINITIONS.get(term.lower(), "Definition not found. Try: consideration, due_process, tort, contract, negligence, strict_liability, jurisdiction, precedent")}
    
    @staticmethod
    def list_terms() -> List[str]:
        return list(LegalDefinitions.DEFINITIONS.keys())

# ============================================================
# MAIN CLI
# ============================================================

class AgentForLaw:
    def __init__(self):
        self.shared = SharedMemory()
        self.shared.register()
        self.agencies = {"sec": "Securities and Exchange Commission", "cftc": "Commodity Futures Trading Commission", "finra": "FINRA"}
        self.domains = {"constitutional": "Constitution", "statutory": "Statutes", "regulatory": "Regulations", "case_law": "Case Law", "contract": "Contract Law", "tort": "Tort Law"}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="agentforlaw - The Ultimate Agent of Law", epilog="Specialized in law, powered by ALL available LLM models (Groq, Ollama, DeepSeek, OpenAI)")
    
    # Info commands
    parser.add_argument("--agencies", action="store_true", help="List regulatory agencies")
    parser.add_argument("--agency", help="Get agency info")
    parser.add_argument("--domains", action="store_true", help="List law domains")
    
    # Memory commands (shared with all claw agents)
    parser.add_argument("--remember", nargs=2, metavar=('KEY', 'VALUE'), help="Store in shared memory")
    parser.add_argument("--recall", help="Recall from shared memory")
    parser.add_argument("--agents", action="store_true", help="Show other claw agents")
    
    # Research commands
    parser.add_argument("--statute", help="Look up US Code statute")
    parser.add_argument("--case", help="Search case law")
    parser.add_argument("--cfr", help="Look up Code of Federal Regulations")
    
    # Constitution commands
    parser.add_argument("--constitution", action="store_true", help="Access Constitution")
    parser.add_argument("--article", type=int, help="Constitution article number")
    parser.add_argument("--section", type=int, help="Constitution section number")
    parser.add_argument("--amendment", type=int, help="Constitution amendment number")
    
    # Drafting commands
    parser.add_argument("--draft-contract", choices=["service", "sale", "employment", "lease", "partnership", "loan"], help="Draft a contract")
    parser.add_argument("--draft-will", action="store_true", help="Draft a last will")
    parser.add_argument("--draft-trust", action="store_true", help="Draft a living trust")
    parser.add_argument("--draft-estate", choices=["power_of_attorney", "healthcare_directive", "living_will"], help="Draft an estate document")
    parser.add_argument("--parties", help="JSON string of party information")
    parser.add_argument("--provisions", help="JSON string of provisions")
    
    # Clause and definition commands
    parser.add_argument("--list-clauses", action="store_true", help="List contract clauses")
    parser.add_argument("--clause", help="Get a contract clause")
    parser.add_argument("--define", help="Define a legal term")
    parser.add_argument("--list-terms", action="store_true", help="List legal terms")
    
    # AI commands (BEST OF EVERYTHING)
    parser.add_argument("--analyze", help="Analyze legal question using AI")
    parser.add_argument("--list-models", action="store_true", help="List all available LLM models")
    parser.add_argument("--model", help="Specify model (e.g., 'llama-3.3-70b-versatile')")
    parser.add_argument("--provider", choices=["groq", "ollama", "deepseek", "openai", "auto"], default="auto", help="LLM provider")
    parser.add_argument("--recommend", help="Get model recommendation for a legal task")
    
    args = parser.parse_args()
    agent = AgentForLaw()
    
    # ========== INFO COMMANDS ==========
    if args.agencies:
        print("\n🏛️ REGULATORY AGENCIES:")
        for a in agent.agencies:
            print(f"  • {a.upper()}: {agent.agencies[a]}")
    
    elif args.agency:
        print(json.dumps({"agency": args.agency, "name": agent.agencies.get(args.agency.lower(), "Not found")}, indent=2))
    
    elif args.domains:
        print("\n📚 LAW DOMAINS:")
        for d, desc in agent.domains.items():
            print(f"  • {d}: {desc}")
    
    # ========== MEMORY COMMANDS ==========
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
        print("\n🦞 OTHER CLAW AGENTS:")
        for name, caps in others:
            print(f"  • {name}: {caps[:80]}...")
    
    # ========== RESEARCH COMMANDS ==========
    elif args.statute:
        print(json.dumps(LawRetriever.get_statute(args.statute), indent=2))
    
    elif args.case:
        print(json.dumps(LawRetriever.get_case(args.case), indent=2))
    
    elif args.cfr:
        print(json.dumps(LawRetriever.get_cfr(args.cfr), indent=2))
    
    # ========== CONSTITUTION COMMANDS ==========
    elif args.constitution:
        if args.amendment:
            print(json.dumps(ConstitutionAccess.get_amendment(args.amendment), indent=2))
        elif args.article:
            print(json.dumps(ConstitutionAccess.get_article(args.article, args.section), indent=2))
        else:
            print(json.dumps({"error": "Use --article or --amendment", "example": "--constitution --article 1 --section 8"}, indent=2))
    
    # ========== DRAFTING COMMANDS ==========
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
    
    # ========== CLAUSE & DEFINITION COMMANDS ==========
    elif args.list_clauses:
        print("\n📋 CONTRACT CLAUSES:")
        for c in ClauseLibrary.list_clauses():
            print(f"  • {c}")
    
    elif args.clause:
        print(ClauseLibrary.get_clause(args.clause))
    
    elif args.define:
        print(json.dumps(LegalDefinitions.define(args.define), indent=2))
    
    elif args.list_terms:
        print("\n📖 LEGAL TERMS:")
        for t in LegalDefinitions.list_terms():
            print(f"  • {t}")
    
    # ========== AI COMMANDS (BEST OF EVERYTHING) ==========
    elif args.list_models:
        models = ModelRegistry.discover_all()
        print("\n🤖 AVAILABLE LLM MODELS")
        print("=" * 60)
        for provider, provider_models in models.items():
            if provider_models:
                print(f"\n📡 {provider.upper()}:")
                for m in provider_models:
                    free_tag = " [FREE]" if m.get("free") else " [PAID]"
                    print(f"   • {m['name']}{free_tag}")
                    print(f"     Speed: {m['speed']} | Best for: {m['best']}")
        
        if not any(models.values()):
            print("\n❌ No AI models detected. Quick setup:")
            print("   • Groq (fastest, free): export GROQ_API_KEY='your-key'")
            print("   • Ollama (local): curl -fsSL https://ollama.com/install.sh | sh")
            print("   • DeepSeek (cheap): export DEEPSEEK_API_KEY='your-key'")
    
    elif args.recommend:
        result = ModelRegistry.get_best_for_task(args.recommend)
        print(f"\n🎯 RECOMMENDATION FOR: {result['task']}")
        print("=" * 40)
        for model in result['recommended']:
            print(f"   • {model}")
    
    elif args.analyze:
        print(f"\n🤖 AgentForLaw analyzing...")
        print(f"   Question: {args.analyze[:100]}...")
        if args.provider != "auto":
            print(f"   Provider: {args.provider}")
        if args.model:
            print(f"   Model: {args.model}")
        print("\n" + "=" * 60)
        result = LegalAnalyzer.analyze(args.analyze, args.model, args.provider)
        print(f"\n{result}\n")
        print("=" * 60)
    
    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("🦞 AGENTFORLAW - Ultimate Agent of Law")
        print("=" * 60)
        print("\nQuick Examples:")
        print("  --list-models              # See all available AI models")
        print("  --analyze 'legal question' # Analyze with best AI")
        print("  --statute '15 USC 78a'     # Look up statute")
        print("  --constitution --article 1 # Read Constitution")
        print("  --draft-contract service   # Draft a contract")
        print("  --draft-will               # Draft a last will")
        print("  --remember key value       # Share memory with other agents")
    
    agent.shared.close()

if __name__ == "__main__":
    main()
