"""
Strømpris API Client
Bruker Hvakosterstrommen.no API for norske strømpriser
"""
import requests
from datetime import datetime, timezone


class ElectricityClient:
    """Klient for å hente strømpriser"""
    
    def __init__(self, region='NO2'):
        """
        Args:
            region: Prisområde (NO1-NO5)
                   NO2 = Sør-Norge (Kristiansand)
        """
        self.region = region
        self.base_url = "https://www.hvakosterstrommen.no/api/v1/prices"
    
    def get_current_price(self):
        """
        Hent nåværende strømpris (øre/kWh inkl mva)
        
        Returns:
            float: Pris i øre/kWh, eller None ved feil
        """
        try:
            # Format: YYYY/MM-DD
            now = datetime.now(timezone.utc)
            date_str = now.strftime('%Y/%m-%d')
            url = f"{self.base_url}/{date_str}_{self.region}.json"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current_hour = now.hour
                
                # Finn pris for nåværende time
                for entry in data:
                    time_start = datetime.fromisoformat(entry['time_start'])
                    if time_start.hour == current_hour:
                        # NOK_per_kWh er inkludert mva
                        price = entry['NOK_per_kWh'] * 100  # Konverter til øre
                        return round(price, 2)
                
                return None
            else:
                print(f"Strømpris API feil: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Feil ved henting av strømpris: {e}")
            return None
    
    def get_todays_prices(self):
        """
        Hent alle dagens priser
        
        Returns:
            list: Liste med priser per time, eller None ved feil
        """
        try:
            now = datetime.now(timezone.utc)
            date_str = now.strftime('%Y/%m-%d')
            url = f"{self.base_url}/{date_str}_{self.region}.json"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices = []
                for entry in data:
                    prices.append({
                        'hour': datetime.fromisoformat(entry['time_start']).hour,
                        'price': round(entry['NOK_per_kWh'] * 100, 2)  # øre/kWh
                    })
                return prices
            
            return None
                
        except Exception as e:
            print(f"Feil ved henting av dagens priser: {e}")
            return None


if __name__ == "__main__":
    # Test
    print("Tester Strømpris API...")
    client = ElectricityClient(region='NO2')
    price = client.get_current_price()
    
    if price is not None:
        print(f"✓ Strømpris NO2 nå: {price} øre/kWh")
    else:
        print("✗ Kunne ikke hente strømpris")
    
    prices = client.get_todays_prices()
    if prices:
        print(f"✓ Hentet {len(prices)} timepriser")
        avg = sum(p['price'] for p in prices) / len(prices)
        print(f"  Gjennomsnitt i dag: {avg:.2f} øre/kWh")
