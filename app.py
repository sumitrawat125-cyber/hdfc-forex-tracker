import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="HDFC Forex Rate Tracker", page_icon="💱", layout="wide")

st.title("💱 HDFC Bank Forex Rate Tracker")
st.markdown("**TT Selling Rates** for foreign currencies to INR")

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
        
        # Create tabs
        tab1, tab2 = st.tabs(["💱 Currency Converter", "📊 All Rates"])
        
        # TAB 1: Currency Converter
        with tab1:
            st.subheader("Quick Currency Converter")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Select currency pair
                currency_list = df['Currency Pair'].tolist()
                selected_pair = st.selectbox(
                    "🔍 Select Currency Pair",
                    options=currency_list,
                    help="Type to search (e.g., USD, EUR, GBP)"
                )
                
                # Get rates for selected pair
                selected_row = df[df['Currency Pair'] == selected_pair].iloc[0]
                tt_buying = selected_row['TT Buying (INR)']
                tt_selling = selected_row['TT Selling (INR)']
                
                # Display selected rates
                st.info(f"**{selected_pair}**")
                rate_col1, rate_col2 = st.columns(2)
                rate_col1.metric("TT Buying", f"₹{tt_buying:,.4f}")
                rate_col2.metric("TT Selling", f"₹{tt_selling:,.4f}")
            
            with col2:
                # Amount input
                foreign_amount = st.number_input(
                    f"💵 Enter Amount in {selected_pair.split('-')[0]}",
                    min_value=0.0,
                    value=1000.0,
                    step=100.0,
                    format="%.2f"
                )
                
                # Calculate conversions
                if foreign_amount > 0:
                    inr_buying = foreign_amount * tt_buying
                    inr_selling = foreign_amount * tt_selling
                    
                    st.success("**Conversion Results:**")
                    
                    st.markdown(f"""
                    **Foreign Amount:** {foreign_amount:,.2f} {selected_pair.split('-')[0]}
                    
                    ---
                    
                    **Using TT Buying Rate:**  
                    ₹ **{inr_buying:,.2f}** INR
                    
                    **Using TT Selling Rate:**  
                    ₹ **{inr_selling:,.2f}** INR
                    
                    ---
                    
                    💡 *Use TT Selling rate for payments/purchases*
                    """)
        
        # TAB 2: All Rates Table
        with tab2:
            st.subheader(f"📊 All Forex Rates for {selected_date.strftime('%d %B %Y')}")
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "TT Buying (INR)": st.column_config.NumberColumn(format="₹%.4f"),
                    "TT Selling (INR)": st.column_config.NumberColumn(format="₹%.4f")
                }
            )
            
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

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.info("""
    **HDFC Forex Rate Tracker**
    
    🔄 Auto-updated daily at 9:30 AM IST
    
    **Features:**
    - Quick currency converter
    - Historical rate lookup
    - CSV export for accounting
    
    **Perfect for:**
    - Freight forwarding invoices
    - GST reconciliation
    - International payments
    """)
    
    st.markdown("---")
    st.caption(f"Last updated: {date_str}")
