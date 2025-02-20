from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from bs4 import BeautifulSoup
import pandas as pd
import requests

app = FastAPI()

# Fixed URL for currency exchange rates
URL = 'https://www.bon-bast.com/'  # Change this to the real URL

# Defining the User-Agent header to use in the GET request below
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/107.0.0.0 Safari/537.36'
}

# Cached currency data
currency_data = {}

def scrape_currency_data():
    """Scrapes the webpage and stores currency data in memory."""
    global currency_data
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch webpage")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the currency exchange table (Modify this if needed)
    currencies_table = soup.find('table')  
    if not currencies_table:
        raise HTTPException(status_code=404, detail="Currency table not found on the page")

    # Extract data and store it in a dictionary
    temp_data = {}
    for row in currencies_table.find_all('tr'):
        columns = row.find_all('td')
        if columns:
            code = columns[0].text.strip()
            currency = columns[1].text.strip()
            sell = columns[2].text.strip()
            buy = columns[3].text.strip()
            temp_data[code] = {"currency": currency, "sell": sell, "buy": buy}

    currency_data = temp_data  # Update global variable


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event that runs when the app starts and stops."""
    print("Starting FastAPI server... Scraping data...")
    scrape_currency_data()
    yield
    print("Shutting down FastAPI server...")

# Initialize FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/currency/{code}")
def get_currency(code: str):
    """Returns the buy and sell price for a given currency code."""
    code = code.upper()  # Convert to uppercase for consistency
    if code not in currency_data:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    return {
        "code": code,
        "currency": currency_data[code]["currency"],
        "sell": currency_data[code]["sell"],
        "buy": currency_data[code]["buy"]
    }

@app.get("/refresh")
def refresh_data():
    """Manually refresh currency data."""
    scrape_currency_data()
    return {"message": "Currency data updated successfully"}
