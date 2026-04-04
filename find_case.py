#!/usr/bin/env python3
"""
Efficient case law search - finds relevant cases using both database and AI
"""

import sys
import requests
import sqlite3
from pathlib import Path

def search_case_law(question):
    """Search for relevant case law"""
    
    # First, check local database
    db_path = Path.home() / ".claw_memory" / "case_law.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Extract keywords from question
    keywords = question.lower().split()
    
    # Search local database
    results = []
    for kw in keywords[:5]:
        cursor.execute("""
            SELECT name, citation, year, holding, keywords
            FROM cases
            WHERE name LIKE ? OR keywords LIKE ? OR holding LIKE ?
            LIMIT 5
        """, (f"%{kw}%", f"%{kw}%", f"%{kw}%"))
        results.extend(cursor.fetchall())
    
    conn.close()
    
    # Remove duplicates
    seen = set()
    unique_results = []
    for r in results:
        if r[0] not in seen:
            seen.add(r[0])
            unique_results.append(r)
    
    if unique_results:
        print(f"\n📚 RELEVANT CASES:\n")
        for r in unique_results[:5]:
            print(f"   • {r[0]} ({r[1]})")
            print(f"     {r[3][:150]}...\n")
        return unique_results
    
    # If no local results, use AI to find relevant cases
    print("   No local cases found. Searching via AI...")
    
    try:
        from groq import Groq
        import os
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a legal research assistant. List the most relevant US Supreme Court cases for the given question. Include case name, citation, and one-sentence holding."},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.3
        )
        print(f"\n📚 AI-SUGGESTED CASES:\n")
        print(response.choices[0].message.content)
        print("\n💡 To save these cases: --teach 'Case Name|citation|year|holding'")
        
    except Exception as e:
        print(f"AI search error: {e}")
    
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        search_case_law(q)
    else:
        print("Usage: python find_case.py 'What case established judicial review?'")
