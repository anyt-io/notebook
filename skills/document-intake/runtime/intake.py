#!/usr/bin/env python3
"""CLI entry point for the document-intake skill.

Parses a domain-specific document and generates a structured question bank.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config import DEFAULT_OUTPUT_DIR
from document_parser import DocumentParser
from question_generator import QuestionGenerator


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Parse domain documents and generate structured question banks.",
    )
    parser.add_argument("--input", "-i", required=True, help="Path to the input document (PDF, txt, or md)")
    parser.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT_DIR), help="Output directory (default: output/)")
    parser.add_argument("--domain", "-d", default="general", help="Domain label for the question bank")
    args = parser.parse_args(argv)

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()

    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Parse the document
    doc_parser = DocumentParser()
    print(f"Parsing: {input_path}")
    parsed = doc_parser.parse_file(input_path)

    # Generate question bank
    generator = QuestionGenerator(domain=args.domain)
    bank = generator.generate_bank(parsed)

    # Write outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    parsed_out = output_dir / "parsed_document.json"
    # Exclude raw_text from the saved parsed document to keep it concise
    parsed_save = {k: v for k, v in parsed.items() if k != "raw_text"}
    parsed_out.write_text(json.dumps(parsed_save, indent=2, ensure_ascii=False), encoding="utf-8")

    bank_out = output_dir / "question_bank.json"
    bank_out.write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary
    print(f"\nSource:     {parsed['source_file']}")
    print(f"Domain:     {args.domain}")
    print(f"Sections:   {len(parsed['sections'])}")
    print(f"Key terms:  {len(parsed['key_terms'])}")
    print(f"Rules:      {len(parsed['rules'])}")
    print(f"Questions:  {bank['metadata']['total_questions']}")
    print("\nOutput:")
    print(f"  {parsed_out}")
    print(f"  {bank_out}")


if __name__ == "__main__":
    main()
