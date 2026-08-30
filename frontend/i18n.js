const translations = {
    id: {
        // Navbar
        "nav.brand": "IDX-Intel AI",
        "nav.badge": "MERAH PUTIH",
        "nav.getStarted": "Mulai Sekarang",
        
        // Hero / PAS Formula
        "hero.problem": "Ketinggalan Info Aksi Korporasi & Akumulasi Konglomerat?",
        "hero.agitate": "Info telat bikin boncos, beli di pucuk saat market maker sudah profit.",
        "hero.solve": "IDX-Intel AI otomatis memantau pergerakan Top 200 Konglomerat dan menyaring noise pasar secara real-time.",
        
        // Action section
        "action.title": "⚡ Mulai Pemantauan Otomatis",
        "action.desc": "Klik tombol di bawah untuk mengumpulkan data terbaru dari berbagai sumber berita dan menganalisisnya secara otomatis menggunakan AI.",
        "action.btn": "🚀 Kumpulkan & Analisis Data Sekarang",
        "action.loading": "⏳ AI Sedang Memproses Data...",
        "action.loadingDesc": "Sistem sedang mengambil, membaca, dan menganalisis aksi korporasi secara real-time.",
        "action.success": "✅ Pipeline AI Selesai!",
        
        // Feed section
        "feed.title": "Corporate Action Feed",
        "feed.filter.all": "Semua",
        "feed.filter.konglo": "Konglomerat",
        "feed.filter.backdoor": "Backdoor Listing",
        "feed.empty": "Tidak ada dokumen korporasi yang ditemukan atau semua sudah terproses.",
        
        // Card section
        "card.analysis": "Analisis Strategis:",
        "card.source": "Sumber",
        "card.date": "Tanggal",
        "card.status": "Status",
        "card.status.analyzed": "Dianalisis",
        "card.status.filtered": "Disaring",
        
        // WA Simulator
        "wa.welcome": "Selamat datang di <b>IDX-Intel AI WhatsApp Bot</b>! 🇮🇩<br>Ketik <b>/cek &lt;TICKER&gt;</b> untuk melihat analisis aksi korporasi & konglomerat terkini, atau <b>/summary</b> untuk rekap harian pasar modal.",
        "wa.placeholder": "Ketik perintah (e.g. /cek BUMI)...",
        "wa.quick1": "Cek GOTO",
        "wa.quick2": "Cek BUMI",
        "wa.quick3": "Rekap Hari Ini",
        
        // Footer
        "footer.text": "IDX-Intel AI v2.0.0",
        // Demo Terminal
        "demo.terminal_title": "Terminal Intelligence",
        "demo.terminal_subtitle": "Model: Qwen-3.5-Instruct (Fine-Tuned)",
        "demo.init_msg": "Inisialisasi sistem berhasil. Memuat data pasar terbaru...<br><br>💡 Ketik <b>/cek BUMI</b> atau <b>/cek BBCA</b> untuk melihat simulasi output <i>Corporate Action</i> secara instan.",
        "demo.user_msg": "Halo AI, apakah ada sentimen terbaru mengenai emiten batu bara?",
        "demo.ai_msg": "Halo! Berdasarkan pantauan data real-time, sektor energi khususnya batu bara menunjukkan adanya akumulasi bertahap. Namun, silakan ketik perintah spesifik seperti <b>/cek BUMI</b> untuk melihat detail analisis dari radar Konglomerat kami.",
        "demo.input_placeholder": "Ketik perintah (contoh: /cek BUMI)",
        "demo.btn_execute": "Eksekusi",
        "demo.analyzing": "<i>Menganalisis data pasar...</i>",
        "demo.bumi_intro": "Berikut adalah analisis intelijen untuk BUMI:",
        "demo.bumi_title": "Aksi Borong Saham oleh Pengendali Baru (Salim Group)",
        "demo.bumi_analysis": "<b>Analisis:</b> Terdeteksi adanya akumulasi masif melalui broker-broker terafiliasi. Ini mengindikasikan persiapan konsolidasi aset besar di bawah kendali pemegang saham pengendali baru. Target resisten terdekat ditembus dengan volume tinggi.",
        "demo.bbca_intro": "Berikut adalah analisis intelijen untuk BBCA:",
        "demo.bbca_title": "Pembagian Dividen Interim 2026",
        "demo.bbca_analysis": "<b>Analisis:</b> Berita reguler tentang dividen interim. Tidak ada anomali atau pergerakan uang pintar (Smart Money) yang signifikan di luar siklus normal. Emiten bergerak sesuai valuasi pasar.",
        "demo.unknown_cmd": "Sistem hanya dapat mensimulasikan data untuk perintah <b>/cek BUMI</b> dan <b>/cek BBCA</b> pada mode demo ini. Untuk analisis <i>real-time</i> emiten lain, silakan aktifkan <i>pipeline</i> utama di halaman beranda.",
        "hero.demo": "Demo"
    },
    en: {
        // Navbar
        "nav.brand": "IDX-Intel AI",
        "nav.badge": "MERAH PUTIH",
        "nav.getStarted": "Get Started",
        
        // Hero / PAS Formula
        "hero.problem": "Missing Out on Corporate Actions & Conglomerate Accumulations?",
        "hero.agitate": "Late info means buying at the peak while market makers profit.",
        "hero.solve": "IDX-Intel AI monitors Top 200 conglomerates and filters market noise in real-time.",
        
        // Action section
        "action.title": "⚡ Start Automated Monitoring",
        "action.desc": "Click the button below to collect the latest data from various news sources and analyze it automatically using AI.",
        "action.btn": "🚀 Collect & Analyze Data Now",
        "action.loading": "⏳ AI is Processing Data...",
        "action.loadingDesc": "The system is currently fetching, reading, and analyzing corporate actions in real-time.",
        "action.success": "✅ AI Pipeline Completed!",
        
        // Feed section
        "feed.title": "Corporate Action Feed",
        "feed.filter.all": "All",
        "feed.filter.konglo": "Conglomerates",
        "feed.filter.backdoor": "Backdoor Listing",
        "feed.empty": "No corporate documents found or all have been processed.",
        
        // Card section
        "card.analysis": "Strategic Analysis:",
        "card.source": "Source",
        "card.date": "Date",
        "card.status": "Status",
        "card.status.analyzed": "Analyzed",
        "card.status.filtered": "Filtered",
        
        // WA Simulator
        "wa.welcome": "Welcome to <b>IDX-Intel AI WhatsApp Bot</b>! 🇮🇩<br>Type <b>/cek &lt;TICKER&gt;</b> to view the latest corporate action & conglomerate analysis, or <b>/summary</b> for a daily market recap.",
        "wa.placeholder": "Type command (e.g. /cek BUMI)...",
        "wa.quick1": "Check GOTO",
        "wa.quick2": "Check BUMI",
        "wa.quick3": "Today's Recap",
        
        // Footer
        "footer.text": "IDX-Intel AI v2.0.0",
        "footer.copy": "© 2026 Ternak Automation",
        
        // Demo Terminal
        "demo.terminal_title": "Terminal Intelligence",
        "demo.terminal_subtitle": "Model: Qwen-3.5-Instruct (Fine-Tuned)",
        "demo.init_msg": "System initialization successful. Loading latest market data...<br><br>💡 Type <b>/cek BUMI</b> or <b>/cek BBCA</b> to instantly see the simulated <i>Corporate Action</i> output.",
        "demo.user_msg": "Hello AI, are there any recent sentiments regarding coal issuers?",
        "demo.ai_msg": "Hello! Based on real-time monitoring, the energy sector, particularly coal, is showing gradual accumulation. However, please type a specific command like <b>/cek BUMI</b> to see detailed analysis from our Conglomerate radar.",
        "demo.input_placeholder": "Type command (e.g., /cek BUMI)",
        "demo.btn_execute": "Execute",
        "demo.analyzing": "<i>Analyzing market data...</i>",
        "demo.bumi_intro": "Here is the intelligence analysis for BUMI:",
        "demo.bumi_title": "Massive Share Buyback by New Controlling Shareholder (Salim Group)",
        "demo.bumi_analysis": "<b>Analysis:</b> Massive accumulation detected through affiliated brokers. This indicates preparation for major asset consolidation under the new controlling shareholder. The nearest resistance target breached with high volume.",
        "demo.bbca_intro": "Here is the intelligence analysis for BBCA:",
        "demo.bbca_title": "Interim Dividend Distribution 2026",
        "demo.bbca_analysis": "<b>Analysis:</b> Regular news about interim dividends. No significant anomalies or Smart Money movements outside the normal cycle. The issuer is moving in line with market valuation.",
        "demo.unknown_cmd": "The system can only simulate data for <b>/cek BUMI</b> and <b>/cek BBCA</b> commands in this demo mode. For <i>real-time</i> analysis of other issuers, please activate the main <i>pipeline</i> on the home page.",
        "hero.demo": "Demo"
    }
};

let currentLang = localStorage.getItem('idx_lang') || 'id';

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            // Check if it's an input placeholder
            if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
                el.setAttribute('placeholder', translations[currentLang][key]);
            } else {
                el.innerHTML = translations[currentLang][key];
            }
        }
    });
    
    // Update toggle button text
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
    
    // Update dynamically rendered content if exists
    if (typeof liveAiData !== 'undefined' && liveAiData.length > 0) {
        renderCards(liveAiData);
    }
}

// Apply on load
document.addEventListener('DOMContentLoaded', applyTranslations);
