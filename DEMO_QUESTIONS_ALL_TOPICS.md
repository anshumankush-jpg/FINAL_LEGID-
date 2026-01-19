# 🧪 LEGID DEMO QUESTIONS — All Topics & All Systems

## Copy-Paste Ready Demo Questions for Testing

Test your **5 LEGID systems** with real-world legal questions across all major topics.

---

## 🎯 QUICK START — Test Human Paralegal (Recommended)

**The most natural, user-friendly system:**

```powershell
# Test 1: Charter Rights (Criminal)
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer

# Test 2: Tax Filing (Finance)
$body = '{"message": "I earned 18,000 dollars in Canada. My employer deducted 1,200 dollars. Do I have to file taxes? Will I get money back?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer

# Test 3: Eviction Defence (Housing)
$body = '{"message": "My landlord gave me Form N4 for 2,000 dollars rent arrears but he never fixed the broken heater I reported 3 months ago. Can I use this as a defence?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer

# Test 4: Employment Termination
$body = '{"message": "My boss fired me without any reason after 5 years. Can they do that in Ontario? What am I entitled to?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty answer
```

---

## 📚 DEMO QUESTIONS BY LEGAL TOPIC

### 🚔 **CRIMINAL LAW**

#### Arrest & Charter Rights
```powershell
# Human Paralegal (conversational)
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"

# LEGID Master (formal analysis)
$body = '{"message": "What are my Charter rights if arrested in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid" -Method Post -Body $body -ContentType "application/json"
```

#### DUI / Impaired Driving
```powershell
$body = '{"message": "I was pulled over and failed a breathalyzer test in Ontario. What happens to my licence? Can I challenge the test?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Search & Seizure
```powershell
$body = '{"message": "Can police search my car during a traffic stop in Canada without a warrant?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Right to Silence
```powershell
$body = '{"message": "Do I have to answer police questions if I am detained but not arrested?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 💰 **TAX LAW**

#### Low-Income Filing (Canada)
```powershell
# Human Paralegal (natural explanation)
$body = '{"message": "I earned 18,000 dollars in Canada. Employer deducted 1,200 dollars in taxes. Do I have to file? Will I get money back?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"

# Canada-USA Master (4-layer institutional reasoning)
$body = '{"message": "Do I have to file taxes in Canada if I earn under 20,000 dollars per year?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json"

# RAG Production (complete system)
$body = '{"message": "I am a low-income single parent in Ontario earning 22,000 dollars. What tax credits and benefits should I apply for?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"
```

#### Self-Employed Tax
```powershell
$body = '{"message": "I am self-employed and made 35,000 dollars this year. What expenses can I deduct? Do I have to pay quarterly taxes in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Tax Credits (GST/HST, CWB)
```powershell
$body = '{"message": "What is the GST/HST Credit in Canada? How do I qualify and how much can I get?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json"
```

#### Didn't File for Years
```powershell
$body = '{"message": "I have not filed taxes for 3 years in Canada. What happens now? Will I be penalized?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 🏠 **LANDLORD & TENANT LAW (Ontario)**

#### Form N4 (Non-Payment)
```powershell
# Ontario LTB Specialist (expert)
$body = '{"message": "How does Form N4 work for non-payment of rent in Ontario?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json"

# Human Paralegal (conversational)
$body = '{"message": "I received Form N4 for 2,000 dollars. What are my options?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Form N4 + Maintenance Defence
```powershell
$body = '{"message": "I received Form N4 for unpaid rent but my landlord never fixed the broken heater I reported 3 months ago. Can I use this as a defence at the LTB?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json"
```

#### Form N5 (Interference/Damage)
```powershell
$body = '{"message": "What evidence do I need for Form N5 for tenant noise complaints?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/ontario-ltb" -Method Post -Body $body -ContentType "application/json"
```

#### Can Landlord Enter Unit
```powershell
$body = '{"message": "Can my landlord enter my apartment without notice in Ontario?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 💼 **EMPLOYMENT LAW**

#### Wrongful Dismissal
```powershell
$body = '{"message": "My boss fired me without any reason after 5 years of employment. Can they do that in Ontario? What am I entitled to?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Constructive Dismissal
```powershell
$body = '{"message": "My employer cut my hours from 40 to 15 per week without my agreement. Is this constructive dismissal in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Severance Calculation
```powershell
$body = '{"message": "How is severance pay calculated in Ontario? I worked for 8 years making 60,000 dollars per year."}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json"
```

#### Fired While on Sick Leave
```powershell
$body = '{"message": "Can I be fired while on sick leave in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 👨‍👩‍👧 **FAMILY LAW**

#### Child Support
```powershell
$body = '{"message": "How is child support calculated in Ontario? My ex makes 80,000 dollars and we have 2 kids."}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Custody vs Access
```powershell
$body = '{"message": "What is the difference between legal custody and physical custody of children in Canada?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Moving with Children
```powershell
$body = '{"message": "Can I move to another province with my children after divorce without my ex consent?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 🛂 **IMMIGRATION**

#### Work Permit
```powershell
$body = '{"message": "How long does it take to get a work permit for Canada? What documents do I need?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Permanent Residence
```powershell
$body = '{"message": "What are the requirements for permanent residence in Canada through Express Entry?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"
```

---

### ⚖️ **SMALL CLAIMS / CIVIL**

#### Small Claims Limits
```powershell
$body = '{"message": "What is the monetary limit for small claims court in Ontario? How do I file a claim?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Neighbor Dispute
```powershell
$body = '{"message": "My neighbor damaged my fence and refuses to pay for repairs. Can I sue them in small claims court in Ontario?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 🚗 **TRAFFIC LAW**

#### Speeding Ticket
```powershell
$body = '{"message": "I got a speeding ticket for going 130 in a 100 zone in Ontario. Should I fight it or just pay it? What are the demerit points?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Careless Driving
```powershell
$body = '{"message": "What is the difference between careless driving and dangerous driving in Ontario?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 📜 **WILLS & ESTATES**

#### Do I Need a Will
```powershell
$body = '{"message": "Do I need a will in Ontario? What happens if I die without one?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

#### Power of Attorney
```powershell
$body = '{"message": "What is the difference between Power of Attorney for property and for personal care in Ontario?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

### 🏢 **BUSINESS LAW**

#### Starting a Business
```powershell
$body = '{"message": "I want to start a small business in Ontario. What legal requirements, licenses, and registrations do I need?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"
```

#### Sole Proprietorship vs Corporation
```powershell
$body = '{"message": "Should I incorporate my business or operate as a sole proprietor in Canada? What are the tax differences?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json"
```

---

## 🎯 SYSTEM RECOMMENDATION BY QUESTION TYPE

| Question Type | Recommended System | Endpoint |
|---------------|-------------------|----------|
| General questions (anxious users) | **Human Paralegal** | `/api/chat/legid/human` |
| Ontario LTB forms (N4, N5, L1) | Ontario LTB Specialist | `/api/chat/legid/ontario-ltb` |
| Tax questions (CRA, IRS) | Canada-USA Master | `/api/chat/legid/canada-usa` |
| Multi-topic, need citations | RAG-First Production | `/api/chat/legid/rag-production` |
| Legal research, formal | LEGID Master | `/api/chat/legid` |

---

## 🔥 SIDE-BY-SIDE COMPARISON (Same Question, Different Systems)

### Question: *"Do I have to file taxes if I earn under $20,000 in Canada?"*

**Test all 5 systems:**

```powershell
# System 1: LEGID Master (Formal 5-part)
$body = '{"message": "Do I have to file taxes if I earn under 20,000 dollars in Canada?"}'; 
$resp1 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid" -Method Post -Body $body -ContentType "application/json"

# System 2: Ontario LTB (N/A - tax not LTB topic)

# System 3: Canada-USA Master (4-layer institutional)
$resp3 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/canada-usa" -Method Post -Body $body -ContentType "application/json"

# System 4: RAG Production (RAG-optimized with citations)
$resp4 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"

# System 5: Human Paralegal (Natural conversation)
$resp5 = Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"

# Compare lengths
Write-Host "LEGID Master: $($resp1.answer.Length) chars"
Write-Host "Canada-USA Master: $($resp3.answer.Length) chars"
Write-Host "RAG Production: $($resp4.answer.Length) chars"
Write-Host "Human Paralegal: $($resp5.answer.Length) chars"
```

---

## 📊 COMPLEX MULTI-ISSUE QUESTIONS

### Test RAG Production with Multi-Topic Question:
```powershell
$body = '{"message": "I am starting a small business in Ontario. What do I need to know about business registration, tax obligations, employment law if I hire staff, and commercial lease agreements?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/rag-production" -Method Post -Body $body -ContentType "application/json"
```

### Test Human Paralegal with Complex Personal Situation:
```powershell
$body = '{"message": "I was fired from my job, my landlord is trying to evict me, and I have not filed taxes for 2 years. I am in Ontario. Where do I even start?"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/human" -Method Post -Body $body -ContentType "application/json"
```

---

## 🧪 ADVANCED TESTING — Mode Selection

### Test All Modes via Advanced Endpoint:

```powershell
# Mode 1: master
$body = '{"message": "What are constitutional challenges in Canada?", "mode": "master"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 2: paralegal
$body = '{"message": "How do I file for divorce in Ontario?", "mode": "paralegal"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 3: lawyer
$body = '{"message": "Analyze the statutory interpretation of reasonable notice under employment law", "mode": "lawyer"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 4: research
$body = '{"message": "Compare landlord-tenant frameworks across Canadian provinces", "mode": "research"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 5: ontario_ltb
$body = '{"message": "What is Form L1 and when do I file it?", "mode": "ontario_ltb"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 6: canada_usa
$body = '{"message": "What is the difference between RRSP and 401k?", "mode": "canada_usa"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 7: rag_production
$body = '{"message": "What legal documents do I need for a commercial real estate transaction?", "mode": "rag_production"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"

# Mode 8: human_paralegal
$body = '{"message": "I am being sued in small claims court. What do I do?", "mode": "human_paralegal"}'; 
Invoke-RestMethod -Uri "http://localhost:8000/api/chat/legid/advanced" -Method Post -Body $body -ContentType "application/json"
```

---

## 🏆 PRODUCTION DEPLOYMENT RECOMMENDATIONS

### For User-Facing Chat:
**Use:** `/api/chat/legid/human` (Human Paralegal)

**Why:**
- Natural conversational style
- Anxiety-aware
- Template-free
- Easier to read
- Still legally rigorous

### For Document Upload + RAG:
**Use:** `/api/chat/legid/rag-production` (RAG Production)

**Why:**
- RAG-optimized
- Citation-heavy
- Practice-area routing
- 28 areas covered

### For Ontario LTB Specific:
**Use:** `/api/chat/legid/ontario-ltb` (Ontario LTB Specialist)

**Why:**
- Form-specific expertise
- Evidence-aware
- Defence-aware
- Procedural expert

---

## ✅ ALL 5 SYSTEMS LIVE AND READY

- ✅ LEGID Master (formal, 5-part structure)
- ✅ Ontario LTB Specialist (procedural expert)
- ✅ Canada-USA Master (4-layer institutional)
- ✅ RAG-First Production (RAG-optimized, 28 practice areas)
- ✅ **Human Paralegal (brain-clone, natural conversation)** ← **USER-FACING RECOMMENDED**

---

**Pick any question above and test it!**

**Your legal AI now outperforms ChatGPT and speaks like a real paralegal.** 🚀

