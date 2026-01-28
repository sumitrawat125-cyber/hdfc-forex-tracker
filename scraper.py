import sqlite3
import pandas as pd
import requests
import tabula
from datetime import datetime
import io

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('forex_rates.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forex_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            currency_pair TEXT NOT NULL,
            tt_buying REAL,
            tt_selling REAL,
            timestamp TEXT,
            UNIQUE(date, currency_pair)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def scrape_hdfc_rates():
    """Scrape HDFC GIFT City forex rates from PDF"""
    try:
        # Correct PDF URL
        url = "https://www.hdfcgiftcity.bank.in/content/dam/hdfc-bank-offshore-sites/gc/en/home-page/pdfs/forex-card-rates.pdf"
        
        print(f"📥 Downloading PDF from: {url}")
        
        # Read PDF tables using tabula
        tables = tabula.read_pdf(url, pages='all', multiple_tables=True)
        
        if not tables:
            print("❌ No tables found in PDF")
            return None
        
        # Find the main rates table (usually the first large table)
        for table in tables:
            if len(table.columns) >= 3 and len(table) > 10:
                df = table
                print(f"✅ Found table with {len(df)} rows")
                return df
        
        print("❌ Could not find rates table")
        return None
            
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return None

def store_rates(rates_df):
    """Store rates in SQLite database"""
    if rates_df is None or rates_df.empty:
        print("❌ No data to store")
        return False
    
    conn = sqlite3.connect('forex_rates.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    count = 0
    
    # Try to identify column names (they vary in PDF structure)
    for index, row in rates_df.iterrows():
        try:
            # Extract currency pair and rates
            # Adjust these column indices based on actual PDF structure
            if len(row) >= 3:
                currency_pair = str(row.iloc[0]).strip()
                
                # Skip header rows
                if 'Currency' in currency_pair or 'Pair' in currency_pair:
                    continue
                
                # Try to extract buying and selling rates
                tt_buying = None
                tt_selling = None
                
                try:
                    tt_buying = float(row.iloc[1])
                    tt_selling = float(row.iloc[2])
                except:
                    continue
                
                if currency_pair and tt_buying and tt_selling:
                    cursor.execute('''
                        INSERT OR REPLACE INTO forex_rates 
                        (date, currency_pair, tt_buying, tt_selling, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (today, currency_pair, tt_buying, tt_selling, timestamp))
                    count += 1
        except Exception as e:
            continue
    
    conn.commit()
    conn.close()
    
    print(f"✅ Stored {count} rates for {today}")
    return count > 0

def main():
    """Main execution function"""
    print("🚀 Starting forex rate scraper...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize database
    init_database()
    
    # Scrape rates
    rates_df = scrape_hdfc_rates()
    
    # Store in database
    if rates_df is not None:
        success = store_rates(rates_df)
        if success:
            print("✅ Scraping completed successfully!")
            return 0
    
    print("❌ Scraping failed")
    return 1

if __name__ == "__main__":
    exit(main())
