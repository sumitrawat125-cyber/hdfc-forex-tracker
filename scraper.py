import sqlite3
import pandas as pd
import requests
import tabula
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
    """Scrape HDFC GIFT City forex rates from PDF"""
    try:
        url = "https://www.hdfcgiftcity.bank.in/content/dam/hdfc-bank-offshore-sites/gc/en/home-page/pdfs/forex-card-rates.pdf"
        
        print(f"📥 Downloading PDF from: {url}")
        
        # Read PDF tables
        tables = tabula.read_pdf(url, pages='all', multiple_tables=False, lattice=True)
        
        if not tables:
            print("❌ No tables found in PDF")
            return None
        
        # Get the main table
        df = tables[0]
        print(f"✅ Found table with {len(df)} rows and {len(df.columns)} columns")
        
        # The PDF has 3 sets of currency pairs in columns:
        # Columns 0-2: First set
        # Columns 3-5: Second set  
        # Columns 6-8: Third set (THIS IS WHAT YOU WANT - has INR pairs!)
        
        all_rates = []
        
        # Extract from columns 6, 7, 8 (7th, 8th, 9th columns - INR pairs)
        if len(df.columns) >= 9:
            for index, row in df.iterrows():
                try:
                    # Column 6 = Currency Pair, Column 7 = TT Buying, Column 8 = TT Selling
                    currency_pair = str(row.iloc[6]).strip()
                    
                    # Skip headers and invalid rows
                    if 'Currency' in currency_pair or 'Pair' in currency_pair or currency_pair == 'nan':
                        continue
                    
                    try:
                        tt_buying = float(row.iloc[7])
                        tt_selling = float(row.iloc[8])
                        
                        if currency_pair and tt_buying > 0 and tt_selling > 0:
                            all_rates.append({
                                'currency_pair': currency_pair,
                                'tt_buying': tt_buying,
                                'tt_selling': tt_selling
                            })
                    except:
                        continue
                except:
                    continue
        
        if all_rates:
            result_df = pd.DataFrame(all_rates)
            print(f"✅ Extracted {len(result_df)} currency pairs from columns 7-9")
            return result_df
        else:
            print("❌ No valid rates found")
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
            cursor.execute('''
                INSERT OR REPLACE INTO forex_rates 
                (date, currency_pair, tt_buying, tt_selling, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (today, row['currency_pair'], row['tt_buying'], row['tt_selling'], timestamp))
            count += 1
        except Exception as e:
            print(f"⚠️ Error storing {row['currency_pair']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Stored {count} rates for {today}")
    return count > 0

def main():
    """Main execution function"""
    print("🚀 Starting forex rate scraper...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    init_database()
    rates_df = scrape_hdfc_rates()
    
    if rates_df is not None:
        success = store_rates(rates_df)
        if success:
            print("✅ Scraping completed successfully!")
            return 0
    
    print("❌ Scraping failed")
    return 1

if __name__ == "__main__":
    exit(main())
