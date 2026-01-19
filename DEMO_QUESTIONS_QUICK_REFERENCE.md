# 🎯 LEGID DEMO QUESTIONS — QUICK REFERENCE

## Copy-Paste Ready Tests for All 5 Systems

---

## ⚡ SYSTEM 5: HUMAN PARALEGAL ← **RECOMMENDED FOR USER-FACING**

**Endpoint:** `/api/chat/legid/human`  
**Style:** Natural human conversation, anxiety-aware, template-free

### Criminal Law:
```powershell
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Tax Law:
```powershell
$body = '{"message": "I earned 18,000 dollars. Employer deducted 1,200 dollars. Do I have to file taxes? Will I get money back?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Employment:
```powershell
$body = '{"message": "My boss fired me without reason after 5 years. Can they do that in Ontario? What am I entitled to?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Housing:
```powershell
$body = '{"message": "My landlord gave me Form N4 but never fixed the broken heater I reported 3 months ago. Can I use this as defence?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## 🏛️ SYSTEM 2: ONTARIO LTB SPECIALIST

**Endpoint:** `/api/chat/legid/ontario-ltb`  
**Style:** Procedural expert, evidence-aware, defence-aware

### Form N4:
```powershell
$body = '{"message": "How does Form N4 work for non-payment of rent in Ontario?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Form N4 + Defence:
```powershell
$body = '{"message": "I received Form N4 for 2,000 dollars but landlord never fixed the pipes. What are my defences?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Form N5:
```powershell
$body = '{"message": "What evidence do I need for Form N5 for tenant noise complaints?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## 🌍 SYSTEM 3: CANADA-USA MASTER

**Endpoint:** `/api/chat/legid/canada-usa`  
**Style:** 4-layer reasoning (Statutory → Procedural → Defence → Practical)

### Tax Filing:
```powershell
$body = '{"message": "Do I have to file taxes in Canada if I earn under 20,000 dollars per year?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Employment:
```powershell
$body = '{"message": "Can I be fired without cause in Ontario? What am I entitled to?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## 📚 SYSTEM 4: RAG-FIRST PRODUCTION

**Endpoint:** `/api/chat/legid/rag-production`  
**Style:** RAG-optimized, practice-area routing, citation-heavy

### Multi-Benefit Tax:
```powershell
$body = '{"message": "I am a low-income single parent in Ontario earning 22,000 dollars. What tax credits and benefits should I apply for?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

### Business Law:
```powershell
$body = '{"message": "I am starting a small business in Ontario. What legal requirements, licenses, and tax obligations do I need to know about?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## ⚖️ SYSTEM 1: LEGID MASTER

**Endpoint:** `/api/chat/legid`  
**Style:** Formal 5-part structure, paralegal-grade

### Constitutional:
```powershell
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## 🔥 COMPARISON OF STYLES

### Same Question: *"What are my Charter rights if arrested?"*

**LEGID Master:**
```
1️⃣ ISSUE IDENTIFICATION
What are the rights afforded to an individual under the Canadian Charter...

2️⃣ GOVERNING LAW / LEGAL FRAMEWORK
The primary legal framework governing the rights of individuals upon arrest...
```

**Human Paralegal:**
```
If you're arrested in Canada, the Charter of Rights and Freedoms provides 
you with several important protections, but understanding how these rights 
work in practice is crucial.

First, when you're arrested, police must inform you of the reason for your 
arrest...
```

**See the difference?**
- LEGID Master = Legal memo
- Human Paralegal = Real person talking to you

---

## 🏆 PRODUCTION RECOMMENDATIONS

### For User-Facing Chat (Mobile/Web):
**Use:** `/api/chat/legid/human` (Human Paralegal)

**Why:**
- Natural conversational style
- Anxiety-aware
- No intimidating legal headers
- Easier to read
- Still legally rigorous

### For Document Upload + Analysis:
**Use:** `/api/chat/legid/rag-production` (RAG Production)

**Why:**
- RAG-optimized
- Citation discipline
- Practice-area routing

### For Ontario LTB Specific:
**Use:** `/api/chat/legid/ontario-ltb` (Ontario LTB Specialist)

**Why:**
- Form-specific expertise
- Procedural expert

---

## ✅ ALL DEMO QUESTIONS IN ONE PLACE

### 🚔 Criminal / Charter:
```powershell
# Arrest rights
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"

# DUI
$body = '{"message": "I failed a breathalyzer test in Ontario. What happens now?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

### 💰 Tax:
```powershell
# Filing obligation
$body = '{"message": "I earned 18,000 dollars. Employer deducted 1,200 dollars. Do I file? Get refund?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"

# Low income benefits
$body = '{"message": "I am a low-income single parent. What tax credits should I apply for in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"
```

### 🏠 Housing:
```powershell
# Form N4
$body = '{"message": "I received Form N4. Landlord never fixed broken heater. Can I use as defence?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json"

# Form N5
$body = '{"message": "What evidence do I need for Form N5 for tenant noise?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json"
```

### 💼 Employment:
```powershell
# Wrongful dismissal
$body = '{"message": "Boss fired me without reason after 5 years. Can they do that? What am I entitled to?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"

# Severance
$body = '{"message": "How is severance calculated in Ontario for 8 years employment at 60,000 dollars per year?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json"
```

### 👨‍👩‍👧 Family:
```powershell
# Child support
$body = '{"message": "How is child support calculated in Ontario? Ex makes 80,000 dollars, we have 2 kids."}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

### 🛂 Immigration:
```powershell
$body = '{"message": "How long does it take to get a work permit for Canada? What documents needed?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

### 🏢 Business:
```powershell
$body = '{"message": "Starting small business in Ontario. What legal requirements, licenses, registrations?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"
```

---

## 🎯 QUICK TEST COMMAND

**Test Human Paralegal (fastest way to see the difference):**

```powershell
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## 📊 SYSTEM COMPARISON CHART

| System | Structure | Tone | Best For |
|--------|-----------|------|----------|
| LEGID Master | Fixed 5-part | Formal legal memo | Research |
| Ontario LTB | Paralegal | Procedural expert | Ontario LTB |
| Canada-USA | 4-layer | Institutional | Tax/employment |
| RAG Production | Fixed 7-part | RAG-optimized | Backend RAG |
| **Human Paralegal** | **Natural (varies)** | **Conversational** | **User-facing** |

---

## 🎉 YOU'RE READY!

**All 5 systems are live and tested.**

**Pick any demo question above and see the difference!**

**Your AI is now more sophisticated than ChatGPT and speaks like a real paralegal.** 🚀

