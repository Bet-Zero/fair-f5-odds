"""
Fair First 5 Innings Odds Calculator

A Streamlit app that calculates fair betting odds for baseball First 5 Innings (F5)
bets using Poisson distribution modeling.
"""

import streamlit as st
from scipy.stats import poisson

# Page configuration
st.set_page_config(page_title="⚾ Fair F5 Odds Calculator", layout="centered")

# Custom CSS for styling
st.markdown("""
<style>
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
st.markdown("<h1 style='font-size: 38px;'>⚾ Fair F5 Odds Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #444;'>
    <span style='font-size: 22px; font-weight: bold;'>First 5 Innings</span>
</div>
""", unsafe_allow_html=True)

st.markdown("Enter projected runs and team names to calculate fair odds for F5 bets.")


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


def calculate_all_odds(team_a_runs: float, team_b_runs: float, max_runs: int = 15) -> dict:
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


# Team name inputs
col_names = st.columns(2)
with col_names[0]:
    team_a_name = st.text_input("Team A Name", value="Team A", max_chars=20)
with col_names[1]:
    team_b_name = st.text_input("Team B Name", value="Team B", max_chars=20)

# Projected runs inputs with tooltips
col_runs = st.columns(2)
with col_runs[0]:
    team_a_runs = st.number_input(
        f"Projected F5 Runs – {team_a_name}",
        min_value=0.0,
        max_value=15.0,
        value=2.00,
        step=0.01,
        help="Expected runs for this team in the first 5 innings based on your projections"
    )
with col_runs[1]:
    team_b_runs = st.number_input(
        f"Projected F5 Runs – {team_b_name}",
        min_value=0.0,
        max_value=15.0,
        value=2.00,
        step=0.01,
        help="Expected runs for this team in the first 5 innings based on your projections"
    )

# Input validation
if team_a_runs == 0.0 and team_b_runs == 0.0:
    st.warning("⚠️ Both teams have 0 projected runs. Results may not be meaningful.")

# Explanatory section (collapsed by default)
with st.expander("ℹ️ What do these bet types mean?"):
    st.markdown("""
    - **+0.5 (Run Line)**: Win if your team is winning OR tied after 5 innings. 
      This is like getting half a run head start.
    - **Moneyline (ML)**: Win if your team is winning after 5 innings. 
      Pushes (refunds) if tied.
    - **-0.5 (Run Line)**: Win ONLY if your team is winning after 5 innings. 
      This is like giving half a run handicap.
    
    *Odds are calculated using Poisson distribution modeling based on your projected run totals.*
    """)

# Calculate and display results automatically
odds = calculate_all_odds(team_a_runs, team_b_runs)

st.markdown("---")
st.markdown("### 📊 Fair Odds – First 5 Innings")

# Header row
header_cols = st.columns([1.5, 1, 1, 1])
with header_cols[0]:
    st.markdown("**Team**")
with header_cols[1]:
    st.markdown("**+0.5**")
with header_cols[2]:
    st.markdown("**Moneyline**")
with header_cols[3]:
    st.markdown("**-0.5**")


def render_odds_cell(prob: float, odds_str: str):
    """Render a single odds cell with probability and moneyline."""
    st.markdown(f"""
    <div class='odds-box'>
        <div class='probability'>{prob*100:.1f}%</div>
        <div class='moneyline'>{odds_str}</div>
    </div>
    """, unsafe_allow_html=True)


# Team A row
row_a = st.columns([1.5, 1, 1, 1])
with row_a[0]:
    st.markdown(f"🟥 **{team_a_name}**")
with row_a[1]:
    render_odds_cell(odds["team_a"]["plus_0_5"]["prob"], odds["team_a"]["plus_0_5"]["odds"])
with row_a[2]:
    render_odds_cell(odds["team_a"]["ml"]["prob"], odds["team_a"]["ml"]["odds"])
with row_a[3]:
    render_odds_cell(odds["team_a"]["minus_0_5"]["prob"], odds["team_a"]["minus_0_5"]["odds"])

# Team B row
row_b = st.columns([1.5, 1, 1, 1])
with row_b[0]:
    st.markdown(f"🟦 **{team_b_name}**")
with row_b[1]:
    render_odds_cell(odds["team_b"]["plus_0_5"]["prob"], odds["team_b"]["plus_0_5"]["odds"])
with row_b[2]:
    render_odds_cell(odds["team_b"]["ml"]["prob"], odds["team_b"]["ml"]["odds"])
with row_b[3]:
    render_odds_cell(odds["team_b"]["minus_0_5"]["prob"], odds["team_b"]["minus_0_5"]["odds"])

# Show tie probability
st.markdown(f"<div style='text-align: center; color: #888; margin-top: 10px;'>Tie probability: {odds['tie_prob']*100:.1f}%</div>", unsafe_allow_html=True)
