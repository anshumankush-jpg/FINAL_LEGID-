# 🏛️ LEGID Ontario LTB Specialist — Integration Complete

## 🎉 What You Just Got

A **specialized Ontario Landlord & Tenant Board (LTB) expert mode** that answers like a **seasoned Ontario paralegal**.

This is **in addition to** the LEGID Master Prompt - it's a specialized variant optimized for Ontario LTB matters.

---

## 🎯 What Makes Ontario LTB Mode Different

### General LEGID Master Prompt:
- Broad legal intelligence
- Multi-jurisdictional
- General legal framework
- 5-part structured analysis

### Ontario LTB Specialist:
- **Ontario-specific** (RTA, LTB focus)
- **Procedural expert** (forms, timelines, service)
- **Evidence-aware** (what LTB wants to see)
- **Defence-aware** (anticipates opposing arguments)
- **Form-specific** (N4, N5, L1 deep knowledge)
- **LTB hearing-focused** ("judge lens" reasoning)
- **Clean formatting** (no emojis, no "pros/cons/risk")

---

## 🚀 How to Use It (3 Ways)

### Option 1: Dedicated Endpoint (Recommended)

```bash
POST /api/chat/legid/ontario-ltb
{
  "message": "How does Form N4 work for non-payment of rent?"
}
```

**Best for:**
- Ontario landlord-tenant questions
- LTB applications and notices
- Form guidance (N4, N5, L1)
- Eviction procedures

---

### Option 2: Mode Selection (Advanced Endpoint)

```bash
POST /api/chat/legid/advanced
{
  "message": "How does Form N4 work?",
  "mode": "ontario_ltb"
}
```

**Now supports 5 modes:**
- `master` — General legal intelligence
- `paralegal` — Practical assistance
- `lawyer` — Maximum sophistication
- `research` — Deep research
- `ontario_ltb` — **Ontario LTB specialist** ← NEW!

---

### Option 3: Direct Python Usage

```python
from app.legid_ontario_ltb_prompt import LEGID_ONTARIO_LTB_PROMPT

messages = [
    {'role': 'system', 'content': LEGID_ONTARIO_LTB_PROMPT},
    {'role': 'user', 'content': 'How does Form N4 work?'}
]
```

---

## 📊 Response Structure (Always Follows This)

### A. Issue Framing
```
You're referencing Ontario's Residential Tenancies Act, 2006 and asking 
how Form N4 functions within the LTB process.
```

### B. What the Law/Process Actually Does
```
In Ontario, eviction is not automatic. A notice (N4) is a procedural step 
that may allow the landlord to apply to the LTB, but only the LTB can order eviction.
```

### C. Form-by-Form Analysis
```
Form N4 (Non-Payment of Rent)

Applies when rent is unpaid after it becomes due.

Legal nature: a conditional notice. If the tenant pays the arrears within 
the notice period, the notice may be voided.

Evidence the LTB typically expects: a rent ledger, the tenancy agreement, 
and a clear arrears calculation.

Common failure points: incorrect dates, incorrect arrears, or service issues; 
inconsistent conduct (e.g., accepting payments in a way that undermines the notice).

Defences to anticipate: payment dispute, arrears miscalculation, and arguments 
tied to maintenance/repair issues (including potential abatement claims).
```

### D. Practical Next Actions
```
Confirm which issue you actually have (arrears vs conduct vs damage).

Gather documents: rent ledger, lease, communications, photos/invoices, 
and a service record.

If you proceed, ensure service and dates are correct because procedural 
defects are a common reason applications fail.
```

### E. Limits + Safety Disclaimer
```
General information only, not legal advice. If you share your facts (arrears 
amount, dates, and what happened), I can outline the most relevant procedural 
path and what evidence typically matters at the LTB.
```

---

## 🔥 Key Features

### 1. **"LTB Judge Lens" Reasoning**

Answers as if preparing for an LTB hearing tomorrow:

✅ Assumes opposing party will raise defences  
✅ Scrutinizes procedural requirements  
✅ Identifies common failure points  
✅ Checks evidence quality  
✅ Flags service and date calculation issues  

### 2. **Defence-Aware**

Always anticipates tenant defences:
- Payment disputes
- Arrears miscalculations
- Maintenance/repair issues
- Improper service
- Retaliation allegations
- Harassment/interference claims

### 3. **Evidence-Focused**

Specifies what LTB typically wants:
- Rent ledgers
- Lease agreements
- Incident logs
- Photos/invoices
- Witness statements
- Service records

### 4. **Form-Specific Knowledge**

Deep expertise on:
- **Form N4** — Non-payment of rent (conditional/voidable)
- **Form N5** — Interference/damage (remedy opportunity)
- **Form L1** — Application after N4 (hearing-based)

### 5. **Clean Professional Formatting**

❌ No emojis  
❌ No "Quick take" sections  
❌ No "Pros/Cons/Risk Level" sections  
❌ No markdown stars for emphasis  

✅ Clean headings  
✅ Simple dashes for bullets  
✅ Short paragraphs (2-3 lines)  
✅ Numbered steps when sequence matters  

---

## 🧪 Test It Now

### Test 1: Form N4 Question

```bash
curl -X POST http://localhost:8000/api/chat/legid/ontario-ltb \
  -H "Content-Type: application/json" \
  -d '{"message": "How does Form N4 work for non-payment of rent in Ontario?"}'
```

**Expected response:**
- Issue framing (RTA, LTB)
- Procedural explanation
- N4 specifics (conditional notice, voidable by payment)
- Evidence requirements (rent ledger, lease, arrears calculation)
- Common failure points
- Tenant defences to anticipate
- Practical next actions
- Clean formatting (no emojis, no "pros/cons")

---

### Test 2: Form N5 Question

```bash
curl -X POST http://localhost:8000/api/chat/legid/ontario-ltb \
  -H "Content-Type: application/json" \
  -d '{"message": "What evidence do I need for Form N5 for tenant interference?"}'
```

**Expected response:**
- Form N5 purpose (interference/damage)
- Evidence expectations (incident logs, emails, photos, invoices)
- Common failure points (vague allegations)
- Defences to anticipate (credibility challenges)
- Practical checklist

---

### Test 3: General LTB Process

```bash
curl -X POST http://localhost:8000/api/chat/legid/ontario-ltb \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the difference between a notice and an eviction order in Ontario?"}'
```

**Expected response:**
- Procedural distinction
- Notice = first step (not eviction)
- LTB order = required for eviction
- Service and timeline requirements
- Common misconceptions

---

## 📈 Comparison: General LEGID vs Ontario LTB Specialist

### Same Question: *"How does Form N4 work?"*

**General LEGID Master Prompt:**
```
ISSUE IDENTIFICATION
────────────────────
The question concerns Form N4 under Ontario's residential tenancy framework.

GOVERNING LAW
─────────────
Residential Tenancies Act, 2006, S.O. 2006, c. 17

LEGAL ANALYSIS
──────────────
[General legal framework analysis...]
```
- Focus: Legal structure and statute
- Style: Formal legal memo
- Tone: General legal intelligence

---

**Ontario LTB Specialist:**
```
Issue Framing

You're referencing Ontario's Residential Tenancies Act, 2006 and asking how Form N4 
functions within the LTB process.

What the Process Actually Does

In Ontario, eviction is not automatic. A notice (N4) is a procedural step that may 
allow the landlord to apply to the LTB, but only the LTB can order eviction.

Form N4 (Non-Payment of Rent)

Applies when rent is unpaid after it becomes due.

Legal nature: a conditional notice. If the tenant pays the arrears within the notice 
period, the notice may be voided.

Evidence the LTB typically expects: a rent ledger, the tenancy agreement, and a 
clear arrears calculation.

Common failure points: incorrect dates, incorrect arrears, or service issues; 
inconsistent conduct (e.g., accepting payments in a way that undermines the notice).

Defences to anticipate: payment dispute, arrears miscalculation, and arguments tied 
to maintenance/repair issues (including potential abatement claims).
```
- Focus: Procedure, evidence, defences
- Style: Paralegal practitioner
- Tone: LTB hearing preparation

---

## 🎯 When to Use Each Mode

### Use **General LEGID Master Prompt** for:
- Multi-jurisdictional questions
- General legal framework analysis
- Statute interpretation
- Constitutional matters
- Non-Ontario jurisdictions

### Use **Ontario LTB Specialist** for:
- ✅ Ontario landlord-tenant disputes
- ✅ LTB applications and notices
- ✅ Form N4, N5, L1 guidance
- ✅ Eviction procedures
- ✅ Rent arrears cases
- ✅ Interference/damage cases
- ✅ Hearing preparation
- ✅ Evidence gathering
- ✅ Service requirements
- ✅ Tenant defence anticipation

---

## 🛠️ Integration with RAG

The Ontario LTB prompt is **designed for RAG** (Retrieval-Augmented Generation):

### Recommended Retrieval Queries:

When user mentions Form N4:
```
"Ontario LTB Form N4 purpose"
"LTB N4 instructions service"
"RTA Ontario non-payment rent notice void"
"LTB application L1 requirements hearing evidence"
```

When user mentions Form N5:
```
"Ontario LTB Form N5 purpose interference"
"LTB N5 damage evidence requirements"
"RTA Ontario substantial interference"
```

### Document Chunking Strategy:

Chunk by:
- **Form sections** (Purpose, Reason, Termination Date, Service)
- **LTB interpretation guidance** (common errors)
- **RTA topics** (rent, repair, interference, remedies)

Chunk size: **300-700 tokens**

Metadata to store:
```json
{
  "jurisdiction": "Ontario",
  "document_type": "form|statute|guide",
  "form_id": "N4|N5|L1",
  "topic": "non-payment|interference|damage"
}
```

---

## 💡 Pro Tips

### 1. **Combine with Document Upload**

```python
# User uploads Form N4
# Extract key data: amount, dates, termination date
# Pass to Ontario LTB specialist with context

messages = [
    {
        'role': 'system', 
        'content': LEGID_ONTARIO_LTB_PROMPT
    },
    {
        'role': 'user', 
        'content': f"""
        Form N4 Details:
        - Amount owing: $3,500
        - Termination date: 2024-02-15
        - Service date: 2024-01-30
        
        Question: Is this notice valid?
        """
    }
]
```

### 2. **Use for Evidence Checklists**

Perfect for generating hearing prep lists:
- What documents to bring
- What witnesses to call
- What photos/logs to prepare
- What service proof to have

### 3. **Anticipate Defences**

Always asks the specialist to consider opposing arguments:
- Helps landlords prepare for tenant defences
- Helps tenants understand their options

### 4. **Low Temperature for Procedural Accuracy**

```python
temperature = 0.2  # Strict procedural accuracy
max_tokens = 2500  # Detailed procedural guidance
```

---

## 📚 Documentation Reference

**New Files:**
- `backend/app/legid_ontario_ltb_prompt.py` — Core prompt
- `LEGID_ONTARIO_LTB_GUIDE.md` — This file

**Updated Files:**
- `backend/app/main.py` — Added Ontario LTB endpoints

**Related:**
- `LEGID_MASTER_PROMPT_INTEGRATION.md` — General LEGID guide
- `LEGID_QUICKSTART.md` — Quick start guide

---

## 🚦 Deployment Checklist

- [x] ✅ Ontario LTB prompt created
- [x] ✅ Integrated into `main.py`
- [x] ✅ New endpoint: `/api/chat/legid/ontario-ltb`
- [x] ✅ Added to advanced endpoint as mode `ontario_ltb`
- [x] ✅ Documentation created
- [ ] ⏳ **TODO:** Test endpoints
- [ ] ⏳ **TODO:** Test with real LTB questions
- [ ] ⏳ **TODO:** Compare to general LEGID responses
- [ ] ⏳ **TODO:** Get paralegal feedback

---

## 🎓 Example Use Cases

### Use Case 1: Landlord with Unpaid Rent
```
Question: "My tenant owes $2,000 in rent. What do I do?"

Ontario LTB Specialist Response:
- Issue framing (RTA, LTB process)
- Explains Form N4 (conditional notice)
- Evidence needed (rent ledger, lease, arrears calc)
- Service requirements
- Common mistakes to avoid
- Tenant defences to expect (payment dispute, maintenance issues)
- Next steps checklist
```

### Use Case 2: Tenant Facing Eviction
```
Question: "I received Form N4. What are my options?"

Ontario LTB Specialist Response:
- Explains N4 is conditional (voidable by payment)
- Payment deadline and calculation
- Options: pay arrears, dispute at hearing, negotiate
- Possible defences (maintenance, improper service)
- Evidence to gather
- How to respond
```

### Use Case 3: Interference/Damage Case
```
Question: "How do I prove tenant interference with Form N5?"

Ontario LTB Specialist Response:
- N5 purpose and trigger
- Evidence requirements (incident logs, emails, witnesses)
- Specificity needed (dates, times, impact)
- Common failure points (vague allegations)
- Defences to anticipate (credibility, alternative explanations)
- Documentation checklist
```

---

## ✅ SUMMARY

**What you have now:**

✅ **5 LEGID modes total:**
1. Master — General legal intelligence
2. Paralegal — Practical assistance
3. Lawyer — Maximum sophistication
4. Research — Deep research
5. **Ontario LTB — Landlord & Tenant Board specialist** ← NEW!

✅ **2 ways to access Ontario LTB mode:**
- Dedicated endpoint: `/api/chat/legid/ontario-ltb`
- Advanced endpoint with mode: `/api/chat/legid/advanced` (mode=ontario_ltb)

✅ **Specialized for:**
- Ontario RTA and LTB procedures
- Forms N4, N5, L1
- Evidence requirements
- Defence anticipation
- Hearing preparation

---

## 🚀 Test It Now

```bash
# Restart backend (if running)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Test Ontario LTB specialist
curl -X POST http://localhost:8000/api/chat/legid/ontario-ltb \
  -H "Content-Type: application/json" \
  -d '{"message": "How does Form N4 work for non-payment of rent in Ontario?"}'
```

**Look for:**
- Clean formatting (no emojis, no "pros/cons")
- Procedural focus
- Evidence requirements
- Defence anticipation
- Practical next actions
- Paralegal-style guidance

---

**You now have a specialist Ontario LTB paralegal built into your AI.** 🏛️

This complements the general LEGID Master Prompt perfectly - use LEGID Master for broad legal questions, and Ontario LTB Specialist for Ontario landlord-tenant matters.

**Welcome to paralegal-grade Ontario LTB intelligence.** 🚀
