// MOVE THIS TO THE TOP OF script.js
function toggleReadMore(id, fullText) {
    const title = document.getElementById(`title-${id}`);
    const link = document.getElementById(`link-${id}`);
    if (title) title.innerText = fullText;
    if (link) link.style.display = 'none';
}

/**
 * 1. SECURITY & AUTH GUARD (TEMP FIX FOR TESTING)
 * Allows dashboard, history, templates_page without login
 */
(function checkSecurity() {
    const sessionData = localStorage.getItem("userSession");
    const user = sessionData ? JSON.parse(sessionData) : null;
    const path = window.location.pathname;

    // Allow main pages during testing
    const allowedPaths = ["/", "/dashboard", "/history", "/templates_page"];

    if (!user && !allowedPaths.includes(path)) {
        console.log("Security bypass active (testing mode):", path);
        // NO redirect during testing
    }
})();

/**
 * 2. UI UPDATES
 */
function updateUI() {
    const sessionData = localStorage.getItem("userSession");
    if (sessionData) {
        const user = JSON.parse(sessionData);
        
        const nameHeading =
            document.querySelector('.user-info h4') ||
            document.querySelector('.user-name');

        const emailPara =
            document.querySelector('.user-info p') ||
            document.querySelector('.user-email');

        if (nameHeading) nameHeading.innerText = user.name;
        if (emailPara) emailPara.innerText = user.email;

        
    }
}

/**
 * 3. CHAT & AI LOGIC
 */
async function sendQuery() {

    const inputField =
        document.querySelector('.search-bar input') ||
        document.querySelector('input[type="text"]');

    const question = inputField ? inputField.value.trim() : "";

    if (!question) return;

    const sqlBox =
        document.querySelector('.generated-sql-content p') ||
        document.querySelector('.sql-box');

    if (sqlBox) sqlBox.innerText = "Generating SQL...";

    try {

        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();


        // ✅ ADD THIS BLOCK
       // ✅ HANDLE BOTH error AND blocked
if (data.status === "error" || data.status === "blocked") {

    if (sqlBox)
        sqlBox.innerText = data.message;

    console.log("Blocked/Error:", data.message);

    return;
}

        if (sqlBox)
            sqlBox.innerText =
                data.sql || data.sql_query || "No SQL generated";


        if (data.rows || data.results)
            console.log("Database Results:", data.rows || data.results);

    } catch (error) {

        console.error("Connection Error:", error);

        if (sqlBox)
            sqlBox.innerText =
                "Error connecting to server.";
    }
}

/**
 * 4. LOGOUT
 */
function handleLogout() {
    localStorage.removeItem("userSession");
    window.location.href = "/";
}

/**
 * 5. INITIALIZATION
 */
document.addEventListener("DOMContentLoaded", () => {

    updateUI();

    const searchBtn =
        document.querySelector('.ph-magnifying-glass')?.parentElement ||
        document.querySelector('.search-button');

    if (searchBtn)
        searchBtn.addEventListener('click', sendQuery);

    const inputField =
        document.querySelector('.search-bar input') ||
        document.querySelector('input[type="text"]');

    if (inputField) {
        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter')
                sendQuery();
        });
    }

});

/**
 * SAVE TEMPLATE
 */
function saveAsTemplate(question, sql) {

    let templates =
        JSON.parse(localStorage.getItem("myTemplates")) || [];

    const newTemplate = {
        id: Date.now(),
        title: question,
        sql: sql,
        category: "History"
    };

    templates.unshift(newTemplate);

    localStorage.setItem(
        "myTemplates",
        JSON.stringify(templates)
    );

    alert("Template saved!");
}

/**
 * RENDER TEMPLATES
 */
function renderTemplates(templates) {

    const container =
        document.getElementById('templateContainer');

    if (!container) return;

    container.innerHTML = '';

    templates.forEach(temp => {

        const isLong =
            temp.question.length > 50;

        const displayPrompt =
            isLong ?
            temp.question.substring(0, 50) + "..."
            : temp.question;

        container.innerHTML += `

            <div class="template-card"
                style="
                margin-bottom:20px;
                padding:20px;
                border:1px solid #eee;
                border-radius:12px;">

                <h3 id="title-${temp.id}"
                    style="
                    font-size:18px;
                    color:#0d4a33;
                    margin-bottom:10px;">

                    ${displayPrompt}

                </h3>

                ${
                    isLong ?
                    `<a href="javascript:void(0)"
                    id="link-${temp.id}"
                    onclick="toggleReadMore('${temp.id}', \`${temp.question.replace(/'/g, "\\'")}\`)"
                    style="
                    color:#1E8F5B;
                    font-size:14px;
                    font-weight:bold;
                    text-decoration:none;">
                    Read More</a>`
                    : ''
                }

                <div class="sql-box"
                    style="
                    background:#f4f4f4;
                    padding:15px;
                    border-radius:8px;
                    font-family:monospace;
                    margin:15px 0;">

                    ${temp.sql_query}

                </div>

                <div style="display:flex;gap:10px;">

                    <button class="use-btn"
                        onclick="useTemplate(\`${temp.sql_query}\`)">
                        Use Template
                    </button>

                    <button class="delete-btn"
                        onclick="deleteTemplate('${temp.id}')"
                        style="
                        background:#fff;
                        color:#ff4d4d;
                        border:1px solid #ff4d4d;
                        padding:10px 20px;
                        border-radius:10px;
                        cursor:pointer;">
                        Delete
                    </button>

                </div>

            </div>
        `;
    });
}

/**
 * TEMPLATE HANDLER
 */
document.addEventListener("DOMContentLoaded", () => {

    const inputField =
        document.getElementById('userInput');

    const pending =
        localStorage.getItem('pendingQuery');

    if (pending && inputField) {

        inputField.value = pending;

        localStorage.removeItem('pendingQuery');

        if (typeof handleSend === "function")
            handleSend();
    }

});

/**
 * EXECUTE QUERY
 */
function executeQuery() {

    const userQuery =
        document.getElementById('queryInput').value;

    fetch('/api/query', {})
        .then(res => res.json())
        .then(data => {

            updateTable(data);

            renderProfessionalChart(data);

        });
}

/**
 * CHART FUNCTION PLACEHOLDER
 */
function renderProfessionalChart(sqlData) {

    console.log("Chart data:", sqlData);

}