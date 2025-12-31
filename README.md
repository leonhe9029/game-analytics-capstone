# Game Analytics Capstone: Character Balance & Meta Analysis

## Overview
This project analyzes competitive game telemetry to evaluate character balance, meta stability, and the impact of balance changes over time. Using SQL, Python, and data visualization, the project simulates how professional game analytics teams assess balance risks, validate patch effectiveness, and model potential tuning decisions.

The analysis focuses on identifying overpowered and underpowered characters, understanding rank-dependent performance, and simulating balance changes to improve overall fairness without destabilizing gameplay.

---

## Key Questions
- Are characters balanced consistently across different skill tiers?
- Do balance patches meaningfully change character performance?
- Can small, targeted tuning adjustments improve overall meta stability?

---

## Data Pipeline
1. **ETL Process**
   - Raw synthetic match telemetry is cleaned and transformed
   - Data is stored in a SQLite database for reproducible analysis
   - Tables include matches, players, sessions, and patches

2. **Technologies Used**
   - Python (pandas, matplotlib, sqlite3)
   - SQL (aggregation, filtering, joins)
   - Jupyter Notebook for exploratory analysis

---

## Analysis Breakdown

### 1. Rank-Specific Balance Analysis
Character win rates were analyzed across skill tiers (Bronze, Silver, Gold, Platinum). Low-sample tiers were excluded to ensure statistical reliability.

**Insight:**  
Most characters perform consistently across ranks, but a subset shows strong skill-dependence. Some characters scale significantly better at higher ranks, suggesting high mechanical ceilings, while others dominate lower ranks due to simpler mechanics.

---

### 2. Patch Impact Evaluation
Character win rates were compared across game patches to measure balance changes over time.

**Insight:**  
Most characters remain close to equilibrium across patches, indicating conservative tuning. However, several characters experienced targeted performance shifts, validating that balance updates successfully moderated outliers without disrupting the meta.

---

### 3. Balance Simulation (What-If Modeling)
A hypothetical tuning pass was simulated:
- Overperforming characters were nerfed by 3%
- Underperforming characters were buffed by 3%

The impact was measured by deviation from a 50% win rate.

**Insight:**  
Simulated adjustments reduced overall win-rate variance and tightened clustering around equilibrium, demonstrating that small, targeted changes can meaningfully improve balance while preserving stability.

---

## Key Takeaways
- Balance issues are often skill-dependent rather than globally dominant
- Patch effectiveness should be measured quantitatively, not anecdotally
- Simulation-based analysis enables safer, data-driven tuning decisions

---

## How to Run
```bash
pip install -r requirements.txt
python -m src.etl
jupyter notebook
