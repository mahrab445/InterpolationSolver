from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file
)

import io

from solver import (
    solve,
    summary,
    pdf_information,
    expression_only,
    answer_only
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

# =====================================================
# RESULT PAGE
# =====================================================

@app.route("/result")
def result_page():

    return render_template(
        "result.html"
    )


# =====================================================
# SOLVE
# =====================================================

@app.route("/solve", methods=["POST"])
def solve_route():

    try:

        method = request.form.get(
            "method"
        )

        mode = request.form.get(
            "mode"
        )

        if method not in {"lagrange", "newton"}:
            return jsonify({
                "success": False,
                "message": "Please select a valid interpolation method."
            }), 400

        if mode not in {"find_y", "find_x"}:
            return jsonify({
                "success": False,
                "message": "Please select a valid calculation mode."
            }), 400

        target_value = request.form.get("target")
        if target_value is None or target_value.strip() == "":
            return jsonify({
                "success": False,
                "message": "A target value is required."
            }), 400

        target = float(target_value)

        independent = []
        dependent = []

        x_values = request.form.getlist(
            "x[]"
        )

        y_values = request.form.getlist(
            "y[]"
        )

        for x, y in zip(
                x_values,
                y_values
        ):

            if (
                x.strip() == ""
                or
                y.strip() == ""
            ):

                continue

            independent.append(
                float(x)
            )

            dependent.append(
                float(y)
            )

        if len(independent) < 2:

            return jsonify({

                "success": False,

                "message":
                "Minimum 2 points required."

            }), 400

        result = solve(

            method=method,

            independent=independent,

            dependent=dependent,

            target=target,

            mode=mode

        )

        return jsonify({

            "success": True,

            "result": result

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 400

# =====================================================
# DOWNLOAD PDF
# =====================================================

@app.route("/download-pdf", methods=["POST"])
def download_pdf():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "No valid result data was provided."
            }), 400

        pdf = pdf_information(data)

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()

        styles["Title"].fontSize = 24
        styles["Title"].leading = 30
        styles["Heading2"].fontSize = 16
        styles["Heading2"].leading = 21
        styles["Normal"].fontSize = 12
        styles["Normal"].leading = 17
        styles["Code"].fontSize = 12
        styles["Code"].leading = 17

        elements = []

        elements.append(
            Paragraph(
                "<b>Interpolation Solver Report</b>",
                styles["Title"]
            )
        )

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph(
                f"<b>Method :</b> {pdf['method']}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Answer :</b> {pdf['answer']}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph(
                "<b>Interpolation Expression</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                str(pdf["expression"]),
                styles["Code"]
            )
        )

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph(
                "<b>Input Table</b>",
                styles["Heading2"]
            )
        )

        table_data = [

            ["Index", "X", "Y"]

        ]

        for row in pdf["input_table"]:

            table_data.append([

                row["index"],

                row["x"],

                row["y"]

            ])

        table = Table(table_data)

        table.setStyle(

            TableStyle([

                ("GRID", (0,0), (-1,-1), 1, colors.black),

                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),

                ("ALIGN", (0,0), (-1,-1), "CENTER"),

                ("FONTSIZE", (0,0), (-1,-1), 11),

                ("TOPPADDING", (0,0), (-1,-1), 7),

                ("BOTTOMPADDING", (0,0), (-1,-1), 7)

            ])

        )

        elements.append(table)

        elements.append(Spacer(1, 20))


        if pdf["difference_table"]:

            elements.append(
                Paragraph(
                    "<b>Difference Table</b>",
                    styles["Heading2"]
                )
            )

            diff_table = []

            for row in pdf["difference_table"]:

                diff_table.append(row)

            table = Table(diff_table)

            table.setStyle(

                TableStyle([

                    ("GRID", (0,0), (-1,-1), 1, colors.black),

                    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),

                    ("ALIGN", (0,0), (-1,-1), "CENTER"),

                    ("FONTSIZE", (0,0), (-1,-1), 11),

                    ("TOPPADDING", (0,0), (-1,-1), 7),

                    ("BOTTOMPADDING", (0,0), (-1,-1), 7)

                ])

            )

            elements.append(table)

            elements.append(
                Spacer(1,20)
            )

        elements.append(

            Paragraph(

                "<b>Calculation Steps</b>",

                styles["Heading2"]

            )

        )

        for step in pdf["steps"]:

            elements.append(

                Paragraph(

                    str(step),

                    styles["Code"]

                )

            )

        doc.build(elements)

        buffer.seek(0)

        return send_file(

            buffer,

            as_attachment=True,

            download_name="Interpolation_Report.pdf",

            mimetype="application/pdf"

        )

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 400

# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
    
