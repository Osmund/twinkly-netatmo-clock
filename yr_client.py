"""
Yr API Client for værdata
Bruker Locationforecast API fra Yr/MET Norway
"""
import requests
from datetime import datetime


class YrClient:
    """Klient for å hente værdata fra Yr"""
    
    def __init__(self, lat=58.0, lon=6.5):
        """
        Args:
            lat: Breddegrad (default: Sokndal ~58.0)
            lon: Lengdegrad (default: Sokndal ~6.5)
        """
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
        self.headers = {
            'User-Agent': 'TwinklyDisplay/1.0 (private home display)'
        }
    
    def get_current_temperature(self):
        """
        Hent nåværende utetemperatur fra Yr
        
        Returns:
            float: Temperatur i celsius, eller None ved feil
        """
        try:
            params = {
                'lat': self.lat,
                'lon': self.lon
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Hent første timeserie (nå)
                timeseries = data.get('properties', {}).get('timeseries', [])
                if timeseries:
                    current = timeseries[0]
                    temp = current.get('data', {}).get('instant', {}).get('details', {}).get('air_temperature')
                    return temp
            else:
                print(f"Yr API feil: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Feil ved henting av Yr data: {e}")
            return None
    
    def get_weather_symbol(self):
        """
        Hent værsymbol (for fremtidig bruk)
        
        Returns:
            str: Værsymbol kode eller None
        """
        try:
            params = {
                'lat': self.lat,
                'lon': self.lon
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                timeseries = data.get('properties', {}).get('timeseries', [])
                if timeseries:
                    current = timeseries[0]
                    symbol = current.get('data', {}).get('next_1_hours', {}).get('summary', {}).get('symbol_code')
                    return symbol
            
            return None
                
        except Exception as e:
            print(f"Feil ved henting av værsymbol: {e}")
            return None


if __name__ == "__main__":
    # Test
    print("Tester Yr API...")
    yr = YrClient(lat=58.0, lon=6.5)  # Sokndal
    temp = yr.get_current_temperature()
    symbol = yr.get_weather_symbol()
    
    if temp is not None:
        print(f"✓ Utetemperatur Sokndal: {temp}°C")
    else:
        print("✗ Kunne ikke hente temperatur")
    
    if symbol:
        print(f"✓ Værsymbol: {symbol}")
