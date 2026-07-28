const message = document.getElementById("resultMessage");
let result;
try { result = JSON.parse(sessionStorage.getItem("interpolationResult")); } catch { result = null; }
if (!result) window.location.replace("/");
else renderResult(result);

function formatNumber(value) {
    if (value === null || value === undefined) return "—";
    return typeof value === "number" ? Number(value.toPrecision(10)).toString() : String(value);
}

function formatExpression(expression) {
    const superscripts = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻" };
    return String(expression)
        .replace(/\b(-?\d+)\.0\b/g, "$1")
        .replace(/(^|[+\-\s])1\*([xy])/g, "$1$2")
        .replace(/(^|[+\-\s])-1\*([xy])/g, "$1-$2")
        .replace(/\*/g, " · ")
        .replace(/ ·  · (-?\d+)/g, (_, power) => [...power].map(char => superscripts[char] || char).join(""))
        .replace(/\s+/g, " ")
        .trim();
}
function makeCell(tag, text) {
    const cell = document.createElement(tag);
    cell.textContent = text;
    return cell;
}

function cleanMathLine(line) {
    return String(line)
        .replace(/\(Variable\s*-\s*([^)]+)\)/g, "(x − $1)")
        .replace(/\b(-?\d+)\.0\b/g, "$1")
        .replace(/(^|[=+\-]\s*)1\*([xy])/g, "$1$2")
        .replace(/(^|[=+\-]\s*)-1\*([xy])/g, "$1−$2")
        .replace(/\*\*(-?\d+)/g, (_, power) => {
            const superscripts = { "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻" };
            return [...power].map(char => superscripts[char] || char).join("");
        })
        .replace(/\*/g, " · ")
        .replace(/ - /g, " − ");
}

function isStepHeading(line) {
    return /^(Input Points:|Input Data|Polynomial|DIVIDED DIFFERENCE TABLE|L\d+\([xy]\))$/i.test(line)
        || (/^[A-Z][A-Z\s]+$/.test(line) && !line.includes("="));
}

function renderSteps(lines) {
    const container = document.getElementById("steps");
    const usefulLines = (lines || []).map(line => String(line).trim()).filter(line =>
        line && !/^[=-]{5,}$/.test(line) && line !== "Interpolation Finished."
    );
    const sections = [];
    let current = null;

    const beginSection = title => {
        current = { title, lines: [] };
        sections.push(current);
    };

    usefulLines.forEach(line => {
        if (/^(LAGRANGE INTERPOLATION|NEWTON DIVIDED DIFFERENCE)$/i.test(line)) return;
        if (/^Substitute [xy] = /i.test(line)) {
            beginSection("Evaluate at the target");
            current.lines.push(line);
        } else if (isStepHeading(line)) {
            const title = line === "Input Data" || line === "Input Points:" ? "Known data points"
                : line === "DIVIDED DIFFERENCE TABLE" ? "Build the difference table"
                : line;
            beginSection(title);
        } else {
            if (!current) beginSection("Set up");
            current.lines.push(line);
        }
    });

    const flow = document.createElement("div");
    flow.className = "calculation-flow";
    sections.filter(section => section.lines.length || /^L\d|Polynomial/.test(section.title)).forEach((section, index) => {
        const card = document.createElement("article");
        card.className = "calculation-step";
        const head = document.createElement("div");
        head.className = "calculation-step-head";
        const number = document.createElement("span");
        number.className = "calculation-index";
        number.textContent = String(index + 1).padStart(2, "0");
        const title = document.createElement("h3");
        title.textContent = section.title;
        head.append(number, title);
        card.appendChild(head);

        const content = document.createElement("div");
        content.className = "calculation-content";
        section.lines.forEach(line => {
            const item = document.createElement("div");
            item.className = /^P\d+\s*=/.test(line) ? "point-chip"
                : /^Answer\s*=/.test(line) ? "answer-line"
                : section.title === "Polynomial" || line.includes("=") || line.startsWith("(") || line.startsWith("/") ? "math-line"
                : "note-line";
            item.textContent = cleanMathLine(line);
            content.appendChild(item);
        });
        card.appendChild(content);
        flow.appendChild(card);
    });
    container.replaceChildren(flow);
}
function renderResult(data) {
    document.getElementById("method").textContent = data.method;
    document.getElementById("answer").textContent = formatNumber(data.answer);
    const variable = /\by\b/.test(data.expression) && !/\bx\b/.test(data.expression) ? "y" : "x";
    document.getElementById("expression").textContent = `f(${variable}) = ${formatExpression(data.expression)}`;
    renderSteps(data.steps);
    const inputTable = document.getElementById("inputTable");
    const inputHead = inputTable.createTHead().insertRow();
    ["#", "x", "y"].forEach(label => inputHead.appendChild(makeCell("th", label)));
    const inputBody = inputTable.createTBody();
    (data.input_table || []).forEach((point, index) => {
        const row = inputBody.insertRow();
        [index + 1, formatNumber(point.x), formatNumber(point.y)].forEach(value => row.appendChild(makeCell("td", value)));
    });
    if (data.difference_table?.length) {
        document.getElementById("differenceSection").hidden = false;
        document.getElementById("stepsNumber").textContent = "04";
        const table = document.getElementById("differenceTable");
        table.className = "difference-table";
        const head = table.createTHead().insertRow();
        const count = Math.max(...data.difference_table.map(row => row.length));
        const superscripts = ["¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"];
        ["x", "f(x)", ...Array.from({ length: count - 2 }, (_, i) => `Δ${superscripts[i] || i + 1} f`)]
            .forEach(label => head.appendChild(makeCell("th", label)));
        const body = table.createTBody();
        data.difference_table.forEach(values => {
            const row = body.insertRow();
            for (let i = 0; i < count; i++) {
                const isEmpty = values[i] === null || values[i] === undefined;
                const cell = makeCell("td", isEmpty ? "" : formatNumber(values[i]));
                if (isEmpty) cell.className = "empty-cell";
                if (i >= 2 && !isEmpty) cell.classList.add("difference-value");
                row.appendChild(cell);
            }
        });
    }
}

document.getElementById("toggleSteps").addEventListener("click", event => {
    const steps = document.getElementById("steps");
    steps.hidden = !steps.hidden;
    event.currentTarget.textContent = steps.hidden ? "Show steps" : "Hide steps";
    event.currentTarget.setAttribute("aria-expanded", String(!steps.hidden));
});
document.getElementById("copyAnswer").addEventListener("click", async event => {
    try {
        await navigator.clipboard.writeText(String(result.answer));
        event.currentTarget.textContent = "Copied";
        setTimeout(() => { event.currentTarget.textContent = "Copy answer"; }, 1400);
    } catch {
        message.textContent = "Copy is unavailable in this browser.";
        message.classList.add("visible");
    }
});
document.getElementById("downloadPDF").addEventListener("click", async event => {
    const button = event.currentTarget;
    button.classList.add("loading");
    button.disabled = true;
    message.classList.remove("visible");
    try {
        const response = await fetch("/download-pdf", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(result) });
        if (!response.ok) {
            const error = await response.json().catch(() => null);
            throw new Error(error?.message || "Report download failed.");
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url; link.download = "Interpolation_Report.pdf"; link.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        message.textContent = error.message;
        message.classList.add("visible");
    } finally {
        button.classList.remove("loading");
        button.disabled = false;
    }
});
