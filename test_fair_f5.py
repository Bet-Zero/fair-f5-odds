"""
Unit tests for the Fair F5 Odds Calculator functions.

Run with: pytest test_fair_f5.py -v
"""

import pytest
from scipy.stats import poisson

# Import constants and functions to test
# Since fair_f5_streamlit.py has Streamlit UI code at module level,
# we need to recreate the core functions here for testing
MAX_RUNS = 15


def to_moneyline(prob: float) -> str:
    """
    Convert a probability to American moneyline odds format.
    """
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


# ============================================================================
# Tests for to_moneyline()
# ============================================================================

class TestToMoneyline:
    """Tests for the to_moneyline probability-to-odds conversion function."""

    def test_favorite_50_percent(self):
        """50% probability should be -100 (even money)."""
        assert to_moneyline(0.5) == "-100"

    def test_heavy_favorite(self):
        """70% probability should be a negative moneyline."""
        result = to_moneyline(0.7)
        assert result.startswith("-")
        assert result == "-233"  # -100 * 0.7 / 0.3 = -233.33

    def test_underdog(self):
        """30% probability should be a positive moneyline."""
        result = to_moneyline(0.3)
        assert result.startswith("+")
        assert result == "+233"  # 100 * 0.7 / 0.3 = 233.33

    def test_extreme_favorite(self):
        """90% probability should be a large negative moneyline."""
        result = to_moneyline(0.9)
        assert result == "-900"

    def test_extreme_underdog(self):
        """10% probability should be a large positive moneyline."""
        result = to_moneyline(0.1)
        assert result == "+900"

    def test_edge_case_zero_probability(self):
        """0% probability should return +∞ (infinitely unlikely)."""
        assert to_moneyline(0.0) == "+∞"

    def test_edge_case_100_percent(self):
        """100% probability should return -∞ (sure thing)."""
        assert to_moneyline(1.0) == "-∞"

    def test_edge_case_negative_probability(self):
        """Negative probability should be treated as 0."""
        assert to_moneyline(-0.1) == "+∞"

    def test_edge_case_over_100_percent(self):
        """Probability > 1 should be treated as 100%."""
        assert to_moneyline(1.5) == "-∞"

    def test_slight_favorite(self):
        """55% probability should be around -122."""
        result = to_moneyline(0.55)
        assert result == "-122"

    def test_slight_underdog(self):
        """45% probability should be around +122."""
        result = to_moneyline(0.45)
        assert result == "+122"


# ============================================================================
# Tests for calculate_all_odds()
# ============================================================================

class TestCalculateAllOdds:
    """Tests for the calculate_all_odds Poisson-based probability calculator."""

    def test_equal_teams(self):
        """Two equal teams should have symmetric odds."""
        result = calculate_all_odds(2.0, 2.0)
        
        # Probabilities should be symmetric
        assert abs(result["team_a"]["ml"]["prob"] - 0.5) < 0.01
        assert abs(result["team_b"]["ml"]["prob"] - 0.5) < 0.01
        
        # Win probabilities should be equal
        assert abs(result["team_a"]["minus_0_5"]["prob"] - 
                   result["team_b"]["minus_0_5"]["prob"]) < 0.01

    def test_stronger_team_favored(self):
        """Team with more projected runs should be favored."""
        result = calculate_all_odds(3.0, 2.0)
        
        # Team A should be favored
        assert result["team_a"]["ml"]["prob"] > result["team_b"]["ml"]["prob"]
        assert result["team_a"]["minus_0_5"]["prob"] > result["team_b"]["minus_0_5"]["prob"]

    def test_probabilities_sum_correctly(self):
        """Win + Tie + Loss probabilities should sum to 1."""
        result = calculate_all_odds(2.5, 2.0)
        
        prob_a_win = result["team_a"]["minus_0_5"]["prob"]
        prob_b_win = result["team_b"]["minus_0_5"]["prob"]
        prob_tie = result["tie_prob"]
        
        total = prob_a_win + prob_b_win + prob_tie
        assert abs(total - 1.0) < 0.001

    def test_plus_half_is_win_or_tie(self):
        """Plus 0.5 probability should equal win probability + tie probability."""
        result = calculate_all_odds(2.0, 2.0)
        
        expected_a_plus = result["team_a"]["minus_0_5"]["prob"] + result["tie_prob"]
        assert abs(result["team_a"]["plus_0_5"]["prob"] - expected_a_plus) < 0.001

    def test_ml_normalized_excludes_ties(self):
        """ML probability should be normalized to exclude ties."""
        result = calculate_all_odds(2.0, 2.0)
        
        # ML probs should sum to 1 (not including ties)
        ml_total = result["team_a"]["ml"]["prob"] + result["team_b"]["ml"]["prob"]
        assert abs(ml_total - 1.0) < 0.001

    def test_zero_runs_edge_case(self):
        """Zero runs should still produce valid probabilities."""
        result = calculate_all_odds(0.0, 0.0)
        
        # With 0 expected runs for both, tie probability should be very high
        # (both teams most likely to score 0)
        assert result["tie_prob"] > 0.9
        
        # Should still have valid structure
        assert "team_a" in result
        assert "team_b" in result
        assert "tie_prob" in result

    def test_high_scoring_game(self):
        """High run projections should still work correctly."""
        result = calculate_all_odds(5.0, 4.5)
        
        # Probabilities should still be valid
        assert 0 < result["team_a"]["ml"]["prob"] < 1
        assert 0 < result["team_b"]["ml"]["prob"] < 1
        assert 0 < result["tie_prob"] < 1

    def test_moneyline_format_in_results(self):
        """Odds should be properly formatted moneylines."""
        result = calculate_all_odds(2.0, 2.0)
        
        # Equal teams should have roughly even odds (around +/- 100)
        ml_a = result["team_a"]["ml"]["odds"]
        ml_b = result["team_b"]["ml"]["odds"]
        
        # With equal projections, ML should be very close to even
        # Could be +100 or -100 depending on tiny floating point variations
        assert ml_a in ["-100", "+100"]
        assert ml_b in ["-100", "+100"]

    def test_asymmetric_odds_format(self):
        """Asymmetric teams should have opposite sign moneylines."""
        result = calculate_all_odds(3.0, 2.0)
        
        # Favorite should have negative ML
        assert result["team_a"]["ml"]["odds"].startswith("-")
        # Underdog should have positive ML
        assert result["team_b"]["ml"]["odds"].startswith("+")


# ============================================================================
# Integration/Sanity Tests
# ============================================================================

class TestIntegration:
    """Integration tests verifying realistic scenarios."""

    def test_realistic_game_scenario(self):
        """Test a realistic MLB F5 scenario."""
        # Typical MLB F5 is around 2-2.5 runs per team
        result = calculate_all_odds(2.14, 2.25)
        
        # Team B slightly favored
        assert result["team_b"]["ml"]["prob"] > result["team_a"]["ml"]["prob"]
        
        # All probabilities in valid range
        for team in ["team_a", "team_b"]:
            for bet_type in ["plus_0_5", "ml", "minus_0_5"]:
                prob = result[team][bet_type]["prob"]
                assert 0 < prob < 1, f"{team} {bet_type} prob out of range: {prob}"

    def test_lopsided_matchup(self):
        """Test a lopsided matchup (e.g., ace vs. poor pitcher)."""
        result = calculate_all_odds(1.5, 4.0)
        
        # Team B heavily favored
        assert result["team_b"]["ml"]["prob"] > 0.65
        assert result["team_a"]["ml"]["prob"] < 0.35
        
        # Team B -0.5 (must win) should still be likely
        assert result["team_b"]["minus_0_5"]["prob"] > 0.5


def apply_vig(prob: float, vig_pct: float) -> float:
    """Local copy of apply_vig for testing (mirrors fair_f5_streamlit.py)."""
    if vig_pct == 0.0:
        return prob
    return min(prob * (1 + vig_pct / 100), 1.0)


class TestApplyVig:
    def test_zero_vig_is_identity(self):
        """With 0% vig, probability is unchanged."""
        assert apply_vig(0.5, 0.0) == 0.5
        assert apply_vig(0.3, 0.0) == 0.3

    def test_standard_vig_inflates_probability(self):
        """4.76% vig (standard -110/-110) inflates a 50% prob to ~52.38%."""
        result = apply_vig(0.5, 4.76)
        assert abs(result - 0.5238) < 0.001

    def test_clamping_at_extreme_values(self):
        """Very high vig on near-certain prob clamps to 1.0."""
        assert apply_vig(0.95, 20.0) == 1.0

    def test_zero_probability_stays_zero(self):
        """Zero probability stays zero regardless of vig."""
        assert apply_vig(0.0, 10.0) == 0.0

    def test_home_advantage_shifts_odds(self):
        """Boosting home team runs should improve their win probability."""
        baseline = calculate_all_odds(2.0, 2.0)
        boosted = calculate_all_odds(2.0 * 1.1, 2.0)
        assert boosted["team_a"]["ml"]["prob"] > baseline["team_a"]["ml"]["prob"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
