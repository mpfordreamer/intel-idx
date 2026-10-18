const translations = {
    id: {
        // Navbar
        "nav.brand": "IDX-Intel AI",
        "nav.us_brand": "US-Intel AI",
        "nav.sp500_brand": "US-Intel AI",
        "nav.badge": "IHSG",
        "nav.badge_us": "S&P 500 & NASDAQ",
        "nav.why": "Kenapa",
        "nav.features": "Fitur",
        "nav.pricing": "Harga",
        "nav.faq": "FAQ",
        "nav.demo": "Demo",
        "nav.back": "Kembali ke Dashboard",
        "nav.getStarted": "Gabung Sekarang",

        // Hero Section
        "hero.badge": "🇮🇩 IDX INTELLIGENCE & 🇺🇸 WALL STREET S&P 500 / NASDAQ",
        "hero.title": "Bangun Sistem yang Mengubah Informasi Pasar Menjadi Keputusan Investasi yang Tepat.",
        "hero.subtitle": "IDX-Intel AI & US-Intel AI memantau pergerakan pasar saham BEI, Wall Street (S&P 500 & NASDAQ), serta komoditas global 24/7 dan mengirimkan ringkasan penting langsung ke WhatsApp Anda.",
        "hero.btn.primary": "Gabung Sekarang",
        "hero.btn.secondary": "Coba Demo",

        // Problem Section
        "prob.badge": "MASALAH UTAMA",
        "prob.title": "Anda bukan kekurangan informasi, masalah anda adalah:",
        "prob.1.title": "Informasi Terlambat Sampai",
        "prob.1.desc1": "Saat berita keterbukaan informasi atau aksi korporasi muncul di portal berita umum, pergerakan harga saham sering kali sudah selesai karena smart money telah bergerak lebih awal.",
        "prob.1.desc2": "Investor ritel yang mengandalkan berita konvensional sering terjebak membeli di harga pucuk (buying at the top) atau menjual saat panik di dasar, kehilangan momentum krusial yang sesungguhnya.",
        "prob.2.title": "Keputusan Berbasis Emosi & FOMO",
        "prob.2.desc1": "Tanpa data objektif dan verifikasi transaksi konglomerat, keputusan investasi mudah terseret euforia pasar saat harga hijau, atau panik berlebih (panic selling) saat koreksi tajam.",
        "prob.2.desc2": "Emosi dan bias psikologis adalah musuh terbesar investor. Mengandalkan intuisi tanpa sistem penyaring informasi terukur secara konsisten mengikis modal portofolio dalam jangka panjang.",
        "prob.3.title": "Tenggelam dalam Ratusan Dokumen",
        "prob.3.desc1": "Setiap hari bursa mempublikasikan puluhan laporan keterbukaan, lapkeu ratusan halaman, hingga prospektus rights issue yang padat regulasi dan istilah hukum yang rumit.",
        "prob.3.desc2": "Membaca dan membedah seluruh dokumen tersebut secara manual membutuhkan waktu berjam-jam yang mustahil dilakukan oleh investor perorangan di tengah rutinitas harian.",
        "prob.4.title": "Ketiadaan Sistem Otomasi Real-Time",
        "prob.4.desc1": "Memantau keterbukaan informasi BEI, rotasi pasar global Wall Street, dan crossing negosiasi jumbo secara manual selama 24 jam adalah pekerjaan yang tidak efisien.",
        "prob.4.desc2": "Tanpa agen AI yang bekerja otomatis memfilter data bursa setiap detik, anomali pergerakan uang pintar dan akumulasi pengendali baru akan terus terlewat dari radar Anda.",

        // Filter / Qualification Section
        "filter.title": "IDX-Intel AI & US-Intel AI bukan untuk semua orang.",
        "filter.btn": "Gabung Komunitas",
        "filter.not.title": "Sistem ini bukan untuk Anda jika:",
        "filter.not.1": "Mencari sinyal beli instan tanpa analisa.",
        "filter.not.2": "Ingin cepat kaya dalam semalam.",
        "filter.not.3": "Tidak mau memahami data dan pergerakan pasar.",
        "filter.yes.title": "Sistem ini cocok jika Anda:",
        "filter.yes.1": "Ingin memantau aktivitas saham IDX dan Wall Street secara objektif.",
        "filter.yes.2": "Ingin mendapatkan ringkasan data penting dalam hitungan detik.",
        "filter.yes.3": "Serius membangun keputusan investasi berbasis data dan teknologi AI.",

        // Deliverables Section
        "deliv.badge": "FITUR UTAMA",
        "deliv.title": "Apa yang akan Anda dapatkan?",
        "deliv.1.title": "🇮🇩 Saham Indonesia & Top 200 Konglomerat BEI (24/7)",
        "deliv.1.desc": "Setiap kali ada pengumuman keterbukaan informasi BEI, Konglo Move, Crossing Jumbo, atau Backdoor Listing, AI langsung merangkum intinya ke WhatsApp Anda.",
        "deliv.2.title": "🇺🇸 S&P 500, NASDAQ & Sektor Komoditas Global",
        "deliv.2.desc": "Analisis rotasi sektor Wall Street, Semikonduktor, Big Tech NASDAQ, Perbankan AS, serta pergerakan komoditas strategis (Emas, Minyak, Timah, Tembaga).",

        // Authority Section
        "auth.badge": "DIBANGUN OLEH",
        "auth.title": "Ternak AI & IDX Intelligence Lab",
        "auth.desc": "Dibangun oleh praktisi pasar modal dan AI engineer yang memahami seluk-beluk keterbukaan informasi bursa. Sistem ini dirancang untuk bekerja secara otomatis, terstruktur, dan akurat tanpa rekayasa data.",

        // Pricing Section
        "price.title": "Daftar & Gabung Sekarang",
        "price.badge": "AKSES PENUH · SEUMUR HIDUP",
        "price.normal": "Rp 999.000",
        "price.free": "Rp 0",
        "price.free.tag": "(GRATIS)",
        "price.check.1": "Pemantauan Keterbukaan Informasi BEI & Aktivitas Saham 24/7",
        "price.check.2": "Notifikasi real-time via WhatsApp langsung ke ponsel Anda",
        "price.check.3": "Analisis cerdas atas aktivitas saham dan pergerakan pasar modal",
        "price.check.4": "Akses tanya jawab interaktif ke AI Customer Service seputar pasar",
        "price.btn": "Daftar & Gabung WhatsApp Gratis",

        // FAQ Section
        "faq.title": "FAQ",
        "faq.q1": "Apakah IDX-Intel AI berbayar?",
        "faq.a1": "Tidak. Saat ini akses 100% GRATIS (dari nilai normal Rp 999.000). Anda bisa langsung bergabung ke grup WhatsApp kami.",
        "faq.q2": "Apakah ini grup sinyal saham?",
        "faq.a2": "Bukan. IDX-Intel AI adalah sistem pemantau data dan penyaring informasi bursa, membantu Anda mendapatkan fakta lebih cepat dan objektif.",
        "faq.q3": "Dari mana data diambil?",
        "faq.a3": "Sistem memantau pengumuman resmi Bursa Efek Indonesia (BEI) dan media finansial terpercaya secara real-time.",
        "faq.q4": "Bagaimana cara bergabung?",
        "faq.a4": "Cukup klik tombol Gabung Sekarang, scan QR Code atau gunakan link undangan grup WhatsApp yang disediakan.",
        "faq.q5": "Apakah saya bisa bertanya ke AI?",
        "faq.a5": "Ya, Anda bisa berinteraksi melalui tombol chat di pojok kanan bawah untuk bertanya seputar informasi bursa.",

        // Closer Section
        "close.badge": "MULAI HARI INI",
        "close.title": "Bangun kebiasaan investasi Anda, perlahan tapi pasti.",
        "close.btn": "Gabung Komunitas Sekarang",

        // Feed Section
        "feed.title": "Live Intelligence Feed",
        "feed.market.idx": "🇮🇩 Saham Indonesia (IDX)",
        "feed.market.us": "🇺🇸 S&P 500 & NASDAQ (US)",
        "feed.filter.all": "Semua",
        "feed.filter.konglo": "👑 Konglomerat",
        "feed.filter.backdoor": "🚀 Backdoor",
        "feed.empty": "Tidak ada dokumen korporasi yang ditemukan atau semua sudah terproses.",
        "card.analysis": "Analisis Strategis:",
        "card.source": "Sumber",
        "card.date": "Tanggal",
        "card.status": "Status",
        "card.status.analyzed": "Dianalisis",
        "card.status.filtered": "Disaring",

        // Connect Page (Unified Community)
        "connect.title": "Gabung Komunitas WhatsApp Intelijen Pasar",
        "connect.desc": "Satu pintu akses notifikasi real-time aksi korporasi BEI, rotasi Wall Street (S&P 500 & NASDAQ), serta komoditas dan makro ekonomi global 24/7.",
        "connect.single_card_title": "Komunitas WhatsApp Resmi",
        "connect.single_card_desc": "Dapatkan update langsung sinyal beli/hold konglomerat BEI, radar crossing jumbo, rotasi sektor Wall Street, dan analisis pergerakan komoditas dunia.",
        "connect.join_btn": "Buka WhatsApp & Gabung Komunitas",
        "connect.loading": "Mengambil QR Code...",
        "connect.instructions": "Cara menghubungkan:",
        "connect.step1": "Buka aplikasi WhatsApp atau kamera/pemindai QR di HP Anda.",
        "connect.step2": "Arahkan kamera untuk memindai QR Code di atas (atau klik tombol jika membuka via HP).",
        "connect.step3": "Klik tautan yang muncul untuk membuka WhatsApp.",
        "connect.step4": "Bergabunglah ke grup komunitas resmi untuk menerima intelijen pasar otomatis.",

        // Action Section (Manual Trigger)
        "action.title": "⚡ Mulai Pemantauan Otomatis",
        "action.desc": "Klik tombol di bawah untuk mengumpulkan data terbaru dari berbagai sumber berita dan menganalisisnya secara otomatis menggunakan AI.",
        "action.btn": "🚀 Kumpulkan & Analisis Data Sekarang",
        "action.loading": "⏳ AI Sedang Memproses Data...",
        "action.loadingDesc": "Sistem sedang mengambil, membaca, dan menganalisis aksi korporasi secara real-time.",
        "action.success": "✅ Pipeline AI Selesai!",

        // Footer
        "footer.tagline": "IDX-Intel AI & US-Intel AI · Platform Intelijen Pasar Modal Indonesia & Global",
        "footer.copy": "© 2026 Ternak Automation. All rights reserved.",

        // Demo Terminal & WA
        "demo.terminal_title": "Terminal Intelligence",
        "demo.terminal_subtitle": "Model: Qwen-3.5-Instruct (Fine-Tuned)",
        "demo.init_msg": "Inisialisasi sistem berhasil. Memuat data pasar terbaru...<br><br>💡 Ketik <b>/cek BUMI</b> atau <b>/cek BBCA</b> untuk melihat simulasi output <i>Corporate Action</i> secara instan.",
        "demo.user_msg": "Halo AI, apakah ada sentimen terbaru mengenai emiten batu bara?",
        "demo.ai_msg": "Halo! Berdasarkan pantauan data real-time, sektor energi khususnya batu bara menunjukkan adanya akumulasi bertahap. Namun, silakan ketik perintah spesifik seperti <b>/cek BUMI</b> untuk melihat detail analisis kami.",
        "demo.input_placeholder": "Ketik perintah (contoh: /cek BUMI)",
        "demo.btn_execute": "Eksekusi",
        "demo.analyzing": "<i>Menganalisis data pasar...</i>",
        "demo.bumi_intro": "Berikut adalah analisis intelijen untuk BUMI:",
        "demo.bumi_title": "Aksi Borong Saham oleh Pengendali Baru (Salim Group)",
        "demo.bumi_analysis": "<b>Analisis:</b> Terdeteksi adanya akumulasi masif melalui broker-broker terafiliasi. Ini mengindikasikan persiapan konsolidasi aset besar di bawah kendali pemegang saham pengendali baru. Target resisten terdekat ditembus dengan volume tinggi.",
        "demo.bbca_intro": "Berikut adalah analisis intelijen untuk BBCA:",
        "demo.bbca_title": "Pembagian Dividen Interim 2026",
        "demo.bbca_analysis": "<b>Analisis:</b> Berita reguler tentang dividen interim. Tidak ada anomali atau pergerakan uang pintar yang signifikan di luar siklus normal. Emiten bergerak sesuai valuasi pasar.",
        "demo.unknown_cmd": "Sistem hanya dapat mensimulasikan data untuk perintah <b>/cek BUMI</b> dan <b>/cek BBCA</b> pada mode demo ini. Untuk analisis <i>real-time</i> emiten lain, silakan aktifkan <i>pipeline</i> utama di halaman beranda.",
        "hero.demo": "Demo"
    },
    en: {
        // Navbar
        "nav.brand": "IDX-Intel AI",
        "nav.us_brand": "US-Intel AI",
        "nav.sp500_brand": "US-Intel AI",
        "nav.badge": "IHSG",
        "nav.badge_us": "S&P 500 & NASDAQ",
        "nav.why": "Why Us",
        "nav.features": "Features",
        "nav.pricing": "Pricing",
        "nav.faq": "FAQ",
        "nav.demo": "Demo",
        "nav.back": "Back to Dashboard",
        "nav.getStarted": "Join Now",

        // Hero Section
        "hero.badge": "🇮🇩 IDX INTELLIGENCE & 🇺🇸 WALL STREET S&P 500 / NASDAQ",
        "hero.title": "Build a System That Turns Market Information Into Smarter Investment Decisions.",
        "hero.subtitle": "IDX-Intel AI & US-Intel AI monitor IDX disclosures, Wall Street (S&P 500 & NASDAQ), and global commodities 24/7, sending intelligent summaries directly to your WhatsApp.",
        "hero.btn.primary": "Join Now",
        "hero.btn.secondary": "Try Demo",

        // Problem Section
        "prob.badge": "CORE PROBLEMS",
        "prob.title": "You don't lack information, your problem is:",
        "prob.1.title": "Information Arrives Too Late",
        "prob.1.desc1": "By the time corporate actions or disclosures appear on generic news portals, price movements have often concluded as smart money already positioned themselves.",
        "prob.1.desc2": "Retail investors relying on mainstream media frequently get trapped buying at market peaks or panic selling at bottoms, missing the actual profitable wave.",
        "prob.2.title": "Decisions Driven by Emotion & FOMO",
        "prob.2.desc1": "Without objective data and verified conglomerate tracking, investment decisions easily succumb to market euphoria when green or excessive panic during sharp corrections.",
        "prob.2.desc2": "Emotional biases are an investor's biggest hazard. Trading on gut feelings without systematic data filters relentlessly erodes portfolio capital over time.",
        "prob.3.title": "Drowning in Hundreds of Documents",
        "prob.3.desc1": "Every day, exchanges release dozens of corporate disclosures, thick multi-hundred page financial statements, and dense legalistic rights issue prospectuses.",
        "prob.3.desc2": "Reading and extracting intelligence from all these filings manually requires hours of dedicated work that individual investors simply do not have.",
        "prob.4.title": "Lack of Automated Real-Time Systems",
        "prob.4.desc1": "Manually monitoring exchange filings, Wall Street sector rotations, and jumbo negotiated crossings 24/7 is an unsustainable human task.",
        "prob.4.desc2": "Without autonomous AI agents filtering exchange data every second, critical smart money signals and major controlling shareholder shifts will slip past your radar.",

        // Filter / Qualification Section
        "filter.title": "IDX-Intel AI & US-Intel AI is not for everyone.",
        "filter.btn": "Join Community",
        "filter.not.title": "This system is not for you if you:",
        "filter.not.1": "Are looking for instant buy signals without analysis.",
        "filter.not.2": "Want to get rich quick overnight.",
        "filter.not.3": "Don't want to understand market data and movements.",
        "filter.yes.title": "This system is a fit for you if you:",
        "filter.yes.1": "Want to monitor IDX and Wall Street movements objectively.",
        "filter.yes.2": "Want to get important data summaries in seconds.",
        "filter.yes.3": "Are serious about building investment decisions based on data and AI technology.",

        // Deliverables Section
        "deliv.badge": "KEY FEATURES",
        "deliv.title": "What will you get?",
        "deliv.1.title": "🇮🇩 Indonesia Equities & Top 200 Conglomerates (24/7)",
        "deliv.1.desc": "Whenever there are official IDX announcements, Conglomerate Moves, Negotiated Crossings, or Backdoor Listings, AI summarizes the core into your WhatsApp.",
        "deliv.2.title": "🇺🇸 S&P 500, NASDAQ & Global Commodities",
        "deliv.2.desc": "Intelligence on Wall Street sector rotations, Semis, Big Tech NASDAQ, US Banks, and critical commodities (Gold, Crude Oil, Tin, Copper).",

        // Authority Section
        "auth.badge": "BUILT BY",
        "auth.title": "Ternak AI & Intelligence Lab",
        "auth.desc": "Built by capital market practitioners and AI engineers who understand the ins and outs of exchange disclosures. The system is designed to work automatically, structured, and accurately without data manipulation.",

        // Pricing Section
        "price.title": "Register & Join Now",
        "price.badge": "FULL ACCESS · LIFETIME",
        "price.normal": "Rp 999.000",
        "price.free": "Rp 0",
        "price.free.tag": "(FREE)",
        "price.check.1": "24/7 Monitoring of IDX & Wall Street Disclosures",
        "price.check.2": "Real-time notifications via WhatsApp direct to your phone",
        "price.check.3": "Smart analysis of stock activities and sector movements",
        "price.check.4": "Interactive Q&A access to AI Customer Service regarding the market",
        "price.btn": "Register & Join WhatsApp Free",

        // FAQ Section
        "faq.title": "FAQ",
        "faq.q1": "Are these alert services paid?",
        "faq.a1": "No. Currently, access is 100% FREE (from a normal value of Rp 999.000). You can join our WhatsApp groups right away.",
        "faq.q2": "Are these stock signal groups?",
        "faq.a2": "No. IDX-Intel AI & US-Intel AI are data monitoring and filtering platforms, helping you get facts faster and objectively.",
        "faq.q3": "Where is the data sourced from?",
        "faq.a3": "The system monitors official Indonesia Stock Exchange (IDX) announcements, Wall Street indices, and trusted global financial media in real-time.",
        "faq.q4": "How do I join?",
        "faq.a4": "Simply click the Join Now button, scan the QR Code, or use the provided WhatsApp group invitation links.",
        "faq.q5": "Can I ask the AI questions?",
        "faq.a5": "Yes, you can interact through the chat button in the bottom right corner to ask questions about exchange information.",

        // Closer Section
        "close.badge": "START TODAY",
        "close.title": "Build your data-driven investment habits, slowly but surely.",
        "close.btn": "Join Community Now",

        // Feed Section
        "feed.title": "Live Intelligence Feed",
        "feed.market.idx": "🇮🇩 Indonesia Equities (IDX)",
        "feed.market.us": "🇺🇸 S&P 500 & NASDAQ (US)",
        "feed.filter.all": "All",
        "feed.filter.konglo": "👑 Conglomerates",
        "feed.filter.backdoor": "🚀 Backdoor",
        "feed.empty": "No corporate documents found or all have been processed.",
        "card.analysis": "Strategic Analysis:",
        "card.source": "Source",
        "card.date": "Date",
        "card.status": "Status",
        "card.status.analyzed": "Analyzed",
        "card.status.filtered": "Filtered",

        // Connect Page (Unified Community)
        "connect.title": "Join the Market Intelligence WhatsApp Community",
        "connect.desc": "Your all-in-one gateway for real-time IDX corporate actions, Wall Street rotations (S&P 500 & NASDAQ), and global macro & commodity alerts 24/7.",
        "connect.single_card_title": "Official WhatsApp Community",
        "connect.single_card_desc": "Get instant notifications on conglomerate buy signals, negotiated market crossings, Wall Street sector rotations, and global commodity price actions.",
        "connect.join_btn": "Open WhatsApp & Join Community",
        "connect.loading": "Fetching QR Code...",
        "connect.instructions": "How to join:",
        "connect.step1": "Open WhatsApp or your camera / QR scanner on your phone.",
        "connect.step2": "Scan the QR Code above (or tap the button if on mobile).",
        "connect.step3": "Tap the link that appears to open WhatsApp.",
        "connect.step4": "Join the official community group to receive automated market intelligence.",

        // Action Section (Manual Trigger)
        "action.title": "⚡ Start Automated Monitoring",
        "action.desc": "Click the button below to collect the latest data from various news sources and analyze it automatically using AI.",
        "action.btn": "🚀 Collect & Analyze Data Now",
        "action.loading": "⏳ AI is Processing Data...",
        "action.loadingDesc": "The system is currently fetching, reading, and analyzing corporate actions in real-time.",
        "action.success": "✅ AI Pipeline Completed!",

        // Footer
        "footer.tagline": "IDX-Intel AI & US-Intel AI · Platform for Indonesian & Global Market Intelligence",
        "footer.copy": "© 2026 Ternak Automation. All rights reserved.",

        // Demo Terminal & WA
        "demo.terminal_title": "Terminal Intelligence",
        "demo.terminal_subtitle": "Model: Qwen-3.5-Instruct (Fine-Tuned)",
        "demo.init_msg": "System initialization successful. Loading latest market data...<br><br>💡 Type <b>/cek BUMI</b> or <b>/cek BBCA</b> to instantly see the simulated <i>Corporate Action</i> output.",
        "demo.user_msg": "Hello AI, are there any recent sentiments regarding coal issuers?",
        "demo.ai_msg": "Hello! Based on real-time monitoring, the energy sector, particularly coal, is showing gradual accumulation. However, please type a specific command like <b>/cek BUMI</b> to see our detailed analysis.",
        "demo.input_placeholder": "Type command (e.g., /cek BUMI)",
        "demo.btn_execute": "Execute",
        "demo.analyzing": "<i>Analyzing market data...</i>",
        "demo.bumi_intro": "Here is the intelligence analysis for BUMI:",
        "demo.bumi_title": "Massive Share Buyback by New Controlling Shareholder (Salim Group)",
        "demo.bumi_analysis": "<b>Analysis:</b> Massive accumulation detected through affiliated brokers. This indicates preparation for major asset consolidation under the new controlling shareholder. The nearest resistance target breached with high volume.",
        "demo.bbca_intro": "Here is the intelligence analysis for BBCA:",
        "demo.bbca_title": "Interim Dividend Distribution 2026",
        "demo.bbca_analysis": "<b>Analysis:</b> Regular news about interim dividends. No significant anomalies or smart money movements outside the normal cycle. The issuer is moving in line with market valuation.",
        "demo.unknown_cmd": "The system can only simulate data for <b>/cek BUMI</b> and <b>/cek BBCA</b> commands in this demo mode. For <i>real-time</i> analysis of other issuers, please activate the main <i>pipeline</i> on the home page.",
        "hero.demo": "Demo"
    }
};

let currentLang = localStorage.getItem('idx_lang') || 'id';

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
                el.setAttribute('placeholder', translations[currentLang][key]);
            } else {
                el.innerHTML = translations[currentLang][key];
            }
        }
    });

    const langBtn = document.getElementById('langToggle');
    if (langBtn) {
        langBtn.innerHTML = currentLang === 'id' ? 'ID' : 'EN';
    }
}

function getTranslation(key) {
    return translations[currentLang][key] || key;
}

function toggleLanguage() {
    currentLang = currentLang === 'id' ? 'en' : 'id';
    localStorage.setItem('idx_lang', currentLang);
    applyTranslations();

    if (typeof liveAiData !== 'undefined' && liveAiData.length > 0 && typeof renderCards === 'function') {
        renderCards(liveAiData);
    }
}

document.addEventListener('DOMContentLoaded', applyTranslations);

