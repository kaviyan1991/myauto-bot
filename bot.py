import requests

TELEGRAM_TOKEN = "8978392233:AAE6P-AcGfMfHPqq3EpIiM6Hi7y6DG5Cp2c"
CHANNEL_ID = "@GeorgIranRadar"
API_URL = "https://api2.myauto.ge/en/products"

def scrape_myauto_direct():
    print("Checking MyAuto...")
    params = {
        "TypeID": "0", "ForRent": "0", "CurrencyID": "3", "Page": "1",
        "PriceFrom": "6000", "PriceTo": "35000", "YearFrom": "2017", "YearTo": "2026",
        "LocID": "2", "HasVin": "1", "HideNegotiable": "1", "FuelTypeID": "1,3,6"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.myauto.ge",
        "Referer": "https://www.myauto.ge/"
    }
    fuel_types = {"1": "بنزینی", "3": "هیبرید", "6": "پلاگین هیبرید"}
    gear_types = {"1": "دستی", "2": "اتوماتیک", "3": "تیپترونیک"}
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            items = data.get("data", {}).get("items", [])
            for item in items[:15]:
                try:
                    car_id = item.get("car_id")
                    if not car_id: continue
                    vin_code = str(item.get("vin", "")).strip()
                    prod_year = item.get("prod_year", "")
                    if prod_year:
                        try:
                            if int(prod_year) < 2017 or int(prod_year) > 2026: continue
                        except: continue
                    title = f"{item.get('man_name', 'Vehicle')} {item.get('model_name', '')} ({prod_year})".strip()
                    price_usd = item.get("price_usd", "Check Site")
                    price = f"${price_usd}" if str(price_usd).isdigit() else "Check Site"
                    link = f"https://www.myauto.ge/en/pr/{car_id}"
                    details = {
                        "vin": vin_code if vin_code else "نامشخص",
                        "car_run": f"{item.get('car_run', 0):,}",
                        "engine": f"{item.get('engine_volume', 0) / 1000:.1f}",
                        "fuel": fuel_types.get(str(item.get("fuel_type_id")), "بنزینی"),
                        "gear": gear_types.get(str(item.get("gear_type_id")), "اتوماتیک")
                    }
                    send_to_telegram(title, price, link, details)
                except: continue
    except Exception as e:
        print(f"Error: {e}")

def send_to_telegram(title, price, link, details):
    caption = (
        f"🚗 **آگهی جدید پیدا شد!**\n\n"
        f"📌 **نام خودرو:** {title}\n"
        f"💰 **قیمت:** {price}\n"
        f"⚙️ **گیربکس:** {details['gear']}\n"
        f"⛽ **نوع سوخت:** {details['fuel']}\n"
        f"📊 **کارکرد:** {details['car_run']} km\n"
        f"🧪 **حجم موتور:** {details['engine']} L\n"
        f"🔑 **کد شاسی (VIN):** `{details['vin']}`\n\n"
        f"🔗 [مشاهده تصاویر و اطلاعات تکمیلی در سایت]({link})"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": caption, "parse_mode": "Markdown", "link_preview_options": {"is_disabled": True}}
    try: requests.post(url, json=payload, timeout=15)
    except: pass

if __name__ == "__main__":
    scrape_myauto_direct()
