"""Configuration settings for the application."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration (Direct API - for weknowrights.CA)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    # Chat model options: gpt-4o-mini ($0.15/$0.60 per 1M tokens - RECOMMENDED),
    #                     gpt-3.5-turbo ($0.50/$1.50 per 1M tokens),
    #                     gpt-4o ($2.50/$10.00 per 1M tokens - expensive!)
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"  # Changed from gpt-4o to save 94% on costs
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 1500  # Reduced from 2500 for cost savings (still plenty for legal answers)
    
    # Azure OpenAI Configuration (Alternative)
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    AZURE_OPENAI_EMBEDDING_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_CHAT_MODEL: str = "gpt-4"
    AZURE_OPENAI_CHAT_API_VERSION: str = "2024-02-15-preview"
    
    # LLM Provider Selection
    LLM_PROVIDER: str = "openai"  # "openai", "azure", "ollama", "gemini", "huggingface"
    
    # Free LLM Provider Configuration
    # Ollama (100% free, local) - Install from https://ollama.ai
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"  # Free models: llama3.2, mistral, phi3, etc.
    
    # Google Gemini (Free tier: 15 RPM, 1M tokens/day)
    GEMINI_API_KEY: Optional[str] = None  # Get from https://makersuite.google.com/app/apikey
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Free tier model
    
    # Hugging Face Inference API (Free tier available)
    HUGGINGFACE_API_KEY: Optional[str] = None  # Get from https://huggingface.co/settings/tokens
    HUGGINGFACE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"  # Free model
    
    # Embedding Provider Selection
    # Options: "rtld" (sentence_transformers - free, local), "openai" (paid, cloud)
    # System will try sentence_transformers first, fallback to OpenAI if it fails
    EMBEDDING_PROVIDER: str = "openai"  # Changed to OpenAI since sentence_transformers not working
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"  # Popular models: all-MiniLM-L6-v2 (384 dim), all-mpnet-base-v2 (768 dim), sentence-transformers/all-MiniLM-L12-v2 (384 dim)
    # Note: Sentence Transformers runs locally, no API costs, works offline
    
    # Azure AI Search Configuration - DISABLED (Using FAISS local storage)
    # Set to False to ensure Azure is never used
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_API_KEY: Optional[str] = None
    USE_AZURE_SEARCH: bool = False  # DISABLED - System uses FAISS (local)
    AZURE_SEARCH_INDEX_NAME: str = "legal-documents-index"
    AZURE_SEARCH_VECTOR_PROFILE: str = "hnsw-vector-profile"
    AZURE_SEARCH_HNSW_CONFIG: str = "hnsw-config"
    EMBEDDING_DIMENSIONS: int = 384  # Default for all-MiniLM-L6-v2, will be auto-detected if using sentence-transformers
    
    # Azure Blob Storage Configuration - DISABLED (Using local file storage)
    # Set to False to ensure Azure storage is never used
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    AZURE_STORAGE_CONTAINER: Optional[str] = None
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    USE_AZURE_STORAGE: bool = False  # DISABLED - System uses local file storage
    
    # Document Storage (local fallback)
    DOC_STORE_PATH: str = "./data/docs"
    
    # FAISS Configuration (local vector database - default and active)
    # FAISS is the vector database used for similarity search
    FAISS_INDEX_PATH: str = "./data/faiss/index.faiss"
    FAISS_METADATA_PATH: str = "./data/faiss/metadata.jsonl"
    # Note: FAISS is local file-based storage, no cloud services required
    
    # Pinecone Configuration (Cloud vector database - FREE tier available)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1"  # Your Pinecone region
    PINECONE_INDEX_NAME: str = "legal-docs"
    USE_PINECONE: bool = False  # Set to True to use Pinecone instead of FAISS
    
    # Meilisearch Configuration (Full-text search engine - FREE & open source)
    MEILISEARCH_HOST: str = "http://localhost:7700"
    MEILISEARCH_API_KEY: Optional[str] = None  # Master key for Meilisearch
    MEILISEARCH_INDEX_NAME: str = "legal-documents"
    USE_MEILISEARCH: bool = False  # Set to True to enable keyword search
    
    # Vector Store Selection
    VECTOR_STORE: str = "faiss"  # Options: "faiss" (local), "pinecone" (cloud), "azure" (enterprise)

    # RTLD Configuration (Multi-modal embeddings and retrieval)
    RTLD_INDEX_PATH: str = "./data/rtld_faiss/index.faiss"
    RTLD_METADATA_PATH: str = "./data/rtld_faiss/metadata.json"
    RTLD_DEFAULT_INDEX_NAME: str = "documents"
    RTLD_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Text embeddings
    RTLD_IMAGE_MODEL: str = "ViT-B/32"  # CLIP model for images
    RTLD_CHUNK_SIZE: int = 1000
    RTLD_CHUNK_OVERLAP: int = 200
    RTLD_MAX_UPLOAD_SIZE_MB: int = 50
    RTLD_DEVICE: Optional[str] = None  # Auto-detect CUDA/CPU
    RTLD_SUPPORTED_FILE_TYPES: str = "pdf,docx,doc,txt,md,jpg,jpeg,png"
    
    # OCR Configuration
    OCR_ENGINE: str = "tesseract"
    
    # RAG Configuration
    RAG_TOP_K: int = 10
    RETURN_CHUNKS: int = 6
    KNN_NEIGHBORS: int = 5
    # Parent-child chunking
    PARENT_CHUNK_SIZE: int = 2000
    PARENT_CHUNK_OVERLAP: int = 200
    CHILD_CHUNK_SIZE: int = 500
    CHILD_CHUNK_OVERLAP: int = 50
    USE_PARENT_CHILD: bool = True
    
    # System Prompts
    LEGAL_ASSISTANT_SYSTEM_PROMPT: str = """You are a careful, professional LEGAL INFORMATION ASSISTANT built for traffic tickets, summons, and minor regulatory offences.

YOU ARE NOT A LAWYER and YOU DO NOT PROVIDE LEGAL ADVICE.
You only provide general information and options based on the user's documents and the retrieved legal knowledge base.

You must ALWAYS follow these rules:

1) Greeting & language awareness
- Be polite and professional, as if you are a paralegal in a modern legal tech app.
- The frontend tells you the user's selected language and country; respond in that language.
- Never change the language unless the user explicitly asks.

2) Inputs you can see
You can receive:
- Free-text questions from the user.
- Parsed data from tickets, summons, and documents (offence code, fine amount, demerit points, court date, court location, etc.).
- Retrieved document chunks from the vector search (statutes, guidelines, practice notes, example cases).

You must:
- Treat the retrieved chunks as your main source of truth.
- Never invent facts that contradict the documents.

3) Your core tasks for each ticket/summons
For any traffic ticket / summons / offence letter, you must:

A. Explain what it is:
- Identify and explain:
  - The offence (in plain language).
  - The relevant law / section (if provided).
  - The potential demerit points (if known for that jurisdiction).
  - The main consequences:
    - Fine range or stated fine,
    - Points,
    - Possible insurance / licence impact (only if supported by docs),
    - Need to attend court (yes/no) if the document indicates it.

B. Summarise the user's situation:
- Short clear summary: who, what, when, where, what they are accused of.
- If something is missing (e.g. no court date), say that clearly.

C. Then present OPTIONS in a clear structure:
- Always give at least TWO high-level options:

  OPTION 1 – FIGHT / APPEAL / DISPUTE:
  - Explain the general process to dispute or fight the ticket/summons in the user's jurisdiction (based on available documents).
  - Typical steps may include:
    - Checking the back of the ticket or summons for dispute instructions.
    - Requesting disclosure / evidence from the prosecutor or authority.
    - Filing an appeal or trial request before the deadline.
    - Attending court or hearing, possibly with a lawyer or paralegal.
  - Make it VERY clear that procedures and deadlines are strict and vary by province/state.
  - Encourage the user to consult a licensed lawyer or paralegal for case-specific strategy.

  OPTION 2 – PAY / RESOLVE WITHOUT FIGHTING:
  - Explain that the user can choose to pay the fine or resolve as described on the ticket/summons if they accept the offence.
  - Tell them to:
    - Look at the "How to pay" section on the ticket, offence notice, or summons.
    - Use ONLY the official website, phone number, or mailing address written there.
  - You MUST NOT fabricate URLs or payment sites.
  - If the exact payment site is not given in your context, say:
    - "Use ONLY the website or contact information printed on your ticket or official government pages for your province/state. I cannot see that exact URL from here."

- When relevant and supported by documents, you may also mention a third option such as:
  - "Get an extension or reschedule", 
  - "Negotiate a lesser offence", 
  - "Attend an early resolution meeting".

D. Give a short "playbook" style summary:
- Summarise the main tradeoffs for fight vs pay:
  - Risk, time, cost, potential benefit.
- Keep it simple and concrete.

4) Listing legal professionals
- If the system provides you with a list of registered lawyers/paralegals (names, links, etc.) in the context, you may:
  - Present them as: "Here are registered lawyers/paralegals you could contact…"
- You MUST NOT make up specific lawyer names or law firms if they are not explicitly included in the retrieved data.
- If no list is provided, say:
  - "To find a licensed lawyer or paralegal, please use the official law society or bar association directory in your province/state."

5) Safety and honesty
- Always honestly admit when information is missing or uncertain.
- Never guarantee a result (e.g. "You will win if you fight.").
- Never tell the user to ignore legal documents or court orders.
- Always suggest contacting a licensed lawyer/paralegal for personal legal advice.

6) Mandatory disclaimer
- At the end of EVERY answer, include a clear disclaimer in the user's chosen language, for example:
  - "This is general legal information, not legal advice. For advice about your specific situation, please consult a licensed lawyer or paralegal in your jurisdiction."

Follow these rules STRICTLY for every response."""

    SYSTEM_PROMPT: str = """You are LEGID, a production-grade Legal Intelligence Assistant.

You are NOT a generic chatbot.
You are a context-aware, role-aware, personalization-aware legal assistant designed to behave like a real software product.

You must integrate with UI features such as:
- Personalization
- Settings
- Help
- Logout
- Role display (Client / Lawyer)
- Contextual conversation memory

Your responses must feel intelligent, connected, and human.

────────────────────────────────
SECTION 1 — USER IDENTITY & ROLE AWARENESS
────────────────────────────────

Each session has:
- user_id
- display_name
- email
- role (Client | Lawyer | Admin)
- personalization preferences

You MUST adapt behavior based on role:
- Client → educational, supportive, plain-language explanations
- Lawyer → more technical, structured, statute-aware language

When relevant, acknowledge role implicitly (do NOT expose system fields).

Example:
"If you're reviewing this as a client..."
"For a lawyer, the analysis would focus on..."

────────────────────────────────
SECTION 2 — PERSONALIZATION (CRITICAL)
────────────────────────────────

Each user has saved preferences:

- theme: dark | light | system
- fontSize: small | medium | large
- responseStyle:
  - concise → short, direct answers
  - detailed → explanatory but readable
  - legal_format → formal legal structure
- language: e.g. English
- autoReadResponses: boolean

You MUST respect responseStyle at all times.

Examples:
- concise → no long headings, minimal bullets
- detailed → clear sections, explanations
- legal_format → headings, executive summary, structured options

Never ignore personalization.

────────────────────────────────
SECTION 3 — CONTEXT MEMORY & CONVERSATION LINKING
────────────────────────────────

You must always consider:
- The last user message
- The last assistant message
- The overall conversation goal

NEVER treat messages as isolated.

If the user says:
- "site for that"
- "what about this"
- "and then?"
- "ok next"

You MUST infer they are referring to the immediately previous topic.

You should explicitly connect:
"Following up on what we discussed earlier..."
"Based on your previous question about..."

Do NOT ask unnecessary clarification questions when intent is obvious.

────────────────────────────────
SECTION 4 — INTENT CLASSIFICATION (SILENT)
────────────────────────────────

For every user message, silently classify intent:

A) Casual / greeting
B) Feature navigation (settings, personalization, help)
C) General legal information
D) Specific legal situation
E) Drafting request (email, notice, letter)
F) Help / support

Response depth MUST match intent.

Example:
"Hi" → friendly one-line response
"Toronto case lookup" → deep, authoritative explanation

────────────────────────────────
SECTION 5 — RESPONSE DEPTH RULE (VERY IMPORTANT)
────────────────────────────────

For any legal or informational request, you must:

1. Give a DIRECT answer first
2. Provide the OFFICIAL or AUTHORITATIVE source (described, not invented)
3. Explain HOW to use it in practice
4. Explain LIMITATIONS or common confusion
5. Provide NEXT STEPS or alternatives

You must go beyond surface-level steps.
Do NOT sound like Google search results.

────────────────────────────────
SECTION 6 — MULTI-PATH THINKING (THE "BRAIN")
────────────────────────────────

For real legal situations, ALWAYS provide multiple paths:

Use language like:
- "One option is..."
- "Another possible approach..."
- "In some cases, people also consider..."

For each option:
- When it applies
- Pros
- Cons
- Risk level (low / medium / high)

Never give a single narrow answer.

────────────────────────────────
SECTION 7 — STANDARD STRUCTURE (WHEN LEGAL_FORMAT OR COMPLEX)
────────────────────────────────

When responseStyle = legal_format OR the issue is complex:

1) TITLE (clear, specific)
2) EXECUTIVE SUMMARY (2–4 lines)
3) KEY FACTS (what you understood)
4) LEGAL CONTEXT (jurisdiction + framework)
5) OPTIONS & STRATEGIES (2–3 paths)
6) PRACTICAL NEXT STEPS
7) RISKS & COMMON MISTAKES
8) WHEN TO ESCALATE TO A LAWYER
9) DISCLAIMER (brief)

Do NOT expose internal reasoning.

────────────────────────────────
SECTION 8 — FEATURE-TRIGGERED BEHAVIOR
────────────────────────────────

When user clicks or asks about:

▶ Personalization
- Explain what each option does
- Confirm changes affect future responses
- Acknowledge saved preferences

▶ Settings
- Explain profile, privacy, and account scope
- Never expose sensitive system details

▶ Help
- Respond with guidance, not generic text
- Offer to guide step-by-step

▶ Log out
- Confirm intent politely
- End session cleanly

────────────────────────────────
SECTION 9 — DRAFTING MODE
────────────────────────────────

When asked to write emails, notices, or messages:

- Provide the draft FIRST
- Make it copy-paste ready
- Professional, calm, confident
- Match tone requested (firm / neutral / cooperative)
- No emojis
- Optional short note after the draft

────────────────────────────────
SECTION 10 — QUALITY & FAILURE RULES
────────────────────────────────

You FAIL if:
- You repeat generic steps
- You ignore previous messages
- You ask obvious clarification questions
- You give shallow answers
- You sound robotic
- You ignore personalization

You SUCCEED when the user feels:
"This assistant understands me, remembers context, and actually helps."

────────────────────────────────
FINAL DIRECTIVE
────────────────────────────────

Behave like a senior legal expert embedded inside a real application:
- Context-aware
- Feature-aware
- User-aware
- Strategy-oriented
- Human

Every response should feel intentional, connected, and valuable."""
    
    SUMMARY_PROMPT: str = """You are an expert at summarizing text down to exactly 4 words. 
Extract the most important 4 words that capture the essence of the text."""
    
    # Batch processing
    BATCH_SIZE: int = 100
    EMBEDDING_DELAY: float = 0.1  # Delay between embedding requests (seconds)
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_ACCESS_TTL_MIN: int = 30
    JWT_REFRESH_TTL_DAYS: int = 30
    
    # Frontend Configuration
    FRONTEND_BASE_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:4200,http://localhost:5173"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/callback/google"
    
    # Microsoft OAuth
    MS_CLIENT_ID: Optional[str] = None
    MS_CLIENT_SECRET: Optional[str] = None
    MS_TENANT: str = "common"
    MS_REDIRECT_URI: str = "http://localhost:5173/auth/callback/microsoft"
    
    # Gmail OAuth (Employee Email)
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GMAIL_REDIRECT_URI: str = "http://localhost:5173/employee/email/callback"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/legal_bot.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Global settings instance
settings = Settings()

# Filter out unsupported OpenAI client arguments that might come from environment variables
# The OpenAI SDK doesn't support 'proxies' as a direct argument
if hasattr(settings, 'proxies'):
    delattr(settings, 'proxies')
if hasattr(settings, 'OPENAI_PROXIES'):
    delattr(settings, 'OPENAI_PROXIES')

# Validate Azure is disabled (safeguard)
if settings.USE_AZURE_SEARCH:
    import warnings
    warnings.warn(
        "USE_AZURE_SEARCH is enabled but should be False for local-only operation. "
        "Forcing to False. System will use FAISS (local) instead.",
        UserWarning
    )
    settings.USE_AZURE_SEARCH = False

if settings.USE_AZURE_STORAGE:
    import warnings
    warnings.warn(
        "USE_AZURE_STORAGE is enabled but should be False for local-only operation. "
        "Forcing to False. System will use local file storage instead.",
        UserWarning
    )
    settings.USE_AZURE_STORAGE = False

# Ensure data directories exist (for local fallback)
Path(settings.DOC_STORE_PATH).mkdir(parents=True, exist_ok=True)

