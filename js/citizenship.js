const { useState, useEffect } = React;

// --- ADATOK: KÉRDÉSEK ÉS OPCIÓK ---
const questionsData = [
    // I. DEMOGRÁFIA
    {
        id: 1, section: "Demográfia", text: "Mely régió állampolgára Ön elsődlegesen?",
        options: [
            { label: "OECD tagállam (EU, USA, CAN, AUS, NZ, JPN, KOR)", points: 5 },
            { label: "Latin-Amerika (MERCOSUR államok)", points: 3 },
            { label: "Egyéb régió", points: 0 }
        ]
    },
    {
        id: 2, section: "Demográfia", text: "Hány éves Ön?",
        options: [
            { label: "25 - 45 év között (Gazdaságilag legaktívabb)", points: 4 },
            { label: "20 - 24 év vagy 46 - 55 év között", points: 2 },
            { label: "55 év felett vagy 20 év alatt", points: 0 }
        ]
    },
    {
        id: 3, section: "Demográfia", text: "Mi a jelenlegi családi állapota?",
        options: [
            { label: "Házas, legalább 1 gyermekkel (Nukleáris család)", points: 4 },
            { label: "Házas, gyermektelen", points: 2 },
            { label: "Egyedülálló / Elvált", points: 0 }
        ]
    },
    {
        id: 4, section: "Demográfia", text: "Milyen szinten beszél angolul és van-e stratégiai nyelvtudása?",
        options: [
            { label: "Angol (C1) + Stratégiai nyelv (Mandarin, Orosz, Arab)", points: 4 },
            { label: "Angol (C1)", points: 2 },
            { label: "Angol (B2 vagy alatta)", points: 0, fatal: true }
        ]
    },
    {
        id: 5, section: "Demográfia", text: "Hány napot garantál, hogy fizikailag Waikiki területén tölt évente?",
        options: [
            { label: "Több mint 183 nap (Adóügyi illetőség)", points: 3 },
            { label: "90 - 182 nap", points: 1 },
            { label: "Kevesebb mint 90 nap", points: 0 }
        ]
    },
    // II. GAZDASÁG
    {
        id: 6, section: "Gazdaság", text: "Mi a legmagasabb iskolai végzettsége?",
        options: [
            { label: "STEM PhD vagy Tier 1 diploma (Fúzió, AI, Orvosi)", points: 8 },
            { label: "MSc/MA diploma piaci tapasztalattal", points: 5 },
            { label: "BSc/BA diploma", points: 2 },
            { label: "Nincs felsőfokú végzettségem", points: 0 }
        ]
    },
    {
        id: 7, section: "Gazdaság", text: "Mekkora az Ön igazolt, azonnal mozgósítható likvid vagyona (USD)?",
        options: [
            { label: "Több mint $10,000,000", points: 8 },
            { label: "Több mint $5,000,000", points: 5 },
            { label: "Több mint $250,000", points: 3 },
            { label: "Kevesebb mint $250,000", points: 0 }
        ]
    },
    {
        id: 8, section: "Gazdaság", text: "Vagyonának mekkora hányadát hajlandó a Waikiki Nemzeti Bankba transzferálni?",
        options: [
            { label: "100% (Teljes pénzügyi áttelepülés)", points: 6 },
            { label: "50% - 99%", points: 4 },
            { label: "Kevesebb mint 50%", points: 0 }
        ]
    },
    {
        id: 9, section: "Gazdaság", text: "Milyen ingatlanvásárlást tervez az első évben?",
        options: [
            { label: "Új építésű ingatlan fejlesztési területen (min. $2M)", points: 5 },
            { label: "Használt vagy kisebb értékű ingatlan", points: 3 },
            { label: "Csak bérelni tervezek", points: 0 }
        ]
    },
    {
        id: 10, section: "Gazdaság", text: "Volt-e cége csődeljárás alatt az elmúlt 10 évben?",
        options: [
            { label: "Soha, minden vállalkozásom stabil", points: 5 },
            { label: "Igen, de mindenkit kifizettünk", points: 2 },
            { label: "Igen, csőddel végződött", points: 0, fatal: true }
        ]
    },
    {
        id: 11, section: "Gazdaság", text: "Jövedelmének hány százaléka passzív forrás?",
        options: [
            { label: "Több mint 75%", points: 4 },
            { label: "25% - 74%", points: 2 },
            { label: "Kevesebb mint 25%", points: 0 }
        ]
    },
    {
        id: 12, section: "Gazdaság", text: "Hajlandó-e tőkét fektetni állami stratégiai startupba (min. $250k)?",
        options: [
            { label: "Igen, azonnal", points: 4 },
            { label: "Megfontolom az üzleti terv alapján", points: 2 },
            { label: "Nem", points: 0 }
        ]
    },
    // III. IDEOLÓGIA
    {
        id: 13, section: "Ideológia", text: "Vészhelyzetben elfogadja a magánszámlák 15%-ának ideiglenes zárolását védelmi kötvényért?",
        options: [
            { label: "Azonnal aláírom (Lojalitás)", points: 6 },
            { label: "Mentesítést kérelmezek", points: 3 },
            { label: "Jogi útra terelem / Menekítem a vagyont", points: 0 }
        ]
    },
    {
        id: 14, section: "Ideológia", text: "Hány polgári peres eljárásban vett részt az elmúlt 5 évben?",
        options: [
            { label: "0 (Konfliktusmentes)", points: 5 },
            { label: "1-2 (Normál üzleti kockázat)", points: 3 },
            { label: "3 vagy több", points: -5 }
        ]
    },
    {
        id: 15, section: "Ideológia", text: "Hányszor függesztették fel közösségi média fiókját moderációs okokból?",
        options: [
            { label: "Soha", points: 5 },
            { label: "Egyszer, tévedésből", points: 2 },
            { label: "Többször / Végleges tiltás", points: 0, fatal: true }
        ]
    },
    {
        id: 16, section: "Ideológia", text: "Hova íratná gyermekét a waikiki szegregált, teljesítményalapú oktatási rendszerben?",
        options: [
            { label: "Elit, versenyalapú tehetséggondozóba", points: 4 },
            { label: "Átlagos állami iskolába", points: 2 },
            { label: "Magántanulónak (verseny elutasítása)", points: 0 }
        ]
    },
    {
        id: 17, section: "Ideológia", text: "Embargó esetén megszakítja-e kapcsolatát származási országával?",
        options: [
            { label: "Azonnal megszüntetem az üzleti kapcsolatot", points: 5 },
            { label: "Külön engedélyt kérek", points: 2 },
            { label: "Kijátszom az embargót", points: 0, fatal: true }
        ]
    },
    {
        id: 18, section: "Ideológia", text: "Hajlandó-e átadni teljes biometrikus profilját a 'The Watcher' rendszernek?",
        options: [
            { label: "Igen, teljes körűen", points: 5 },
            { label: "Csak a törvényi minimumot", points: 2 },
            { label: "Nem, elutasítom", points: 0, fatal: true }
        ]
    },
    {
        id: 19, section: "Ideológia", text: "Hajlandó-e 5 éves egészségügyi fedezeti alapot befizetni kockázat esetén?",
        options: [
            { label: "Igen, elfogadom", points: 5 },
            { label: "Csak ha visszatérítendő", points: 3 },
            { label: "Nem, ingyenes ellátást várok", points: 0 }
        ]
    },
    {
        id: 20, section: "Ideológia", text: "Volt-e tagja radikális politikai szervezetnek?",
        options: [
            { label: "Soha, semleges vagyok", points: 5 },
            { label: "Régen, diákként", points: 0 },
            { label: "Igen, jelenleg is", points: 0, fatal: true }
        ]
    }
];

// --- COMPONENTS ---

const colors = {
    primary: '#0071BC',
    secondary: '#0E308E',
    tertiary: '#00B0C3',
    gold: '#BC9200',
    silver: '#9CA3AF',
    bronze: '#B45309',
    dark: '#0A1930',
    light: '#F5F9FC',
    white: '#FFFFFF',
    danger: '#DC2626'
};

const AssessmentForm = ({ onClose }) => {
    const [currentQ, setCurrentQ] = useState(0);
    const [score, setScore] = useState(0);
    const [isFatal, setIsFatal] = useState(false);
    const [stage, setStage] = useState('intro'); // intro, quiz, analyzing, result

    const handleOptionClick = (points, fatal) => {
        const newScore = score + points;
        setScore(newScore);

        if (fatal) {
            setIsFatal(true);
        }

        if (currentQ < questionsData.length - 1) {
            setCurrentQ(currentQ + 1);
        } else {
            setStage('analyzing');
        }
    };

    useEffect(() => {
        if (stage === 'analyzing') {
            const timer = setTimeout(() => {
                setStage('result');
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [stage]);

    // ÚJ: 4 Szintű Tier Rendszer + Elutasítás
    const getTier = () => {
        if (isFatal) return 'REJECTED';
        if (score >= 90) return 'GOLD';
        if (score >= 75) return 'SILVER';
        if (score >= 60) return 'BRONZE';
        if (score >= 45) return 'BLUE';
        return 'REJECTED';
    };

    const tier = getTier();
    const progress = (currentQ / questionsData.length) * 100;

    const renderIntro = () => (
        <div className="text-center p-6">
            <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <i className="fas fa-scale-balanced text-4xl" style={{ color: colors.gold }}></i>
            </div>
            <h3 className="text-3xl font-bold mb-4" style={{ color: colors.secondary }}>W-MAP Protokoll</h3>
            <p className="text-gray-600 mb-6">A Waikiki Merit Assessment Protocol egy többszintű értékelési rendszer. Célunk nem csak a vagyon, hanem a tehetség és az elkötelezettség mérése. A rendszer 4 jogosultsági szintet különböztet meg.</p>
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg text-sm text-left mb-8">
                <p className="font-bold text-yellow-800 mb-2"><i className="fas fa-triangle-exclamation mr-2"></i>Figyelmeztetés</p>
                <ul className="list-disc list-inside text-yellow-700 space-y-1">
                    <li>A válaszai jogi kötelezettségvállalásnak minősülnek.</li>
                    <li>A "The Watcher" AI minden adatot ellenőriz a háttérben.</li>
                    <li>A hamis adatszolgáltatás automatikus kitiltással jár.</li>
                </ul>
            </div>
            <button onClick={() => setStage('quiz')} className="w-full py-4 rounded-lg text-white font-bold text-lg shadow-lg hover:scale-[1.02] transition-transform" style={{ backgroundColor: colors.primary }}>Értékelés Indítása</button>
        </div>
    );

    const renderQuiz = () => {
        const q = questionsData[currentQ];
        return (
            <div className="p-6">
                <div className="mb-6">
                    <div className="flex justify-between text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
                        <span>{q.section}</span>
                        <span>{currentQ + 1} / {questionsData.length}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full transition-all duration-500 ease-out" style={{ width: `${progress}%`, backgroundColor: colors.gold }}></div>
                    </div>
                </div>

                <h4 className="text-xl md:text-2xl font-bold mb-8 text-gray-800 leading-snug">{q.text}</h4>

                <div className="space-y-3">
                    {q.options.map((opt, idx) => (
                        <button key={idx} onClick={() => handleOptionClick(opt.points, opt.fatal)} className="w-full text-left p-4 rounded-xl border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-all group flex items-start gap-3">
                            <div className="w-6 h-6 rounded-full border-2 border-gray-300 group-hover:border-blue-500 flex-shrink-0 mt-0.5"></div>
                            <span className="text-gray-700 font-medium group-hover:text-blue-900">{opt.label}</span>
                        </button>
                    ))}
                </div>
            </div>
        );
    };

    const renderAnalyzing = () => (
        <div className="text-center p-12 flex flex-col items-center justify-center h-full">
            <div className="w-24 h-24 rounded-full border-4 border-t-transparent animate-spin mb-8" style={{ borderColor: `${colors.gold} transparent ${colors.gold} ${colors.gold}` }}></div>
            <h3 className="text-2xl font-bold mb-2 animate-pulse" style={{ color: colors.secondary }}>The Watcher Elemzése...</h3>
            <p className="text-gray-500 text-sm">Biometrikus adatok ellenőrzése...<br/>Pénzügyi háttér validálása...<br/>Social Credit pontszámítás...</p>
        </div>
    );

    const renderResult = () => {
        let title, desc, icon, bgClass, btnText, badge;

        switch (tier) {
            case 'GOLD':
                title = 'GOLD TIER: Stratégiai Vagyontárgy';
                desc = 'Azonnali állampolgárság. Ön a tökéletes jelölt. Nincs várakozási idő, nincs ingatlanminimum, VIP ügyintézés.';
                icon = 'fas fa-crown';
                bgClass = 'bg-gradient-to-b from-yellow-50 to-white border-yellow-400';
                btnText = 'Hivatalos Kérelem ($5,000)';
                badge = '90+ PONT';
                break;
            case 'SILVER':
                title = 'SILVER TIER: Kiemelt Befektető';
                desc = 'Gyorsított eljárás. Állampolgárság 1 év után, feltéve, hogy teljesíti a $1M kötvényvásárlást és az ingatlanbefektetést.';
                icon = 'fas fa-medal';
                bgClass = 'bg-gray-50 border-gray-400';
                btnText = 'Befektetési Terv Indítása';
                badge = '75-89 PONT';
                break;
            case 'BRONZE':
                title = 'BRONZE TIER: Szakképzett Rezidens';
                desc = 'Letelepedési engedély (Residency). Állampolgárság 5 év után kérvényezhető. Biztonsági letét ($100k) és igazolt munkaviszony szükséges.';
                icon = 'fas fa-user-shield';
                bgClass = 'bg-orange-50 border-orange-300';
                btnText = 'Letelepedési Kérelem';
                badge = '60-74 PONT';
                break;
            case 'BLUE':
                title = 'BLUE TIER: Talent / Nomad Vízum';
                desc = 'Ideiglenes munkavállalói státusz. Fiatal tehetségeknek, akik nem rendelkeznek nagy vagyonnal, de kritikus tudással igen. 10 éves út az állampolgárságig.';
                icon = 'fas fa-laptop-code';
                bgClass = 'bg-blue-50 border-blue-300';
                btnText = 'Talent Program Jelentkezés';
                badge = '45-59 PONT';
                break;
            default:
                title = 'ELUTASÍTVA: High Risk';
                desc = isFatal ? 'A rendszer KIZÁRÓ OKOT (Red Flag) azonosított. Kérelmét elutasítottuk.' : 'Pontszáma (45 alatt) nem éri el a minimális belépési küszöböt.';
                icon = 'fas fa-ban';
                bgClass = 'bg-red-50 border-red-200';
                btnText = 'Bezárás';
                badge = 'ELÉGTELEN';
        }

        return (
            <div className="p-8 text-center animate-fade-up">
                <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl text-3xl ${tier === 'REJECTED' ? 'bg-red-100 text-red-600' : 'bg-white'}`} style={{ color: tier === 'GOLD' ? colors.gold : tier === 'SILVER' ? colors.silver : tier === 'BRONZE' ? colors.bronze : tier === 'BLUE' ? colors.primary : '' }}>
                    <i className={icon}></i>
                </div>

                <div className={`p-6 rounded-xl border-2 mb-8 relative overflow-hidden ${bgClass}`}>
                    <div className="absolute top-0 right-0 px-3 py-1 bg-black/10 text-xs font-bold rounded-bl-lg">{badge}</div>
                    <h3 className="text-2xl font-bold mb-2 text-gray-900">{title}</h3>
                    <div className="text-4xl font-extrabold mb-4" style={{ color: tier === 'REJECTED' ? colors.danger : colors.primary }}>{score} / 100</div>
                    <p className="text-gray-700 leading-relaxed text-sm">{desc}</p>
                </div>

                {tier !== 'REJECTED' && (
                    <div className="text-left bg-gray-50 p-4 rounded-lg mb-6 text-sm text-gray-600">
                        <p><strong>Következő lépés:</strong> A besorolása alapján Ön jogosult a fenti program elindítására. Kérjük, foglaljon időpontot a biometrikus azonosításra.</p>
                    </div>
                )}

                <button onClick={onClose} className={`w-full py-4 rounded-lg text-white font-bold text-lg shadow-lg transition-transform hover:scale-[1.02] ${tier === 'REJECTED' ? 'bg-gray-500' : 'bg-[#BC9200]'}`}>{btnText}</button>
            </div>
        );
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl relative">
                <div className="sticky top-0 bg-white/95 backdrop-blur px-6 py-4 border-b flex justify-between items-center z-10">
                    <span className="font-bold text-gray-400 text-xs tracking-widest">W-MAP v2.1 PROTOCOL</span>
                    <button onClick={onClose} className="text-gray-400 hover:text-red-500 transition-colors"><i className="fas fa-times text-xl"></i></button>
                </div>

                <div className="min-h-[400px]">
                    {stage === 'intro' && renderIntro()}
                    {stage === 'quiz' && renderQuiz()}
                    {stage === 'analyzing' && renderAnalyzing()}
                    {stage === 'result' && renderResult()}
                </div>
            </div>
        </div>
    );
};

// Modal mounting helpers: render AssessmentForm into #modal-root
let modalRoot = null;

function openAssessment() {
    const el = document.getElementById('modal-root');
    if (!el) return;
    if (!modalRoot) modalRoot = ReactDOM.createRoot(el);
    modalRoot.render(React.createElement(AssessmentForm, { onClose: closeAssessment }));
    document.body.style.overflow = 'hidden';
}

function closeAssessment() {
    if (!modalRoot) return;
    modalRoot.unmount();
    modalRoot = null;
    document.body.style.overflow = '';
}

function initAssessmentBindings() {
    document.querySelectorAll('.open-assessment').forEach(btn => {
        btn.addEventListener('click', openAssessment);
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAssessment();
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAssessmentBindings);
} else {
    initAssessmentBindings();
}
