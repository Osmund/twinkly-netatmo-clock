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
    
    def get_weather_data(self):
        """
        Hent komplett værdata
        
        Returns:
            dict: Værdata med temperatur, symbol, nedbør, vind, etc. eller None
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
                    current = timeseries[0]['data']
                    instant = current.get('instant', {}).get('details', {})
                    next_hour = current.get('next_1_hours', {})
                    
                    weather_data = {
                        'temperature': instant.get('air_temperature'),
                        'humidity': instant.get('relative_humidity'),
                        'wind_speed': instant.get('wind_speed'),
                        'wind_direction': instant.get('wind_from_direction'),
                        'symbol': next_hour.get('summary', {}).get('symbol_code'),
                        'precipitation': next_hour.get('details', {}).get('precipitation_amount', 0)
                    }
                    return weather_data
            
            return None
                
        except Exception as e:
            print(f"Feil ved henting av værdata: {e}")
            return None
    
    def is_rainy(self):
        """Sjekk om det regner"""
        symbol = self.get_weather_symbol()
        if symbol:
            return 'rain' in symbol or 'drizzle' in symbol
        return False
    
    def is_snowy(self):
        """Sjekk om det snør"""
        symbol = self.get_weather_symbol()
        if symbol:
            return 'snow' in symbol or 'sleet' in symbol
        return False
    
    def is_sunny(self):
        """Sjekk om det er sol"""
        symbol = self.get_weather_symbol()
        if symbol:
            return 'clearsky' in symbol or 'fair' in symbol
        return False
    
    def is_cloudy(self):
        """Sjekk om det er overskyet"""
        symbol = self.get_weather_symbol()
        if symbol:
            return 'cloudy' in symbol or 'partlycloudy' in symbol
        return False
    
    def has_thunder(self):
        """Sjekk om det er torden"""
        symbol = self.get_weather_symbol()
        if symbol:
            return 'thunder' in symbol
        return False
    
    def is_foggy(self):
        """Sjekk om det er tåke"""
        symbol = self.get_weather_symbol()
        if symbol:
            return 'fog' in symbol
        return False


if __name__ == "__main__":
    # Test
    print("Tester Yr API...")
    yr = YrClient(lat=58.35, lon=6.63)  # Sokndal
    temp = yr.get_current_temperature()
    symbol = yr.get_weather_symbol()
    
    if temp is not None:
        print(f"✓ Utetemperatur Sokndal: {temp}°C")
    else:
        print("✗ Kunne ikke hente temperatur")
    
    if symbol:
        print(f"✓ Værsymbol: {symbol}")
