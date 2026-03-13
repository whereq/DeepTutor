from pathlib import Path

from deeptutor.services.config.env_store import EnvStore
from deeptutor.services.config.model_catalog import ModelCatalogService


def test_load_hydrates_empty_catalog_from_env(tmp_path: Path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "LLM_BINDING=google",
                "LLM_MODEL=gemini-3-flash-preview",
                "LLM_API_KEY=test-llm-key",
                "LLM_HOST=https://example-llm.test/v1",
                "EMBEDDING_BINDING=openai",
                "EMBEDDING_MODEL=text-embedding-3-large",
                "EMBEDDING_API_KEY=test-emb-key",
                "EMBEDDING_HOST=https://example-emb.test/v1",
                "EMBEDDING_DIMENSION=3072",
                "SEARCH_PROVIDER=perplexity",
                "SEARCH_API_KEY=test-search-key",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    catalog_path = tmp_path / "model_catalog.json"
    catalog_path.write_text(
        """{
  "version": 1,
  "services": {
    "llm": {"active_profile_id": null, "active_model_id": null, "profiles": []},
    "embedding": {"active_profile_id": null, "active_model_id": null, "profiles": []},
    "search": {"active_profile_id": null, "profiles": []}
  }
}
""",
        encoding="utf-8",
    )

    env_store = EnvStore(path=env_path)
    monkeypatch.setattr("deeptutor.services.config.model_catalog.get_env_store", lambda: env_store)

    service = ModelCatalogService(path=catalog_path)
    catalog = service.load()

    assert catalog["services"]["llm"]["profiles"][0]["binding"] == "google"
    assert catalog["services"]["llm"]["profiles"][0]["extra_headers"] == {}
    assert catalog["services"]["llm"]["profiles"][0]["models"][0]["model"] == "gemini-3-flash-preview"
    assert catalog["services"]["embedding"]["profiles"][0]["models"][0]["dimension"] == "3072"
    assert catalog["services"]["search"]["profiles"][0]["provider"] == "perplexity"
    assert catalog["services"]["search"]["profiles"][0]["proxy"] == ""
