
import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Fair F5 Odds Calculator", layout="centered")

st.title("⚾ Fair First 5 Innings Odds Calculator")

st.markdown("Enter projected runs for each team in the first 5 innings to calculate fair odds for +0.5 and ML bets.")

team_a_runs = st.number_input("Projected F5 Runs – Team A", min_value=0.0, max_value=10.0, value=2.14, step=0.01)
team_b_runs = st.number_input("Projected F5 Runs – Team B", min_value=0.0, max_value=10.0, value=2.25, step=0.01)

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
        "Team A +0.5 F5 (Tied or Leading)": {
            "probability": round(prob_a_win_or_tie * 100, 2),
            "moneyline": to_moneyline(prob_a_win_or_tie)
        },
        "Team A ML F5 (Must Be Leading)": {
            "probability": round(prob_a_win_only * 100, 2),
            "moneyline": to_moneyline(prob_a_win_only)
        },
        "Team B +0.5 F5 (Tied or Leading)": {
            "probability": round(prob_b_win_or_tie * 100, 2),
            "moneyline": to_moneyline(prob_b_win_or_tie)
        },
        "Team B ML F5 (Must Be Leading)": {
            "probability": round(prob_b_win_only * 100, 2),
            "moneyline": to_moneyline(prob_b_win_only)
        }
    }

if st.button("Calculate Fair Odds"):
    results = calculate_fair_odds(team_a_runs, team_b_runs)
    st.markdown("### 📊 Fair Odds")
    for label, data in results.items():
        st.markdown(f"**{label}**")
        st.markdown(f"- Probability: {data['probability']}%")
        st.markdown(f"- Fair Moneyline: `{data['moneyline']}`")
        st.markdown("---")
