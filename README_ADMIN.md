# Smart Knowledge Base - Admin Mode

## 🔐 Admin Console s Plnými Právy

Je to **admin panel** s úplnou kontrolou nad znalostní databází.

---

## 📋 FUNKCE

### ✅ Základní Operace
- **Přidej znalost** - Přidej nové záznamy
- **Hledej znalost** - Vyhledej podle klíčového slova
- **Edituj znalost** - Uprav stávající záznamy
- **Smaž znalost** - Smaž nežádoucí záznamy
- **Zobraz statistiky** - Přehled databáze

### 🔐 Admin Funkce
- **Backup databáze** - Vytvoř zálohu
- **Obnoví backup** - Vrať se k staršímu stavu
- **Exportuj data** - JSON/CSV export
- **Importuj data** - Hromadné přidání ze souboru
- **Audit log** - Sleduj všechny akce

### 🤖 Gemini Integrace
- **Generuj insights** - AI analýza znalostí
- **Odpověz na otázku** - Otázky-odpovědi na základě databáze

---

## 🚀 SPUŠTĚNÍ

```bash
# 1. Instaluj dependence
pip install pandas google-generativeai

# 2. Nastav API klíč
export GEMINI_API_KEY="tvůj-klíč"

# 3. (Volitelně) Nastav admin heslo
export ADMIN_PASSWORD="tvoje-silne-heslo"

# 4. Spusť
python smart_knowledge_admin.py
```

---

## 🔑 PŘIHLÁŠENÍ

**Výchozí heslo:** `admin123`

První spuštění:
```
🔐 Zadej admin heslo: admin123
✅ SUPER ADMIN mód aktivován!
```

---

## 📤 IMPORT DAT

Použ `example_data.json` pro rychlé plnění databáze:

```bash
# V admin konzoli:
Vyberte volbu: 9  # Importuj data
Cesta k JSON souboru: example_data.json
✅ Importováno: 5 položek
```

---

## 📊 OPERACE V DETAILU

### Přidej Znalost
```
Téma: Python Best Practices
Popis: Klíčové postupy...
Detail: PEP 8, type hints...
Tagy: python, coding, best-practices
Důležitost (1-10): 9
```

### Hledej
```
Klíčové slovo: python
🔍 Nalezeno: 2 záznamů pro 'python'
```

### Edituj
```
Index znalosti: 0
Nové téma: [nechte prázdné pro změnu]
Nový popis: Nový popis...
✏️ Editováno
```

### Smaž
```
Index znalosti k smazání: 0
Jste si jisti? (ano/ne): ano
🗑️ Smazáno
```

### Backup
```
Vyberte volbu: 6
✅ Backup vytvořen: backups/kb_backup_20250528_143022.csv
```

### Gemini Insights
```
Vyberte volbu: 10
Téma pro insights: Python Best Practices
🤖 Generuji insights...
[Gemini odpověď s analýzou]
```

---

## 📜 AUDIT LOG

Všechny akce jsou logovány:

```
[2025-05-28T14:30:22.123456] LOGIN - SUCCESS
[2025-05-28T14:30:45.234567] ADD_KNOWLEDGE - SUCCESS
[2025-05-28T14:31:12.345678] BACKUP - SUCCESS
```

Zobraz log:
```
Vyberte volbu: 12
📜 AUDIT LOG (posledních 50 akcí)
```

---

## 🔒 BEZPEČNOST

- ✅ Admin heslo chráněné
- ✅ Všechny akce logované
- ✅ Oprávnění kontroly (AdminLevel)
- ✅ Audit trail pro compliance

---

## 🔄 WORKFLOW

### Typický Pracovní Den:

1. **Spusť admin konzoli** → Přihlášení
2. **Kontrola statistik** → Přehled
3. **Přidej nové znalosti** → Učení
4. **Hledej a edituj** → Údržba
5. **Gemini insights** → Analýza
6. **Backup** → Bezpečnost
7. **Audit log** → Compliance
8. **Odhlášení** → Konec

---

## 💡 TIPY

- Importuj `example_data.json` pro rychlý start
- Dělej backupy před velkými změnami
- Gemini insights jsou nejlepší pro shrnutí
- Audit log je vždy dostupný pro review

---

## 📞 SUPPORT

Jednoduché otázky? Zkus **admin console** → **11. Odpověz na otázku**

---

**Status:** ✅ Plně funkční  
**Poslední update:** 2025-05-28  
**Verze:** 2.0 - Admin Edition
