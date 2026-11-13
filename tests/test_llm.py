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


@pytest.fixture
def wire(monkeypatch):
    sent, queue = [], []

    def post(url, headers=None, json=None, timeout=None):
        sent.append(json)
        return queue.pop(0) if queue else Reply(200)

    monkeypatch.setattr(llm.requests, "post", post)
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    monkeypatch.setenv("TEST_KEY", "x")
    llm._hold_until.clear()
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
