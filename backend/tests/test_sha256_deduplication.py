from datetime import datetime, timezone
from app.repositories.event_repository import generate_event_hash


def test_event_hash_determinism():
    pub_date = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    h1 = generate_event_hash("BUMI", "KONGLO_MOVE", pub_date, "Grup Salim Masuk BUMI")
    h2 = generate_event_hash("bumi", "konglo_move", pub_date, "  Grup Salim Masuk BUMI  ")

    assert len(h1) == 64
    assert h1 == h2


def test_event_hash_uniqueness_on_different_titles():
    pub_date = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)
    h1 = generate_event_hash("BUMI", "KONGLO_MOVE", pub_date, "Grup Salim Masuk BUMI")
    h2 = generate_event_hash("BUMI", "KONGLO_MOVE", pub_date, "Grup Bakrie Tambah Kepemilikan BUMI")

    assert h1 != h2
