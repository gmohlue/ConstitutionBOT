"""CLI entry point for Content Manager."""

import argparse
import asyncio
import sys


def run_dashboard(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the admin dashboard."""
    import uvicorn

    uvicorn.run(
        "contentmanager.dashboard.app:app",
        host=host,
        port=port,
        reload=reload,
    )


def run_bot():
    """Run the Twitter bot."""
    from contentmanager.twitter.bot import run_bot as _run_bot

    asyncio.run(_run_bot())


def init_database():
    """Initialize the database."""
    from contentmanager.database import init_db

    asyncio.run(init_db())
    print("Database initialized successfully")


def upload_document(file_path: str):
    """Upload and parse a document file."""
    import asyncio
    from pathlib import Path

    from contentmanager.core.document.loader import DocumentLoader
    from contentmanager.database import async_session_maker, init_db
    from contentmanager.database.repositories.document import DocumentRepository, DocumentSectionRepository

    async def _upload():
        await init_db()

        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            return

        # Derive name from filename
        doc_name = path.stem.replace("_", " ").replace("-", " ").title()
        short_name = doc_name[:50] if len(doc_name) > 50 else doc_name

        loader = DocumentLoader()
        print(f"Parsing {path.name}...")

        document = loader.parse_file(path, name=doc_name, short_name=short_name)
        loader.save_processed(document)

        print(f"Found {len(document.chapters)} chapters, {len(document.all_sections)} sections")

        async with async_session_maker() as session:
            # Create or get document record
            doc_repo = DocumentRepository(session)
            existing_doc = await doc_repo.get_by_short_name(short_name)
            if existing_doc:
                db_doc = existing_doc
            else:
                db_doc = await doc_repo.create(
                    name=doc_name,
                    short_name=short_name,
                    description=document.description,
                )
            await doc_repo.set_active(db_doc.id)

            # Clear and upload sections
            repo = DocumentSectionRepository(session, document_id=db_doc.id)
            await repo.clear_all(document_id=db_doc.id)

            records = loader.to_database_records(document, document_id=db_doc.id)
            await repo.bulk_create(records, document_id=db_doc.id)
            await session.commit()

        print("Document uploaded successfully")

    asyncio.run(_upload())


def generate_content(topic: str, content_type: str = "tweet"):
    """Generate content from the command line."""
    import asyncio

    from contentmanager.core.modes.user_provided import UserProvidedMode
    from contentmanager.database import async_session_maker, init_db
    from contentmanager.database.repositories.content_queue import ContentQueueRepository

    async def _generate():
        await init_db()

        async with async_session_maker() as session:
            mode = UserProvidedMode(session)

            if content_type == "thread":
                content = await mode.generate_thread(topic)
            else:
                content = await mode.generate_tweet(topic)

            print("\n--- Generated Content ---")
            print(f"Topic: {content.topic}")
            print(f"Type: {content.content_type}")
            print(f"\n{content.formatted_content}")

            if content.citations:
                print(f"\nCitations: {', '.join(f'Section {c['section_num']}' for c in content.citations)}")

            if content.validation:
                if content.validation.warnings:
                    print(f"\nWarnings: {', '.join(content.validation.warnings)}")

            # Add to queue
            repo = ContentQueueRepository(session)
            item = await repo.create(
                raw_content=content.raw_content,
                formatted_content=content.formatted_content,
                content_type=content.content_type,
                mode="user_provided",
                topic=content.topic,
                citations=content.citations,
            )
            await session.commit()

            print(f"\nAdded to queue (ID: {item.id})")

    asyncio.run(_generate())


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Content Manager - AI-powered content generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  contentmanager dashboard              Start the admin dashboard
  contentmanager bot                    Start the Twitter bot
  contentmanager init                   Initialize the database
  contentmanager upload document.pdf    Upload a document file
  contentmanager generate "Right to equality"  Generate content
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start the admin dashboard")
    dashboard_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    dashboard_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    dashboard_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Bot command
    subparsers.add_parser("bot", help="Start the Twitter bot")

    # Init command
    subparsers.add_parser("init", help="Initialize the database")

    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a document file")
    upload_parser.add_argument("file", help="Path to PDF or TXT file")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate content")
    generate_parser.add_argument("topic", help="Topic to generate content about")
    generate_parser.add_argument(
        "--type", choices=["tweet", "thread"], default="tweet", help="Content type"
    )

    args = parser.parse_args()

    if args.command == "dashboard":
        run_dashboard(host=args.host, port=args.port, reload=args.reload)
    elif args.command == "bot":
        run_bot()
    elif args.command == "init":
        init_database()
    elif args.command == "upload":
        upload_document(args.file)
    elif args.command == "generate":
        generate_content(args.topic, args.type)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
