
import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="⚾ Fair Odds Calculator", layout="centered")

# Colors
dark_bg = "#1E1E1E"
green_text = "#00C805"
label_bg = "#2C2C2C"
box_border = "#3A3A3A"

# Title & subtitle
st.markdown("<h1 style='font-size: 42px;'>⚾ Fair Odds Calculator</h1>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='
        margin-top: 8px;
        margin-bottom: 24px;
        display: inline-block;
        font-size: 24px;
        font-weight: bold;
        color: white;
        border-bottom: 2px solid white;
    '>First 5 Innings</div>
""", unsafe_allow_html=True)

# Inputs
team_a_runs = st.number_input("Projected F5 Runs – Team A", min_value=0.0, max_value=10.0, value=2.00, step=0.01)
team_b_runs = st.number_input("Projected F5 Runs – Team B", min_value=0.0, max_value=10.0, value=2.00, step=0.01)

# Button styling
button_style = """
<style>
div.stButton > button:first-child {
    background-color: #2A2A2A;
    color: white;
    border: 1px solid #555;
    padding: 0.6em 1.5em;
    border-radius: 8px;
}
div.stButton > button:first-child:active {
    background-color: #444;
    border-color: #777;
}
</style>
"""
st.markdown(button_style, unsafe_allow_html=True)

# Odds logic
def to_moneyline(prob):
    if prob >= 0.5:
        return f"{round(-100 * prob / (1 - prob))}"
    else:
        return f"+{round(100 * (1 - prob) / prob)}"

def calculate_all_odds(team_a_runs, team_b_runs, max_runs=15):
    prob_a_win = 0
    prob_tie = 0

    for a in range(max_runs + 1):
        for b in range(max_runs + 1):
            p_a = poisson.pmf(a, team_a_runs)
            p_b = poisson.pmf(b, team_b_runs)

            if a > b:
                prob_a_win += p_a * p_b
            elif a == b:
                prob_tie += p_a * p_b

    prob_b_win = 1 - prob_a_win - prob_tie
    prob_a_win_or_tie = prob_a_win + prob_tie
    prob_b_win_or_tie = prob_b_win + prob_tie

    odds_a_ml = to_moneyline(prob_a_win / (1 - prob_tie))
    odds_b_ml = to_moneyline(prob_b_win / (1 - prob_tie))
    odds_a_minus_0_5 = to_moneyline(prob_a_win)
    odds_b_minus_0_5 = to_moneyline(prob_b_win)
    odds_a_plus_0_5 = to_moneyline(prob_a_win_or_tie)
    odds_b_plus_0_5 = to_moneyline(prob_b_win_or_tie)

    return {
        "Team A": {
            "(<span style='font-weight:normal;'>+0.5</span>)": (prob_a_win_or_tie, odds_a_plus_0_5),
            "Moneyline": (prob_a_win, odds_a_ml),
            "(<span style='font-weight:normal;'>-0.5</span>)": (prob_a_win, odds_a_minus_0_5)
        },
        "Team B": {
            "(<span style='font-weight:normal;'>+0.5</span>)": (prob_b_win_or_tie, odds_b_plus_0_5),
            "Moneyline": (prob_b_win, odds_b_ml),
            "(<span style='font-weight:normal;'>-0.5</span>)": (prob_b_win, odds_b_minus_0_5)
        }
    }

# Output
if st.button("Calculate Fair Odds"):
    odds = calculate_all_odds(team_a_runs, team_b_runs)

    st.markdown(f"<div style='background-color: {label_bg}; padding: 8px 14px; margin-top: 20px; border-radius: 6px; font-size: 20px;'><strong>Fair Odds – First 5 Innings</strong></div>", unsafe_allow_html=True)
    st.markdown("")

    st.markdown(f"""
        <div style='background-color: {label_bg}; padding: 10px 30px; margin-top: 10px; border-radius: 6px; display: flex; font-size: 18px; font-weight: bold; color: white;'>
            <div style='width: 160px;'>&nbsp;</div>
            <div style='width: 120px; text-align: center;'>(<span style='font-weight:normal;'>+0.5</span>)</div>
            <div style='width: 120px; text-align: center;'>Moneyline</div>
            <div style='width: 120px; text-align: center;'>(<span style='font-weight:normal;'>-0.5</span>)</div>
        </div>
    """, unsafe_allow_html=True)

    def render_team_row(team_name, color, data):
        return f"""
        <div style='display: flex; padding: 14px 30px; align-items: center; font-size: 20px;'>
            <div style='width: 160px; display: flex; align-items: center; color: white; font-weight: bold;'>{color} {team_name}</div>
            {''.join([
                f"<div style='width: 120px; text-align: center;'><div style='border: 1px solid {box_border}; border-radius: 6px; padding: 12px 8px;'>"
                f"<div style='color: white; font-size: 21px; font-weight: bold;'>{data[bet][0]*100:.1f}%</div>"
                f"<div style='background-color: {label_bg}; color: {green_text}; font-weight: bold; padding: 3px 8px; border-radius: 4px; margin-top: 4px; display: inline-block; font-size: 18px;'>{data[bet][1]}</div>"
                f"</div></div>" for bet in data
            ])}
        </div>
        """

    st.markdown(render_team_row("Team A", "🟥", odds["Team A"]), unsafe_allow_html=True)
    st.markdown(f"<hr style='margin: 8px 30px 6px 30px; border: none; border-top: 1px solid {label_bg};'>", unsafe_allow_html=True)
    st.markdown(render_team_row("Team B", "🟦", odds["Team B"]), unsafe_allow_html=True)
    