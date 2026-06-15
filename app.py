import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Rental Property Investment Analyzer", layout="wide")

st.title("Rental Property Investment Analyzer")
st.caption("Built for evaluating rental deals in Whatcom County, WA — model real cash flow, ghost costs, and remodel ROI before you buy.")

st.markdown("---")

# ============================================================
# SIDEBAR - Property & Loan Inputs
# ============================================================
st.sidebar.header("Property Details")
purchase_price = st.sidebar.number_input("Purchase Price ($)", value=575000, step=10000)
down_payment_pct = st.sidebar.slider("Down Payment (%)", 5, 50, 20)
interest_rate = st.sidebar.slider("Interest Rate (%)", 3.0, 9.0, 6.75, step=0.05)
loan_term_years = st.sidebar.selectbox("Loan Term (years)", [15, 20, 30], index=2)

st.sidebar.header("Rental Income")
monthly_rent = st.sidebar.number_input("Monthly Rent ($)", value=2400, step=100)
annual_rent_growth = st.sidebar.slider("Annual Rent Growth (%)", 0.0, 6.0, 3.0, step=0.5)

st.sidebar.header("Ghost Costs (% of rent unless noted)")
vacancy_pct = st.sidebar.slider("Vacancy Rate (%)", 0, 15, 6)
maintenance_pct = st.sidebar.slider("Maintenance Reserve (%)", 0, 15, 7)
capex_pct = st.sidebar.slider("CapEx Reserve (%)", 0, 15, 7)
mgmt_pct = st.sidebar.slider("Property Management (%)", 0, 15, 9)

st.sidebar.header("Fixed Annual Costs")
property_taxes = st.sidebar.number_input("Property Taxes ($/yr)", value=5200, step=100)
insurance = st.sidebar.number_input("Insurance ($/yr)", value=1400, step=50)
hoa = st.sidebar.number_input("HOA Fees ($/yr)", value=0, step=50)

st.sidebar.header("Appreciation")
annual_appreciation = st.sidebar.slider("Annual Appreciation (%)", 0.0, 8.0, 3.5, step=0.5)
hold_period_years = st.sidebar.slider("Hold Period (years)", 1, 30, 10)

# ============================================================
# CORE CASH FLOW CALCULATIONS
# ============================================================
down_payment = purchase_price * (down_payment_pct / 100)
loan_amount = purchase_price - down_payment

monthly_rate = (interest_rate / 100) / 12
n_payments = loan_term_years * 12

if monthly_rate > 0:
    monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / \
                        ((1 + monthly_rate) ** n_payments - 1)
else:
    monthly_mortgage = loan_amount / n_payments

annual_rent = monthly_rent * 12
vacancy_cost = annual_rent * (vacancy_pct / 100)
maintenance_cost = annual_rent * (maintenance_pct / 100)
capex_cost = annual_rent * (capex_pct / 100)
mgmt_cost = annual_rent * (mgmt_pct / 100)

ghost_costs_total = vacancy_cost + maintenance_cost + capex_cost + mgmt_cost
fixed_costs_total = property_taxes + insurance + hoa
annual_mortgage = monthly_mortgage * 12

effective_gross_income = annual_rent - vacancy_cost
operating_expenses = maintenance_cost + capex_cost + mgmt_cost + fixed_costs_total
noi = effective_gross_income - operating_expenses  # Net Operating Income (before debt)

annual_cash_flow = noi - annual_mortgage
monthly_cash_flow = annual_cash_flow / 12

cap_rate = (noi / purchase_price) * 100
cash_invested = down_payment  # simplified: assumes no closing costs/rehab folded in here
cash_on_cash = (annual_cash_flow / cash_invested) * 100 if cash_invested > 0 else 0

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Cash Flow & Ghost Costs",
    "Remodel ROI",
    "Long-Term Returns",
    "Scenario Comparison (A/B)"
])

# ------------------------------------------------------------
# TAB 1: Cash Flow
# ------------------------------------------------------------
with tab1:
    st.subheader("Monthly Cash Flow Breakdown")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Cash Flow", f"${monthly_cash_flow:,.0f}")
    col2.metric("Cap Rate", f"{cap_rate:.2f}%")
    col3.metric("Cash-on-Cash Return", f"{cash_on_cash:.2f}%")
    col4.metric("Monthly Mortgage (P&I)", f"${monthly_mortgage:,.0f}")

    st.markdown("### Where the rent actually goes")
    breakdown = pd.DataFrame({
        "Category": [
            "Mortgage (P&I)", "Property Taxes", "Insurance", "HOA",
            "Vacancy Reserve", "Maintenance Reserve", "CapEx Reserve", "Property Management",
            "Cash Flow"
        ],
        "Monthly Cost ($)": [
            monthly_mortgage, property_taxes/12, insurance/12, hoa/12,
            vacancy_cost/12, maintenance_cost/12, capex_cost/12, mgmt_cost/12,
            monthly_cash_flow
        ]
    })
    st.bar_chart(breakdown.set_index("Category"))
    st.dataframe(breakdown.style.format({"Monthly Cost ($)": "${:,.0f}"}), use_container_width=True)

    st.markdown("### Deal Score")
    # Simple weighted score: cash flow (40%), cap rate (30%), cash-on-cash (30%)
    cf_score = min(max(monthly_cash_flow / 5, 0), 40)  # $200/mo cash flow = 40 pts
    cap_score = min(max(cap_rate * 6, 0), 30)  # 5% cap rate = 30 pts
    coc_score = min(max(cash_on_cash * 3, 0), 30)  # 10% CoC = 30 pts
    deal_score = cf_score + cap_score + coc_score

    st.progress(min(deal_score / 100, 1.0))
    if deal_score >= 70:
        st.success(f"Deal Score: {deal_score:.0f}/100 — Strong deal")
    elif deal_score >= 45:
        st.warning(f"Deal Score: {deal_score:.0f}/100 — Marginal, depends on your goals")
    else:
        st.error(f"Deal Score: {deal_score:.0f}/100 — Weak on cash flow / returns")

    st.caption("Score weights: Monthly Cash Flow (40%), Cap Rate (30%), Cash-on-Cash Return (30%). "
               "This is a simplified heuristic, not investment advice — use it to compare deals against each other, not as a final answer.")

# ------------------------------------------------------------
# TAB 2: Remodel ROI
# ------------------------------------------------------------
with tab2:
    st.subheader("Remodel / Rehab ROI Calculator")
    st.caption("Will the remodel pay for itself? Compare cost vs. value added.")

    rcol1, rcol2 = st.columns(2)

    with rcol1:
        st.markdown("**Rehab Budget by Category**")
        kitchen = st.number_input("Kitchen ($)", value=15000, step=500)
        bathroom = st.number_input("Bathroom(s) ($)", value=8000, step=500)
        flooring = st.number_input("Flooring ($)", value=6000, step=500)
        roof = st.number_input("Roof ($)", value=0, step=500)
        paint_curb = st.number_input("Paint / Curb Appeal ($)", value=3000, step=500)
        other_rehab = st.number_input("Other ($)", value=2000, step=500)

    total_rehab_cost = kitchen + bathroom + flooring + roof + paint_curb + other_rehab

    with rcol2:
        st.markdown("**Value Impact**")
        current_value = st.number_input("Current 'As-Is' Value ($)", value=purchase_price, step=5000)
        arv = st.number_input("After-Repair Value (ARV) ($)", value=int(purchase_price * 1.12), step=5000)
        rent_increase = st.number_input("Monthly Rent Increase After Remodel ($)", value=150, step=25)

    value_added = arv - current_value
    remodel_roi = ((value_added - total_rehab_cost) / total_rehab_cost * 100) if total_rehab_cost > 0 else 0
    annual_rent_increase = rent_increase * 12
    rent_payback_years = total_rehab_cost / annual_rent_increase if annual_rent_increase > 0 else float('inf')

    st.markdown("### Results")
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Total Rehab Cost", f"${total_rehab_cost:,.0f}")
    mcol2.metric("Value Added (ARV - Current)", f"${value_added:,.0f}")
    mcol3.metric("ROI on Remodel", f"{remodel_roi:.1f}%")

    if remodel_roi > 0:
        st.success(f"This remodel adds **${value_added - total_rehab_cost:,.0f}** more in value than it costs. "
                    f"Plus it pays back through rent increases in **{rent_payback_years:.1f} years**.")
    else:
        st.error(f"This remodel costs more than the value it adds (-${abs(value_added - total_rehab_cost):,.0f}). "
                 f"Only do it if the rent increase justifies it — payback would take {rent_payback_years:.1f} years.")

    rehab_df = pd.DataFrame({
        "Category": ["Kitchen", "Bathroom(s)", "Flooring", "Roof", "Paint/Curb Appeal", "Other"],
        "Cost ($)": [kitchen, bathroom, flooring, roof, paint_curb, other_rehab]
    })
    st.bar_chart(rehab_df.set_index("Category"))

# ------------------------------------------------------------
# TAB 3: Long-Term Returns
# ------------------------------------------------------------
with tab3:
    st.subheader(f"{hold_period_years}-Year Hold: Total Return Projection")

    years = list(range(1, hold_period_years + 1))
    property_values = []
    loan_balances = []
    cumulative_cash_flow = []
    rents = []

    balance = loan_amount
    cum_cf = 0
    rent = monthly_rent

    for year in years:
        # Property value with appreciation
        prop_value = purchase_price * ((1 + annual_appreciation/100) ** year)
        property_values.append(prop_value)

        # Rent grows annually
        if year > 1:
            rent = rent * (1 + annual_rent_growth/100)
        rents.append(rent * 12)

        # Recalculate cash flow with new rent (costs scale with rent for variable items)
        ann_rent = rent * 12
        vac = ann_rent * (vacancy_pct/100)
        maint = ann_rent * (maintenance_pct/100)
        cap = ann_rent * (capex_pct/100)
        mgmt = ann_rent * (mgmt_pct/100)
        egi = ann_rent - vac
        opex = maint + cap + mgmt + fixed_costs_total
        year_noi = egi - opex
        year_cf = year_noi - annual_mortgage
        cum_cf += year_cf
        cumulative_cash_flow.append(cum_cf)

        # Loan amortization (rough annual paydown)
        for _ in range(12):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_mortgage - interest_payment
            balance -= principal_payment
        loan_balances.append(max(balance, 0))

    equity_from_paydown = [loan_amount - lb for lb in loan_balances]
    equity_from_appreciation = [pv - purchase_price for pv in property_values]
    total_equity = [property_values[i] - loan_balances[i] - down_payment for i in range(len(years))]

    df = pd.DataFrame({
        "Year": years,
        "Property Value": property_values,
        "Loan Balance": loan_balances,
        "Cumulative Cash Flow": cumulative_cash_flow,
        "Total Profit (Equity Gain + Cash Flow)": [total_equity[i] + cumulative_cash_flow[i] for i in range(len(years))]
    })

    final_property_value = property_values[-1]
    final_loan_balance = loan_balances[-1]
    final_equity = final_property_value - final_loan_balance
    total_profit = (final_equity - down_payment) + cumulative_cash_flow[-1]
    total_return_pct = (total_profit / down_payment) * 100
    annualized_return = ((1 + total_return_pct/100) ** (1/hold_period_years) - 1) * 100

    st.markdown("### Summary")
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric(f"Total Profit ({hold_period_years} yrs)", f"${total_profit:,.0f}")
    scol2.metric("Total Return on Down Payment", f"{total_return_pct:.0f}%")
    scol3.metric("Annualized Return (IRR-style)", f"{annualized_return:.1f}%")

    st.markdown("### Equity & Cash Flow Over Time")
    st.line_chart(df.set_index("Year")[["Property Value", "Loan Balance", "Total Profit (Equity Gain + Cash Flow)"]])

    with st.expander("See full year-by-year table"):
        st.dataframe(df.style.format({
            "Property Value": "${:,.0f}",
            "Loan Balance": "${:,.0f}",
            "Cumulative Cash Flow": "${:,.0f}",
            "Total Profit (Equity Gain + Cash Flow)": "${:,.0f}"
        }), use_container_width=True)

# ------------------------------------------------------------
# TAB 4: Scenario Comparison (A/B Test style)
# ------------------------------------------------------------
with tab4:
    st.subheader("Scenario A/B Comparison")
    st.caption("Compare two financing or strategy scenarios side by side — e.g. 20% down vs. 25% down, or buy-and-hold vs. add a remodel.")

    acol, bcol = st.columns(2)

    with acol:
        st.markdown("#### Scenario A")
        a_down_pct = st.slider("Down Payment % (A)", 5, 50, down_payment_pct, key="a_down")
        a_rate = st.slider("Interest Rate % (A)", 3.0, 9.0, interest_rate, step=0.05, key="a_rate")
        a_rehab = st.number_input("Rehab Cost Added Upfront ($) (A)", value=0, step=1000, key="a_rehab")
        a_rent = st.number_input("Monthly Rent (A)", value=monthly_rent, step=50, key="a_rent")

    with bcol:
        st.markdown("#### Scenario B")
        b_down_pct = st.slider("Down Payment % (B)", 5, 50, 25, key="b_down")
        b_rate = st.slider("Interest Rate % (B)", 3.0, 9.0, interest_rate, step=0.05, key="b_rate")
        b_rehab = st.number_input("Rehab Cost Added Upfront ($) (B)", value=total_rehab_cost, step=1000, key="b_rehab")
        b_rent = st.number_input("Monthly Rent (B)", value=monthly_rent + rent_increase, step=50, key="b_rent")

    def calc_scenario(down_pct, rate, rehab, rent):
        dp = purchase_price * (down_pct/100)
        loan = purchase_price - dp
        m_rate = (rate/100)/12
        n = loan_term_years * 12
        if m_rate > 0:
            pmt = loan * (m_rate * (1+m_rate)**n) / ((1+m_rate)**n - 1)
        else:
            pmt = loan / n
        ann_rent = rent * 12
        vac = ann_rent * (vacancy_pct/100)
        maint = ann_rent * (maintenance_pct/100)
        cap = ann_rent * (capex_pct/100)
        mgmt = ann_rent * (mgmt_pct/100)
        egi = ann_rent - vac
        opex = maint + cap + mgmt + fixed_costs_total
        noi_s = egi - opex
        cf = noi_s - (pmt * 12)
        cash_invested_s = dp + rehab
        coc = (cf / cash_invested_s) * 100 if cash_invested_s > 0 else 0
        return {
            "Cash Invested": cash_invested_s,
            "Monthly Cash Flow": cf / 12,
            "Annual Cash Flow": cf,
            "Cash-on-Cash Return": coc,
            "Monthly Payment": pmt
        }

    result_a = calc_scenario(a_down_pct, a_rate, a_rehab, a_rent)
    result_b = calc_scenario(b_down_pct, b_rate, b_rehab, b_rent)

    comparison_df = pd.DataFrame({
        "Metric": ["Cash Invested ($)", "Monthly Cash Flow ($)", "Annual Cash Flow ($)", "Cash-on-Cash Return (%)", "Monthly Mortgage Payment ($)"],
        "Scenario A": [result_a["Cash Invested"], result_a["Monthly Cash Flow"], result_a["Annual Cash Flow"], result_a["Cash-on-Cash Return"], result_a["Monthly Payment"]],
        "Scenario B": [result_b["Cash Invested"], result_b["Monthly Cash Flow"], result_b["Annual Cash Flow"], result_b["Cash-on-Cash Return"], result_b["Monthly Payment"]],
    })

    st.markdown("### Side-by-Side Results")
    st.dataframe(comparison_df.style.format({"Scenario A": "{:,.2f}", "Scenario B": "{:,.2f}"}), use_container_width=True)

    winner = "A" if result_a["Cash-on-Cash Return"] > result_b["Cash-on-Cash Return"] else "B"
    diff = abs(result_a["Cash-on-Cash Return"] - result_b["Cash-on-Cash Return"])
    st.info(f"**Scenario {winner}** has the better cash-on-cash return, by **{diff:.2f} percentage points**. "
            f"Higher down payments reduce your mortgage but tie up more cash — the 'better' choice depends on whether you're optimizing for cash flow now or capital growth long-term.")

st.markdown("---")
st.caption("This tool is for educational/illustrative purposes. Not financial advice. Always verify your numbers with a lender, CPA, or licensed professional before making investment decisions.")
