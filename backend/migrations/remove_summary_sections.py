#!/usr/bin/env python3
"""
Migration: Remove specific sections from existing testimony summaries

This script will:
1. Fetch testimonies that have a 'summary' field.
2. For each summary, remove the "**Resumen:**" prefix.
3. Then, find and remove the "**Etiquetas doctrinales:**" section and all subsequent text.
4. Update the testimonies with the modified summaries.

Usage:
    python remove_summary_sections.py [--dry-run]
"""

import argparse
import os
import sys
import traceback
from typing import Any, Dict, List

# Add the src directory to the Python path
# This assumes the script is in backend/migrations/ and src is backend/src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from app.crud import update_testimony
    from app.deps import get_supabase
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the 'backend/migrations' directory")
    print("or that the 'backend/src' directory is correctly added to PYTHONPATH.")
    print("Current sys.path:", sys.path)
    sys.exit(1)


def get_testimonies_with_summaries(supabase, dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Get testimonies that have non-empty summaries.
    For dry run, if supabase client is None, returns sample data.
    """
    if dry_run and supabase is None:
        print("   [DRY RUN] Using sample data as Supabase connection is not available or failed.")
        return [
            {
                "id": 1,
                "summary": "**Resumen:** Este es un resumen de prueba. **Etiquetas doctrinales:** #etiqueta1 #etiqueta2",
            },
            {
                "id": 2,
                "summary": "**Resumen:** Otro resumen sin etiquetas.",
            },
            {
                "id": 3,
                "summary": "Un resumen que no necesita cambios.",
            },
            {
                "id": 4,
                "summary": "**Etiquetas doctrinales:** #solaetiqueta #otra", # No "Resumen:"
            },
            {
                "id": 5,
                "summary": "**Resumen:** Mezclado con **Etiquetas doctrinales:** #dificil #caso Y más texto.",
            },
            {
                "id": 6,
                "summary": "", # Empty summary
            },
            {
                "id": 7,
                "summary": "**Resumen:** Solo resumen.", # No etiquetas
            },
            {
                 "id": 8, # Text before Resumen
                 "summary": "Texto normal antes. **Resumen:** Esto es raro. **Etiquetas doctrinales:** #raro",
            },
            {
                 "id": 9, # Only etiquetas
                 "summary": "**Etiquetas doctrinales:** #solitaria",
            },
            {
                "id": 10, # No markers
                "summary": "Plain old summary text here, nothing special.",
            }
        ]

    if supabase is None: # Covers both (not dry_run and supabase is None) which is an error, and (dry_run and supabase is None) which means sample data should have been returned.
        if not dry_run:
             print("❌ ERROR: Supabase client is None in non-dry_run mode. Cannot fetch real data.")
        # If dry_run and supabase is None, sample data was already returned.
        # If we reach here in dry_run, it means supabase was not None initially but became None, which is unexpected.
        # However, the primary path for dry_run with no supabase is handled above.
        return []

    try:
        # Select testimonies that have a summary field that is not null and not empty
        print("   Fetching real testimonies from Supabase...")
        result = (
            supabase.table("testimonies")
            .select("id, summary")
            .not_.is_("summary", "null")
            .not_.eq("summary", "")
            .execute()
        )

        if result.data:
            print(f"   Successfully fetched {len(result.data)} real testimonies.")
            return result.data
        print("   No real testimonies found or an issue with data retrieval.")
        return []
    except Exception as e:
        print(f"❌ ERROR fetching real testimonies with summaries: {e}")
        traceback.print_exc()
        return []


def modify_summary(original_summary: str) -> str:
    """
    Modifies the summary by removing specific sections.
    """
    if not original_summary:
        return ""

    modified_summary = original_summary

    # Remove "**Resumen:**"
    resumen_marker = "**Resumen:**"
    if resumen_marker in modified_summary:
        modified_summary = modified_summary.split(resumen_marker, 1)[-1].strip()

    # Remove "**Etiquetas doctrinales:**" and everything after it
    etiquetas_marker = "**Etiquetas doctrinales:**"
    if etiquetas_marker in modified_summary:
        modified_summary = modified_summary.split(etiquetas_marker, 1)[0].strip()

    return modified_summary.strip()


def update_testimony_summary(
    supabase, testimony_id: int, new_summary: str, dry_run: bool = False
) -> bool:
    """
    Update a testimony with its modified summary.
    """
    if dry_run:
        # In dry run, we don't actually update, just signify success
        return True

    try:
        update_testimony(supabase, testimony_id, {"summary": new_summary})
        return True
    except Exception as e:
        print(f"   ❌ ERROR updating testimony {testimony_id} in DB: {e}")
        traceback.print_exc()
        return False


def run_migration(dry_run: bool = False):
    """
    Main migration function.
    """
    mode_str = "DRY RUN" if dry_run else "LIVE"
    print(f"🚀 Starting migration: Remove sections from summaries ({mode_str})")
    print("=" * 60)

    # Initialize Supabase client
    supabase = None
    if not dry_run:  # Always try to connect if not in dry_run
        try:
            supabase = get_supabase()
            print("✅ Connected to Supabase for LIVE mode.")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase for LIVE mode: {e}")
            print("Make sure your environment variables are set correctly (SUPABASE_URL, SUPABASE_KEY).")
            return False
    else: # In dry_run mode
        try:
            # Try to connect, but don't fail the script if it doesn't work
            supabase = get_supabase()
            print("✅ Connected to Supabase for DRY RUN (optional).")
        except Exception as e:
            print(f"⚠️  Could not connect to Supabase for DRY RUN: {e}")
            print("   Proceeding with dry run as Supabase client is None.")
            supabase = None # Ensure supabase is None if connection failed

    # Get testimonies with summaries
    print("\n📋 Fetching testimonies with summaries...")
    testimonies = get_testimonies_with_summaries(supabase, dry_run=dry_run)

    if not testimonies:
        print("✅ No testimonies with summaries found to process. Migration complete!")
        return True

    print(f"📊 Found {len(testimonies)} testimonies with summaries to process.")

    # User confirmation for live mode
    if not dry_run:
        print("\n⚠️  You are in LIVE mode. This will modify the database.")
        response = (
            input(
                f"Are you sure you want to modify {len(testimonies)} summaries? (y/N): "
            )
            .strip()
            .lower()
        )
        if response not in ["y", "yes"]:
            print("Migration cancelled by user.")
            return True # Consider this a "successful" cancellation

    # Process each testimony
    processed_count = 0
    updated_count = 0
    error_count = 0
    no_change_count = 0

    for i, testimony in enumerate(testimonies, 1):
        testimony_id = testimony["id"]
        original_summary = testimony.get("summary", "")

        print(f"\n[{i}/{len(testimonies)}] Processing testimony ID: {testimony_id}")
        # print(f"   📄 Original Summary (first 100 chars): '{original_summary[:100]}...'")


        if not original_summary:
            print("   ⚠️  Original summary is empty or missing. Skipping.")
            no_change_count +=1
            processed_count +=1
            continue

        try:
            modified_summary = modify_summary(original_summary)
            processed_count += 1

            if original_summary == modified_summary:
                print("   ✅ Summary requires no changes.")
                no_change_count += 1
            else:
                print(f"   🔄 Original Summary (first 100 chars): '{original_summary[:100]}...'")
                print(f"   ✨ Modified Summary (first 100 chars): '{modified_summary[:100]}...'")

                if dry_run:
                    print(f"   [DRY RUN] Would update testimony {testimony_id} with the modified summary.")
                    updated_count +=1 # In dry-run, count as "would be updated"
                else:
                    if update_testimony_summary(supabase, testimony_id, modified_summary):
                        print(f"   💾 Successfully updated testimony {testimony_id} in the database.")
                        updated_count += 1
                    else:
                        print(f"   ❌ Failed to update testimony {testimony_id} in the database.")
                        error_count += 1

        except Exception as e:
            print(f"   ❌ ERROR processing testimony {testimony_id}: {e}")
            traceback.print_exc()
            error_count += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 MIGRATION SUMMARY ({mode_str})")
    print("=" * 60)
    print(f"Processed testimonies: {processed_count}")
    if dry_run:
        print(f"Would be updated:      {updated_count}")
    else:
        print(f"Successfully updated:  {updated_count}")
    print(f"Required no changes:   {no_change_count}")
    print(f"Errors:                {error_count}")
    print(f"Total testimonies checked: {len(testimonies)}")

    if error_count == 0:
        print("\n🎉 Migration completed successfully!")
        return True
    else:
        print("\n⚠️  Migration completed with some errors.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Remove specific sections from testimony summaries.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying the database.",
    )
    args = parser.parse_args()

    print("Migration: Remove specific sections from testimony summaries")

    if args.dry_run:
        print("\n🔍 Running in DRY RUN mode - no database changes will be made.")
    # Confirmation for live mode is handled in run_migration()

    success = run_migration(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
