import pytest

from excre import llm
from excre.llm import DiskCache, ModelUnavailable, OpenAICompatModel


class Reply:
    def __init__(self, status, text="ok", headers=None, body=""):
        self.status_code = status
        self.headers = headers or {}
        self.text = body
        self._text = text

    def json(self):
        return {"choices": [{"message": {"content": self._text},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 7}}


class Sent(list):
    def __init__(self):
        super().__init__()
        self.headers = []


@pytest.fixture
def wire(monkeypatch):
    sent, queue = Sent(), []

    def post(url, headers=None, json=None, timeout=None):
        sent.append(json)
        sent.headers.append(headers or {})
        return queue.pop(0) if queue else Reply(200)

    monkeypatch.setattr(llm.requests, "post", post)
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    monkeypatch.setenv("TEST_KEY", "x")
    llm._hold_until.clear()
    llm._exhausted_keys.clear()
    llm._last_call.clear()
    return sent, queue


def model(tmp_path, **kw):
    return OpenAICompatModel("m", "http://host/v1", "m-1", "TEST_KEY",
                             min_interval_s=0, cache=DiskCache(str(tmp_path)), **kw)


def test_seed_keys_the_cache_but_is_not_sent(wire, tmp_path):
    sent, _ = wire
    m = model(tmp_path, send_seed=False)
    msg = [{"role": "user", "content": "q"}]
    m.chat(msg, seed=0)
    m.chat(msg, seed=1)
    m.chat(msg, seed=1)
    assert len(sent) == 2
    assert all("seed" not in p for p in sent)


def test_minute_limits_never_bench_a_model(wire, tmp_path):
    sent, queue = wire
    limit = '{"error": "on output tokens per minute (OTPM): Limit 1000, Requested 2000"}'
    queue.extend([Reply(429, body=limit)] * 9)
    text, usage = model(tmp_path).chat([{"role": "user", "content": "q"}])
    assert text == "ok" and len(sent) == 10


def test_daily_limit_benches_at_once(wire, tmp_path):
    sent, queue = wire
    queue.append(Reply(429, body="Rate limit reached on tokens per day (TPD): Limit 200000"))
    with pytest.raises(ModelUnavailable):
        model(tmp_path).chat([{"role": "user", "content": "q"}])
    assert len(sent) == 1


def test_server_errors_still_run_out(wire, tmp_path):
    sent, queue = wire
    queue.extend([Reply(503)] * 6)
    with pytest.raises(ModelUnavailable):
        model(tmp_path).chat([{"role": "user", "content": "q"}])
    assert len(sent) == 6


def test_output_pacing_holds_the_next_call(wire, tmp_path):
    m = model(tmp_path, output_tpm=1000)
    m.chat([{"role": "user", "content": "q"}])
    gate = ("http://host/v1", "m-1")
    assert llm._hold_until[gate] > llm.time.monotonic()


def test_resolve_api_keys(monkeypatch):
    monkeypatch.delenv("TEST_ROT", raising=False)
    monkeypatch.setenv("TEST_ROT", "k1, k2 ,k3")
    assert llm.resolve_api_keys("TEST_ROT") == ["k1", "k2", "k3"]

    monkeypatch.delenv("TEST_ROT", raising=False)
    monkeypatch.setenv("TEST_ROT_1", "keyA")
    monkeypatch.setenv("TEST_ROT_2", "keyB")
    monkeypatch.setenv("TEST_ROT_3", "keyC")
    assert llm.resolve_api_keys("TEST_ROT") == ["keyA", "keyB", "keyC"]

    # Deduplication
    monkeypatch.setenv("TEST_ROT", "keyA")
    assert llm.resolve_api_keys("TEST_ROT") == ["keyA", "keyB", "keyC"]


def test_multi_key_round_robin_rotation(wire, monkeypatch, tmp_path):
    sent, _ = wire
    monkeypatch.delenv("TEST_KEY", raising=False)
    monkeypatch.setenv("TEST_KEY_1", "key1")
    monkeypatch.setenv("TEST_KEY_2", "key2")
    monkeypatch.setenv("TEST_KEY_3", "key3")

    m = model(tmp_path)
    # Chat with differing inputs to avoid cache hits
    m.chat([{"role": "user", "content": "q1"}])
    m.chat([{"role": "user", "content": "q2"}])
    m.chat([{"role": "user", "content": "q3"}])
    m.chat([{"role": "user", "content": "q4"}])

    auths = [h.get("Authorization") for h in sent.headers]
    assert auths == ["Bearer key1", "Bearer key2", "Bearer key3", "Bearer key1"]


def test_multi_key_failover_on_daily_quota(wire, monkeypatch, tmp_path):
    sent, queue = wire
    monkeypatch.delenv("TEST_KEY", raising=False)
    monkeypatch.setenv("TEST_KEY", "k_primary, k_backup")

    # Primary key hits daily limit on the first call, backup succeeds
    queue.append(Reply(429, body="Rate limit reached on tokens per day (TPD): Limit 200000"))
    queue.append(Reply(200, text="success from backup"))

    m = model(tmp_path)
    text, _ = m.chat([{"role": "user", "content": "q1"}])
    assert text == "success from backup"

    # Next call should use k_backup directly without hitting k_primary
    m.chat([{"role": "user", "content": "q2"}])
    auths = [h.get("Authorization") for h in sent.headers]
    assert auths == ["Bearer k_primary", "Bearer k_backup", "Bearer k_backup"]


def test_multi_key_all_exhausted_raises(wire, monkeypatch, tmp_path):
    _, queue = wire
    monkeypatch.delenv("TEST_KEY", raising=False)
    monkeypatch.setenv("TEST_KEY", "k1, k2")

    queue.append(Reply(429, body="Rate limit reached on tokens per day (TPD)"))
    queue.append(Reply(429, body="Rate limit reached on tokens per day (TPD)"))

    m = model(tmp_path)
    with pytest.raises(ModelUnavailable) as exc_info:
        m.chat([{"role": "user", "content": "q1"}])
    assert "daily quota used up" in str(exc_info.value)


def test_multi_key_failover_on_unauthorized(wire, monkeypatch, tmp_path):
    sent, queue = wire
    monkeypatch.delenv("TEST_KEY", raising=False)
    monkeypatch.setenv("TEST_KEY", "bad_key, good_key")

    # First key fails with 401 Unauthorized, second succeeds
    queue.append(Reply(401, body="Invalid API key"))
    queue.append(Reply(200, text="success from good key"))

    m = model(tmp_path)
    text, _ = m.chat([{"role": "user", "content": "q1"}])
    assert text == "success from good key"
    assert [h.get("Authorization") for h in sent.headers] == ["Bearer bad_key", "Bearer good_key"]
