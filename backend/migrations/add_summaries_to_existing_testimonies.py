#!/usr/bin/env python3
"""
Migration: Add summaries to existing testimonies with transcripts
This script will:
1. Find testimonies that have transcripts but no summaries
2. Generate summaries using the existing generate_summary function
3. Update the testimonies with the new summaries
"""

import os
import sys
import traceback
from typing import Any, Dict, List

# Add the src directory to the Python path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from app.crud import update_testimony
from app.deps import get_supabase
from app.tasks import generate_summary


def get_testimonies_needing_summaries(supabase) -> List[Dict[str, Any]]:
    """
    Get testimonies that have transcripts but no summaries.
    """
    try:
        result = supabase.table("testimonies").select("id, transcript, summary").execute()

        testimonies_needing_summaries = []
        for testimony in result.data:
            # Check if testimony has transcript but no summary
            if testimony.get("transcript") and testimony["transcript"].strip() and not testimony.get("summary"):
                testimonies_needing_summaries.append(testimony)

        return testimonies_needing_summaries
    except Exception as e:
        print(f"ERROR fetching testimonies: {e}")
        traceback.print_exc()
        return []


def update_testimony_with_summary(supabase, testimony_id: int, summary: str) -> bool:
    """
    Update a testimony with its generated summary.
    """
    try:
        update_testimony(supabase, testimony_id, {"summary": summary})
        return True
    except Exception as e:
        print(f"ERROR updating testimony {testimony_id}: {e}")
        traceback.print_exc()
        return False


def run_migration():
    """
    Main migration function.
    """
    print("🚀 Starting migration: Add summaries to existing testimonies")
    print("=" * 60)

    # Initialize Supabase client
    try:
        supabase = get_supabase()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

    # Get testimonies that need summaries
    print("\n📋 Finding testimonies that need summaries...")
    testimonies = get_testimonies_needing_summaries(supabase)

    if not testimonies:
        print("✅ No testimonies need summaries. Migration complete!")
        return True

    print(f"📊 Found {len(testimonies)} testimonies that need summaries")

    # Process each testimony
    success_count = 0
    error_count = 0

    for i, testimony in enumerate(testimonies, 1):
        testimony_id = testimony["id"]
        transcript = testimony["transcript"]

        print(f"\n[{i}/{len(testimonies)}] Processing testimony ID: {testimony_id}")
        print(f"   Transcript length: {len(transcript)} characters")

        try:
            # Generate summary
            print("   ⏳ Generating summary...")
            summary = generate_summary(transcript)

            if summary and summary.strip():
                # Update testimony with summary
                print(f"   ✅ Summary generated ({len(summary)} characters)")
                if update_testimony_with_summary(supabase, testimony_id, summary):
                    print(f"   💾 Successfully updated testimony {testimony_id}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to update testimony {testimony_id}")
                    error_count += 1
            else:
                print(f"   ⚠️  Empty summary generated for testimony {testimony_id}")
                error_count += 1

        except Exception as e:
            print(f"   ❌ ERROR processing testimony {testimony_id}: {e}")
            traceback.print_exc()
            error_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📈 Total testimonies: {len(testimonies)}")

    if error_count == 0:
        print("🎉 Migration completed successfully!")
        return True
    else:
        print("⚠️  Migration completed with some errors.")
        return False


if __name__ == "__main__":
    print("Migration: Add summaries to existing testimonies")
    print("This script will generate summaries for testimonies that have transcripts but no summaries.")

    # Confirm before running
    response = input("\nDo you want to proceed? (y/N): ").strip().lower()
    if response not in ["y", "yes"]:
        print("Migration cancelled.")
        sys.exit(0)

    success = run_migration()
    sys.exit(0 if success else 1)
