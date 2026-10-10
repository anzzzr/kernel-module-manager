"""CLI interface for kernel-diagnostic-ai."""

import argparse
import json
import sys

from kernel_diagnostic_ai import __version__


def serve_command(args):
    """Start the FastAPI diagnostic server."""
    import uvicorn

    print(f"Starting Kernel Diagnostic AI Service on {args.host}:{args.port}...")
    uvicorn.run(
        "kernel_diagnostic_ai.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def rag_status_command(args):
    """Check the status of the local RAG documentation store."""
    from kernel_diagnostic_ai.config import get_config
    from kernel_diagnostic_ai.rag.documents import load_documents
    from kernel_diagnostic_ai.rag.store import get_collection, init_store

    cfg = get_config()
    docs_dir = cfg["docs_dir"]
    print(f"Docs Directory: {docs_dir}")

    docs = load_documents(docs_dir)
    print(f"Discovered Markdown Documents: {len(docs)}")
    for d in docs:
        print(f"  - {d['source']} ({d['title']}) [{len(d['text'])} chars]")

    init_store(cfg["chroma_persist_dir"])
    coll = get_collection()
    count = coll.count() if coll else 0
    print(f"ChromaDB Store: {cfg['chroma_persist_dir']}")
    print(f"Indexed Chunks: {count}")


def diagnose_command(args):
    """Run an AI diagnostic on a module using provided evidence or local telemetry."""
    import asyncio

    from kernel_diagnostic_ai.models import Evidence
    from kernel_diagnostic_ai.services.llm_client import call_llm
    from kernel_diagnostic_ai.services.rag_service import retrieve_context

    module = args.module
    commands = {}
    errors = {}

    if args.evidence_file:
        with open(args.evidence_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            commands = data.get("commands", {})
            errors = data.get("errors", {})
            module = data.get("module", module)
    else:
        # Minimal diagnostic payload
        commands = {"info": f"Manual CLI request for module {module}"}

    evidence = Evidence(module=module, commands=commands, errors=errors)
    print(f"Diagnosing module '{module}'...")

    async def _run():
        print("Retrieving technical documentation from RAG...")
        context, results = retrieve_context(evidence)
        print(f"Retrieved {len(results)} relevant documentation sections.")
        print("Consulting LLM reasoning engine...")
        diagnosis = await call_llm(evidence.model_dump_json(), context or None)
        print("\n=== AI DIAGNOSTIC REPORT ===")
        print(json.dumps(diagnosis, indent=2))

    try:
        asyncio.run(_run())
    except Exception as e:
        print(f"Diagnosis failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="kernel-ai",
        description="AI-Powered Linux Kernel Module Diagnostic Assistant & RAG Service",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI AI service")
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind server to (default: 0.0.0.0)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to listen on (default: 8001)",
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    serve_parser.set_defaults(func=serve_command)

    # rag-status command
    rag_parser = subparsers.add_parser(
        "rag-status",
        help="Inspect ChromaDB vector store and documentation corpus",
    )
    rag_parser.set_defaults(func=rag_status_command)

    # diagnose command
    diag_parser = subparsers.add_parser(
        "diagnose",
        help="Run diagnostic analysis on a kernel module",
    )
    diag_parser.add_argument(
        "--module",
        "-m",
        required=True,
        help="Name of kernel module (e.g. nvidia, loop, ext4)",
    )
    diag_parser.add_argument(
        "--evidence-file",
        "-f",
        help="Path to JSON file containing collected diagnostic evidence",
    )
    diag_parser.set_defaults(func=diagnose_command)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
