import os

from openai import OpenAI

from .config import EMB_DIM, MODEL_NAME

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_texts(texts: list[str]) -> list[list[float]]:
    rsp = client.embeddings.create(
        model=MODEL_NAME,
        input=texts,
        dimensions=EMB_DIM,
    )
    return [d.embedding for d in rsp.data]
