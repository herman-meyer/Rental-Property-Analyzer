# 🏠 Rental Property Investment Analyzer

A Streamlit tool for evaluating rental property deals — built around how investors in markets like Whatcom County, WA actually underwrite a property: real cash flow (including the "ghost costs" most people forget), remodel ROI, and long-term return projections.

**[Live App →](#)** *(add your Streamlit Cloud link here once deployed)*

---

## Why I built this

Most rental property calculators online either oversimplify the numbers (ignoring vacancy, maintenance, CapEx reserves — the "ghost costs" that quietly eat your cash flow) or they're locked behind a subscription. I wanted a tool that:

1. Forces you to account for the real costs of owning a rental, not just mortgage + rent
2. Lets you test "what if" scenarios side by side (different down payments, financing, or whether to remodel before renting)
3. Projects what the deal actually looks like 5-10 years out, not just month one

This is also a practical exercise in **data-driven decision making** — the same mindset that applies to evaluating any business deal, not just real estate.

---

## What it does

### 1. Cash Flow & Ghost Costs
Input a property's price, financing terms, and rent. The tool breaks down exactly where the rent goes — mortgage, taxes, insurance, vacancy reserve, maintenance reserve, CapEx reserve, and property management — and shows what's actually left over each month. Outputs a **Deal Score (0-100)** based on cash flow, cap rate, and cash-on-cash return.

### 2. Remodel ROI Calculator
Input a rehab budget by category (kitchen, bathroom, flooring, roof, etc.) and compare it against the After-Repair Value (ARV) and rent increase. Tells you whether the remodel pays for itself — and how long it takes to pay back through higher rent.

### 3. Long-Term Returns
Projects property value, loan paydown, equity, and cumulative cash flow over a custom hold period (1-30 years), accounting for appreciation and rent growth. Shows total profit and an annualized return.

### 4. Scenario Comparison (A/B Test)
Compare two strategies side by side — e.g., 20% down vs. 25% down, or buy-as-is vs. buy-and-remodel — and see which produces a better cash-on-cash return. Same logic as an A/B test, applied to a financing decision instead of a marketing one.

---

## Built vs. Buy

Tools like BiggerPockets' calculators already exist and are solid. I built this anyway because:

- **Customization**: ghost cost assumptions (vacancy %, maintenance %, CapEx %, management %) are sliders you control, not locked defaults
- **Scenario comparison**: most free calculators don't let you A/B test two financing structures side by side
- **Transparency**: it's open source — every formula is visible and editable, nothing is a black box
- **Cost**: free to run and modify, no subscription

For a one-off deal evaluation, an existing calculator is faster. For repeatedly evaluating deals with your own assumptions baked in, owning the tool is worth the setup.

---

## Tech

- **Python** + **Streamlit** (UI)
- **Pandas** for data handling and tables
- All calculations are standard real estate underwriting formulas (amortization, cap rate, cash-on-cash return, NOI)

---

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Disclaimer

This tool is for educational and illustrative purposes only. It is not financial or investment advice. Always verify assumptions with a lender, CPA, or licensed real estate professional before making investment decisions.
