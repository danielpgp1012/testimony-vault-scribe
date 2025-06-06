#!/usr/bin/env python3
"""
Batch evaluation script for testimony summarization.

This script runs multiple test cases and saves the results for comparison and analysis.
Useful for testing changes to the summarization prompt or model.

Usage:
    python eval_summaries.py
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path to import from tasks
sys.path.append(str(Path(__file__).parent / "src"))

from app.tasks import generate_summary

# Test cases with expected characteristics
TEST_CASES = [
    {
        "name": "healing_testimony",
        "transcript": """
        Hermanos, quiero dar testimonio de cómo el Señor me sanó. Hace tres meses estaba muy enfermo,
        los doctores no sabían qué hacer conmigo. Tenía dolores terribles en todo el cuerpo y no podía
        caminar bien. Un día en la iglesia, durante la oración, el hermano pastor me dijo una palabra
        del Señor: "Hijo mío, yo soy tu sanador, confía en mí y verás mi gloria". Esa misma noche
        comencé a sentir mejoría. Día tras día el Señor me fue sanando completamente. Hoy estoy aquí
        sano y fuerte, dando testimonio de su poder. Gloria a Dios por su fidelidad. El Señor cumple
        sus promesas hermanos. Como dice en Isaías 53:5, "por sus llagas fuimos nosotros curados".
        """,
        "expected_tags": ["sanidad", "promesa_cumplida", "fe", "profecia"],
        "expected_elements": ["promesa recibida", "proceso de sanidad", "resultado positivo"],
    },
    {
        "name": "provision_testimony",
        "transcript": """
        Buenos días hermanos. Vengo a dar testimonio de la provisión del Señor. Estaba pasando por
        una situación económica muy difícil, no tenía trabajo y las deudas se acumulaban. Mi familia
        estaba preocupada. Durante una vigilia, el Señor me habló y me dijo: "No temas, yo soy tu
        proveedor, confía en mí". A la semana siguiente recibí una llamada inesperada para un trabajo
        mejor del que tenía antes. El sueldo era exactamente lo que necesitaba para cubrir todas mis
        necesidades. El Señor nunca nos abandona hermanos. Él conoce nuestras necesidades antes que
        se las pidamos. Como dice en Filipenses 4:19, "Mi Dios, pues, suplirá todo lo que os falta".
        """,
        "expected_tags": ["provision", "promesa_cumplida", "fe", "confianza"],
        "expected_elements": ["situación difícil", "palabra del Señor", "provisión concreta"],
    },
    {
        "name": "family_restoration",
        "transcript": """
        Quiero compartir con ustedes hermanos cómo el Señor restauró mi matrimonio. Mi esposo y yo
        estábamos al borde del divorcio, ya no nos hablábamos, había mucha amargura entre nosotros.
        Durante un culto especial, la hermana profetisa me dio una palabra: "Hija, el Señor va a
        restaurar tu hogar, lo que parecía perdido será recuperado". Yo lloré mucho esa noche y le
        pedí al Señor que obrara en nuestro matrimonio. Poco a poco comenzamos a hablar, a perdonarnos.
        El Señor cambió nuestros corazones. Hoy después de seis meses estamos más unidos que nunca.
        Dios restaura lo que está quebrado hermanos. Nunca perdamos la fe en su poder.
        """,
        "expected_tags": ["familia", "restauracion", "promesa_cumplida", "profecia"],
        "expected_elements": ["crisis matrimonial", "profecía recibida", "proceso de restauración"],
    },
    # Add your real transcripts here by replacing the dummy ones above
    # Format:
    # {
    #     "name": "your_test_name",
    #     "transcript": """Your real transcript here...""",
    #     "expected_tags": ["tag1", "tag2"],
    #     "expected_elements": ["element1", "element2"]
    # },
]


def evaluate_summary(summary, expected_tags=None, expected_elements=None):
    """
    Evaluate the quality of a generated summary.

    Returns a dict with evaluation metrics.
    """
    if not summary:
        return {
            "word_count": 0,
            "has_format": False,
            "has_tags": False,
            "has_expected_tags": 0,
            "has_expected_elements": 0,
            "has_biblical_reference": False,
            "quality_score": 0,
        }

    # Basic metrics
    word_count = len(summary.split())
    has_format = "**Resumen:**" in summary and "**Virtudes:**" in summary
    has_tags = "#" in summary
    has_biblical_reference = any(
        book in summary
        for book in [
            "Génesis",
            "Éxodo",
            "Levítico",
            "Números",
            "Deuteronomio",
            "Josué",
            "Jueces",
            "Rut",
            "Samuel",
            "Reyes",
            "Crónicas",
            "Esdras",
            "Nehemías",
            "Ester",
            "Job",
            "Salmos",
            "Proverbios",
            "Eclesiastés",
            "Cantares",
            "Isaías",
            "Jeremías",
            "Lamentaciones",
            "Ezequiel",
            "Daniel",
            "Oseas",
            "Joel",
            "Amós",
            "Abdías",
            "Jonás",
            "Miqueas",
            "Nahúm",
            "Habacuc",
            "Sofonías",
            "Hageo",
            "Zacarías",
            "Malaquías",
            "Mateo",
            "Marcos",
            "Lucas",
            "Juan",
            "Hechos",
            "Romanos",
            "Corintios",
            "Gálatas",
            "Efesios",
            "Filipenses",
            "Colosenses",
            "Tesalonicenses",
            "Timoteo",
            "Tito",
            "Filemón",
            "Hebreos",
            "Santiago",
            "Pedro",
            "Juan",
            "Judas",
            "Apocalipsis",
        ]
    )

    # Check for expected tags
    has_expected_tags = 0
    if expected_tags:
        for tag in expected_tags:
            if tag in summary.lower():
                has_expected_tags += 1

    # Check for expected narrative elements
    has_expected_elements = 0
    if expected_elements:
        for element in expected_elements:
            if any(word in summary.lower() for word in element.lower().split()):
                has_expected_elements += 1

    # Calculate quality score (0-100)
    quality_score = 0
    if has_format:
        quality_score += 25
    if has_tags:
        quality_score += 15
    if 100 <= word_count <= 200:
        quality_score += 20
    elif 80 <= word_count <= 250:
        quality_score += 15
    elif word_count > 0:
        quality_score += 5

    if expected_tags:
        quality_score += (has_expected_tags / len(expected_tags)) * 20
    if expected_elements:
        quality_score += (has_expected_elements / len(expected_elements)) * 15

    if has_biblical_reference:
        quality_score += 5

    return {
        "word_count": word_count,
        "has_format": has_format,
        "has_tags": has_tags,
        "has_expected_tags": has_expected_tags,
        "total_expected_tags": len(expected_tags) if expected_tags else 0,
        "has_expected_elements": has_expected_elements,
        "total_expected_elements": len(expected_elements) if expected_elements else 0,
        "has_biblical_reference": has_biblical_reference,
        "quality_score": min(100, quality_score),
    }


def run_evaluation():
    """Run evaluation on all test cases."""
    print("🧪 RUNNING TESTIMONY SUMMARIZATION EVALUATION")
    print("=" * 60)

    # Check OpenAI client
    try:
        from app.tasks import openai_client

        if openai_client is None:
            print("❌ ERROR: OpenAI client not initialized")
            return
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return

    results = {"timestamp": datetime.now().isoformat(), "test_cases": [], "summary_stats": {}}

    total_cases = len(TEST_CASES)
    passed_cases = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📋 Test {i}/{total_cases}: {test_case['name']}")
        print("-" * 40)

        transcript = test_case["transcript"].strip()
        print(f"📝 Transcript: {len(transcript)} chars")

        start_time = time.time()

        try:
            summary = generate_summary(transcript)
            generation_time = time.time() - start_time

            if summary:
                evaluation = evaluate_summary(
                    summary, test_case.get("expected_tags"), test_case.get("expected_elements")
                )

                print(f"✅ Summary generated in {generation_time:.1f}s")
                print(f"📊 Quality score: {evaluation['quality_score']:.1f}/100")
                print(f"📏 Word count: {evaluation['word_count']}")
                print(f"🏷️  Has tags: {'✅' if evaluation['has_tags'] else '❌'}")
                print(f"📖 Has format: {'✅' if evaluation['has_format'] else '❌'}")

                if evaluation["quality_score"] >= 70:
                    passed_cases += 1
                    print("🎉 PASSED")
                else:
                    print("⚠️  NEEDS IMPROVEMENT")

                # Store results
                results["test_cases"].append(
                    {
                        "name": test_case["name"],
                        "transcript_length": len(transcript),
                        "summary": summary,
                        "generation_time": generation_time,
                        "evaluation": evaluation,
                    }
                )

            else:
                print("❌ No summary generated")
                results["test_cases"].append(
                    {
                        "name": test_case["name"],
                        "transcript_length": len(transcript),
                        "summary": "",
                        "generation_time": generation_time,
                        "evaluation": {"quality_score": 0, "error": "No summary generated"},
                    }
                )

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["test_cases"].append(
                {
                    "name": test_case["name"],
                    "transcript_length": len(transcript),
                    "summary": "",
                    "generation_time": 0,
                    "evaluation": {"quality_score": 0, "error": str(e)},
                }
            )

    # Summary stats
    results["summary_stats"] = {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "pass_rate": (passed_cases / total_cases) * 100 if total_cases > 0 else 0,
        "average_quality_score": sum(tc.get("evaluation", {}).get("quality_score", 0) for tc in results["test_cases"])
        / total_cases
        if total_cases > 0
        else 0,
    }

    # Print summary
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("-" * 30)
    print(f"🎯 Passed: {passed_cases}/{total_cases} ({results['summary_stats']['pass_rate']:.1f}%)")
    print(f"📈 Average Quality Score: {results['summary_stats']['average_quality_score']:.1f}/100")

    # Save results
    output_file = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to: {output_file}")

    return results


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key before running evaluations.\n")
        exit(1)

    run_evaluation()
