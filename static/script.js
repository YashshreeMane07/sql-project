// MOVE THIS TO THE TOP OF script.js
function toggleReadMore(id, fullText) {
    const title = document.getElementById(`title-${id}`);
    const link = document.getElementById(`link-${id}`);

    if (title) title.innerText = fullText;
    if (link) link.style.display = 'none';
}

/**
 * 1. SECURITY & AUTH GUARD (TEMP FIX FOR TESTING)
 */
(function checkSecurity() {

    const sessionData = localStorage.getItem("userSession");
    const user = sessionData ? JSON.parse(sessionData) : null;
    const path = window.location.pathname;

    const allowedPaths = [
        "/",
        "/dashboard",
        "/history",
        "/templates_page"
    ];

    if (!user && !allowedPaths.includes(path)) {

        console.log(
            "Security bypass active (testing mode):",
            path
        );

    }

})();

/**
 * 2. UI UPDATE
 */
function updateUI() {

    const sessionData =
        localStorage.getItem("userSession");

    if (!sessionData) return;

    const user =
        JSON.parse(sessionData);

    const nameHeading =
        document.querySelector('.user-info h4') ||
        document.querySelector('.user-name');

    const emailPara =
        document.querySelector('.user-info p') ||
        document.querySelector('.user-email');

    if (nameHeading)
        nameHeading.innerText = user.name;

    if (emailPara)
        emailPara.innerText = user.email;

}

/**
 * 3. SEND QUERY TO BACKEND
 */
async function sendQuery() {

    const inputField =
        document.querySelector('.search-bar input') ||
        document.querySelector('input[type="text"]');

    const question =
        inputField ?
        inputField.value.trim() :
        "";

    if (!question) return;

    const sqlBox =
        document.querySelector('.generated-sql-content p') ||
        document.querySelector('.sql-box');

    if (sqlBox)
        sqlBox.innerText = "Generating SQL...";

    try {

        const response =
            await fetch('/ask', {

                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({
                    question: question
                })

            });

        const data =
            await response.json();

        // HANDLE BLOCK / ERROR
        if (
            data.status === "error" ||
            data.status === "blocked"
        ) {

            if (sqlBox)
                sqlBox.innerText =
                data.message;

            console.log(
                "Blocked/Error:",
                data.message
            );

            return;
        }

        if (sqlBox)
            sqlBox.innerText =
            data.sql ||
            data.sql_query ||
            "No SQL generated";

        if (data.rows || data.results)
            console.log(
                "DB Results:",
                data.rows || data.results
            );

    }
    catch (error) {

        console.error(
            "Connection Error:",
            error
        );

        if (sqlBox)
            sqlBox.innerText =
            "Server connection error.";

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
 * 5. PAGE INIT
 */
document.addEventListener(
    "DOMContentLoaded",
    () => {

        updateUI();

        const searchBtn =
            document.querySelector('.ph-magnifying-glass')
            ?.parentElement ||
            document.querySelector('.search-button');

        if (searchBtn)
            searchBtn.addEventListener(
                'click',
                sendQuery
            );

        const inputField =
            document.querySelector('.search-bar input') ||
            document.querySelector('input[type="text"]');

        if (inputField) {

            inputField.addEventListener(
                'keypress',
                (e) => {

                    if (e.key === 'Enter')
                        sendQuery();

                });

        }

    });

/**
 * 6. SAVE TEMPLATE (FIXED)
 */
function saveAsTemplate(question, sql) {

    let templates =
        JSON.parse(
            localStorage.getItem("myTemplates")
        ) || [];

    const newTemplate = {

        id: Date.now(),

        title: question,   // FULL prompt saved

        sql: sql,          // SQL saved correctly

        category: "History",

        dateCreated:
            new Date()
            .toLocaleString()

    };

    templates.unshift(newTemplate);

    localStorage.setItem(
        "myTemplates",
        JSON.stringify(templates)
    );

    alert("Template saved!");

}

/**
 * 7. RENDER TEMPLATES (FULL PROMPT FIXED)
 */
function renderTemplates(templates) {

    const container =
        document.getElementById(
            'templateContainer'
        );

    if (!container) return;

    container.innerHTML = '';

    templates.forEach(temp => {

        // SHOW FULL PROMPT (NO TRUNCATION)
        const displayPrompt =
            temp.title ||
            temp.question ||
            "Untitled Query";

        const sqlCode =
            temp.sql ||
            temp.sql_query ||
            "No SQL";

        container.innerHTML += `

        <div class="template-card"
            style="
                margin-bottom:20px;
                padding:20px;
                border:1px solid #eee;
                border-radius:12px;
                background:white;
            ">

            <h3 id="title-${temp.id}"
                style="
                    font-size:18px;
                    color:#0d4a33;
                    margin-bottom:10px;
                    word-break:break-word;
                ">

                ${displayPrompt}

            </h3>

            <div class="sql-box"
                style="
                    background:#f4f4f4;
                    padding:15px;
                    border-radius:8px;
                    font-family:monospace;
                    margin:15px 0;
                    word-break:break-word;
                ">

                ${sqlCode}

            </div>

            <div style="
                display:flex;
                gap:10px;
            ">

                <button class="use-btn"
                    onclick="useTemplate(\`${sqlCode}\`)">

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
                        cursor:pointer;
                    ">

                    Delete

                </button>

            </div>

        </div>

        `;

    });

}

/**
 * 8. HANDLE PENDING QUERY
 */
document.addEventListener(
    "DOMContentLoaded",
    () => {

        const inputField =
            document.getElementById(
                'userInput'
            );

        const pending =
            localStorage.getItem(
                'pendingQuery'
            );

        if (pending && inputField) {

            inputField.value =
                pending;

            localStorage.removeItem(
                'pendingQuery'
            );

            if (typeof handleSend === "function")
                handleSend();

        }

    });

/**
 * 9. EXECUTE QUERY
 */
function executeQuery() {

    const userQuery =
        document.getElementById(
            'queryInput'
        ).value;

    fetch('/api/query', {})
    .then(res => res.json())
    .then(data => {

        updateTable(data);

        renderProfessionalChart(data);

    });

}

/**
 * 10. CHART PLACEHOLDER
 */
function renderProfessionalChart(sqlData) {

    console.log(
        "Chart data:",
        sqlData
    );

}