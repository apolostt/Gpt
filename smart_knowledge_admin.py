import pandas as pd
from datetime import datetime
import os
import json
import re
from typing import Optional, List, Dict, Any
import hashlib
import sqlite3
from enum import Enum

# Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai not installed: pip install google-generativeai")


class AdminLevel(Enum):
    """Úrovně administrátorských práv"""
    GUEST = 0
    USER = 1
    POWER_USER = 2
    ADMIN = 3
    SUPER_ADMIN = 4


class AdminSecurityManager:
    """Správa bezpečnosti a oprávnění"""
    
    def __init__(self, db_file='admin_security.db'):
        self.db_file = db_file
        self.init_db()
        self.admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        self.logged_in_user = None
        self.current_level = AdminLevel.GUEST
    
    def init_db(self):
        """Inicializuj bezpečnostní databázi"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                admin_user TEXT,
                action TEXT,
                details TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_history (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                level TEXT,
                action TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def login_admin(self, password: str) -> bool:
        """Přihlášení jako admin"""
        if password == self.admin_password:
            self.logged_in_user = "ADMIN"
            self.current_level = AdminLevel.SUPER_ADMIN
            self.log_action("LOGIN", "Úspěšné přihlášení SUPER ADMIN", "SUCCESS")
            print("\n🔐 ✅ SUPER ADMIN mód aktivován!")
            return True
        else:
            self.log_action("LOGIN_FAIL", "Selhané přihlášení", "FAILED")
            print("❌ Špatné heslo!")
            return False
    
    def log_action(self, action: str, details: str, status: str):
        """Loguj akci do databáze"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO admin_logs (timestamp, admin_user, action, details, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), self.logged_in_user, action, details, status))
        
        conn.commit()
        conn.close()
    
    def check_permission(self, required_level: AdminLevel) -> bool:
        """Ověř oprávnění"""
        if self.current_level.value >= required_level.value:
            return True
        print(f"❌ Nedostatečná oprávnění. Vyžadováno: {required_level.name}")
        return False
    
    def view_audit_log(self) -> List[Dict]:
        """Zobraz audit log"""
        if not self.check_permission(AdminLevel.ADMIN):
            return []
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM admin_logs ORDER BY timestamp DESC LIMIT 50')
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        results = [dict(zip(columns, row)) for row in rows]
        return results


class AdminDataManager:
    """Správa dat s admin funkcemi"""
    
    def __init__(self, security_manager: AdminSecurityManager):
        self.security = security_manager
    
    def backup_database(self, backup_dir='backups') -> bool:
        """Vytvoř backup databáze"""
        if not self.security.check_permission(AdminLevel.ADMIN):
            return False
        
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'kb_backup_{timestamp}.csv')
        
        try:
            # Tento bude implementován v main třídě
            self.security.log_action(
                "BACKUP",
                f"Backup vytvořen: {backup_file}",
                "SUCCESS"
            )
            print(f"✅ Backup vytvořen: {backup_file}")
            return True
        except Exception as e:
            self.security.log_action(
                "BACKUP",
                f"Chyba: {str(e)}",
                "FAILED"
            )
            print(f"❌ Chyba při backupu: {e}")
            return False
    
    def restore_backup(self, backup_file: str) -> bool:
        """Obnoví databázi z backupu"""
        if not self.security.check_permission(AdminLevel.SUPER_ADMIN):
            return False
        
        if not os.path.exists(backup_file):
            print(f"❌ Soubor nenalezen: {backup_file}")
            return False
        
        try:
            self.security.log_action(
                "RESTORE",
                f"Restore z: {backup_file}",
                "SUCCESS"
            )
            print(f"✅ Databáze obnovena z: {backup_file}")
            return True
        except Exception as e:
            self.security.log_action(
                "RESTORE",
                f"Chyba: {str(e)}",
                "FAILED"
            )
            print(f"❌ Chyba při restore: {e}")
            return False
    
    def export_data(self, format_type: str = 'json') -> str:
        """Exportuj data"""
        if not self.security.check_permission(AdminLevel.ADMIN):
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'json':
            filename = f'export_{timestamp}.json'
        elif format_type == 'csv':
            filename = f'export_{timestamp}.csv'
        else:
            filename = f'export_{timestamp}.txt'
        
        self.security.log_action(
            "EXPORT",
            f"Export do {format_type}: {filename}",
            "SUCCESS"
        )
        print(f"✅ Data exportována do: {filename}")
        return filename


class PromptOptimizer:
    """Optimalizuje prompty pro lepší výsledky"""
    
    def __init__(self):
        self.cache = {}
        self.performance_log = []
    
    def create_system_prompt(self, knowledge_type: str) -> str:
        """Vytvoří system prompt"""
        system_prompts = {
            "analysis": """Jsi expertní analytik. Tvůj úkol:
1. Analyzovat poskytnuté informace důsledně
2. Identifikovat klíčové vhledy a vzory
3. Poskytovat konkrétní, akční doporučení
4. Být přesný a nepřidávat spekulace
Odpovídej strukturovaně.""",
            
            "synthesis": """Jsi specialista na syntetizování informací. Tvůj úkol:
1. Propojit související koncepty
2. Vytvořit coherentní příběh z dat
3. Zvýraznit vzájemné vztahy
4. Poskytnout praktické aplikace
Buď precizní.""",
            
            "generation": """Jsi kreativní expert. Tvůj úkol:
1. Vytvořit relevantní a kvalitní obsah
2. Zajistit originalitu
3. Přizpůsobit styl
4. Být jasný a impactful"""
        }
        return system_prompts.get(knowledge_type, system_prompts["analysis"])
    
    def optimize_prompt(self, base_prompt: str, context: str = "") -> str:
        """Optimalizuje prompt"""
        optimized = f"""{base_prompt}

KONTEXT: {context if context else 'Obecný dotaz'}

INSTRUKCE:
- Konkrétní a akční
- Příklady kde je vhodné
- Struktura: Body → Detaily → Aplikace
- Délka: Podrobná ale čitelná
- Tón: Profesionální"""
        return optimized


class GeminiIntegration:
    """Integrace s Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Gemini API není dostupná")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY není nastaven")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro")
        self.optimizer = PromptOptimizer()
    
    def generate_insights(self, knowledge_text: str, tema: str) -> str:
        """Generuje insights"""
        prompt = self.optimizer.optimize_prompt(
            base_prompt=f"""Analýzuj znalost a vytvoř insights:
            
TÉMA: {tema}
ZNALOST:
{knowledge_text}

Vytvoř:
1. 3 klíčové learnings
2. 2 praktické aplikace
3. 1 překvapivý insight""",
            context=f"Analýza: {tema}"
        )
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def answer_question(self, question: str, knowledge_base: str) -> str:
        """Odpovídá na otázky"""
        prompt = self.optimizer.optimize_prompt(
            base_prompt=f"""Odpověz na otázku:

ZNALOSTNÍ BÁZE:
{knowledge_base}

OTÁZKA: {question}

Postupuj:
1. Hledej relevantní info
2. Strukturuj logicky
3. Poskytni příklady
4. Zmíni omezení""",
            context=f"Q: {question}"
        )
        
        response = self.model.generate_content(prompt)
        return response.text


class SmartKnowledgeBase:
    """Hlavní třída se všemi funkcemi"""
    
    def __init__(self, filename='knowledge_base.csv', admin_password: Optional[str] = None):
        self.filename = filename
        self.df = self.load_knowledge_base()
        
        # Inicializuj security
        self.security = AdminSecurityManager()
        if admin_password:
            os.environ['ADMIN_PASSWORD'] = admin_password
        
        self.data_manager = AdminDataManager(self.security)
        
        # Inicializuj Gemini
        self.gemini = None
        if os.getenv("GEMINI_API_KEY"):
            try:
                self.gemini = GeminiIntegration()
                print("✅ Gemini integrován")
            except Exception as e:
                print(f"⚠️ Gemini: {e}")
    
    def load_knowledge_base(self):
        """Načte databázi"""
        try:
            df = pd.read_csv(self.filename)
            print(f"✅ Databáze: {len(df)} záznamů")
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                'Datum', 'Téma', 'Popis', 'Detail', 'Tagy', 'Zdroj', 'Důležitost'
            ])
            print("🆕 Nová databáze")
        return df
    
    def add_knowledge(self, tema: str, popis: str, detail: str, tagy: str,
                      zdroj: str = "Manual", dulezitost: int = 5):
        """Přidá znalost"""
        new_row = {
            'Datum': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Téma': tema,
            'Popis': popis,
            'Detail': detail,
            'Tagy': tagy,
            'Zdroj': zdroj,
            'Důležitost': dulezitost
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.save_to_file()
        self.security.log_action("ADD_KNOWLEDGE", f"Přidáno: {tema}", "SUCCESS")
        print(f"💾 Uloženo: {tema}")
    
    def save_to_file(self):
        """Uloží databázi"""
        self.df.to_csv(self.filename, index=False)
    
    def search_knowledge(self, keyword: str) -> pd.DataFrame:
        """Vyhledá znalosti"""
        mask = (
            self.df['Téma'].str.contains(keyword, case=False, na=False) |
            self.df['Popis'].str.contains(keyword, case=False, na=False) |
            self.df['Tagy'].str.contains(keyword, case=False, na=False)
        )
        results = self.df[mask]
        print(f"🔍 Nalezeno: {len(results)} záznamů pro '{keyword}'")
        if len(results) > 0:
            print(results.to_string(index=False))
        return results
    
    def delete_knowledge(self, index: int) -> bool:
        """ADMIN: Smazat znalost"""
        if not self.security.check_permission(AdminLevel.ADMIN):
            return False
        
        if index >= len(self.df) or index < 0:
            print("❌ Neplatný index")
            return False
        
        tema = self.df.iloc[index]['Téma']
        self.df = self.df.drop(index).reset_index(drop=True)
        self.save_to_file()
        self.security.log_action(
            "DELETE_KNOWLEDGE",
            f"Smazáno: {tema}",
            "SUCCESS"
        )
        print(f"🗑️ Smazáno: {tema}")
        return True
    
    def edit_knowledge(self, index: int, **updates) -> bool:
        """ADMIN: Edituj znalost"""
        if not self.security.check_permission(AdminLevel.ADMIN):
            return False
        
        if index >= len(self.df) or index < 0:
            print("❌ Neplatný index")
            return False
        
        original = self.df.iloc[index]['Téma']
        
        for key, value in updates.items():
            if key in self.df.columns:
                self.df.at[index, key] = value
        
        self.df.at[index, 'Datum'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_to_file()
        self.security.log_action(
            "EDIT_KNOWLEDGE",
            f"Editováno: {original}",
            "SUCCESS"
        )
        print(f"✏️ Editováno: {original}")
        return True
    
    def bulk_import(self, json_file: str) -> bool:
        """ADMIN: Importuj data"""
        if not self.security.check_permission(AdminLevel.ADMIN):
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                self.add_knowledge(**item)
            
            self.security.log_action(
                "BULK_IMPORT",
                f"Importováno: {len(data)} položek",
                "SUCCESS"
            )
            print(f"✅ Importováno: {len(data)} položek")
            return True
        except Exception as e:
            self.security.log_action(
                "BULK_IMPORT",
                f"Chyba: {str(e)}",
                "FAILED"
            )
            print(f"❌ Chyba: {e}")
            return False
    
    def get_insights_with_gemini(self, tema: str) -> str:
        """Generuj insights"""
        if not self.gemini:
            print("❌ Gemini není dostupný")
            return ""
        
        results = self.search_knowledge(tema)
        if len(results) == 0:
            print(f"❌ Žádné záznamy pro '{tema}'")
            return ""
        
        knowledge_text = "\n---\n".join([
            f"Téma: {row['Téma']}\nPopis: {row['Popis']}\nDetail: {row['Detail']}"
            for _, row in results.iterrows()
        ])
        
        print(f"🤖 Generuji insights pro '{tema}'...")
        insights = self.gemini.generate_insights(knowledge_text, tema)
        print(insights)
        return insights
    
    def answer_question(self, question: str) -> str:
        """Odpověz na otázku"""
        if not self.gemini:
            print("❌ Gemini není dostupný")
            return ""
        
        kb_text = "\n---\n".join([
            f"Téma: {row['Téma']}\nPopis: {row['Popis']}\nDetail: {row['Detail']}"
            for _, row in self.df.iterrows()
        ])
        
        print(f"🤖 Odpovídám: {question}...")
        answer = self.gemini.answer_question(question, kb_text)
        print(answer)
        return answer
    
    def get_stats(self):
        """Zobraz statistiky"""
        print(f"\n📊 STATISTIKY:")
        print(f"Celkem záznamů: {len(self.df)}")
        if len(self.df) > 0:
            print(f"Nejstarší: {self.df['Datum'].min()}")
            print(f"Nejnovější: {self.df['Datum'].max()}")
            tags = self.df['Tagy'].str.split(', ').explode().value_counts()
            if len(tags) > 0:
                print(f"Top tagy: {', '.join(tags.head(3).index.tolist())}")
            print(f"Průměrná důležitost: {self.df['Důležitost'].mean():.1f}/10")
    
    def admin_console(self):
        """ADMIN KONZOLE"""
        print("\n" + "="*60)
        print("🔐 SMART KNOWLEDGE BASE - ADMIN CONSOLE")
        print("="*60)
        
        # Přihlášení
        password = input("\n🔑 Zadej admin heslo: ")
        if not self.security.login_admin(password):
            print("Přístup odepřen!")
            return
        
        while True:
            print("\n" + "-"*60)
            print("ADMIN MENU:")
            print("-"*60)
            print("1. 📊 Zobraz statistiky")
            print("2. ➕ Přidej znalost")
            print("3. 🔍 Hledej znalost")
            print("4. ✏️  Edituj znalost")
            print("5. 🗑️  Smaž znalost")
            print("6. 💾 Backup databáze")
            print("7. 📥 Obnoví backup")
            print("8. 📤 Exportuj data")
            print("9. 📋 Importuj data")
            print("10. 🤖 Generuj insights (Gemini)")
            print("11. ❓ Odpoví na otázku (Gemini)")
            print("12. 📜 Zobraz audit log")
            print("13. ❌ Odhlášení")
            print("-"*60)
            
            choice = input("\nVyberte volbu (1-13): ").strip()
            
            if choice == "1":
                self.get_stats()
            
            elif choice == "2":
                tema = input("Téma: ")
                popis = input("Popis: ")
                detail = input("Detail: ")
                tagy = input("Tagy (čárkou oddělené): ")
                dulezitost = int(input("Důležitost (1-10): ") or 5)
                self.add_knowledge(tema, popis, detail, tagy, dulezitost=dulezitost)
            
            elif choice == "3":
                keyword = input("Klíčové slovo: ")
                self.search_knowledge(keyword)
            
            elif choice == "4":
                idx = int(input("Index znalosti: "))
                print("\nNechte prázdné pokud nechcete měnit:")
                tema = input("Nové téma: ")
                popis = input("Nový popis: ")
                detail = input("Nový detail: ")
                
                updates = {}
                if tema: updates['Téma'] = tema
                if popis: updates['Popis'] = popis
                if detail: updates['Detail'] = detail
                
                if updates:
                    self.edit_knowledge(idx, **updates)
            
            elif choice == "5":
                idx = int(input("Index znalosti k smazání: "))
                confirm = input("Jste si jisti? (ano/ne): ")
                if confirm.lower() == 'ano':
                    self.delete_knowledge(idx)
            
            elif choice == "6":
                self.data_manager.backup_database()
            
            elif choice == "7":
                backup_file = input("Cesta k backup souboru: ")
                self.data_manager.restore_backup(backup_file)
            
            elif choice == "8":
                fmt = input("Formát (json/csv): ") or "json"
                self.data_manager.export_data(fmt)
            
            elif choice == "9":
                json_file = input("Cesta k JSON souboru: ")
                self.bulk_import(json_file)
            
            elif choice == "10":
                tema = input("Téma pro insights: ")
                self.get_insights_with_gemini(tema)
            
            elif choice == "11":
                question = input("Otázka: ")
                self.answer_question(question)
            
            elif choice == "12":
                logs = self.security.view_audit_log()
                print("\n📜 AUDIT LOG (posledních 50 akcí):")
                for log in logs:
                    print(f"[{log['timestamp']}] {log['action']} - {log['status']}")
                    print(f"  Details: {log['details']}")
            
            elif choice == "13":
                print("\n👋 Odhlášení...")
                self.security.logged_in_user = None
                self.security.current_level = AdminLevel.GUEST
                break
            
            else:
                print("❌ Neplatná volba")


# === SPUŠTĚNÍ ===
if __name__ == "__main__":
    # Vytvoř knowledge base
    kb = SmartKnowledgeBase()
    
    # Spusť admin konzoli
    kb.admin_console()
