"""
Enterprise PII Redaction Tool - CLI Entry Point
==============================================
Usage:
    python main.py
    python main.py --input "Red Herring Prospectus.docx" --output "Redacted_Red_Herring_Prospectus.docx"
"""

import argparse
import os
import sys
from src.docx_processor import redact_full_docx

def main():
    parser = argparse.ArgumentParser(description="Enterprise PII Redaction Tool for Word Documents & Logs")
    parser.add_argument("--input", "-i", default="Red Herring Prospectus.docx", help="Path to input .docx document")
    parser.add_argument("--output", "-o", default="Redacted_Red_Herring_Prospectus.docx", help="Path to save redacted .docx document")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Seed for deterministic Faker replacements")

    args = parser.parse_args()

    input_file = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)

    if not os.path.exists(input_file):
        print(f"Error: Input document file not found at: {input_file}")
        sys.exit(1)

    print(f"==================================================")
    print(f"Enterprise PII Redaction Pipeline Started")
    print(f"Input Document : {os.path.basename(input_file)}")
    print(f"Output Target  : {os.path.basename(output_file)}")
    print(f"==================================================")

    print("Step 1: Redacting Text Content across document...")
    print("Step 2: Redacting Embedded Media Images inside archive...")

    text_redactions, media_redactions = redact_full_docx(input_file, output_file, seed=args.seed)

    print("\n--------------------------------------------------")
    print(f"Pipeline Completed Successfully!")
    print(f"- Text PII Entities Redacted : {text_redactions}")
    print(f"- Embedded Media Images Modified: {media_redactions}")
    print(f"- Redacted Output Saved To   : {output_file}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
