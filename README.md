# ConstitutionBOT

Civic Education Assistant for the South African Constitution (1996).

## Features

- **Twitter/X Bot**: Automated educational content generation
- **Admin Dashboard**: Review, edit, and approve content before posting
- **AI-Powered**: Uses Claude API for intelligent content generation
- **Safety First**: Built-in content filters and legal advice detection

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your API keys

# Initialize database
constitutionbot init

# Start dashboard
constitutionbot dashboard
```

Visit http://127.0.0.1:8000 (default login: admin/admin)

## Commands

- `constitutionbot dashboard` - Start admin dashboard
- `constitutionbot bot` - Start Twitter bot
- `constitutionbot init` - Initialize database
- `constitutionbot upload <file>` - Upload constitution PDF/TXT
- `constitutionbot generate "<topic>"` - Generate content

## License

MIT
