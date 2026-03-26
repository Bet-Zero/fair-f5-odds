"""
Fair First 5 Innings Odds Calculator

A Streamlit app that calculates fair betting odds for baseball First 5 Innings (F5)
bets using Poisson distribution modeling.
"""

import streamlit as st
from scipy.stats import poisson

# Constants
MAX_RUNS = 15  # Maximum runs to consider in probability calculations

# Page configuration
st.set_page_config(page_title="⚾ Fair F5 Odds Calculator", layout="centered")

# Custom CSS for styling
st.markdown("""
<style>
/* Tighten default block vertical gaps */
.block-container {
    padding-top: 3.5rem;
    padding-bottom: 1rem;
}
/* Hide sidebar entirely */
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="collapsedControl"] {
    display: none;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.25rem;
}
/* Make team name text inputs look like plain editable text */
div[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px dashed #555 !important;
    border-radius: 0 !important;
    padding: 2px 4px !important;
    font-size: 14px !important;
    color: #fff !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus {
    border-bottom: 1px solid #aaa !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-testid="stTextInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}/* Constrain runs number input width, keeping arrows visible */
div[data-testid="stNumberInput"] {
    max-width: 140px;
    margin-right: 8px;
}
/* Color number input step buttons */
button[data-testid="stNumberInputStepUp"]:hover {
    background-color: #004d00 !important;
    border-color: #00C805 !important;
    box-shadow: none !important;
    outline: none !important;
}
button[data-testid="stNumberInputStepDown"]:hover {
    background-color: #4d0000 !important;
    border-color: #ff4444 !important;
    box-shadow: none !important;
    outline: none !important;
}
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepUp"]:focus,
button[data-testid="stNumberInputStepUp"]:active,
button[data-testid="stNumberInputStepUp"]:focus-visible,
button[data-testid="stNumberInputStepDown"],
button[data-testid="stNumberInputStepDown"]:focus,
button[data-testid="stNumberInputStepDown"]:active,
button[data-testid="stNumberInputStepDown"]:focus-visible {
    background-color: transparent !important;
    border-color: transparent !important;
    box-shadow: none !important;
    outline: none !important;
}
/* Compact number inputs so text field and arrows are close */
div[data-testid="stHorizontalBlock"] {
    gap: 0.5rem;
}
div.stButton > button:first-child {
    background-color: #2A2A2A;
    color: white;
    border: 1px solid #555;
    padding: 0.6em 1.5em;
    border-radius: 8px;
}
div.stButton > button:first-child:hover {
    background-color: #444;
    border-color: #777;
}
.odds-box {
    border: 1px solid #3A3A3A;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
    margin: 4px;
}
.probability {
    font-size: 20px;
    font-weight: bold;
}
.moneyline {
    background-color: #2C2C2C;
    color: #00C805;
    font-weight: bold;
    padding: 4px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("""
<div style='margin-bottom: 8px; padding-bottom: 8px; border-bottom: 2px solid #444;'>
    <span style='font-size: 30px; font-weight: bold;'>⚾ Fair F5 Odds Calculator</span>
    <span style='font-size: 16px; color: #aaa; margin-left: 12px;'>First 5 Innings</span>
</div>
""", unsafe_allow_html=True)


def to_moneyline(prob: float) -> str:
    """
    Convert a probability to American moneyline odds format.
    
    Args:
        prob: Win probability as a decimal (0.0 to 1.0)
        
    Returns:
        Moneyline odds as a string (e.g., "-150" or "+120")
    """
    # Handle edge cases to avoid division by zero
    if prob <= 0.0:
        return "+∞"
    if prob >= 1.0:
        return "-∞"
    
    if prob >= 0.5:
        return f"{round(-100 * prob / (1 - prob))}"
    else:
        return f"+{round(100 * (1 - prob) / prob)}"


def calculate_all_odds(team_a_runs: float, team_b_runs: float, max_runs: int = MAX_RUNS) -> dict:
    """
    Calculate fair odds for all F5 bet types using Poisson distribution.
    
    Args:
        team_a_runs: Projected runs for Team A in first 5 innings
        team_b_runs: Projected runs for Team B in first 5 innings
        max_runs: Maximum runs to consider in probability calculation
        
    Returns:
        Dictionary containing probabilities and moneylines for all bet types
    """
    prob_a_win = 0.0
    prob_tie = 0.0

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

    # For ML odds, we normalize by excluding ties (since ML pushes on tie)
    prob_a_ml_normalized = prob_a_win / (1 - prob_tie) if prob_tie < 1 else 0.5
    prob_b_ml_normalized = prob_b_win / (1 - prob_tie) if prob_tie < 1 else 0.5

    return {
        "team_a": {
            "plus_0_5": {"prob": prob_a_win_or_tie, "odds": to_moneyline(prob_a_win_or_tie)},
            "ml": {"prob": prob_a_ml_normalized, "odds": to_moneyline(prob_a_ml_normalized)},
            "minus_0_5": {"prob": prob_a_win, "odds": to_moneyline(prob_a_win)},
        },
        "team_b": {
            "plus_0_5": {"prob": prob_b_win_or_tie, "odds": to_moneyline(prob_b_win_or_tie)},
            "ml": {"prob": prob_b_ml_normalized, "odds": to_moneyline(prob_b_ml_normalized)},
            "minus_0_5": {"prob": prob_b_win, "odds": to_moneyline(prob_b_win)},
        },
        "tie_prob": prob_tie,
    }


# Seed session state defaults
if "runs_a" not in st.session_state:
    st.session_state["runs_a"] = 2.00
if "runs_b" not in st.session_state:
    st.session_state["runs_b"] = 2.00

# Calculate odds from current session state values (before inputs are rendered)
odds = calculate_all_odds(st.session_state["runs_a"], st.session_state["runs_b"])

# Input validation
if st.session_state["runs_a"] == 0.0 and st.session_state["runs_b"] == 0.0:
    st.warning("⚠️ Both teams have 0 projected runs. Results may not be meaningful.")

st.markdown("<div style='border-top: 1px solid #444; margin-top: 16px;'></div><div style='height: 20px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-size: 13px; color: #666; margin-bottom: 10px; letter-spacing: 0.05em; text-transform: uppercase;'>Fair Odds &mdash; First 5 Innings</div>", unsafe_allow_html=True)

# Header row  — 5 cols: team | runs | +0.5 | ML | -0.5
header_cols = st.columns([1.2, 1.3, 1, 1, 1])
with header_cols[0]:
    st.markdown("<div></div>", unsafe_allow_html=True)
with header_cols[1]:
    st.markdown("<div style='text-align: center; font-weight: bold; color: #888; font-size: 13px;'>F5 Runs</div>", unsafe_allow_html=True)
with header_cols[2]:
    st.markdown("<div style='text-align: center; font-weight: bold; color: #ccc;'>+0.5</div>", unsafe_allow_html=True)
with header_cols[3]:
    st.markdown("<div style='text-align: center; font-weight: bold; color: #ccc;'>Moneyline</div>", unsafe_allow_html=True)
with header_cols[4]:
    st.markdown("<div style='text-align: center; font-weight: bold; color: #ccc;'>-0.5</div>", unsafe_allow_html=True)


def render_odds_cell(prob: float, odds_str: str):
    """Render a single odds cell with probability and moneyline."""
    st.markdown(f"""
    <div class='odds-box'>
        <div class='probability'>{prob*100:.1f}%</div>
        <div class='moneyline'>{odds_str}</div>
    </div>
    """, unsafe_allow_html=True)


# Team A row
row_a = st.columns([1.2, 1.3, 1, 1, 1])
with row_a[0]:
    st.markdown("<div style='display:flex; align-items:center; min-height:90px; font-size:20px; font-weight:bold; padding-left:4px;'><span style='margin-right:8px;'>🟥</span>Team A</div>", unsafe_allow_html=True)
with row_a[1]:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.number_input("runs_a", min_value=0.0, max_value=float(MAX_RUNS), step=0.01, key="runs_a", label_visibility="collapsed", help="Expected F5 runs")
with row_a[2]:
    render_odds_cell(odds["team_a"]["plus_0_5"]["prob"], odds["team_a"]["plus_0_5"]["odds"])
with row_a[3]:
    render_odds_cell(odds["team_a"]["ml"]["prob"], odds["team_a"]["ml"]["odds"])
with row_a[4]:
    render_odds_cell(odds["team_a"]["minus_0_5"]["prob"], odds["team_a"]["minus_0_5"]["odds"])

# Team B row
row_b = st.columns([1.2, 1.3, 1, 1, 1])
with row_b[0]:
    st.markdown("<div style='display:flex; align-items:center; min-height:90px; font-size:20px; font-weight:bold; padding-left:4px;'><span style='margin-right:8px;'>🟦</span>Team B</div>", unsafe_allow_html=True)
with row_b[1]:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.number_input("runs_b", min_value=0.0, max_value=float(MAX_RUNS), step=0.01, key="runs_b", label_visibility="collapsed", help="Expected F5 runs")
with row_b[2]:
    render_odds_cell(odds["team_b"]["plus_0_5"]["prob"], odds["team_b"]["plus_0_5"]["odds"])
with row_b[3]:
    render_odds_cell(odds["team_b"]["ml"]["prob"], odds["team_b"]["ml"]["odds"])
with row_b[4]:
    render_odds_cell(odds["team_b"]["minus_0_5"]["prob"], odds["team_b"]["minus_0_5"]["odds"])

# Show tie probability
st.markdown(f"<div style='text-align: center; color: #888; margin-top: 18px; margin-bottom: 18px;'>Tie probability: {odds['tie_prob']*100:.1f}%</div>", unsafe_allow_html=True)

# Decorative bottom rectangle
st.markdown("<div style='border: 1px solid #3A3A3A; border-radius: 8px; height: 48px; margin-top: 4px;'></div>", unsafe_allow_html=True)
