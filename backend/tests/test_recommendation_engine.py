from app.agents.nodes.recommendation_node import _fallback_recommendation


def test_strong_buy_akumulasi_when_top_konglo_present():
    """
    Mandatory rule: When Top 200 Konglomerat (e.g. Salim, Prajogo Pangestu / Barito, Bakrie,
    Djarum, Agung Sedayu) is involved in KONGLO_MOVE or BACKDOOR_LISTING, output MUST be STRONG_BUY_AKUMULASI.
    """
    extracted = {"investor_or_group": "Mach Energy (Grup Salim)"}
    rec = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted=extracted,
        title="Grup Salim Masuk BUMI",
        text="Crossing pasar negosiasi Rp 24 Triliun",
    )
    assert rec == "STRONG_BUY_AKUMULASI"


def test_buy_when_positive_corporate_action_without_tier1_konglo():
    extracted = {"investor_or_group": "General Institutional Fund"}
    rec = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted=extracted,
        title="Institutional Investor Acquires Stake",
        text="Crossing saham oleh institusi luar negeri",
    )
    assert rec == "BUY"


def test_hold_watch_default():
    rec = _fallback_recommendation(
        category="IRRELEVANT",
        extracted=None,
        title="Berita Umum Pasar Saham",
        text="Pergerakan IHSG hari ini",
    )
    assert rec == "HOLD_WATCH"
