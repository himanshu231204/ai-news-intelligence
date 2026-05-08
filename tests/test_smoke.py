from app.newsletter.generator import build_newsletter


def test_newsletter_generation_smoke() -> None:
    newsletter = build_newsletter([], [])
    assert "AI Daily Brief" in newsletter
