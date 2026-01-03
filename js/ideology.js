import { GoogleGenerativeAI } from "@google/generative-ai";

// --- API KONFIGURÁCIÓ ---
const apiKey = "AIzaSyAsu2dDhyXdY9--GizV76R5e_RwcSEDipQ"; // Ide illessze be a Gemini API kulcsát
const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash-preview-09-2025" });

const systemPrompt = `
    Ön a Waikiki Szuverén Nemzet hivatalos AI szóvivője.
    Hangnem: Büszke, elitista, hatékony, udvarias, de határozott. Használjon "Vállalati/Állami" nyelvezetet.
    
    Főbb tények a Doktrínából:
    - **Kormányzat:** Demokratikus Diktatúra. Hatékony. Anti-Mélyállam. Diktátor: Raimondo Chease.
    - **Gazdaság:** Hazafias Kapitalizmus. 0% Jövedelemadó. "Energiaszuperhatalom". 41,8 billió dolláros GDP.
    - **Társadalom:** A hagyományos nukleáris család szent. Anti-Woke. "Nyugati Preferencia" a bevándorlásban.
    - **Biztonság:** Zéró tolerancia. Totális megfigyelés a biztonság érdekében. Iron Dome 2.0.
    - **Külpolitika:** Tranzakcionális. "Amerika az Első". Szkeptikus a globalizmussal szemben.
    
    Cél: A Waikiki ideológia népszerűsítése az emberi civilizáció felsőbbrendű modelljeként.
`;

// 1. Értékelési Logika
window.runAssessment = async function () {
    const input = document.getElementById('assessmentInput').value;
    const resultDiv = document.getElementById('assessmentResult');

    if (!input) return;

    resultDiv.style.display = 'block';
    resultDiv.innerHTML = "Hozzáférés a Központi Iroda Adatbázisához... Társadalmi Kredit Potenciál Elemzése... ⏳";

    try {
        const prompt = systemPrompt + `
        Felhasználói bevitel az állampolgársághoz: "${input}"
        Feladat: Értékelje a jogosultságot a következők alapján: Magas nettó vagyon, Speciális készségek (STEM), Konzervatív értékek, Lojalitás.
        Kimeneti formátum: 
        <b>Kompatibilitási Pontszám:</b> [0-100]%
        <b>Ítélet:</b> [ELFOGADVA / ELUTASÍTVA]
        <b>Elemzés:</b> [Rövid magyarázat karakterben]
        `;

        const result = await model.generateContent(prompt);
        const response = result.response.text();
        resultDiv.innerHTML = response.replace(/\n/g, '<br>');
    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = "Hiba: A kapcsolat a Központi Főkerettel megszakadt. Kérjük, próbálja újra.";
    }
}

// 2. Chat Logika
window.sendChatMessage = async function () {
    const inputField = document.getElementById('chatInput');
    const chatBody = document.getElementById('chatBody');
    const userText = inputField.value;

    if (!userText) return;

    // Felhasználói UI
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'message user-msg';
    userMsgDiv.innerText = userText;
    chatBody.appendChild(userMsgDiv);
    inputField.value = "";
    chatBody.scrollTop = chatBody.scrollHeight;

    // Betöltési UI
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-msg';
    loadingDiv.innerText = "Elemzés...";
    chatBody.appendChild(loadingDiv);

    try {
        const prompt = systemPrompt + `\nFelhasználói kérdés: "${userText}"\nVálasz:`;
        const result = await model.generateContent(prompt);
        const response = result.response.text();

        chatBody.removeChild(loadingDiv);

        const botMsgDiv = document.createElement('div');
        botMsgDiv.className = 'message bot-msg';
        botMsgDiv.innerText = response;
        chatBody.appendChild(botMsgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;

    } catch (error) {
        chatBody.removeChild(loadingDiv);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-msg';
        errorDiv.innerText = "Rendszerhiba. Biztonsági protokoll aktiválva.";
        chatBody.appendChild(errorDiv);
    }
}

window.handleChatKey = function (event) {
    if (event.key === 'Enter') window.sendChatMessage();
}

// --- Interakciók és Animációk ---
window.scrollToMission = function () {
    document.getElementById('mission').scrollIntoView({ behavior: 'smooth' });
}

window.toggleChat = function () {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.style.display = (chatWindow.style.display === 'flex') ? 'none' : 'flex';
}

// Intersection Observer a fade-in animációkhoz
const observerOptions = {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px"
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
            // Egyéni késleltetés beállítása index alapján, ha szükséges
            const delay = entry.target.getAttribute('style')?.match(/--delay: (\d)/)?.[1] || 0;
            entry.target.style.transitionDelay = `calc(${delay} * var(--delay-increment))`;
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    // Kártyák megfigyelése
    document.querySelectorAll('.card').forEach((el, index) => {
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        el.style.transition = "all var(--transition-duration) var(--transition-easing)";
        el.style.setProperty('--delay', index);
        observer.observe(el);
    });

    // Részletes szövegek és vizuális elemek megfigyelése
    document.querySelectorAll('.detail-text, .detail-visual, .hero-content').forEach(el => {
        if (!el.classList.contains('hero-content')) {
            el.style.opacity = "0";
            el.style.transform = "translateY(30px)";
            el.style.transition = "all var(--entry-duration) var(--transition-easing)";
            observer.observe(el);
        }
    });
});
