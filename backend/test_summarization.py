#!/usr/bin/env python3
"""
Test script for evaluating the testimony summarization function.

This script allows you to test the generate_summary function from tasks.py
with various transcript examples before using it in production.

Usage:
    python test_summarization.py
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path to import from tasks
sys.path.append(str(Path(__file__).parent / "src"))

from app.tasks import generate_summary

# Test transcripts - replace these with real examples
TEST_TRANSCRIPTS = {
    "dummy_healing": """
    Hermanos, quiero dar testimonio de cómo el Señor me sanó. Hace tres meses estaba muy enfermo,
    los doctores no sabían qué hacer conmigo. Tenía dolores terribles en todo el cuerpo y no podía
    caminar bien. Un día en la iglesia, durante la oración, el hermano pastor me dijo una palabra
    del Señor: "Hijo mío, yo soy tu sanador, confía en mí y verás mi gloria". Esa misma noche
    comencé a sentir mejoría. Día tras día el Señor me fue sanando completamente. Hoy estoy aquí
    sano y fuerte, dando testimonio de su poder. Gloria a Dios por su fidelidad. El Señor cumple
    sus promesas hermanos. Como dice en Isaías 53:5, "por sus llagas fuimos nosotros curados".
    """,
    "dummy_provision": """
    Buenos días hermanos. Vengo a dar testimonio de la provisión del Señor. Estaba pasando por
    una situación económica muy difícil, no tenía trabajo y las deudas se acumulaban. Mi familia
    estaba preocupada. Durante una vigilia, el Señor me habló y me dijo: "No temas, yo soy tu
    proveedor, confía en mí". A la semana siguiente recibí una llamada inesperada para un trabajo
    mejor del que tenía antes. El sueldo era exactamente lo que necesitaba para cubrir todas mis
    necesidades. El Señor nunca nos abandona hermanos. Él conoce nuestras necesidades antes que
    se las pidamos. Como dice en Filipenses 4:19, "Mi Dios, pues, suplirá todo lo que os falta".
    """,
    "dummy_family_restoration": """
    Quiero compartir con ustedes hermanos cómo el Señor restauró mi matrimonio. Mi esposo y yo
    estábamos al borde del divorcio, ya no nos hablábamos, había mucha amargura entre nosotros.
    Durante un culto especial, la hermana profetisa me dio una palabra: "Hija, el Señor va a
    restaurar tu hogar, lo que parecía perdido será recuperado". Yo lloré mucho esa noche y le
    pedí al Señor que obrara en nuestro matrimonio. Poco a poco comenzamos a hablar, a perdonarnos.
    El Señor cambió nuestros corazones. Hoy después de seis meses estamos más unidos que nunca.
    Dios restaura lo que está quebrado hermanos. Nunca perdamos la fe en su poder.
    """,
    "empty_transcript": "",
    "short_transcript": "Gloria a Dios hermanos, el Señor me bendijo mucho esta semana.",
}


def test_summarization():
    """Test the summarization function with various transcript examples."""
    print("=== TESTIMONY SUMMARIZATION EVALUATION ===\n")

    # Check if OpenAI client is properly initialized
    try:
        from app.tasks import openai_client

        if openai_client is None:
            print("❌ ERROR: OpenAI client is not initialized.")
            print("Make sure your OPENAI_API_KEY environment variable is set.")
            return False
        else:
            print("✅ OpenAI client is properly initialized.\n")
    except Exception as e:
        print(f"❌ ERROR importing OpenAI client: {e}")
        return False

    # Test each transcript
    for test_name, transcript in TEST_TRANSCRIPTS.items():
        print(f"🔍 Testing: {test_name}")
        print("-" * 50)

        if transcript.strip():
            print(f"📝 Input transcript ({len(transcript)} chars):")
            print(f"   {transcript.strip()[:100]}{'...' if len(transcript) > 100 else ''}")
        else:
            print("📝 Input transcript: (empty)")

        print("\n⏳ Generating summary...")

        try:
            summary = generate_summary(transcript)

            if summary:
                print(f"✅ Summary generated ({len(summary)} chars):")
                print("📋 RESULT:")
                print("-" * 30)
                print(summary)
                print("-" * 30)
            else:
                print("⚠️  Empty summary returned")

        except Exception as e:
            print(f"❌ ERROR generating summary: {e}")

        print("\n" + "=" * 70 + "\n")

    return True


def test_custom_transcript():
    """Allow testing with a custom transcript input."""
    print("🔧 CUSTOM TRANSCRIPT TEST")
    print("-" * 30)
    print("Choose input method:")
    print("1. Paste directly (for shorter texts)")
    print("2. Read from temporary file (for large texts)")
    print("3. Multi-line input with Ctrl+D to finish (Unix/Mac)")

    choice = input("\nEnter your choice (1-3): ").strip()
    custom_transcript = ""

    if choice == "1":
        print("\nPaste your transcript below (press Enter twice to finish):")
        lines = []
        empty_line_count = 0

        while True:
            try:
                line = input()
                if line.strip() == "":
                    empty_line_count += 1
                    # Break if we get two consecutive empty lines, or one empty line after content
                    if empty_line_count >= 2 or (empty_line_count >= 1 and lines):
                        break
                    lines.append(line)
                else:
                    empty_line_count = 0
                    lines.append(line)
            except KeyboardInterrupt:
                print("\n❌ Test cancelled.")
                return

        # Remove trailing empty lines
        while lines and lines[-1].strip() == "":
            lines.pop()

        custom_transcript = "\n".join(lines)

    elif choice == "2":
        import os

        # Get the current working directory and script directory
        current_dir = os.getcwd()
        script_dir = os.path.dirname(os.path.abspath(__file__))

        temp_file = "temp_transcript.txt"
        temp_file_path = os.path.join(script_dir, temp_file)

        print("\n📄 Instructions for large text input:")
        print("1. Copy your testimony to clipboard")
        print(f"2. Create a file called '{temp_file}' in one of these locations:")
        print(f"   📁 Script directory: {script_dir}")
        print(f"   📁 Current directory: {current_dir}")
        print("3. Paste your testimony into that file and save it")
        print("4. Press Enter here to continue")

        input("\nPress Enter when you've created the file...")

        # Try multiple possible locations for the file
        possible_paths = [
            temp_file_path,  # Same directory as script
            os.path.join(current_dir, temp_file),  # Current working directory
            temp_file,  # Relative to current directory
        ]

        custom_transcript = ""
        file_found = False

        for path in possible_paths:
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Filter out empty lines and strip whitespace
                    transcripts = [line.strip() for line in lines if line.strip()]

                    if not transcripts:
                        print(f"❌ File {path} is empty or contains no valid transcripts")
                        return

                    print(f"✅ Successfully read {len(transcripts)} transcript(s) from {path}")
                    print(f"📁 File kept at: {path} (you can add more examples to this file)")
                    file_found = True

                    # Process each transcript
                    for i, transcript in enumerate(transcripts, 1):
                        print(f"\n{'=' * 70}")
                        print(f"🔍 TRANSCRIPT {i}/{len(transcripts)}")
                        print(f"{'=' * 70}")
                        print(f"📝 Length: {len(transcript)} characters")

                        # Show preview of transcript
                        preview = transcript[:150] + "..." if len(transcript) > 150 else transcript
                        print(f"📄 Preview: {preview}")

                        print(f"\n⏳ Generating summary for transcript {i}...")

                        try:
                            summary = generate_summary(transcript)

                            if summary:
                                print(f"✅ Summary {i} generated ({len(summary)} chars):")
                                print("📋 RESULT:")
                                print("-" * 50)
                                print(summary)
                                print("-" * 50)
                            else:
                                print(f"⚠️  Empty summary returned for transcript {i}")

                        except Exception as e:
                            print(f"❌ ERROR generating summary for transcript {i}: {e}")

                        # Add a pause between transcripts for readability
                        if i < len(transcripts):
                            print(f"\n⏸️  Press Enter to continue to transcript {i + 1}...")
                            try:
                                input()
                            except KeyboardInterrupt:
                                print("\n❌ Testing cancelled.")
                                return

                    print(f"\n🎉 Completed processing all {len(transcripts)} transcript(s)!")
                    return  # Exit the function after processing

            except Exception:
                continue

        if not file_found:
            print(f"❌ File '{temp_file}' not found in any of these locations:")
            for path in possible_paths:
                print(f"   - {path}")
            print(f"\n💡 Current working directory: {current_dir}")
            print("💡 Please create the file in one of the above locations and try again.")
            return

    elif choice == "3":
        print("\nPaste or type your transcript below.")
        print("When finished, press Ctrl+D (Unix/Mac) or Ctrl+Z (Windows) on a new line:")
        print("-" * 50)

        lines = []
        try:
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    # This is expected when user presses Ctrl+D
                    break
                except KeyboardInterrupt:
                    print("\n❌ Test cancelled.")
                    return
        except Exception:
            pass

        custom_transcript = "\n".join(lines).strip()
        print(f"\n✅ Collected {len(custom_transcript)} characters")

    else:
        print("❌ Invalid choice.")
        return

    # For options 1 and 3, we still need the single transcript processing
    if choice in ["1", "3"] and custom_transcript:
        if not custom_transcript.strip():
            print("⚠️  No transcript provided.")
            return

        print(f"\n📝 Testing custom transcript ({len(custom_transcript)} chars)")

        # Show a preview of the transcript
        preview = custom_transcript[:200] + "..." if len(custom_transcript) > 200 else custom_transcript
        print(f"📄 Preview: {preview}")

        print("⏳ Generating summary...")

        try:
            summary = generate_summary(custom_transcript)

            if summary:
                print(f"✅ Summary generated ({len(summary)} chars):")
                print("📋 RESULT:")
                print("-" * 50)
                print(summary)
                print("-" * 50)
            else:
                print("⚠️  Empty summary returned")

        except Exception as e:
            print(f"❌ ERROR generating summary: {e}")


def main():
    """Main test runner."""
    print("TESTIMONY SUMMARIZATION TESTER")
    print("=" * 50)

    while True:
        print("\nChoose an option:")
        print("1. Run all predefined tests")
        print("2. Test with custom transcript")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            test_summarization()
        elif choice == "2":
            test_custom_transcript()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY environment variable not found.")
        print("Make sure to set it before running the tests.\n")

    main()
