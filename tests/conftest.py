import os
import sys

os.environ.setdefault("OPENAI_API_KEY", "test")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

