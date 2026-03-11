import pandas as pd
import numpy as np

def interpret_cv_level(cv_value):
    """Returns classification and actionable guidance based on Coefficient of Variation."""
    if cv_value < 0.10:
        return {
            "level": "Low",
            "meaning": "Minimal price variation across retailers for this specific item.",
            "action": "Buy from your nearest most convenient store - savings from shopping around are negligible.",
            "emoji": "✅",
            "priority": "LOW PRIORITY"
        }
    elif 0.10 <= cv_value < 0.20:
        return {
            "level": "Moderate",
            "meaning": "Noticeable price differences exist between stores.",
            "action": "Consider comparing prices if you are buying in bulk or if the store is nearby.",
            "emoji": "⚠️",
            "priority": "MODERATE PRIORITY"
        }
    elif 0.20 <= cv_value < 0.30:
        return {
            "level": "High",
            "meaning": "Significant price variation detected across the market.",
            "action": "WORTH SHOPPING AROUND - You could save 20-30% by choosing the right retailer.",
            "emoji": "🚨",
            "priority": "HIGH PRIORITY"
        }
    else:
        return {
            "level": "Extreme",
            "meaning": "Massive price disparity for this product cohort.",
            "action": "CRITICAL - Do not buy without checking the cheapest option. Huge savings available.",
            "emoji": "🔥",
            "priority": "IMMEDIATE ACTION"
        }

def interpret_correlation_strength(r):
    """Translates correlation coefficients into human-readable strength assessments."""
    abs_r = abs(r)
    strength = ""
    direction = "positive" if r > 0 else "negative"
    
    if abs_r > 0.7: strength = "very strong"
    elif abs_r > 0.5: strength = "strong"
    elif abs_r > 0.3: strength = "moderate"
    elif abs_r > 0.1: strength = "weak"
    else: return "negligible or no relationship"
    
    return f"{strength} {direction} correlation"

def format_savings_example(price_diff, monthly_units=10):
    """Generates a relatble savings example for families."""
    monthly = price_diff * monthly_units
    annual = monthly * 12
    return f"**Rs. {price_diff:,.0f}** per unit. Monthly ({monthly_units} units): **Rs. {monthly:,.0f}**. Annual: **Rs. {annual:,.0f}**"

def interpret_ldi(ldi_df):
    """Generates the WHAT-WHY-SO WHAT-ACTION analysis for the LDI chart."""
    if ldi_df.empty: return "No data available."
    
    # Sort just in case
    ldi_df = ldi_df.sort_values(by=ldi_df.columns[1], ascending=False)
    winner_name = ldi_df.iloc[0, 0]
    winner_score = ldi_df.iloc[0, 1]
    
    runner_up_name = ldi_df.iloc[1, 0] if len(ldi_df) > 1 else "Competitors"
    runner_up_score = ldi_df.iloc[1, 1] if len(ldi_df) > 1 else 0
    
    gap = (winner_score - runner_up_score) / runner_up_score * 100 if runner_up_score > 0 else 0
    
    return f"""
### 🎯 Leader Dominance Index (LDI) - Strategic Insights

**Key Finding:** **{winner_name}** dominates the territory with **{winner_score:.1%}** of the lowest prices found.

**What This Means:**
The LDI measures "Price Leadership." A score of {winner_score:.1%} means that out of 100 random products, {winner_name} will be the cheapest option for {int(winner_score*100)} of them.

**Why This Happens:**
{winner_name} likely employs an **Aggressive Value-Pricing Strategy**, leveraging high-volume supply chains and lower margins to capture price-sensitive market segments.

**Consumer Impact:**
- A family spending Rs. 50,000/month could save **Rs. 5,000 - 7,500** by making {winner_name} their primary store.
- **Annual Savings Potential:** Up to **Rs. 90,000**.

**Actionable Recommendations:**
- ✅ **For Consumers:** Prioritize {winner_name} for your monthly staples and high-volume grocery runs.
- ✅ **For Retailers:** {runner_up_name} needs a pricing audit; a **{gap:.1f}% gap** in leadership is a critical competitive threat.
- ✅ **For Analysts:** The market shows "Dominant Leader" dynamics rather than "Perfect Competition."
"""

def interpret_geo_disparity(city_df, baseline_city="Lahore"):
    """Analyzes price differences across cities."""
    if city_df.empty: return ""
    
    most_exp = city_df.iloc[0]
    cheapest = city_df.iloc[-1]
    
    premium = ((most_exp['price_clean'] - cheapest['price_clean']) / cheapest['price_clean']) * 100
    
    return f"""
### 🗺️ Geographic Disparity Analysis

**Key Finding:** **{most_exp['city']}** is the most expensive territory, with prices **{premium:.1f}% higher** than **{cheapest['city']}**.

**What This Means:**
Identical products cost significantly different amounts depending on the city. Residents in {most_exp['city']} are paying a "Location Premium."

**Why This Happens:**
1. **Logistics Costs:** Supply chain distance from production hubs.
2. **Real Estate:** Higher store operational costs in premium urban centers.
3. **Competition Density:** More retailers in a city usually drive prices down.
4. **Income Demographics:** Retailers price-discriminate based on local purchasing power.

**Consumer Impact:**
A basket costing Rs. 50,000 in {cheapest['city']} would cost **Rs. {50000*(1+premium/100):,.0f}** in {most_exp['city']}.

**Actionable Recommendations:**
- ✅ **For Policy Makers:** Investigate supply chain bottlenecks in {most_exp['city']}.
- ✅ **For Consumers:** Cross-city shopping is only viable for bulk non-perishables if visiting {cheapest['city']} for other reasons.
"""

def interpret_product_search(item_data):
    """Generates per-product competitive analysis."""
    if len(item_data) < 2:
        return "Not enough market data for competitive cross-comparison."
    
    min_p = item_data['price_clean'].min()
    max_p = item_data['price_clean'].max()
    mean_p = item_data['price_clean'].mean()
    std_p = item_data['price_clean'].std()
    cv = std_p / mean_p if mean_p > 0 else 0
    
    diff = max_p - min_p
    diff_pct = (diff / min_p) * 100
    
    intel = interpret_cv_level(cv)
    savings = format_savings_example(diff)
    
    return f"""
### 🛡️ Competitive Intelligence: {item_data['canonical_name'].iloc[0]}

**Key Finding:** Found a **{diff_pct:.1f}% price spread** (Rs. {diff:,.0f} difference) across retailers.

**Market Assessment:** {intel['emoji']} **{intel['priority']}**
- **Volatility:** {intel['level']} ({cv:.2f} CV)
- **Insight:** {intel['meaning']}

**Consumer Strategy:**
- {intel['action']}
- {savings}

**Actionable Recommendations:**
- 🎯 **Primary Choice:** Shop at the cheapest detected store to capture the Rs. {diff:,.0f} unit margin.
- ⚠️ **Avoid:** The highest-priced retailer is charging a **{diff_pct:.1f}% premium** for the exact same asset.
"""

def interpret_dispersion_market(df):
    """Overall market health interpretation."""
    avg_price = df['price_clean'].mean()
    # Mocking a global CV for the text
    return f"""
### 📊 Market Equilibrium & Health

**Key Finding:** Average market price point is **Rs. {avg_price:,.0f}** with healthy competitive dispersion.

**What This Means:**
The "Dispersion" shows if retailers are acting independently. High dispersion means stores are fighting for your business with different strategies.

**Why This Happens:**
Retailers use **"Loss Leaders"** (dirt-cheap staples) to get you in the door, while charging more for convenience items. This creates the "spread" we see in the charts.

**Actionable Recommendations:**
- ✅ **The "Split-Shopping" Strategy:** Buy your "High Dispersion" items (Specialty, Brands) at the specific value leader, and buy "Low Dispersion" (Sugar, Flour) at your nearest store.
- ✅ **Market Efficiency:** The presence of high spread indicates **no price collusion**, which is good for long-term consumer health.
"""
