import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
    """Scrape HDFC forex rates"""
    try:
        url = "https://www.hdfcbank.com/personal/resources/learning-centre/forex/treasury-forex-card-rates"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML table
        tables = pd.read_html(response.text)
        
        if tables:
            df = tables[0]
            print(f"✅ Scraped {len(df)} currency pairs")
            return df
        else:
            print("❌ No tables found")
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
    for index, row in rates_df.iterrows():
        try:
            # Adjust column names based on actual table structure
            currency_pair = row.get('Currency Pair', None)
            tt_buying = row.get('T.T Buying(Inw Rem)', None)
            tt_selling = row.get('T.T Selling(O / w Rem)', None)
            
            if currency_pair:
                cursor.execute('''
                    INSERT OR REPLACE INTO forex_rates 
                    (date, currency_pair, tt_buying, tt_selling, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (today, currency_pair, tt_buying, tt_selling, timestamp))
                count += 1
        except Exception as e:
            print(f"⚠️ Error inserting row {index}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Stored {count} rates for {today}")
    return True

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
