from __future__ import annotations

from types import SimpleNamespace

from app.telegram import handlers


class _FakeApplication:
    def __init__(self) -> None:
        self.handlers = []
        self.polling_args = None

    def add_handler(self, handler) -> None:
        self.handlers.append(handler)

    def run_polling(self, **kwargs) -> None:
        self.polling_args = kwargs


class _FakeBuilder:
    def __init__(self, application: _FakeApplication) -> None:
        self.application = application
        self.token_value = None

    def token(self, token: str):
        self.token_value = token
        return self

    def build(self):
        return self.application


def test_register_bot_handlers_wires_section_commands(monkeypatch):
    fake_application = _FakeApplication()

    monkeypatch.setattr(
        handlers,
        "get_settings",
        lambda: SimpleNamespace(telegram_bot_token="test-token", telegram_chat_id="123"),
    )
    monkeypatch.setattr(
        handlers.Application,
        "builder",
        classmethod(lambda cls: _FakeBuilder(fake_application)),
    )

    handlers.run_telegram_bot()

    registered_commands = [list(handler.commands)[0] for handler in fake_application.handlers]
    assert registered_commands == ["start", "daily", "trending", "opensource", "research"]
    assert fake_application.polling_args == {"drop_pending_updates": True}
