import pytest
from pydantic import BaseModel

from core.config import get_settings
from providers.base import AgentRequest, AIProvider, Completion, Usage
from providers.mock import MockProvider
from providers.registry import build_provider
from providers.routing import RoutingProvider
from services.settings_service import env_defaults


class Out(BaseModel):
    who: str


class Named(AIProvider):
    def __init__(self, name: str, model: str) -> None:
        self.name, self.model = name, model

    def generate(self, request, schema):
        return Completion(schema(who=self.name), Usage(), self.name, self.model, False)

    def check(self, deep=False):  # noqa: ARG002
        return {"provider": self.name, "ok": True}


def ask(provider: AIProvider, task: str) -> Completion:
    return provider.generate(AgentRequest(agent="a", task=task, system="s", user="u"), Out)


def test_listed_tasks_go_to_the_secondary_and_completions_keep_their_real_model():
    router = RoutingProvider(
        Named("meta", "muse-spark-1.3"), Named("openai", "muse-open"), frozenset({"repair"})
    )
    hyp, rep = ask(router, "hypotheses"), ask(router, "repair")
    assert (hyp.output.who, hyp.model) == ("meta", "muse-spark-1.3")
    assert (rep.output.who, rep.model) == ("openai", "muse-open")
    assert router.name == "meta+openai" and router.model == "muse-spark-1.3 + muse-open"
    assert router.check()["ok"] and router.describe()["routing"]["secondary"]["tasks"] == ["repair"]


@pytest.fixture
def env(monkeypatch):
    def apply(**values):
        for key, value in values.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield apply
    get_settings.cache_clear()


def test_registry_builds_a_router_only_when_both_providers_are_usable(env):
    env(
        AI_PROVIDER="meta",
        META_API_KEY="meta-test-key-000",
        AI_SECONDARY_PROVIDER="openai",
        AI_SECONDARY_TASKS="experiments, repair",
        OPENAI_COMPAT_API_KEY="open-test-key-000",
    )
    selection = build_provider(env_defaults())
    assert isinstance(selection.provider, RoutingProvider)
    assert selection.provider.tasks == {"experiments", "repair"}

    env(OPENAI_COMPAT_API_KEY="")
    selection = build_provider(env_defaults())
    assert selection.provider.name == "meta"
    assert "not usable" in (selection.fallback_reason or "")


def test_mock_primary_is_never_routed(env):
    env(AI_PROVIDER="mock", AI_SECONDARY_PROVIDER="openai", OPENAI_COMPAT_API_KEY="open-test-key-000")
    assert isinstance(build_provider(env_defaults()).provider, MockProvider)
