#!/usr/bin/env python3
"""
Migration: Re-generate summaries for all testimonies with transcripts, overwriting existing summaries.

This script will:
1. Ensure a row exists in summary_prompts capturing today's prompt+model configuration
2. Find testimonies that have transcripts (any) and re-generate a summary
3. Overwrite testimonies.summary and set testimonies.summary_prompt_id accordingly

Usage:
  python backfill_resummaries_with_prompt.py [--dry-run]
"""

import argparse
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List

# Add the src directory to the Python path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from app.crud import get_or_create_summary_prompt, update_testimony
from app.deps import get_supabase
from app.tasks import (
    CURRENT_SUMMARY_PROMPT,
    SUMMARY_MAX_TOKENS,
    SUMMARY_MODEL,
    SUMMARY_PROMPT_VERSION,
    SUMMARY_TEMPERATURE,
    generate_summary,
)


def get_testimonies_with_transcripts_needing_update(supabase, current_prompt_id: int) -> List[Dict[str, Any]]:
    """Get testimonies that have a transcript and either no prompt id or a different one than current."""
    result = supabase.table("testimonies").select("id, transcript, summary_prompt_id").execute()
    testimonies: List[Dict[str, Any]] = []
    for row in result.data:
        transcript = (row.get("transcript") or "").strip()
        summary_prompt_id = row.get("summary_prompt_id")
        if transcript and summary_prompt_id != current_prompt_id:
            testimonies.append({"id": row["id"], "transcript": transcript})
    return testimonies


def main(dry_run: bool) -> bool:
    print(f"🚀 Starting migration: Backfill re-summaries (dry_run={dry_run})")
    print("=" * 60)

    # Initialize Supabase client
    try:
        supabase = get_supabase()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

    # Ensure prompt row exists
    version = SUMMARY_PROMPT_VERSION
    try:
        prompt_id = get_or_create_summary_prompt(
            supabase,
            name="summary",
            version=version,
            prompt_template=CURRENT_SUMMARY_PROMPT,
            model_name=SUMMARY_MODEL,
            temperature=SUMMARY_TEMPERATURE,
            max_tokens=SUMMARY_MAX_TOKENS,
        )
        print(f"📝 Using summary_prompt_id={prompt_id} (version={version})")
    except Exception as e:
        print(f"❌ Failed to ensure summary prompt row: {e}")
        traceback.print_exc()
        return False

    # Fetch testimonies to process
    print("\n📋 Finding testimonies with transcripts needing update (different or missing prompt id)...")
    testimonies = get_testimonies_with_transcripts_needing_update(supabase, prompt_id)
    print(f"📊 Found {len(testimonies)} testimonies to re-summarize")

    if len(testimonies) == 0:
        print("✅ Nothing to do. Migration complete!")
        return True

    success = 0
    errors = 0
    for i, t in enumerate(testimonies, 1):
        tid = t["id"]
        transcript = t["transcript"]
        print(f"\n[{i}/{len(testimonies)}] Testimony ID: {tid}")
        print(f"   📝 Transcript length: {len(transcript)}")
        try:
            if dry_run:
                preview = generate_summary(transcript)
                print(f"   🔎 Preview (first 160): {preview[:160]}")
                success += 1
            else:
                summary = generate_summary(transcript)
                if not summary:
                    print("   ⚠️ Empty summary, skipping update")
                    errors += 1
                    continue
                update_testimony(
                    supabase,
                    tid,
                    {"summary": summary, "summary_prompt_id": prompt_id, "updated_at": datetime.utcnow().isoformat()},
                )
                print(f"   💾 Updated testimony {tid}")
                success += 1
        except Exception as e:
            print(f"   ❌ ERROR processing testimony {tid}: {e}")
            traceback.print_exc()
            errors += 1

    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {success}")
    print(f"❌ Errors: {errors}")
    print(f"📈 Total testimonies: {len(testimonies)}")
    return errors == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill re-summaries with prompt tracking")
    parser.add_argument("--dry-run", action="store_true", help="Generate summaries but do not write to DB")
    args = parser.parse_args()

    ok = main(dry_run=args.dry_run)
    sys.exit(0 if ok else 1)
