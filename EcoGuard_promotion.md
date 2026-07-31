# EcoGuard: Lightweight Rust+Tauri App for Real-Time Carbon Footprint Reduction

We just launched **EcoGuard**, a lightweight desktop app built with Rust + Tauri that pulls real-time air quality, weather, and grid carbon intensity data.

## Real Data Snapshot (Tokyo)
- Air Quality: {"time": "2026-07-14T17:00", "interval": 3600, "european_aqi": 66, "pm2_5": 27.5, "pm10": 29.3}
- Weather: {"time": "2026-07-14T17:30", "interval": 900, "temperature_2m": 29.8, "relative_humidity_2m": 67, "wind_speed_10m": 5.8}
- Grid Carbon Intensity: {"from": "2026-07-14T08:00Z", "to": "2026-07-14T08:30Z", "intensity": {"forecast": 96, "actual": 76, "index": "low"}}

## AI-Generated Daily Summary
**Daily Environmental Summary (Tokyo, 2026-07-14 ~17:00 JST)**
- **Weather:** Warm and humid summer conditions at **29.8°C** with **67% relative humidity** and light winds (5.8 km/h).
- **Air Quality:** Moderate-to-poor (European AQI **66**), with PM2.5 particulate levels at **27.5 µg/m³**—elevated enough to be cautious with prolonged outdoor exertion.
- **Grid Status:** The local electricity grid is currently running clean with a **low carbon intensity** (actual **76 gCO2/kWh**, indexed as "low"), making this a favorable window for energy use.

**3 Actionable Tips to Reduce Your Carbon Footprint**
1. **Shift Energy Use to Low-Carbon Windows:** Take advantage of the current low grid carbon intensity (index: low) by running energy-intensive appliances—such as laundry, dishwashers, or EV charging—now rather than during peak, higher-emission periods later in the day.
2. **Cool Smartly:** With temperatures near 30°C and high humidity, avoid over-reliance on high-power air conditioning. Use fans, cross-ventilation, or set your AC to an efficient 27–28°C to cut electricity demand and associated emissions.
3. **Choose Low-Emission Transport:** Given the elevated PM2.5 levels, swap short car trips for public transit, walking, or cycling. This reduces both your personal greenhouse gas output and local air pollutants.

## Subscription Tiers (via Stripe)
- **Light**: Free – basic monitoring.
- **Standard**: ¥5,000/month – detailed analytics, push alerts, personalized recommendations.
- **Enterprise**: ¥30,000/month – full data export, API access, priority support.

We also integrated Ko-fi for optional donations and TOAI_Mail for confirmations.

## Get Involved
Read the code, star the repo, and subscribe! Your support powers further development.

### Support Us
If you find this useful, consider a donation or subscription:
- Ko-fi: https://ko-fi.com/phenox_noc2
- Stripe subscriptions available in-app.

*Every ¥5,000 subscription funds ~10 hours of open-source Rust development.*
