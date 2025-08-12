#!/usr/bin/env python3
"""
Migration: Add summaries to existing testimonies with transcripts

This script will:
1. Find testimonies that have transcripts but no summaries
2. Generate summaries using the existing generate_summary function
3. Update the testimonies with the new summaries

Usage:
    python add_summaries_migration.py [--dry-run]
"""

import argparse
import os
import sys
import traceback
from typing import Any, Dict, List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from app.crud import update_testimony
    from app.deps import get_supabase
    from app.tasks import generate_summary
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the backend directory")
    print("and that all dependencies are installed.")
    sys.exit(1)


def get_testimonies_needing_summaries(supabase) -> List[Dict[str, Any]]:
    """
    Get testimonies that have transcripts but no summaries.
    """
    try:
        result = supabase.table("testimonies").select("id, transcript, summary").execute()

        testimonies_needing_summaries = []
        for testimony in result.data:
            # Check if testimony has transcript but no summary
            if (
                testimony.get("transcript")
                and testimony["transcript"].strip()
                and (not testimony.get("summary") or not testimony["summary"].strip())
            ):
                testimonies_needing_summaries.append(testimony)

        return testimonies_needing_summaries
    except Exception as e:
        print(f"❌ ERROR fetching testimonies: {e}")
        traceback.print_exc()
        return []


def update_testimony_with_summary(supabase, testimony_id: int, summary: str, dry_run: bool = False) -> bool:
    """
    Update a testimony with its generated summary.
    """
    if dry_run:
        print(f"   [DRY RUN] Would update testimony {testimony_id} with summary")
        return True

    try:
        update_testimony(supabase, testimony_id, {"summary": summary})
        return True
    except Exception as e:
        print(f"   ❌ ERROR updating testimony {testimony_id}: {e}")
        traceback.print_exc()
        return False


def run_migration(dry_run: bool = False):
    """
    Main migration function.
    """
    mode_str = "DRY RUN" if dry_run else "LIVE"
    print(f"🚀 Starting migration: Add summaries to existing testimonies ({mode_str})")
    print("=" * 60)

    # Initialize Supabase client
    try:
        supabase = get_supabase()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("Make sure your environment variables are set correctly:")
        print("- SUPABASE_URL")
        print("- SUPABASE_KEY")
        return False

    # Get testimonies that need summaries
    print("\n📋 Finding testimonies that need summaries...")
    testimonies = get_testimonies_needing_summaries(supabase)

    if not testimonies:
        print("✅ No testimonies need summaries. Migration complete!")
        return True

    print(f"📊 Found {len(testimonies)} testimonies that need summaries")

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made to the database")
        print("Testimonies that would be processed:")
        for testimony in testimonies:
            transcript_preview = (
                testimony["transcript"][:100] + "..." if len(testimony["transcript"]) > 100 else testimony["transcript"]
            )
            print(f"  - ID {testimony['id']}: {len(testimony['transcript'])} chars - '{transcript_preview}'")

        response = (
            input(
                f"\nWould you like to proceed with generating summaries for these {len(testimonies)} testimonies? (y/N): "
            )
            .strip()
            .lower()
        )
        if response not in ["y", "yes"]:
            print("Migration cancelled.")
            return True

    # Process each testimony
    success_count = 0
    error_count = 0

    for i, testimony in enumerate(testimonies, 1):
        testimony_id = testimony["id"]
        transcript = testimony["transcript"]

        print(f"\n[{i}/{len(testimonies)}] Processing testimony ID: {testimony_id}")
        print(f"   📝 Transcript length: {len(transcript)} characters")

        try:
            # Generate summary
            print("   ⏳ Generating summary...")
            summary = generate_summary(transcript)

            if summary and summary.strip():
                # Update testimony with summary
                print(f"   ✅ Summary generated ({len(summary)} characters)")
                if not dry_run:
                    # Show preview of summary
                    summary_preview = summary[:150] + "..." if len(summary) > 150 else summary
                    print(f"   📄 Preview: {summary_preview}")

                if update_testimony_with_summary(supabase, testimony_id, summary, dry_run):
                    print(
                        f"   💾 {'[DRY RUN] Would update' if dry_run else 'Successfully updated'} testimony {testimony_id}"
                    )
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
    print(f"📊 MIGRATION SUMMARY ({mode_str})")
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


def main():
    parser = argparse.ArgumentParser(description="Add summaries to existing testimonies with transcripts")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be done without making changes")
    args = parser.parse_args()

    print("Migration: Add summaries to existing testimonies")
    print("This script will generate summaries for testimonies that have transcripts but no summaries.")

    if args.dry_run:
        print("\n🔍 Running in DRY RUN mode - no changes will be made")
    else:
        print("\n⚠️  This will make changes to your database!")
        # Confirm before running
        response = input("\nDo you want to proceed? (y/N): ").strip().lower()
        if response not in ["y", "yes"]:
            print("Migration cancelled.")
            return

    success = run_migration(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
