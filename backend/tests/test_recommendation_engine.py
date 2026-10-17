from app.agents.nodes.recommendation_node import _fallback_recommendation


def test_strong_buy_akumulasi_when_top_konglo_present():
    """
    Mandatory rule: When Top 200 Konglomerat (e.g. Salim, Prajogo Pangestu / Barito, Bakrie,
    Djarum, Agung Sedayu) is involved in KONGLO_MOVE or BACKDOOR_LISTING, output MUST be STRONG_BUY_AKUMULASI.
    """
    extracted = {"investor_or_group": "Mach Energy (Grup Salim)"}
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted=extracted,
        title="Grup Salim Masuk BUMI",
        text="Crossing pasar negosiasi Rp 24 Triliun",
        ticker="BUMI",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "STRONG_BUY_AKUMULASI"
    assert "multi_horizon" in res
    assert "short_term" in res["multi_horizon"]
    assert "invalidation_triggers" in res


def test_buy_when_positive_corporate_action_without_tier1_konglo():
    extracted = {"investor_or_group": "General Institutional Fund"}
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted=extracted,
        title="Institutional Investor Acquires Stake",
        text="Crossing saham oleh institusi luar negeri",
        ticker="AUTO",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "BUY"


def test_hold_watch_default():
    res = _fallback_recommendation(
        category="IRRELEVANT",
        extracted=None,
        title="Berita Umum Pasar Saham",
        text="Pergerakan IHSG hari ini",
        ticker="IHSG",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "HOLD_WATCH"


def test_jarr_agunan_and_bakrie_analogy_returns_hold_watch():
    """
    Case test: News about 'Agunan Saham JARR PGUN di Bank Mandiri, Risiko Saham Bakrie 2008 Membayangi'.
    Must NOT return STRONG_BUY_AKUMULASI despite mentioning 'Bakrie'.
    """
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": None},
        title="Agunan Saham JARR PGUN di Bank Mandiri, Risiko Saham Bakrie 2008 Membayangi",
        text="Total eksposur kredit perbankan mencapai Rp 73 Triliun",
        ticker="JARR",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec in {"HOLD_WATCH", "AVOID"}
    assert rec != "STRONG_BUY_AKUMULASI"


def test_avoid_on_severe_debt_default():
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": "Grup Bakrie"},
        title="Emiten Mengalami Gagal Bayar dan Wanprestasi Utang",
        text="Agunan disita oleh pihak kreditur",
        ticker="EMITEN",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "AVOID"


def test_extractor_ignores_historical_analogy_bakrie():
    from app.agents.nodes.extractor_node import _fallback_regex_extract

    title = "Agunan Saham JARR PGUN di Bank Mandiri, Risiko Saham Bakrie 2008 Membayangi"
    text = "Fasilitas kredit Rp 73 Triliun"
    res = _fallback_regex_extract(title, text)

    assert res["investor_or_group"] is None
    assert res["action_type"] == "Agunan Saham / Fasilitas Kredit"


def test_classifier_filters_pledge_news_as_irrelevant():
    from app.agents.nodes.classifier_node import _fallback_keyword_classify

    res = _fallback_keyword_classify(
        ticker="JARR",
        title="Agunan Saham JARR PGUN di Bank Mandiri, Risiko Saham Bakrie 2008 Membayangi",
        text="Penjaminan saham sebagai agunan fasilitas pinjaman",
    )
    assert res.category == "IRRELEVANT"


def test_avoid_on_ojk_sanction():
    """
    Case: OJK sanctions DSSA/BREN/CUAN for stock manipulation.
    Despite mentioning Prajogo/Barito, must return AVOID.
    """
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": "Prajogo Pangestu / Barito"},
        title="OJK Jatuhkan Sanksi dan Denda pada DSSA BREN dan CUAN Terkait Manipulasi Harga Saham",
        text="OJK menjatuhkan sanksi administratif berupa denda kepada PT Dian Swastatika Sentosa Tbk terkait manipulasi harga saham",
        ticker="DSSA",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "AVOID"
    assert rec != "STRONG_BUY_AKUMULASI"


def test_avoid_on_manipulasi_harga_with_konglo():
    """
    Case: News about manipulasi harga saham even with konglo keywords present.
    """
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": "Grup Salim"},
        title="Investigasi Manipulasi Harga Saham Emiten Grup Salim",
        text="BEI melakukan penyelidikan terkait manipulasi harga saham",
        ticker="TEST",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "AVOID"
    assert rec != "STRONG_BUY_AKUMULASI"


def test_avoid_on_bren_ojk_periksa_investor_kakap():
    """
    Case: OJK inspects big investors demanding IPO allocation for BREN CUAN.
    Must return AVOID, NEVER STRONG_BUY_AKUMULASI.
    """
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": "Grup Barito / Prajogo Pangestu"},
        title="OJK periksa investor kakap yang minta jatah IPO saham BREN CUAN",
        text="OJK mendalami periksa keterlibatan sejumlah pihak terkait alokasi jatah IPO saham BREN dan CUAN.",
        ticker="BREN",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "AVOID"
    assert rec != "STRONG_BUY_AKUMULASI"


def test_classifier_filters_ojk_periksa_as_irrelevant():
    """
    Case: Classifier fallback correctly labels OJK periksa news as IRRELEVANT.
    """
    from app.agents.nodes.classifier_node import _fallback_keyword_classify

    res = _fallback_keyword_classify(
        ticker="BREN",
        title="OJK periksa investor kakap yang minta jatah IPO saham BREN CUAN",
        text="Pemeriksaan OJK terkait permohonan jatah IPO saham BREN dan CUAN Barito.",
    )
    assert res.category == "IRRELEVANT"


def test_hold_watch_on_konglo_mention_without_transaction():
    """
    Case: Conglomerate name is mentioned, but it is merely general news without transaction keywords.
    Must return HOLD_WATCH, NEVER STRONG_BUY_AKUMULASI.
    """
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": "Prajogo Pangestu"},
        title="Prajogo Pangestu Hadiri Diskusi Pasar Modal dan Berikan Pandangan Bisnis",
        text="Prajogo Pangestu memberikan pandangan mengenai industri energi hijau di Indonesia.",
        ticker="BREN",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "HOLD_WATCH"
    assert rec != "STRONG_BUY_AKUMULASI"


def test_strong_buy_on_actual_konglo_transaction():
    """
    Case: Real conglomerate transaction with crossing / akuisisi keywords.
    Must return STRONG_BUY_AKUMULASI.
    """
    res = _fallback_recommendation(
        category="KONGLO_MOVE",
        extracted={"investor_or_group": "Prajogo Pangestu / Barito"},
        title="Prajogo Pangestu Eksekusi Crossing Pasar Negosiasi Akuisisi Saham BREN",
        text="Transaksi crossing pasar negosiasi jumbo dan akuisisi kepemilikan oleh Grup Barito senilai Rp 2 Triliun.",
        ticker="BREN",
    )
    rec = res["recommendation_class"] if isinstance(res, dict) else res
    assert rec == "STRONG_BUY_AKUMULASI"
