import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

def get_rates_by_date(selected_date):
    """Fetch rates from database"""
    if not os.path.exists('forex_rates.db'):
        return pd.DataFrame()
    
    conn = sqlite3.connect('forex_rates.db', check_same_thread=False)
    query = '''
        SELECT currency_pair, tt_buying, tt_selling, timestamp
        FROM forex_rates
        WHERE date = ?
        ORDER BY currency_pair
    '''
    df = pd.read_sql_query(query, conn, params=(selected_date,))
    conn.close()
    return df

def get_available_dates():
    """Get all dates that have data"""
    if not os.path.exists('forex_rates.db'):
        return []
    
    conn = sqlite3.connect('forex_rates.db', check_same_thread=False)
    query = 'SELECT DISTINCT date FROM forex_rates ORDER BY date DESC'
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['date'].tolist()

def main():
    st.set_page_config(
        page_title="HDFC Forex Rate Tracker", 
        page_icon="💱", 
        layout="wide"
    )
    
    # Header
    st.title("💱 HDFC Bank Forex Rate Tracker")
    st.markdown("**TT Selling Rates** for foreign currencies to INR")
    
    # Sidebar info
    with st.sidebar:
        st.header("ℹ️ About")
        st.info("""
        This tool displays historical HDFC Bank forex rates.
        
        🔄 **Auto-updated daily** at 9:30 AM IST via GitHub Actions
        
        📊 Data includes TT Buying and TT Selling rates
        """)
        
        # Show available dates
        available_dates = get_available_dates()
        if available_dates:
            st.success(f"📅 **{len(available_dates)} days** of data available")
            st.caption(f"Latest: {available_dates[0]}")
            st.caption(f"Oldest: {available_dates[-1]}")
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📅 Select Date")
        selected_date = st.date_input(
            "Choose a date",
            value=date.today(),
            max_value=date.today()
        )
    
    # Convert date to string
    date_str = selected_date.strftime('%Y-%m-%d')
    
    # Fetch and display rates
    st.subheader(f"📊 Forex Rates for {selected_date.strftime('%d %B %Y')}")
    
    rates_df = get_rates_by_date(date_str)
    
    if not rates_df.empty:
        # Rename columns
        rates_df.columns = ['Currency Pair', 'TT Buying (INR)', 'TT Selling (INR)', 'Last Updated']
        
        # Display table
        st.dataframe(
            rates_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "TT Buying (INR)": st.column_config.NumberColumn(
                    format="₹%.4f"
                ),
                "TT Selling (INR)": st.column_config.NumberColumn(
                    format="₹%.4f"
                )
            }
        )
        
        # Download button
        csv = rates_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"hdfc_forex_{date_str}.csv",
            mime="text/csv"
        )
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📌 Total Pairs", len(rates_df))
        with col2:
            st.metric("📅 Data Date", date_str)
        with col3:
            highest = rates_df['TT Selling (INR)'].max()
            st.metric("📈 Highest Rate", f"₹{highest:.2f}")
            
    else:
        st.warning(f"⚠️ No data available for {date_str}")
        st.info("💡 Data is automatically fetched d
