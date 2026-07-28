const tableBody = document.getElementById("tableBody");
const form = document.getElementById("solverForm");
const message = document.getElementById("formMessage");
const submitButton = form.querySelector(".solve-button");
const MAX_POINTS = 25;
const MIN_POINTS = 2;

function safeValue(value) {
    return String(value).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function updateRows() {
    [...tableBody.rows].forEach((row, index) => {
        row.querySelector(".row-index").textContent = String(index + 1).padStart(2, "0");
        row.querySelector(".remove-point").disabled = tableBody.rows.length <= MIN_POINTS;
    });
    document.getElementById("pointCount").textContent = tableBody.rows.length;
    document.getElementById("addRow").disabled = tableBody.rows.length >= MAX_POINTS;
}

function addRow(x = "", y = "") {
    if (tableBody.rows.length >= MAX_POINTS) return;
    const row = document.createElement("tr");
    row.className = "point-row";
    row.innerHTML = `<td class="row-index"></td>
        <td><input type="number" step="any" name="x[]" value="${safeValue(x)}" placeholder="0.00" required inputmode="decimal" aria-label="x value"></td>
        <td><input type="number" step="any" name="y[]" value="${safeValue(y)}" placeholder="0.00" required inputmode="decimal" aria-label="y value"></td>
        <td><button class="remove-point" type="button" aria-label="Remove point">×</button></td>`;
    row.querySelector(".remove-point").addEventListener("click", () => {
        if (tableBody.rows.length > MIN_POINTS) {
            row.classList.add("leaving");
            setTimeout(() => { row.remove(); updateRows(); }, 180);
        }
    });
    tableBody.appendChild(row);
    updateRows();
}

function showMessage(text) {
    message.textContent = text;
    message.classList.toggle("visible", Boolean(text));
}

document.getElementById("addRow").addEventListener("click", () => addRow());

document.querySelectorAll(".segment").forEach(button => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".segment").forEach(item => item.classList.remove("active"));
        button.classList.add("active");
        const findY = button.dataset.mode === "find_y";
        document.getElementById("mode").value = button.dataset.mode;
        document.getElementById("targetSymbol").textContent = findY ? "x" : "y";
        document.getElementById("targetPrefix").textContent = findY ? "x =" : "y =";
        document.getElementById("modeHint").textContent = findY ? "Estimate y at a known x" : "Estimate x at a known y";
    });
});

document.getElementById("method").addEventListener("change", event => {
    document.getElementById("methodHint").textContent = event.target.value === "lagrange"
        ? "Direct basis-polynomial construction" : "Efficient recursive difference table";
});

form.addEventListener("reset", () => {
    setTimeout(() => {
        tableBody.innerHTML = "";
        addRow(1, 2); addRow(2, 5); addRow(4, 17);
        document.querySelector('[data-mode="find_y"]').click();
        showMessage("");
    });
});

form.addEventListener("submit", async event => {
    event.preventDefault();
    showMessage("");
    if (!form.reportValidity()) return;
    const xValues = [...form.querySelectorAll('[name="x[]"]')].map(input => Number(input.value));
    const yValues = [...form.querySelectorAll('[name="y[]"]')].map(input => Number(input.value));
    const mode = document.getElementById("mode").value;
    const independent = mode === "find_y" ? xValues : yValues;
    if (new Set(independent).size !== independent.length) {
        showMessage(`The ${mode === "find_y" ? "x" : "y"} values must be unique for this calculation.`);
        return;
    }
    submitButton.classList.add("loading");
    submitButton.disabled = true;
    try {
        const response = await fetch("/solve", { method: "POST", body: new FormData(form) });
        const data = await response.json().catch(() => null);
        if (!response.ok || !data?.success) throw new Error(data?.message || "The calculation could not be completed.");
        sessionStorage.setItem("interpolationResult", JSON.stringify(data.result));
        window.location.assign("/result");
    } catch (error) {
        showMessage(error.message || "Something went wrong. Please check your values and try again.");
        submitButton.classList.remove("loading");
        submitButton.disabled = false;
    }
});

addRow(1, 2);
addRow(2, 5);
addRow(4, 17);
