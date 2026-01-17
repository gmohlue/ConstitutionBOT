# Content Manager

AI-powered content generation and management system for civic education. Originally designed for the South African Constitution, now supports any document-based content generation.

## Features

- **Document-Based Content**: Upload PDFs/text files and generate educational content from them
- **Multi-Format Output**: Generate tweets, threads, and video scripts
- **Interactive Chat**: Conversational interface for exploring documents and generating content
- **Admin Dashboard**: Review, edit, approve, and schedule content before posting
- **Twitter/X Integration**: Automated posting with mention monitoring and reply management
- **AI-Powered**: Supports multiple LLM providers (Anthropic Claude, OpenAI, Ollama)
- **Safety First**: Built-in content filters and legal advice detection

## Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the dashboard
python -m contentmanager.dashboard
```

Visit http://127.0.0.1:8000

**Default credentials**: admin / admin (change in .env for production)

## Configuration

Create a `.env` file with the following options:

```env
# LLM Provider (anthropic, openai, ollama)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here

# Dashboard Settings
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your_secure_password
DASHBOARD_SECRET_KEY=your_secret_key
DASHBOARD_SECURE_COOKIES=false  # Set true for HTTPS

# Twitter/X API (optional)
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
TWITTER_BEARER_TOKEN=

# Bot Settings
BOT_ENABLED=false
AUTO_GENERATE_ENABLED=false
```

## CLI Commands

```bash
# Start admin dashboard
constitutionbot dashboard

# Start Twitter bot (requires Twitter credentials)
constitutionbot bot

# Initialize/reset database
constitutionbot init

# Upload a document
constitutionbot upload <file.pdf>

# Generate content from command line
constitutionbot generate "<topic>"
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/login` | Login page |
| POST | `/login` | Submit login credentials |
| GET | `/logout` | Log out current user |

### Content Queue
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/queue` | List content queue items |
| GET | `/api/queue/{id}` | Get specific item |
| PUT | `/api/queue/{id}` | Update item |
| POST | `/api/queue/{id}/approve` | Approve item |
| POST | `/api/queue/{id}/reject` | Reject item |
| DELETE | `/api/queue/{id}` | Delete item |

### Content Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/suggestions/generate` | Generate content |
| GET | `/api/suggestions/topics` | Get topic suggestions |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/conversations` | List conversations |
| POST | `/api/chat/conversations` | Create conversation |
| GET | `/api/chat/conversations/{id}` | Get conversation with messages |
| POST | `/api/chat/conversations/{id}/messages` | Send message |
| DELETE | `/api/chat/conversations/{id}` | Delete conversation |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents` | List documents |
| POST | `/api/documents/upload` | Upload document |
| GET | `/api/documents/sections` | Get document sections |
| GET | `/api/documents/search` | Search sections |

### Calendar & Scheduling
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar` | Get scheduled items |
| POST | `/api/calendar/schedule` | Schedule content |
| DELETE | `/api/calendar/{id}` | Unschedule item |

### History & Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/history` | Get post history |
| GET | `/api/history/stats` | Get posting statistics |
| GET | `/api/history/analytics` | Get engagement analytics |

### Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/queue/csv` | Export content queue to CSV |
| GET | `/api/export/queue/json` | Export content queue to JSON |
| GET | `/api/export/history/csv` | Export post history to CSV |
| GET | `/api/export/history/json` | Export post history to JSON |
| GET | `/api/export/conversations/json` | Export conversations to JSON |

### Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings` | Get current settings |
| GET | `/api/settings/credentials` | Get credential status |
| POST | `/api/settings/credentials` | Update credentials |
| GET | `/api/settings/llm` | Get LLM configuration |
| POST | `/api/settings/llm/test` | Test LLM connection |

## Project Structure

```
content-manager/
├── src/contentmanager/
│   ├── cli/                 # Command-line interface
│   ├── config.py            # Configuration management
│   ├── core/
│   │   ├── chat/            # Chat service
│   │   ├── content/         # Content generation & validation
│   │   ├── llm/             # LLM provider abstraction
│   │   └── modes/           # Generation modes
│   ├── dashboard/
│   │   ├── routers/         # API route handlers
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── templates/       # Jinja2 HTML templates
│   │   ├── app.py           # FastAPI application
│   │   ├── auth.py          # Authentication
│   │   └── csrf.py          # CSRF protection
│   ├── database/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── repositories/    # Data access layer
│   └── twitter/
│       ├── client.py        # Twitter API client
│       ├── bot.py           # Bot runner
│       └── handlers/        # Mention & posting handlers
├── tests/                   # Unit tests
├── e2e/                     # End-to-end tests (Playwright)
└── data/                    # Data directory (documents, database)
```

## Development

### Setup

```bash
# Clone and setup
git clone https://github.com/gmohlue/ConstitutionBOT.git
cd ConstitutionBOT
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Install Playwright for e2e tests
npm install
npx playwright install
```

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# End-to-end tests (requires running server)
npx playwright test

# Run specific browser
npx playwright test --project=chromium
```

### Code Quality

The project follows these practices:
- **Type hints**: Full typing throughout the codebase
- **Async/await**: Async database operations with SQLAlchemy 2.0
- **Pydantic v2**: Request/response validation
- **Security**: CSRF protection, secure cookies, input sanitization

## Security Notes

- Change default credentials before deploying
- Set `DASHBOARD_SECURE_COOKIES=true` when using HTTPS
- Set a strong `DASHBOARD_SECRET_KEY` - this is used to derive encryption keys for credential storage
- API credentials are encrypted using Fernet symmetric encryption with keys derived via PBKDF2
- Existing base64-encoded credentials are automatically migrated to encrypted format on access
- CSRF protection is enabled on the login form

## License

MIT
