try:
    from sympy import symbols, expand, simplify, latex
except Exception as e:
    raise ImportError(
        "sympy is required to run this module. Install it with 'pip install sympy'. Original error: " + str(e)
    )

# =====================================================
# Global Symbol
# =====================================================

X = symbols('x')
Y = symbols('y')


# =====================================================
# Validation
# =====================================================

def validate_points(independent, dependent):

    if len(independent) != len(dependent):
        raise ValueError("Number of x and y values must be equal.")

    if len(independent) < 2:
        raise ValueError("Minimum 2 points required.")

    if len(independent) > 25:
        raise ValueError("Maximum 25 points allowed.")

    if len(set(independent)) != len(independent):
        raise ValueError("Duplicate independent values are not allowed.")


# =====================================================
# Convert String To Float
# =====================================================

def to_float_list(values):

    data = []

    for value in values:

        try:

            data.append(float(value))

        except:

            raise ValueError(f"Invalid Number : {value}")

    return data


# =====================================================
# Polynomial Formatter
# =====================================================

def polynomial_to_string(poly):

    try:

        return str(expand(poly))

    except:

        return str(poly)


# =====================================================
# Latex Formatter
# =====================================================

def polynomial_to_latex(poly):

    try:

        return latex(expand(poly))

    except:

        return latex(poly)


# =====================================================
# Rounding
# =====================================================

def r(value, digit=6):

    return round(float(value), digit)


# =====================================================
# Generate Point Table
# =====================================================

def generate_input_table(x_values, y_values):

    table = []

    for i in range(len(x_values)):

        table.append({

            "index": i,

            "x": x_values[i],

            "y": y_values[i]

        })

    return table


# =====================================================
# Copy Data
# =====================================================

def duplicate(values):

    return list(values)


# =====================================================
# Build Empty Difference Table
# =====================================================

def empty_difference_table(n):

    table = []

    for i in range(n):

        row = []

        for j in range(n):

            row.append(None)

        table.append(row)

    return table


# =====================================================
# Calculation Steps
# =====================================================

class StepLogger:

    def __init__(self):

        self.steps = []

    def add(self, text):

        self.steps.append(text)

    def blank(self):

        self.steps.append("")

    def get(self):

        return self.steps


# =====================================================
# Expression Builder
# =====================================================

class ExpressionBuilder:

    def __init__(self):
        self.expression = []

    def add(self, text):
        self.expression.append(text)

    def blank(self):
        self.expression.append("")

    def get(self):
        return "\n".join(self.expression)



# =====================================================
# Final Result Dictionary
# =====================================================

def result_dictionary():

    return {

        "method": "",

        "expression": "",

        "latex": "",

        "answer": None,

        "steps": [],

        "difference_table": [],

        "graph": "",

        "input_table": []

    }


# =====================================================
# Swap Variables
# =====================================================

def swap_xy(x, y):

    return duplicate(y), duplicate(x)

# =====================================================
# LAGRANGE INTERPOLATION
# =====================================================

def lagrange_interpolation(
        independent,
        dependent,
        target,
        variable='x'
):

    validate_points(independent, dependent)

    logger = StepLogger()
    expression = ExpressionBuilder()

    independent = duplicate(independent)
    dependent = duplicate(dependent)

    n = len(independent)

    logger.add("========================================")
    logger.add("LAGRANGE INTERPOLATION")
    logger.add("========================================")
    logger.blank()

    logger.add("Input Points:")

    for i in range(n):

        logger.add(
            f"P{i} = ({independent[i]}, {dependent[i]})"
        )

    logger.blank()

    poly = 0

    symbol = X if variable == 'x' else Y

    expression.add("Lagrange Polynomial")
    expression.add("------------------------------")
    expression.blank()

    for i in range(n):

        numerator = 1
        denominator = 1

        logger.add("----------------------------------------")
        logger.add(f"L{i}({variable})")
        logger.add("----------------------------------------")

        expression.add(f"L{i}")

        for j in range(n):

            if i == j:
                continue

            numerator *= (symbol - independent[j])

            denominator *= (
                independent[i] -
                independent[j]
            )

            logger.add(
                f"(Variable - {independent[j]})"
            )

        Li = numerator / denominator

        logger.add("")
        logger.add(f"Denominator = {denominator}")

        logger.add(
            f"L{i} = ({expand(numerator)}) / ({denominator})"
        )

        logger.blank()

        expression.add(
            polynomial_to_string(Li)
        )

        poly += dependent[i] * Li

    poly = expand(poly)

    logger.blank()
    logger.add("========================================")
    logger.add("Polynomial")
    logger.add("========================================")

    logger.add(
        polynomial_to_string(poly)
    )

    expression.blank()

    expression.add("Final Polynomial")

    expression.add(
        polynomial_to_string(poly)
    )

    logger.blank()

    logger.add(
        f"Substitute {variable} = {target}"
    )

    answer = poly.subs(
        symbol,
        target
    )

    answer = simplify(answer)

    logger.add(
        f"Answer = {answer}"
    )

    logger.blank()

    logger.add("Interpolation Finished.")

    result = result_dictionary()

    result["method"] = "Lagrange"

    result["expression"] = (
        polynomial_to_string(poly)
    )

    result["latex"] = (
        polynomial_to_latex(poly)
    )

    result["answer"] = float(answer)

    result["steps"] = logger.get()

    result["input_table"] = generate_input_table(
        independent,
        dependent
    )

    return result

# =====================================================
# FIND Y USING LAGRANGE
# =====================================================

def find_y_by_lagrange(x_values, y_values, x):

    return lagrange_interpolation(
        independent=x_values,
        dependent=y_values,
        target=x,
        variable='x'
    )


# =====================================================
# FIND X USING LAGRANGE
# =====================================================

def find_x_by_lagrange(x_values, y_values, y):

    return lagrange_interpolation(
        independent=y_values,
        dependent=x_values,
        target=y,
        variable='y'
    )


# =====================================================
# GENERATE LAGRANGE BASIS FUNCTIONS
# =====================================================

def lagrange_basis(independent, index):

    symbol = X

    numerator = 1
    denominator = 1

    n = len(independent)

    for j in range(n):

        if j == index:
            continue

        numerator *= (symbol - independent[j])

        denominator *= (
            independent[index] -
            independent[j]
        )

    return expand(
        numerator / denominator
    )


# =====================================================
# GENERATE LAGRANGE EXPRESSION ONLY
# =====================================================

def lagrange_expression(
        independent,
        dependent
):

    validate_points(
        independent,
        dependent
    )

    symbol = X

    polynomial = 0

    steps = []

    n = len(independent)

    steps.append(
        "========== LAGRANGE BASIS =========="
    )

    for i in range(n):

        Li = lagrange_basis(
            independent,
            i
        )

        steps.append(
            f"L{i}(x) = {expand(Li)}"
        )

        polynomial += dependent[i] * Li

    polynomial = expand(polynomial)

    steps.append("")
    steps.append(
        "========== FINAL POLYNOMIAL =========="
    )

    steps.append(
        polynomial_to_string(
            polynomial
        )
    )

    return {

        "expression":
            polynomial_to_string(
                polynomial
            ),

        "latex":
            polynomial_to_latex(
                polynomial
            ),

        "steps":
            steps
    }


# =====================================================
# EVALUATE POLYNOMIAL
# =====================================================

def evaluate_polynomial(
        polynomial,
        value,
        variable='x'
):

    symbol = X if variable == 'x' else Y

    return float(

        polynomial.subs(

            symbol,

            value

        )

    )


# =====================================================
# SHOW INPUT TABLE
# =====================================================

def print_input_table(
        independent,
        dependent
):

    rows = []

    for i in range(len(independent)):

        rows.append({

            "Point": f"P{i}",

            "Independent": independent[i],

            "Dependent": dependent[i]

        })

    return rows

# =====================================================
# NEWTON DIVIDED DIFFERENCE TABLE
# =====================================================

def divided_difference_table(independent, dependent):

    validate_points(independent, dependent)

    n = len(independent)

    table = []

    for i in range(n):

        row = []

        for j in range(n):

            row.append(None)

        row[0] = float(dependent[i])

        table.append(row)

    steps = []

    steps.append("===================================")
    steps.append("DIVIDED DIFFERENCE TABLE")
    steps.append("===================================")
    steps.append("")

    for col in range(1, n):

        for row in range(n-col):

            numerator = (
                table[row+1][col-1]
                -
                table[row][col-1]
            )

            denominator = (
                independent[row+col]
                -
                independent[row]
            )

            table[row][col] = numerator / denominator

            steps.append(
                f"Δ^{col}y{row}"
            )

            steps.append(
                f"= ({table[row+1][col-1]} - {table[row][col-1]})"
            )

            steps.append(
                f"/ ({independent[row+col]} - {independent[row]})"
            )

            steps.append(
                f"= {numerator} / {denominator}"
            )

            steps.append(
                f"= {table[row][col]}"
            )

            steps.append("")

    return table, steps

# =====================================================
# PRINT DIFFERENCE TABLE
# =====================================================

def format_difference_table(
        x_values,
        table
):

    output = []

    n = len(x_values)

    for i in range(n):

        row = {

            "x": x_values[i]

        }

        for j in range(n-i):

            row[f"d{j}"] = table[i][j]

        output.append(row)

    return output

# =====================================================
# FIRST COLUMN
# =====================================================

def first_column(table):

    values = []

    for i in range(len(table)):

        values.append(table[i][0])

    return values

# =====================================================
# NEWTON POLYNOMIAL
# =====================================================

def newton_polynomial(
        x_values,
        table,
        variable="x"
):

    symbol = X if variable == "x" else Y


    polynomial = table[0][0]

    term = 1

    n = len(x_values)

    for i in range(1, n):

        term *= (
            symbol -
            x_values[i-1]
        )

        polynomial += (
            table[0][i] * term
        )

    return expand(polynomial)


# =====================================================
# NEWTON EXPRESSION
# =====================================================

def newton_expression(
        x_values,
        y_values
):

    table, steps = divided_difference_table(
        x_values,
        y_values
    )

    polynomial = newton_polynomial(
        x_values,
        table
    )

    return {

        "expression":
            polynomial_to_string(
                polynomial
            ),

        "latex":
            polynomial_to_latex(
                polynomial
            ),

        "steps":
            steps,

        "table":
            table

    }

# =====================================================
# BUILD NEWTON FORMULA STRING
# =====================================================

def build_newton_formula(x_values, table):

    formula = []

    formula.append("P(x) = ")

    formula.append(str(table[0][0]))

    for i in range(1, len(x_values)):

        term = ""

        for j in range(i):

            term += f"(x-{x_values[j]})"

        term += f"({table[0][i]})"

        formula.append("+ " + term)

    return " ".join(formula)


# =====================================================
# LATEX NEWTON FORMULA
# =====================================================

def newton_formula_latex(x_values, table):

    poly = newton_polynomial(
        x_values,
        table
    )

    return polynomial_to_latex(poly)


# =====================================================
# SHOW COMPLETE DIFFERENCE TABLE
# =====================================================

def complete_difference_table(x_values, table):

    rows = []

    n = len(x_values)

    for i in range(n):

        row = []

        row.append(x_values[i])

        for j in range(n-i):

            row.append(table[i][j])

        rows.append(row)

    return rows

# =====================================================
# DISPLAY TABLE HEADERS
# =====================================================

def difference_headers(n):

    headers = ["x", "y"]

    for i in range(1, n):

        headers.append(f"Δ^{i}y")

    return headers

# =====================================================
# EVALUATE NEWTON POLYNOMIAL
# =====================================================

def evaluate_newton(
        x_values,
        y_values,
        value
):

    table, _ = divided_difference_table(
        x_values,
        y_values
    )

    poly = newton_polynomial(
        x_values,
        table
    )

    ans = poly.subs(
        X,
        value
    )

    return float(ans)


# =====================================================
# RETURN TABLE ONLY
# =====================================================

def get_difference_table(
        x_values,
        y_values
):

    table, steps = divided_difference_table(
        x_values,
        y_values
    )

    return {

        "table": complete_difference_table(
            x_values,
            table
        ),

        "headers": difference_headers(
            len(x_values)
        ),

        "steps": steps

    }

# =====================================================
# NEWTON INTERPOLATION SOLVER
# =====================================================

def newton_interpolation(
        independent,
        dependent,
        target,
        variable='x'
):

    validate_points(independent, dependent)

    logger = StepLogger()

    independent = duplicate(independent)
    dependent = duplicate(dependent)

    result = result_dictionary()

    logger.add("===================================")
    logger.add("NEWTON DIVIDED DIFFERENCE")
    logger.add("===================================")
    logger.blank()

    logger.add("Input Data")

    for i in range(len(independent)):

        logger.add(
            f"P{i} = ({independent[i]}, {dependent[i]})"
        )

    logger.blank()

    table, diff_steps = divided_difference_table(
        independent,
        dependent
    )

    for step in diff_steps:

        logger.add(step)

    logger.blank()

    polynomial = newton_polynomial(
    independent,
    table,
    variable
    )

    logger.add("===================================")
    logger.add("Polynomial")
    logger.add("===================================")

    logger.add(
        polynomial_to_string(polynomial)
    )

    logger.blank()

    symbol = X if variable == "x" else Y

    answer = polynomial.subs(
        symbol,
        target
    )

    answer = simplify(answer)

    logger.add(
        f"Substitute {variable} = {target}"
    )

    logger.add(
        f"Answer = {answer}"
    )

    logger.blank()


    result["method"] = "Newton Divided Difference"

    result["expression"] = polynomial_to_string(
        polynomial
    )

    result["latex"] = polynomial_to_latex(
        polynomial
    )

    result["answer"] = float(answer)

    result["steps"] = logger.get()

    result["difference_table"] = complete_difference_table(
        independent,
        table
    )

    result["input_table"] = generate_input_table(
        independent,
        dependent
    )

    return result

# =====================================================
# FIND Y USING NEWTON
# =====================================================

def find_y_by_newton(
        x_values,
        y_values,
        x
):

    return newton_interpolation(

        independent=x_values,

        dependent=y_values,

        target=x,

        variable='x'

    )


# =====================================================
# FIND X USING NEWTON
# =====================================================

def find_x_by_newton(
        x_values,
        y_values,
        y
):

    return newton_interpolation(

        independent=y_values,

        dependent=x_values,

        target=y,

        variable='y'

    )


# =====================================================
# NEWTON FORMULA STEP GENERATOR
# =====================================================

def newton_formula_steps(
        independent,
        table,
        variable="x"
):
    

    steps = []

    steps.append(
        "Interpolation Formula"
    )

    steps.append("")

    formula = f"P({variable}) = "

    formula += str(table[0][0])

    for i in range(1, len(independent)):

        formula += " + "

        for j in range(i):

            formula += f"({variable}-{independent[j]})"

        formula += f"({table[0][i]})"

    steps.append(formula)

    return steps


# =====================================================
# SUBSTITUTE VALUE STEP
# =====================================================

def substitution_steps(
        independent,
        table,
        target,
        variable="x"
):

    steps = []

    poly = newton_polynomial(
    independent,
    table,
    variable
)

    steps.append("")

    steps.append(
    f"Substitute {variable} = {target}"
    )

    symbol = X if variable == "x" else Y

    answer = poly.subs(
    symbol,
    target
    )

    steps.append(
        polynomial_to_string(poly)
    )

    steps.append("")

    steps.append(

        f"Answer = {answer}"

    )

    return steps

# =====================================================
# COMPLETE STEP COLLECTION
# =====================================================

def collect_newton_steps(
        independent,
        dependent,
        target,
        variable="x"
):

    table, diff = divided_difference_table(
        independent,
        dependent
    )

    formula = newton_formula_steps(
    independent,
    table,
    variable
    )

    substitute = substitution_steps(
    independent,
    table,
    target,
    variable
    )

    steps = []

    steps.extend(diff)

    steps.extend(formula)

    steps.extend(substitute)

    return steps

# =====================================================
# SHOW POLYNOMIAL
# =====================================================

def polynomial_only(
        independent,
        dependent
):

    table, _ = divided_difference_table(
        independent,
        dependent
    )

    poly = newton_polynomial(
        independent,
        table
    )

    return {

        "expression": polynomial_to_string(poly),

        "latex": polynomial_to_latex(poly)

    }

# =====================================================
# SOLVE USING LAGRANGE
# =====================================================

def solve_lagrange(
        independent,
        dependent,
        target,
        mode="find_y"
):

    if mode == "find_y":

        return find_y_by_lagrange(
            independent,
            dependent,
            target
        )

    else:

        return find_x_by_lagrange(
            independent,
            dependent,
            target
        )


# =====================================================
# SOLVE USING NEWTON
# =====================================================

def solve_newton(
        independent,
        dependent,
        target,
        mode="find_y"
):

    if mode == "find_y":

        return find_y_by_newton(
            independent,
            dependent,
            target
        )

    else:

        return find_x_by_newton(
            independent,
            dependent,
            target
        )

# =====================================================
# MAIN SOLVER
# =====================================================

def solve(
        method,
        independent,
        dependent,
        target,
        mode="find_y"
):

    if method.lower() == "lagrange":

        return solve_lagrange(

            independent,

            dependent,

            target,

            mode

        )

    elif method.lower() == "newton":

        return solve_newton(

            independent,

            dependent,

            target,

            mode

        )

    else:

        raise ValueError(
            "Unknown Method."
        )

# =====================================================
# EXPORT EXPRESSION
# =====================================================

def expression_only(result):

    return result["expression"]


# =====================================================
# EXPORT ANSWER
# =====================================================

def answer_only(result):

    return result["answer"]

# =====================================================
# PDF DATA
# =====================================================

def pdf_information(result):

    return {

        "method": result["method"],

        "input_table": result["input_table"],

        "difference_table": result["difference_table"],

        "expression": result["expression"],

        "answer": result["answer"],

        "steps": result["steps"]

    }

# =====================================================
# RESULT SUMMARY
# =====================================================

def summary(result):

    return {

        "Method": result["method"],

        "Answer": result["answer"],

        "Expression": result["expression"]

    }

# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    x = [1,2,4,5]

    y = [2,5,17,26]

    result = solve(

        method="lagrange",

        independent=x,

        dependent=y,

        target=3,

        mode="find_y"

    )

    print(result["answer"])



