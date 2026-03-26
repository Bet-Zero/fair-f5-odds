# ⚾ Fair F5 Odds Calculator

A Streamlit web app that calculates **fair betting odds** for baseball **First 5 Innings (F5)** bets using Poisson distribution modeling.

## 🎯 What It Does

Enter your projected run totals for each team in the first 5 innings, and the calculator will compute fair odds for:

- **+0.5 (Run Line)**: Probability of winning OR tying after 5 innings
- **Moneyline (ML)**: Probability of winning outright (pushes on tie)
- **-0.5 (Run Line)**: Probability of leading after 5 innings

All odds are displayed in **American moneyline format** (e.g., -150, +120).

## 📊 The Math

The calculator uses **Poisson distribution** to model the probability of each team scoring 0, 1, 2, ... runs. For projected runs λ, the probability of scoring exactly k runs is:

```
P(X = k) = (λ^k × e^(-λ)) / k!
```

By computing the joint probabilities for all score combinations, we determine:
- Win probability for each team
- Tie probability
- Fair moneyline odds (converted from implied probability)

## 🚀 Getting Started

### Option 1: GitHub Codespaces (Easiest)
1. Click the green **Code** button on this repo
2. Select **Codespaces** → **Create codespace on main**
3. The app will automatically start and open in the preview pane

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/Bet-Zero/fair-f5-odds.git
cd fair-f5-odds

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run fair_f5_streamlit.py
```

The app will open in your browser at `http://localhost:8501`.

## 📦 Dependencies

- **streamlit** – Web app framework
- **scipy** – Statistical functions (Poisson distribution)

## 📝 Usage Tips

1. **Team Names**: Enter custom team names for easier reference
2. **Projected Runs**: Use your own projections or pull from a source like FanGraphs
3. **Interpreting Results**: Compare the fair odds to sportsbook lines to find value

## 🤔 What is "Fair" Odds?

Fair odds represent the **true probability** of an outcome without any sportsbook margin (vig/juice). If a sportsbook offers odds that are worse than your fair odds calculation, you've found potential value.

**Example**: If your model says Team A ML is fair at -130, and a book offers -110, that's a +EV bet.

## 📄 License

MIT License – feel free to use, modify, and share!
