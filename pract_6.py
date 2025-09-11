import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# --- Step 1: Define fuzzy inputs & output ---
rsi = ctrl.Antecedent(np.arange(0, 101, 1), 'RSI')
sentiment = ctrl.Antecedent(np.arange(-1, 1.1, 0.1), 'Sentiment')
volatility = ctrl.Antecedent(np.arange(0, 101, 1), 'Volatility')
trend = ctrl.Consequent(np.arange(-1, 1.1, 0.1), 'Trend')

# --- Step 2: Membership functions ---
rsi['low'] = fuzz.trimf(rsi.universe, [0, 0, 50])
rsi['medium'] = fuzz.trimf(rsi.universe, [30, 50, 70])
rsi['high'] = fuzz.trimf(rsi.universe, [50, 100, 100])

sentiment['negative'] = fuzz.trimf(sentiment.universe, [-1, -1, 0])
sentiment['neutral'] = fuzz.trimf(sentiment.universe, [-0.2, 0, 0.2])
sentiment['positive'] = fuzz.trimf(sentiment.universe, [0, 1, 1])

volatility['low'] = fuzz.trimf(volatility.universe, [0, 0, 50])
volatility['medium'] = fuzz.trimf(volatility.universe, [30, 50, 70])
volatility['high'] = fuzz.trimf(volatility.universe, [50, 100, 100])

trend['bearish'] = fuzz.trimf(trend.universe, [-1, -1, 0])
trend['neutral'] = fuzz.trimf(trend.universe, [-0.2, 0, 0.2])
trend['bullish'] = fuzz.trimf(trend.universe, [0, 1, 1])

# --- Step 3: Define rules ---
rules = [
    ctrl.Rule(rsi['low'] & sentiment['negative'], trend['bearish']),
    ctrl.Rule(rsi['high'] & sentiment['positive'] & volatility['low'], trend['bullish']),
    ctrl.Rule(rsi['medium'] & sentiment['neutral'], trend['neutral']),
    ctrl.Rule(sentiment['positive'] & volatility['low'], trend['bullish']),
    ctrl.Rule(sentiment['negative'] & volatility['high'], trend['bearish']),
    ctrl.Rule(volatility['high'] & rsi['low'], trend['bearish']),
    ctrl.Rule(volatility['medium'] & rsi['medium'], trend['neutral'])
]

# --- Step 4: Control system ---
trend_ctrl = ctrl.ControlSystem(rules)
trend_sim = ctrl.ControlSystemSimulation(trend_ctrl)

# --- Step 5: Get user input safely ---
try:
    rsi_val = float(input("Enter RSI value (0–100): "))
    sentiment_val = float(input("Enter Sentiment value (-1 negative to 1 positive): "))
    volatility_val = float(input("Enter Volatility percentage (0–100): "))
except ValueError:
    print("Invalid input! Please enter numeric values.")
    exit()

# Validate input ranges
if not (0 <= rsi_val <= 100):
    print("RSI must be between 0 and 100")
    exit()
if not (-1 <= sentiment_val <= 1):
    print("Sentiment must be between -1 and 1")
    exit()
if not (0 <= volatility_val <= 100):
    print("Volatility must be between 0 and 100")
    exit()

# --- Step 6: Compute fuzzy output ---
trend_sim.input['RSI'] = rsi_val
trend_sim.input['Sentiment'] = sentiment_val
trend_sim.input['Volatility'] = volatility_val
trend_sim.compute()

# --- Step 7: Show result ---
output_value = round(trend_sim.output['Trend'], 2)
print("\nPredicted Market Trend (−1 bearish, 0 neutral, 1 bullish):", output_value)

if output_value < -0.3:
    print("Prediction: Bearish Market : down")
elif output_value > 0.3:
    print("Prediction: Bullish Market :up")
else:
    print("Prediction: Neutral Market")
