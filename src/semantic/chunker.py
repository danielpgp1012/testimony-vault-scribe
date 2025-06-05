import nltk
from transformers import AutoTokenizer

from .config import MAX_TOKENS, OVERLAP

nltk.download("punkt", quiet=True)

try:
    _tokenizer = AutoTokenizer.from_pretrained("text-embedding-3-small")
except Exception:  # fallback if model not available
    class _Dummy:
        def encode(self, txt, add_special_tokens=False):
            return txt.split()

    _tokenizer = _Dummy()


def _tok_len(txt: str) -> int:
    return len(_tokenizer.encode(txt, add_special_tokens=False))


def make_chunks(text: str, max_tokens: int = MAX_TOKENS, overlap: int = OVERLAP):
    if _tok_len(text) <= max_tokens:
        yield {"idx": 0, "text": text, "tokens": _tok_len(text)}
        return

    try:
        sents = nltk.sent_tokenize(text, language="spanish")
    except LookupError:
        words = text.split()
        for i in range(0, len(words), max_tokens - overlap):
            chunk = words[i : i + max_tokens]
            yield {"idx": i // (max_tokens - overlap), "text": " ".join(chunk), "tokens": len(chunk)}
        return
    buf: list[str] = []
    buf_tok = 0
    idx = 0
    for s in sents:
        t = _tok_len(s)
        if buf_tok + t > max_tokens:
            yield {"idx": idx, "text": " ".join(buf), "tokens": buf_tok}
            idx += 1
            # start new buffer with overlap
            buf = buf[-overlap:] if overlap else []
            buf_tok = _tok_len(" ".join(buf)) if buf else 0
        buf.append(s)
        buf_tok += t
    if buf:
        yield {"idx": idx, "text": " ".join(buf), "tokens": buf_tok}
