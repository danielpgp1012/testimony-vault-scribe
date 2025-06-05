
from semantic.chunker import make_chunks
from semantic.embedder import embed_texts


def test_chunk_size_limit():
    text = "palabra " * 2500
    chunks = list(make_chunks(text))
    assert all(c["tokens"] <= 400 for c in chunks)


def test_embedding_mock(monkeypatch):
    dummy = [0.1] * 768
    monkeypatch.setattr(
        "semantic.embedder.client.embeddings.create",
        lambda **kw: type("R", (), {"data": [type("D", (), {"embedding": dummy}) for _ in kw["input"]]})(),
    )
    vecs = embed_texts(["test1", "test2"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 768
