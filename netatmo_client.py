"""
Netatmo API Client
Henter temperaturdata fra Netatmo værstasjon
"""
import requests
import time
from typing import Optional, Dict


class NetatmoClient:
    """Klient for å kommunisere med Netatmo API"""
    
    AUTH_URL = "https://api.netatmo.com/oauth2/token"
    STATION_URL = "https://api.netatmo.com/api/getstationsdata"
    
    def __init__(self, client_id: str, client_secret: str, username: str = None, password: str = None, refresh_token: str = None):
        """
        Initialiserer Netatmo klienten
        
        Args:
            client_id: Netatmo app client ID
            client_secret: Netatmo app client secret
            username: Netatmo bruker e-post (valgfri hvis refresh_token er gitt)
            password: Netatmo bruker passord (valgfri hvis refresh_token er gitt)
            refresh_token: Netatmo refresh token (valgfri hvis username/password er gitt)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = refresh_token
        self.token_expires_at: float = 0
    
    def _authenticate(self) -> bool:
        """
        Autentiserer med Netatmo API og henter access token
        
        Returns:
            True hvis autentisering var vellykket
        """
        try:
            payload = {
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': self.password,
                'scope': 'read_station'
            }
            
            response = requests.post(self.AUTH_URL, data=payload)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            # Sett utløpstid litt før faktisk utløp (buffer på 5 minutter)
            self.token_expires_at = time.time() + data['expires_in'] - 300
            
            print("✓ Autentisert med Netatmo API")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Feil ved autentisering: {e}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """
        Fornyer access token ved bruk av refresh token
        
        Returns:
            True hvis fornyelse var vellykket
        """
        try:
            payload = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(self.AUTH_URL, data=payload)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.token_expires_at = time.time() + data['expires_in'] - 300
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Feil ved fornyelse av token: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Sjekker om vi er autentisert og fornyer token om nødvendig"""
        if not self.access_token or time.time() >= self.token_expires_at:
            if self.refresh_token:
                return self._refresh_access_token()
            else:
                return self._authenticate()
        return True
    
    def get_temperature(self, module_name: str = None) -> Optional[float]:
        """
        Henter gjeldende temperatur fra værstasjonen
        
        Args:
            module_name: Navn på modul å hente fra (None = hovedmodul)
        
        Returns:
            Temperatur i grader Celsius, eller None hvis feil
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.post(self.STATION_URL, headers=headers)
            
            # Hvis 403, prøv å fornye token og prøv igjen
            if response.status_code == 403:
                print("  [Token utløpt, fornyer...]")
                if self._refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.post(self.STATION_URL, headers=headers)
                else:
                    print("✗ Kunne ikke fornye token")
                    return None
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'body' not in data or 'devices' not in data['body']:
                print("✗ Ingen enheter funnet i Netatmo responsen")
                return None
            
            devices = data['body']['devices']
            if not devices:
                print("✗ Ingen værstasjoner funnet")
                return None
            
            device = devices[0]
            
            # Hvis ingen modul spesifisert, bruk hovedmodulen
            if module_name is None:
                if 'dashboard_data' in device and 'Temperature' in device['dashboard_data']:
                    temperature = device['dashboard_data']['Temperature']
                    location = device.get('module_name', device.get('station_name', 'Ukjent'))
                    print(f"✓ Temperatur hentet ({location}): {temperature}°C")
                    return temperature
            else:
                # Søk i moduler
                if 'modules' in device:
                    for module in device['modules']:
                        if module.get('module_name', '').lower() == module_name.lower():
                            if 'dashboard_data' in module and 'Temperature' in module['dashboard_data']:
                                temperature = module['dashboard_data']['Temperature']
                                print(f"✓ Temperatur hentet ({module_name}): {temperature}°C")
                                return temperature
                
                # Sjekk også hovedmodulen hvis navn matcher
                device_name = device.get('module_name', device.get('station_name', ''))
                if device_name.lower() == module_name.lower():
                    if 'dashboard_data' in device and 'Temperature' in device['dashboard_data']:
                        temperature = device['dashboard_data']['Temperature']
                        print(f"✓ Temperatur hentet ({module_name}): {temperature}°C")
                        return temperature
            
            print(f"✗ Ingen temperaturdata funnet for {module_name or 'hovedmodul'}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Feil ved henting av data: {e}")
            return None
    
    def get_all_temperatures(self) -> Dict[str, float]:
        """
        Henter temperatur fra alle tilgjengelige moduler
        
        Returns:
            Dictionary med modulnavn -> temperatur
        """
        if not self._ensure_authenticated():
            return {}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.post(self.STATION_URL, headers=headers)
            
            # Hvis 403, prøv å fornye token og prøv igjen
            if response.status_code == 403:
                print("  [Token utløpt, fornyer...]")
                if self._refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.post(self.STATION_URL, headers=headers)
                else:
                    print("✗ Kunne ikke fornye token")
                    return {}
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'body' not in data or 'devices' not in data['body']:
                return {}
            
            devices = data['body']['devices']
            if not devices:
                return {}
            
            device = devices[0]
            temperatures = {}
            
            # Hovedmodul
            if 'dashboard_data' in device and 'Temperature' in device['dashboard_data']:
                name = device.get('module_name', device.get('station_name', 'Hovedmodul'))
                temperatures[name] = device['dashboard_data']['Temperature']
            
            # Andre moduler
            if 'modules' in device:
                for module in device['modules']:
                    if 'dashboard_data' in module and 'Temperature' in module['dashboard_data']:
                        name = module.get('module_name', f"Modul {module.get('_id', 'ukjent')}")
                        temperatures[name] = module['dashboard_data']['Temperature']
            
            return temperatures
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Feil ved henting av data: {e}")
            return {}
    
    def get_station_data(self) -> Optional[Dict]:
        """
        Henter full stasjondata inkludert alle moduler
        
        Returns:
            Dictionary med all stasjondata, eller None hvis feil
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.post(self.STATION_URL, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Feil ved henting av stasjondata: {e}")
            return None
