<<<<<<< HEAD
from fastmcp import Context, FastMCP

from pydantic import BaseModel, Field

 

mcp = FastMCP("Rbank Mortgage MCP Server")

 

MORTGAGE_TYPES = {

    "annuiteiten": "Annuïteiten",

    "lineair": "Lineair",

    "aflossingsvrij": "Aflossingsvrij",

    "overbrugging": "Overbrugging",

    "opbouwhypotheek": "Opbouwhypotheek",

}

 

CONDITION_TYPES = {

    "basisvoorwaarden": "Basisvoorwaarden",

    "plusvoorwaarden": "Plusvoorwaarden",

}

 

RATE_TABLE = {

    "1 jaar": {"NHG": 4.25, "<= 67,5%": 4.55, "<= 90,0%": 4.65, "> 90,0%": 4.70},

    "5 jaar": {"NHG": 4.40, "<= 67,5%": 4.75, "<= 90,0%": 4.85, "> 90,0%": 4.90},

    "10 jaar": {"NHG": 4.40, "<= 67,5%": 4.75, "<= 90,0%": 4.85, "> 90,0%": 4.90},

    "20 jaar": {"NHG": 4.95, "<= 67,5%": 5.30, "<= 90,0%": 5.40, "> 90,0%": 5.45},

    "30 jaar": {"NHG": 5.25, "<= 67,5%": 5.45, "<= 90,0%": 5.55, "> 90,0%": 5.60},

}

 

TARIFF_CLASS_ALIASES = {

    "nhg": "NHG",

    "<= 67,5%": "<= 67,5%",

    "≤ 67,5%": "<= 67,5%",

    "<= 90,0%": "<= 90,0%",

    "≤ 90,0%": "<= 90,0%",

    "> 90,0%": "> 90,0%",

}

 

LEGACY_PRODUCTS = {

    "annuity-10y-fixed": ("annuiteiten", "basisvoorwaarden", "NHG", "10 jaar"),

    "annuity-20y-fixed": ("annuiteiten", "basisvoorwaarden", "NHG", "20 jaar"),

    "annuity-30y-fixed": ("annuiteiten", "basisvoorwaarden", "NHG", "30 jaar"),

}

 

 

def normalize(value: str) -> str:

    return " ".join(value.strip().casefold().split()).replace("ï", "i")

 

@mcp.resource("rates://mortgages")

def mortgage_rates() -> dict:

    """

    Exposes mortgage rates as a readable MCP resource.

 

    Resources are useful for reference data that the assistant can inspect.

    """

    return {

        "source": "Rbank demo mortgage rate table",

        "description": "Demo rates for training purposes only.",

        "rates": MORTGAGE_RATES

    }

 

MORTGAGE_PRODUCTS = {

    "annuity-10y-fixed": {

        "name": "Annuity Mortgage - 10 Year Fixed",

        "description": "A mortgage with fixed monthly payments and a 10-year fixed interest period.",

        "risk_note": "After 10 years, the interest rate may change."

    },

    "annuity-20y-fixed": {

        "name": "Annuity Mortgage - 20 Year Fixed",

        "description": "A mortgage with fixed monthly payments and a 20-year fixed interest period.",

        "risk_note": "Provides longer interest certainty, but may have a higher rate."

    },

    "annuity-30y-fixed": {

        "name": "Annuity Mortgage - 30 Year Fixed",

        "description": "A mortgage with fixed monthly payments and a 30-year fixed interest period.",

        "risk_note": "Provides maximum interest certainty, but usually at a higher rate."

    },

    "variable": {

        "name": "Variable Rate Mortgage",

        "description": "A mortgage where the interest rate can change over time.",

        "risk_note": "Monthly payments can increase when market rates rise."

    }

}

 

@mcp.prompt

def mortgage_advice(

    client_name: str = "",

    product: str = "",

    loan_amount: float | None = None,

    term_years: int | None = None,

    gross_monthly_income: float | None = None,

) -> str:

    """

    Provides a reusable mortgage advice workflow.

 

    ALWAYS start by calling the `start_mortgage_advice` tool, which opens the

    in-chat form to collect the client's details. Only use this prompt's text

    directly if the form (elicitation) is unavailable. Do not improvise an

    answer.

 

    All arguments are optional. Fill in whatever the user has provided and leave

    the rest blank; the workflow will ask for or infer anything still missing.

 

    The `product` argument should be one of the known product keys:

    - annuity-10y-fixed

    - annuity-20y-fixed

    - annuity-30y-fixed

    - variable

 

    If the user does not name a product, do NOT ask them to pick one up front.

    Instead, choose the most suitable product key yourself based on the context

    of their questions (e.g. desired interest certainty, term, risk appetite),

    and explain why you picked it.

    """

    return _build_mortgage_advice(

        client_name=client_name,

        product=product,

        loan_amount=loan_amount,

        term_years=term_years,

        gross_monthly_income=gross_monthly_income,

    )

 

 

def _build_mortgage_advice(

    client_name: str = "",

    product: str = "",

    loan_amount: float | None = None,

    term_years: int | None = None,

    gross_monthly_income: float | None = None,

) -> str:

    valid_products = ", ".join(MORTGAGE_PRODUCTS.keys())

 

    return f"""

You are a Rbank mortgage advisor preparing a demo mortgage explanation.

 

Client:

- Name: {client_name or "(not provided)"}

- Gross monthly income: {f"€{gross_monthly_income}" if gross_monthly_income is not None else "(not provided)"}

 

Mortgage request:

- Product: {product or "(not provided - choose the best fit yourself)"}

- Loan amount: {f"€{loan_amount}" if loan_amount is not None else "(not provided)"}

- Term: {f"{term_years} years" if term_years is not None else "(not provided)"}

 

Available products (pick the key that best matches the client's situation):

{valid_products}

 

Follow this workflow:

1. If a product was not provided, infer the best-fitting product key from the

   context of the user's questions and state which one you chose and why.

2. Read the mortgage rates from rates://mortgages.

3. Find the rate for the selected product.

4. Read product information from products://mortgages.

5. Call calculate_monthly_payment using:

   - principal: the loan amount

   - annual_rate: the selected product rate

   - term_years: the requested term

6. Compare the estimated payment with the gross monthly income.

7. Write a short, structured explanation with:

   - product name

   - trusted rate used

   - estimated monthly payment

   - affordability comment

   - risk note

   - clear disclaimer that this is a training demo, not official advice.

 

For any detail the user has not provided, either make a reasonable assumption

(and state it clearly) or ask a brief follow-up question.

Do not invent mortgage rates.

"""

 

 

class MortgageRequest(BaseModel):

    """Fields shown in the in-chat mortgage advice form."""

 

    client_name: str = Field(default="", description="Client's full name")

    product: str = Field(

        default="",

        description=(

            "Product key (annuity-10y-fixed, annuity-20y-fixed, "

            "annuity-30y-fixed, variable). Leave blank to let the advisor choose."

        ),

    )

    loan_amount: float = Field(default=0, description="Requested loan amount in €")

    term_years: int = Field(default=30, description="Mortgage term in years")

    gross_monthly_income: float = Field(

        default=0, description="Gross monthly income in €"

    )

 

 

@mcp.tool

async def start_mortgage_advice(ctx: Context) -> str:

    """

    Opens an in-chat form (popup) to collect the client's mortgage details,

    then returns the mortgage advice workflow to follow.

 

    ALWAYS call this tool first whenever a user asks for mortgage advice, a

    mortgage explanation, or help choosing a mortgage. The user must fill in the

    UI form before any advice is given - do not collect the details by asking

    questions in chat and do not skip the form.

    """

    result = await ctx.elicit(

        message="Please provide the mortgage details",

        response_type=MortgageRequest,

    )

 

    if result.action != "accept":

        return "Mortgage advice cancelled - no details were provided."

 

    data = result.data

    return _build_mortgage_advice(

        client_name=data.client_name,

        product=data.product,

        loan_amount=data.loan_amount or None,

        term_years=data.term_years,

        gross_monthly_income=data.gross_monthly_income or None,

    )

 

 

@mcp.resource("products://mortgages")

def mortgage_products() -> dict:

    """

    Exposes mortgage product information as reference data.

    """

    return MORTGAGE_PRODUCTS

@mcp.tool

def calculate_monthly_payment(

    principal: float,

    annual_rate: float,

    term_years: int

) -> str:

    """

    Calculates the estimated monthly mortgage payment.

 

    This calculation uses the standard annuity mortgage formula.

    The result is a demo estimate and not financial advice.

    """

    monthly_rate = annual_rate / 100 / 12

    months = term_years * 12

 

    if monthly_rate == 0:

        payment = principal / months

    else:

        payment = principal * (

            monthly_rate * (1 + monthly_rate) ** months

        ) / (

            (1 + monthly_rate) ** months - 1

        )

 

    return f"Estimated monthly payment: €{payment:.2f}"

 

 

@mcp.tool

def get_mortgage_rate(

    product: str | None = None,

    mortgage_type: str = "annuiteiten",

    conditions: str = "basisvoorwaarden",

    tariff_class: str = "NHG",

    fixed_period: str = "20 jaar",

) -> str:

    """

    Returns the mortgage rate for a mortgage product.

 

    Prefer these specific values:

    - mortgage_type: annuiteiten, lineair, aflossingsvrij, overbrugging, opbouwhypotheek

    - conditions: basisvoorwaarden, plusvoorwaarden

    - tariff_class: NHG, <= 67,5%, <= 90,0%, > 90,0%

    - fixed_period: 1 jaar, 5 jaar, 10 jaar, 20 jaar, 30 jaar

 

    Legacy product values are also supported:

    - annuity-10y-fixed

    - annuity-20y-fixed

    - annuity-30y-fixed

    """

    if product:

        legacy_product = LEGACY_PRODUCTS.get(product)

 

        if legacy_product is None:

            available_products = ", ".join(LEGACY_PRODUCTS.keys())

            return (

                f"Unknown product: {product}. "

                f"Available legacy products are: {available_products}."

            )

 

        mortgage_type, conditions, tariff_class, fixed_period = legacy_product

 

    mortgage_type_label = MORTGAGE_TYPES.get(normalize(mortgage_type))

 

    if mortgage_type_label is None:

        available_types = ", ".join(MORTGAGE_TYPES.keys())

        return (

            f"Unknown mortgage_type: {mortgage_type}. "

            f"Available mortgage types are: {available_types}."

        )

 

    conditions_label = CONDITION_TYPES.get(normalize(conditions))

 

    if conditions_label is None:

        available_conditions = ", ".join(CONDITION_TYPES.keys())

        return (

            f"Unknown conditions: {conditions}. "

            f"Available conditions are: {available_conditions}."

        )

 

    period_rates = RATE_TABLE.get(fixed_period)

 

    if period_rates is None:

        available_periods = ", ".join(RATE_TABLE.keys())

        return (

            f"Unknown fixed_period: {fixed_period}. "

            f"Available fixed periods are: {available_periods}."

        )

 

    normalized_tariff_class = TARIFF_CLASS_ALIASES.get(normalize(tariff_class))

    rate = period_rates.get(normalized_tariff_class)

 

    if rate is None:

        available_tariff_classes = ", ".join(next(iter(RATE_TABLE.values())).keys())

        return (

            f"Unknown tariff_class: {tariff_class}. "

            f"Available tariff classes are: {available_tariff_classes}."

        )

 

    return (

        f"The trusted demo rate for {mortgage_type_label}, {conditions_label}, "

        f"tariff class {normalized_tariff_class}, fixed period {fixed_period} is {rate}%. "

        "No rights can be derived from this information."

    )

 

 

if __name__ == "__main__":

    # HTTP transport = your server is a web service on a port.

    # 127.0.0.1 keeps it local to your machine (safe for a workshop).

=======
from fastmcp import Context, FastMCP

from pydantic import BaseModel, Field

 

mcp = FastMCP("Rbank Mortgage MCP Server")

 

MORTGAGE_TYPES = {

    "annuiteiten": "Annuïteiten",

    "lineair": "Lineair",

    "aflossingsvrij": "Aflossingsvrij",

    "overbrugging": "Overbrugging",

    "opbouwhypotheek": "Opbouwhypotheek",

}

 

CONDITION_TYPES = {

    "basisvoorwaarden": "Basisvoorwaarden",

    "plusvoorwaarden": "Plusvoorwaarden",

}

 

RATE_TABLE = {

    "1 jaar": {"NHG": 4.25, "<= 67,5%": 4.55, "<= 90,0%": 4.65, "> 90,0%": 4.70},

    "5 jaar": {"NHG": 4.40, "<= 67,5%": 4.75, "<= 90,0%": 4.85, "> 90,0%": 4.90},

    "10 jaar": {"NHG": 4.40, "<= 67,5%": 4.75, "<= 90,0%": 4.85, "> 90,0%": 4.90},

    "20 jaar": {"NHG": 4.95, "<= 67,5%": 5.30, "<= 90,0%": 5.40, "> 90,0%": 5.45},

    "30 jaar": {"NHG": 5.25, "<= 67,5%": 5.45, "<= 90,0%": 5.55, "> 90,0%": 5.60},

}

 

TARIFF_CLASS_ALIASES = {

    "nhg": "NHG",

    "<= 67,5%": "<= 67,5%",

    "≤ 67,5%": "<= 67,5%",

    "<= 90,0%": "<= 90,0%",

    "≤ 90,0%": "<= 90,0%",

    "> 90,0%": "> 90,0%",

}

 

LEGACY_PRODUCTS = {

    "annuity-10y-fixed": ("annuiteiten", "basisvoorwaarden", "NHG", "10 jaar"),

    "annuity-20y-fixed": ("annuiteiten", "basisvoorwaarden", "NHG", "20 jaar"),

    "annuity-30y-fixed": ("annuiteiten", "basisvoorwaarden", "NHG", "30 jaar"),

}

 

 

def normalize(value: str) -> str:

    return " ".join(value.strip().casefold().split()).replace("ï", "i")

 

@mcp.resource("rates://mortgages")

def mortgage_rates() -> dict:

    """

    Exposes mortgage rates as a readable MCP resource.

 

    Resources are useful for reference data that the assistant can inspect.

    """

    return {

        "source": "Rbank demo mortgage rate table",

        "description": "Demo rates for training purposes only.",

        "rates": MORTGAGE_RATES

    }

 

MORTGAGE_PRODUCTS = {

    "annuity-10y-fixed": {

        "name": "Annuity Mortgage - 10 Year Fixed",

        "description": "A mortgage with fixed monthly payments and a 10-year fixed interest period.",

        "risk_note": "After 10 years, the interest rate may change."

    },

    "annuity-20y-fixed": {

        "name": "Annuity Mortgage - 20 Year Fixed",

        "description": "A mortgage with fixed monthly payments and a 20-year fixed interest period.",

        "risk_note": "Provides longer interest certainty, but may have a higher rate."

    },

    "annuity-30y-fixed": {

        "name": "Annuity Mortgage - 30 Year Fixed",

        "description": "A mortgage with fixed monthly payments and a 30-year fixed interest period.",

        "risk_note": "Provides maximum interest certainty, but usually at a higher rate."

    },

    "variable": {

        "name": "Variable Rate Mortgage",

        "description": "A mortgage where the interest rate can change over time.",

        "risk_note": "Monthly payments can increase when market rates rise."

    }

}

 

@mcp.prompt

def mortgage_advice(

    client_name: str = "",

    product: str = "",

    loan_amount: float | None = None,

    term_years: int | None = None,

    gross_monthly_income: float | None = None,

) -> str:

    """

    Provides a reusable mortgage advice workflow.

 

    ALWAYS start by calling the `start_mortgage_advice` tool, which opens the

    in-chat form to collect the client's details. Only use this prompt's text

    directly if the form (elicitation) is unavailable. Do not improvise an

    answer.

 

    All arguments are optional. Fill in whatever the user has provided and leave

    the rest blank; the workflow will ask for or infer anything still missing.

 

    The `product` argument should be one of the known product keys:

    - annuity-10y-fixed

    - annuity-20y-fixed

    - annuity-30y-fixed

    - variable

 

    If the user does not name a product, do NOT ask them to pick one up front.

    Instead, choose the most suitable product key yourself based on the context

    of their questions (e.g. desired interest certainty, term, risk appetite),

    and explain why you picked it.

    """

    return _build_mortgage_advice(

        client_name=client_name,

        product=product,

        loan_amount=loan_amount,

        term_years=term_years,

        gross_monthly_income=gross_monthly_income,

    )

 

 

def _build_mortgage_advice(

    client_name: str = "",

    product: str = "",

    loan_amount: float | None = None,

    term_years: int | None = None,

    gross_monthly_income: float | None = None,

) -> str:

    valid_products = ", ".join(MORTGAGE_PRODUCTS.keys())

 

    return f"""

You are a Rbank mortgage advisor preparing a demo mortgage explanation.

 

Client:

- Name: {client_name or "(not provided)"}

- Gross monthly income: {f"€{gross_monthly_income}" if gross_monthly_income is not None else "(not provided)"}

 

Mortgage request:

- Product: {product or "(not provided - choose the best fit yourself)"}

- Loan amount: {f"€{loan_amount}" if loan_amount is not None else "(not provided)"}

- Term: {f"{term_years} years" if term_years is not None else "(not provided)"}

 

Available products (pick the key that best matches the client's situation):

{valid_products}

 

Follow this workflow:

1. If a product was not provided, infer the best-fitting product key from the

   context of the user's questions and state which one you chose and why.

2. Read the mortgage rates from rates://mortgages.

3. Find the rate for the selected product.

4. Read product information from products://mortgages.

5. Call calculate_monthly_payment using:

   - principal: the loan amount

   - annual_rate: the selected product rate

   - term_years: the requested term

6. Compare the estimated payment with the gross monthly income.

7. Write a short, structured explanation with:

   - product name

   - trusted rate used

   - estimated monthly payment

   - affordability comment

   - risk note

   - clear disclaimer that this is a training demo, not official advice.

 

For any detail the user has not provided, either make a reasonable assumption

(and state it clearly) or ask a brief follow-up question.

Do not invent mortgage rates.

"""

 

 

class MortgageRequest(BaseModel):

    """Fields shown in the in-chat mortgage advice form."""

 

    client_name: str = Field(default="", description="Client's full name")

    product: str = Field(

        default="",

        description=(

            "Product key (annuity-10y-fixed, annuity-20y-fixed, "

            "annuity-30y-fixed, variable). Leave blank to let the advisor choose."

        ),

    )

    loan_amount: float = Field(default=0, description="Requested loan amount in €")

    term_years: int = Field(default=30, description="Mortgage term in years")

    gross_monthly_income: float = Field(

        default=0, description="Gross monthly income in €"

    )

 

 

@mcp.tool

async def start_mortgage_advice(ctx: Context) -> str:

    """

    Opens an in-chat form (popup) to collect the client's mortgage details,

    then returns the mortgage advice workflow to follow.

 

    ALWAYS call this tool first whenever a user asks for mortgage advice, a

    mortgage explanation, or help choosing a mortgage. The user must fill in the

    UI form before any advice is given - do not collect the details by asking

    questions in chat and do not skip the form.

    """

    result = await ctx.elicit(

        message="Please provide the mortgage details",

        response_type=MortgageRequest,

    )

 

    if result.action != "accept":

        return "Mortgage advice cancelled - no details were provided."

 

    data = result.data

    return _build_mortgage_advice(

        client_name=data.client_name,

        product=data.product,

        loan_amount=data.loan_amount or None,

        term_years=data.term_years,

        gross_monthly_income=data.gross_monthly_income or None,

    )

 

 

@mcp.resource("products://mortgages")

def mortgage_products() -> dict:

    """

    Exposes mortgage product information as reference data.

    """

    return MORTGAGE_PRODUCTS

@mcp.tool

def calculate_monthly_payment(

    principal: float,

    annual_rate: float,

    term_years: int

) -> str:

    """

    Calculates the estimated monthly mortgage payment.

 

    This calculation uses the standard annuity mortgage formula.

    The result is a demo estimate and not financial advice.

    """

    monthly_rate = annual_rate / 100 / 12

    months = term_years * 12

 

    if monthly_rate == 0:

        payment = principal / months

    else:

        payment = principal * (

            monthly_rate * (1 + monthly_rate) ** months

        ) / (

            (1 + monthly_rate) ** months - 1

        )

 

    return f"Estimated monthly payment: €{payment:.2f}"

 

 

@mcp.tool

def get_mortgage_rate(

    product: str | None = None,

    mortgage_type: str = "annuiteiten",

    conditions: str = "basisvoorwaarden",

    tariff_class: str = "NHG",

    fixed_period: str = "20 jaar",

) -> str:

    """

    Returns the mortgage rate for a mortgage product.

 

    Prefer these specific values:

    - mortgage_type: annuiteiten, lineair, aflossingsvrij, overbrugging, opbouwhypotheek

    - conditions: basisvoorwaarden, plusvoorwaarden

    - tariff_class: NHG, <= 67,5%, <= 90,0%, > 90,0%

    - fixed_period: 1 jaar, 5 jaar, 10 jaar, 20 jaar, 30 jaar

 

    Legacy product values are also supported:

    - annuity-10y-fixed

    - annuity-20y-fixed

    - annuity-30y-fixed

    """

    if product:

        legacy_product = LEGACY_PRODUCTS.get(product)

 

        if legacy_product is None:

            available_products = ", ".join(LEGACY_PRODUCTS.keys())

            return (

                f"Unknown product: {product}. "

                f"Available legacy products are: {available_products}."

            )

 

        mortgage_type, conditions, tariff_class, fixed_period = legacy_product

 

    mortgage_type_label = MORTGAGE_TYPES.get(normalize(mortgage_type))

 

    if mortgage_type_label is None:

        available_types = ", ".join(MORTGAGE_TYPES.keys())

        return (

            f"Unknown mortgage_type: {mortgage_type}. "

            f"Available mortgage types are: {available_types}."

        )

 

    conditions_label = CONDITION_TYPES.get(normalize(conditions))

 

    if conditions_label is None:

        available_conditions = ", ".join(CONDITION_TYPES.keys())

        return (

            f"Unknown conditions: {conditions}. "

            f"Available conditions are: {available_conditions}."

        )

 

    period_rates = RATE_TABLE.get(fixed_period)

 

    if period_rates is None:

        available_periods = ", ".join(RATE_TABLE.keys())

        return (

            f"Unknown fixed_period: {fixed_period}. "

            f"Available fixed periods are: {available_periods}."

        )

 

    normalized_tariff_class = TARIFF_CLASS_ALIASES.get(normalize(tariff_class))

    rate = period_rates.get(normalized_tariff_class)

 

    if rate is None:

        available_tariff_classes = ", ".join(next(iter(RATE_TABLE.values())).keys())

        return (

            f"Unknown tariff_class: {tariff_class}. "

            f"Available tariff classes are: {available_tariff_classes}."

        )

 

    return (

        f"The trusted demo rate for {mortgage_type_label}, {conditions_label}, "

        f"tariff class {normalized_tariff_class}, fixed period {fixed_period} is {rate}%. "

        "No rights can be derived from this information."

    )

 

 

if __name__ == "__main__":

    # HTTP transport = your server is a web service on a port.

    # 127.0.0.1 keeps it local to your machine (safe for a workshop).

>>>>>>> f9591471fe5397d9ba2af8bf67cbd2d16e481b0c
    mcp.run(transport="http", host="127.0.0.1", port=8001)