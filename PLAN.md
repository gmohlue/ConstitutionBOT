# ConstitutionBOT Implementation Plan

## Overview
A Civic Education Assistant for the South African Constitution (1996) with:
- **Twitter/X Bot**: Automated content generation for posting
- **Admin Dashboard (Web App)**: Your control center to review, edit, approve content before posting

**Key Workflow**: Bot generates content → Queue → You review/approve → Posts to Twitter

**Tech Stack**: Python, FastAPI, Tweepy, Anthropic SDK (Claude API), SQLite, HTMX + Tailwind CSS

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADMIN DASHBOARD (Web App)                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Content Queue │  │ Reply Queue  │  │ Constitution Upload  │  │
│  │ - Review      │  │ - @mentions  │  │ - PDF/TXT upload     │  │
│  │ - Edit        │  │ - Draft reply│  │ - Parse & index      │  │
│  │ - Approve     │  │ - Approve    │  │ - View sections      │  │
│  │ - Reject      │  │ - Reject     │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Suggestions  │  │ Posted Log   │  │ Bot Settings         │  │
│  │ - Request    │  │ - History    │  │ - Posting schedule   │  │
│  │   topics     │  │ - Analytics  │  │ - Auto-generate      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CORE ENGINE (Backend)                        │
├─────────────────────────────────────────────────────────────────┤
│  Claude API + System Prompt → Content Generator → Format Handler │
│  Constitution Retriever ← Parsed Constitution Data               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TWITTER BOT (Tweepy)                         │
├─────────────────────────────────────────────────────────────────┤
│  - Posts approved content from queue                             │
│  - Monitors @mentions → sends to Reply Queue                     │
│  - Posts approved replies                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
ConstitutionBOT/
├── pyproject.toml
├── .env.example
├── src/constitutionbot/
│   ├── config.py                      # Pydantic settings
│   │
│   ├── core/                          # Shared business logic
│   │   ├── claude_client.py           # Anthropic SDK wrapper
│   │   ├── constitution/
│   │   │   ├── loader.py              # Parse PDF/TXT constitution
│   │   │   ├── retriever.py           # Section lookup
│   │   │   └── models.py              # Section/Chapter models
│   │   ├── content/
│   │   │   ├── generator.py           # Main content orchestrator
│   │   │   ├── formats.py             # Tweet/Thread/Script formatters
│   │   │   ├── validators.py          # Citation & length validation
│   │   │   └── templates.py           # Prompt builder
│   │   ├── modes/
│   │   │   ├── bot_proposed.py        # Mode 1: Suggest topics
│   │   │   ├── user_provided.py       # Mode 2: User requests
│   │   │   └── historical.py          # Mode 3: Event analysis
│   │   └── safety/
│   │       ├── filters.py             # Content filtering
│   │       ├── escalation.py          # Legal advice detection
│   │       └── disclaimers.py         # Disclaimer injection
│   │
│   ├── database/                      # Data persistence
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── database.py                # DB connection
│   │   └── repositories/
│   │       ├── content_queue.py       # Content queue CRUD
│   │       ├── reply_queue.py         # Reply queue CRUD
│   │       └── post_history.py        # Posted content log
│   │
│   ├── twitter/                       # Twitter integration
│   │   ├── client.py                  # Tweepy v2 wrapper
│   │   ├── bot.py                     # Bot runner
│   │   └── handlers/
│   │       ├── mentions.py            # Monitor @mentions
│   │       └── poster.py              # Post approved content
│   │
│   ├── dashboard/                     # Admin Dashboard (FastAPI)
│   │   ├── app.py                     # FastAPI application
│   │   ├── auth.py                    # Simple auth (protect dashboard)
│   │   ├── routers/
│   │   │   ├── content_queue.py       # /api/queue/* endpoints
│   │   │   ├── reply_queue.py         # /api/replies/* endpoints
│   │   │   ├── constitution.py        # /api/constitution/* (upload)
│   │   │   ├── suggestions.py         # /api/suggestions/*
│   │   │   ├── history.py             # /api/history/*
│   │   │   └── settings.py            # /api/settings/*
│   │   ├── schemas/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── templates/                 # Jinja2 templates with HTMX
│   │   │   ├── base.html              # Base layout with Tailwind
│   │   │   ├── dashboard.html         # Main dashboard
│   │   │   ├── queue.html             # Content queue view
│   │   │   ├── replies.html           # Reply queue view
│   │   │   ├── constitution.html      # Upload & browse sections
│   │   │   ├── history.html           # Post history
│   │   │   └── partials/              # HTMX partial templates
│   │   │       ├── queue_item.html
│   │   │       ├── reply_item.html
│   │   │       └── toast.html
│   │   └── static/
│   │       └── css/
│   │           └── tailwind.css       # Compiled Tailwind
│   │
│   └── cli/
│       └── main.py                    # CLI: start dashboard, start bot
│
├── data/
│   ├── constitution/
│   │   ├── uploads/                   # User-uploaded files
│   │   └── processed/                 # Parsed JSON
│   ├── prompts/
│   │   └── system_prompts/
│   └── database/
│       └── constitutionbot.db         # SQLite database
│
└── tests/
```

---

## Database Schema

```sql
-- Content Queue (posts waiting for approval)
CREATE TABLE content_queue (
    id INTEGER PRIMARY KEY,
    content_type TEXT,          -- 'tweet', 'thread', 'script'
    raw_content TEXT,           -- Generated content
    formatted_content TEXT,     -- Twitter-ready content
    mode TEXT,                  -- 'bot_proposed', 'user_provided', 'historical'
    topic TEXT,                 -- Topic/subject
    citations JSON,             -- Referenced sections
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'posted'
    admin_notes TEXT,           -- Your notes/edits
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Reply Queue (replies to @mentions)
CREATE TABLE reply_queue (
    id INTEGER PRIMARY KEY,
    mention_id TEXT,            -- Twitter mention ID
    mention_text TEXT,          -- What they asked
    mention_author TEXT,        -- Who asked
    draft_reply TEXT,           -- AI-generated reply
    final_reply TEXT,           -- Your edited version
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'posted'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Post History (what's been posted)
CREATE TABLE post_history (
    id INTEGER PRIMARY KEY,
    tweet_id TEXT,              -- Twitter post ID
    content TEXT,
    content_type TEXT,
    posted_at TIMESTAMP,
    engagement JSON             -- likes, retweets, replies (optional)
);

-- Constitution Sections (parsed document)
CREATE TABLE constitution_sections (
    id INTEGER PRIMARY KEY,
    chapter_num INTEGER,
    chapter_title TEXT,
    section_num INTEGER,
    section_title TEXT,
    content TEXT,
    subsections JSON
);
```

---

## Implementation Phases

### Phase 1: Foundation
1. Initialize project with `pyproject.toml`
2. Create config management (`config.py`)
3. Set up SQLite database with SQLAlchemy models
4. Implement Constitution loader (PDF + TXT parsing with PyMuPDF)
5. Build section retriever

### Phase 2: Core Content Engine
6. Implement Claude client wrapper
7. Build prompt template system with your system prompt
8. Create content generator with three modes
9. Implement format handlers (Tweet, Thread, Script)
10. Add safety filters and validators

### Phase 3: Admin Dashboard Backend
11. Create FastAPI app with auth
12. Build Content Queue API:
    - `GET /api/queue` - List pending content
    - `GET /api/queue/{id}` - View single item
    - `PATCH /api/queue/{id}` - Edit content
    - `POST /api/queue/{id}/approve` - Approve for posting
    - `POST /api/queue/{id}/reject` - Reject content
13. Build Reply Queue API (same pattern)
14. Build Constitution Upload API:
    - `POST /api/constitution/upload` - Upload PDF/TXT
    - `GET /api/constitution/sections` - Browse sections
15. Build Suggestions API:
    - `POST /api/suggestions/generate` - Request new topic

### Phase 4: Admin Dashboard Frontend (HTMX + Tailwind)
16. Set up Tailwind CSS build pipeline
17. Create base template with navigation and layout
18. Build dashboard pages with HTMX interactivity:
    - Content queue: inline edit, approve/reject buttons with instant feedback
    - Reply queue: same pattern
    - Constitution upload with drag-and-drop
    - Topic suggestion with live generation
    - Post history with pagination

### Phase 5: Twitter Bot Integration
19. Implement Twitter client with Tweepy
20. Build mention monitor (polls for @mentions → adds to reply queue)
21. Build poster service (posts approved content from queue)
22. Add scheduler for periodic content generation

### Phase 6: Testing & Polish
23. Unit tests for core components
24. Integration tests for API endpoints
25. End-to-end workflow tests

---

## Dashboard API Endpoints

### Content Queue
```
GET    /api/queue                    # List pending content
GET    /api/queue/{id}               # Get single item
PATCH  /api/queue/{id}               # Edit content
POST   /api/queue/{id}/approve       # Approve → moves to posting
POST   /api/queue/{id}/reject        # Reject with reason
DELETE /api/queue/{id}               # Delete item
```

### Reply Queue
```
GET    /api/replies                  # List pending replies
GET    /api/replies/{id}             # Get single reply
PATCH  /api/replies/{id}             # Edit reply
POST   /api/replies/{id}/approve     # Approve → posts reply
POST   /api/replies/{id}/reject      # Reject
```

### Constitution Management
```
POST   /api/constitution/upload      # Upload PDF/TXT file
GET    /api/constitution/sections    # List all sections
GET    /api/constitution/sections/{num}  # Get specific section
DELETE /api/constitution             # Clear and re-upload
```

### Suggestions & Generation
```
POST   /api/generate/topic           # Bot suggests a topic
POST   /api/generate/content         # Generate content for topic
POST   /api/generate/reply           # Regenerate a reply draft
```

### History & Settings
```
GET    /api/history                  # Posted content history
GET    /api/settings                 # Bot settings
PATCH  /api/settings                 # Update settings
```

---

## Key Dependencies

```
# Core
anthropic>=0.76.0              # Claude API
pydantic>=2.6.0                # Data validation
pydantic-settings>=2.1.0       # Settings management
python-dotenv>=1.0.0           # Environment variables

# Web/Dashboard
fastapi>=0.109.0               # Web framework
uvicorn[standard]>=0.27.0      # ASGI server
python-multipart>=0.0.6        # File uploads
jinja2>=3.1.0                  # Jinja2 templates
# HTMX via CDN (no Python package needed)
# Tailwind CSS via standalone CLI or Node

# Database
sqlalchemy>=2.0.0              # ORM
aiosqlite>=0.19.0              # Async SQLite

# Twitter
tweepy>=4.14.0                 # Twitter API v2

# Document Processing
pymupdf>=1.23.0                # PDF text extraction

# Scheduling
apscheduler>=3.10.0            # Task scheduling
```

### Frontend (CDN/CLI tools)
- **HTMX**: `<script src="https://unpkg.com/htmx.org@2.0.0"></script>` (loaded in base template)
- **Tailwind CSS**: Use standalone CLI (`tailwindcss`) or Node package

---

## Critical Files (Implement First)

1. **`src/constitutionbot/config.py`** - Settings for all API keys
2. **`src/constitutionbot/database/models.py`** - SQLAlchemy models for queues
3. **`src/constitutionbot/core/constitution/loader.py`** - PDF/TXT parsing
4. **`src/constitutionbot/core/content/generator.py`** - Content generation
5. **`src/constitutionbot/dashboard/app.py`** - FastAPI dashboard

---

## User Workflow Example

1. **Upload Constitution**: Go to dashboard → Upload → Select PDF or TXT → System parses and indexes sections

2. **Generate Content**:
   - Click "Generate Topic" → Bot proposes topic using Mode 1
   - Or enter your own topic → Bot generates content using Mode 2
   - Content appears in queue as "pending"

3. **Review & Approve**:
   - View content in queue
   - Edit if needed (fix wording, add hashtags)
   - Click "Approve" → Content scheduled for posting
   - Or "Reject" with notes for regeneration

4. **Handle Replies**:
   - Bot monitors @mentions automatically
   - New mentions appear in Reply Queue with draft responses
   - Review, edit, approve → Bot posts reply

5. **View History**: See all posted content, engagement stats

---

## Verification Plan

1. **Upload Test**: Upload Constitution PDF → verify sections parsed correctly
2. **Generation Test**: Request topic → verify Claude generates appropriate content with citations
3. **Queue Test**: Approve content → verify it appears in "ready to post" state
4. **Twitter Test**: Connect Twitter credentials → verify posting works
5. **Reply Test**: Simulate @mention → verify reply draft generated and approval workflow

---

## Required Inputs

1. **Anthropic API Key** - For Claude API access
2. **Twitter API Credentials** (when ready):
   - API Key & Secret
   - Access Token & Secret
   - Bearer Token
3. **Constitution Document** - PDF or TXT file (uploaded via dashboard)
