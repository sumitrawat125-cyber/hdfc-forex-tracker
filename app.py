import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="HDFC Forex Rate Tracker", page_icon="💱", layout="wide")

st.title("💱 HDFC Bank Forex Rate Tracker")
st.markdown("**TT Selling Rates** for foreign currencies to INR")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.info("This tool displays historical HDFC Bank forex rates. Auto-updated daily at 9:30 AM IST via GitHub Actions.")

# Check if database exists
if not os.path.exists('forex_rates.db'):
    st.error("⚠️ Database file not found!")
    st.info("💡 The database will be created when GitHub Actions runs at 9:30 AM IST daily.")
    st.stop()

# Date picker
selected_date = st.date_input("📅 Select Date", value=date.today(), max_value=date.today())
date_str = selected_date.strftime('%Y-%m-%d')

# Fetch rates
try:
    conn = sqlite3.connect('forex_rates.db', check_same_thread=False)
    query = '''
        SELECT currency_pair, tt_buying, tt_selling, timestamp
        FROM forex_rates
        WHERE date = ?
        ORDER BY currency_pair
    '''
    df = pd.read_sql_query(query, conn, params=(date_str,))
    conn.close()
    
    if not df.empty:
        df.columns = ['Currency Pair', 'TT Buying (INR)', 'TT Selling (INR)', 'Last Updated']
        
        st.subheader(f"📊 Forex Rates for {selected_date.strftime('%d %B %Y')}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"hdfc_forex_{date_str}.csv",
            mime="text/csv"
        )
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Total Pairs", len(df))
        col2.metric("📅 Data Date", date_str)
        col3.metric("📈 Highest Rate", f"₹{df['TT Selling (INR)'].max():.2f}")
        
    else:
        st.warning(f"⚠️ No data available for {date_str}")
        st.info("💡 Data is automatically fetched daily at 9:30 AM IST")
        
except Exception as e:
    st.error(f"❌ Error: {e}")
