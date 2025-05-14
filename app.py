
import streamlit as st
import pandas as pd
import requests

@st.cache_data
def load_ssrp():
    df = pd.read_csv("SSRP.csv", sep=";", header=None)
    countries = df.iloc[1]
    currencies = df.iloc[2]
    prices = df.iloc[3:].reset_index(drop=True)
    prices.columns = countries
    return prices, countries, currencies

def get_live_price(app_id, cc):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc={cc}&l=en"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        price = data[str(app_id)]["data"]["price_overview"]["final"] / 100
        return round(price, 2)
    except:
        return None

st.title("Steam Price Comparator")

app_id = st.text_input("Enter Steam App ID")
partner_share = st.number_input("Partner Share (%)", min_value=1, max_value=100, value=70)

if app_id:
    prices_df, countries, currencies = load_ssrp()
    base_prices = prices_df["us"].astype(float)

    # Получаем фактическую цену в USD
    usd_price = get_live_price(app_id, "us")
    if not usd_price:
        st.error("Can't fetch live USD price from Steam.")
        st.stop()

    closest_row = prices_df.iloc[(base_prices - usd_price).abs().idxmin()]
    df = pd.DataFrame({
        "Country": closest_row.index,
        "Currency": [currencies[i].strip().upper() for i in range(len(closest_row))],
        "Recommended SRP": closest_row.values
    })

    df["Live Price"] = df["Country"].apply(lambda cc: get_live_price(app_id, cc.lower()))
    df["Δ %"] = ((df["Live Price"] - df["Recommended SRP"]) / df["Recommended SRP"] * 100).round(2)

    st.dataframe(df)
