import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Fair First 5 Odds", layout="centered")

st.title("⚾ Fair First 5 Innings Odds Calculator")
st.markdown("Enter projected runs for each team in the first 5 innings to calculate fair odds for +0.5 and ML bets.")

# Inputs
team_a_runs = st.number_input("Projected F5 Runs – Team A", min_value=0.0, max_value=10.0, value=2.14, step=0.01)
team_b_runs = st.number_input("Projected F5 Runs – Team B", min_value=0.0, max_value=10.0, value=2.25, step=0.01)

# Core calculation
def calculate_fair_odds(team_a_runs, team_b_runs, max_runs=15):
    prob_a_win_or_tie = 0
    prob_a_win_only = 0

    for a_runs in range(max_runs + 1):
        for b_runs in range(max_runs + 1):
            p_a = poisson.pmf(a_runs, team_a_runs)
            p_b = poisson.pmf(b_runs, team_b_runs)
            if a_runs >= b_runs:
                prob_a_win_or_tie += p_a * p_b
            if a_runs > b_runs:
                prob_a_win_only += p_a * p_b

    prob_b_win_or_tie = 1 - prob_a_win_only
    prob_b_win_only = 1 - prob_a_win_or_tie

    def to_moneyline(prob):
        if prob >= 0.5:
            return f"{round(-100 * prob / (1 - prob))}"
        else:
            return f"+{round(100 * (1 - prob) / prob)}"

    return {
        "Team A +0.5 F5": {
            "probability": round(prob_a_win_or_tie * 100, 2),
            "moneyline": to_moneyline(prob_a_win_or_tie)
        },
        "Team A ML F5": {
            "probability": round(prob_a_win_only * 100, 2),
            "moneyline": to_moneyline(prob_a_win_only)
        },
        "Team B +0.5 F5": {
            "probability": round(prob_b_win_or_tie * 100, 2),
            "moneyline": to_moneyline(prob_b_win_or_tie)
        },
        "Team B ML F5": {
            "probability": round(prob_b_win_only * 100, 2),
            "moneyline": to_moneyline(prob_b_win_only)
        }
    }

# Output
if st.button("Calculate Fair Odds"):
    results = calculate_fair_odds(team_a_runs, team_b_runs)
    st.markdown("### 📊 Fair Odds")

    # Team A Output
    st.markdown("#### 🟥 Team A")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**+0.5 F5**")
        st.markdown(f"- Probability: {results['Team A +0.5 F5']['probability']}%")
        st.markdown(f"- Moneyline: `{results['Team A +0.5 F5']['moneyline']}`")
    with col2:
        st.markdown("**ML F5**")
        st.markdown(f"- Probability: {results['Team A ML F5']['probability']}%")
        st.markdown(f"- Moneyline: `{results['Team A ML F5']['moneyline']}`")

    # Divider
    st.markdown("---")

    # Team B Output
    st.markdown("#### 🟦 Team B")
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown("**+0.5 F5**")
        st.markdown(f"- Probability: {results['Team B +0.5 F5']['probability']}%")
        st.markdown(f"- Moneyline: `{results['Team B +0.5 F5']['moneyline']}`")
    with col4:
        st.markdown("**ML F5**")
        st.markdown(f"- Probability: {results['Team B ML F5']['probability']}%")
        st.markdown(f"- Moneyline: `{results['Team B ML F5']['moneyline']}`")
