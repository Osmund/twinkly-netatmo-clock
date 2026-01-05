"""
Twinkly Square Display Client
Viser tall og mønstre på Twinkly Square
"""
from xled.discover import discover
from xled.control import HighControlInterface
from typing import Optional, Tuple
import time
import io
from icons import get_icon_for_location


# 5x7 font for siffer (0-9) og spesialtegn - kompakt for 24 pixler bredde
# Hvert siffer er representert som en liste med 7 rader, hver rad er 5 piksler
DIGIT_FONT = {
    '0': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    '1': [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [1, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 1, 1]
    ],
    '2': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1]
    ],
    '3': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    '4': [
        [0, 0, 0, 1, 0],
        [0, 0, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0]
    ],
    '5': [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    '6': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    '7': [
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0]
    ],
    '8': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    '9': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    '-': [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    '.': [  # Punktum for desimaltall - ekstra kompakt
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 0, 0]
    ],
    '°': [  # Grad-symbol - kompakt
        [0, 1, 1, 0, 0],
        [1, 0, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]
}


class TwinklySquare:
    """Klient for å kommunisere med Twinkly Square"""
    
    def __init__(self, ip_address: Optional[str] = None):
        """
        Initialiserer Twinkly Square klienten
        
        Args:
            ip_address: IP-adressen til Twinkly Square (auto-discover hvis None)
        """
        self.ip_address = ip_address
        self.control: Optional[HighControlInterface] = None
        self.width = 24  # 3 paneler bredt (3 x 8)
        self.height = 16  # 2 paneler høyt (2 x 8)
        self.led_layout = None  # LED koordinater fra Twinkly
    
    def connect(self) -> bool:
        """
        Kobler til Twinkly Square
        
        Returns:
            True hvis tilkobling var vellykket
        """
        try:
            if not self.ip_address:
                print("Søker etter Twinkly enheter...")
                devices = discover()
                if not devices:
                    print("✗ Ingen Twinkly enheter funnet")
                    return False
                self.ip_address = devices[0].ip_address
                print(f"✓ Fant Twinkly på {self.ip_address}")
            
            self.control = HighControlInterface(self.ip_address)
            
            # Hent enhetsinformasjon for å verifisere tilkobling
            device_info = self.control.get_device_info()
            total_leds = device_info.get('number_of_led', 384)
            
            # Hent LED layout (koordinater)
            try:
                layout = self.control.get_led_layout()
                if 'coordinates' in layout:
                    self.led_layout = layout['coordinates']
                    print(f"✓ Hentet LED layout med {len(self.led_layout)} LEDs")
            except Exception as e:
                print(f"⚠ Kunne ikke hente LED layout: {e}")
                print(f"  Bruker standard rekkefølge")
            
            print(f"✓ Koblet til Twinkly array (totalt {total_leds} LEDs)")
            print(f"  Layout: {self.width}x{self.height} ({self.width//8}x{self.height//8} paneler)")
            print(f"  Kontrollpanel: midten nederst")
            return True
            
        except Exception as e:
            print(f"✗ Feil ved tilkobling til Twinkly: {e}")
            return False
    
    def set_mode_rt(self) -> bool:
        """
        Setter Twinkly til realtime modus for direktekontroll
        
        Returns:
            True hvis vellykket
        """
        try:
            self.control.set_mode("rt")
            return True
        except Exception as e:
            print(f"✗ Feil ved setting av realtime modus: {e}")
            return False
    
    def create_frame(self, pattern: list) -> list:
        """
        Lager en frame fra et 2D mønster, mapper korrekt til Twinkly LEDs
        
        Args:
            pattern: 2D liste med RGB tupler eller 0/1 verdier
        
        Returns:
            Liste med RGB verdier for alle LEDs i Twinkly sin rekkefølge
        """
        if self.led_layout is None:
            # Fallback til enkel rad-for-rad mapping
            frame = []
            for row in pattern:
                for pixel in row:
                    if isinstance(pixel, tuple):
                        frame.extend(pixel)
                    elif pixel == 1:
                        frame.extend([255, 255, 255])
                    else:
                        frame.extend([0, 0, 0])
            
            total_pixels = self.width * self.height
            while len(frame) < total_pixels * 3:
                frame.extend([0, 0, 0])
            return frame[:total_pixels * 3]
        
        # Bruk LED layout for korrekt mapping
        frame = [(0, 0, 0)] * len(self.led_layout)
        
        for led_idx, coord in enumerate(self.led_layout):
            # Twinkly koordinater: x går fra -1 til 1, y går fra 0 til 1
            # Konverter til pikselkoordinater:
            # x: -1 til 1 -> 0 til 23 (24 piksler bredt)
            # y: 0 til 1 -> 0 til 15 (16 piksler høyt)
            x = int((coord['x'] + 1.0) / 2.0 * self.width)
            y = int((1.0 - coord['y']) * self.height)  # Inverterer Y - Twinkly Y=0 er bunn, vi vil ha topp
            
            # Begrens til gyldige koordinater
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            
            # Sjekk at koordinater er innenfor bounds
            if 0 <= y < len(pattern) and 0 <= x < len(pattern[0]):
                pixel = pattern[y][x]
                if isinstance(pixel, tuple):
                    frame[led_idx] = pixel
                elif pixel == 1:
                    frame[led_idx] = (255, 255, 255)
                else:
                    frame[led_idx] = (0, 0, 0)
        
        # Konverter til flat liste
        result = []
        for r, g, b in frame:
            result.extend([r, g, b])
        
        return result
    
    def show_pattern(self, pattern: list) -> bool:
        """
        Viser et mønster på Twinkly Square
        
        Args:
            pattern: 2D liste med 0/1 verdier eller RGB tupler
        
        Returns:
            True hvis vellykket
        """
        try:
            if not self.control:
                print("✗ Ikke koblet til Twinkly")
                return False
            
            frame = self.create_frame(pattern)
            # Konverter til BytesIO objekt som xled forventer
            frame_io = io.BytesIO(bytes(frame))
            self.control.set_rt_frame_socket(frame_io, 3)  # version 3 for RGB
            return True
            
        except Exception as e:
            print(f"✗ Feil ved visning av mønster: {e}")
            # Prøv å reaktivere realtime-modus
            try:
                self.set_mode_rt()
            except:
                pass
            return False
    
    def render_temperature(self, temperature: float, color: Tuple[int, int, int] = (255, 100, 0)) -> list:
        """
        Renderer temperaturen som et visuelt mønster
        
        Args:
            temperature: Temperaturen som skal vises
            color: RGB farge for tallene (standard: oransje)
        
        Returns:
            2D liste med mønsteret for displayet
        """
        # Lag tomt canvas (24x16)
        canvas = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        
        # Formater temperatur (avrund til heltall)
        temp_int = int(round(temperature))
        display_str = str(temp_int)
        
        # Beregn total bredde av teksten (hvert siffer er 5 bred + 1 mellomrom)
        # Legg til plass for gradsymbol (5 bred)
        chars_to_display = list(display_str) + ['°']
        total_width = 0
        for i, char in enumerate(chars_to_display):
            if char in DIGIT_FONT:
                if char == '.':
                    total_width += 3  # Punktum: 2 bred + 1 mellomrom
                else:
                    # Sjekk om neste tegn er punktum
                    next_char = chars_to_display[i + 1] if i + 1 < len(chars_to_display) else None
                    if next_char == '.':
                        total_width += 5  # Kutt 1 piksel før punktum
                    else:
                        total_width += 6  # 5 piksler + 1 mellomrom
        
        # Sentrer teksten horisontalt og vertikalt på 24x16 displayet
        start_x = (self.width - total_width) // 2 + 1  # +1 for å flytte 1 piksel til høyre
        start_y = (self.height - 7) // 2  # 7 høyt nå
        
        # Tegn hvert tegn
        x_offset = start_x
        for i, char in enumerate(chars_to_display):
            if char in DIGIT_FONT:
                digit = DIGIT_FONT[char]
                
                for y, row in enumerate(digit):
                    for x, pixel in enumerate(row):
                        if pixel == 1:
                            canvas_y = start_y + y
                            canvas_x = x_offset + x
                            if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
                                canvas[canvas_y][canvas_x] = color
                
                # Juster offset basert på tegntype og neste tegn
                if char == '.':
                    x_offset += 3  # Punktum får mindre plass
                else:
                    # Sjekk om neste tegn er punktum
                    next_char = chars_to_display[i + 1] if i + 1 < len(chars_to_display) else None
                    if next_char == '.':
                        x_offset += 5  # Kun 5 piksler før punktum (kutt 1 piksel mellomrom)
                    else:
                        x_offset += 6  # Flytt til neste tegn (5 bred + 1 mellomrom)
        
        return canvas
    
    def show_temperature(self, temperature: float) -> bool:
        """
        Viser temperaturen på Twinkly Square
        
        Args:
            temperature: Temperaturen som skal vises
        
        Returns:
            True hvis vellykket
        """
        # Velg farge basert på temperatur
        if temperature < 0:
            color = (0, 100, 255)  # Blå for kaldt
        elif temperature < 10:
            color = (0, 200, 255)  # Lyseblå
        elif temperature < 20:
            color = (255, 200, 0)  # Gul
        else:
            color = (255, 50, 0)  # Rød/oransje for varmt
        
        pattern = self.render_temperature(temperature, color)
        return self.show_pattern(pattern)
    
    def show_temperature_with_icon(self, temperature: float, location_name: str) -> bool:
        """
        Viser temperaturen med et lokasjon-ikon på Twinkly Square
        For strømpris vises tall uten °C
        
        Args:
            temperature: Temperaturen (eller strømprisen) som skal vises
            location_name: Navn på lokasjonen
        
        Returns:
            True hvis vellykket
        """
        # Sjekk om det er strømpris
        is_electricity = 'strøm' in location_name.lower() or 'electricity' in location_name.lower()
        
        # Velg farge basert på verdi
        if is_electricity:
            # Fargekoding for strømpris (øre/kWh)
            if temperature < 50:
                temp_color = (0, 255, 0)  # Grønn (billig)
            elif temperature < 100:
                temp_color = (255, 200, 0)  # Gul (middels)
            else:
                temp_color = (255, 0, 0)  # Rød (dyrt)
        else:
            # Fargekoding for temperatur
            if temperature < 0:
                temp_color = (0, 100, 255)  # Blå for kaldt
            elif temperature < 10:
                temp_color = (0, 200, 255)  # Lyseblå
            elif temperature < 20:
                temp_color = (255, 200, 0)  # Gul
            else:
                temp_color = (255, 50, 0)  # Rød/oransje for varmt
        
        # Hent bakgrunnsikon for lokasjonen (24x16)
        icon = get_icon_for_location(location_name)
        
        # Lag canvas med bakgrunnsikon
        canvas = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        icon_color = (20, 20, 40)  # Mørk blå/grå for subtil bakgrunn
        
        # Tegn bakgrunnsikon over hele skjermen
        for y in range(len(icon)):
            for x in range(len(icon[0])):
                if icon[y][x] == 1:
                    canvas[y][x] = icon_color
        
        # Formater verdi - vis 1 desimal for både temp og strømpris
        display_str = f"{temperature:.1f}"
        
        # Beregn total bredde av teksten
        if is_electricity:
            # For strømpris: bare tall (med eventuell desimal)
            chars_to_display = list(display_str)
        else:
            # For temperatur: tall + °
            chars_to_display = list(display_str) + ['°']
        
        total_width = 0
        for i, char in enumerate(chars_to_display):
            if char in DIGIT_FONT:
                if char == '.':
                    total_width += 3  # Punktum: bare 2 bred + 1 mellomrom
                else:
                    # Sjekk om neste tegn er punktum
                    next_char = chars_to_display[i + 1] if i + 1 < len(chars_to_display) else None
                    if next_char == '.':
                        total_width += 5  # Kutt 1 piksel før punktum
                    else:
                        total_width += 6  # 5 piksler bred font + 1 mellomrom
        
        # Sentrer temperatur på skjermen
        start_x = (self.width - total_width) // 2 + 1
        start_y = (self.height - 7) // 2
        
        # Tegn temperatur OVER bakgrunnen
        x_offset = start_x
        for i, char in enumerate(chars_to_display):
            if char in DIGIT_FONT:
                digit = DIGIT_FONT[char]
                
                for y, row in enumerate(digit):
                    for x, pixel in enumerate(row):
                        if pixel == 1:
                            canvas_y = start_y + y
                            canvas_x = x_offset + x
                            if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
                                canvas[canvas_y][canvas_x] = temp_color
                
                # Juster offset basert på tegntype og neste tegn
                if char == '.':
                    x_offset += 3  # Punktum får mindre plass
                else:
                    # Sjekk om neste tegn er punktum
                    next_char = chars_to_display[i + 1] if i + 1 < len(chars_to_display) else None
                    if next_char == '.':
                        x_offset += 5  # Kun 5 piksler før punktum (kutt 1 piksel mellomrom)
                    else:
                        x_offset += 6  # 5 bred + 1 mellomrom
        
        return self.show_pattern(canvas)
    
    def show_clock(self, hours: int, minutes: int) -> bool:
        """
        Viser en fancy digital klokke på Twinkly Square (HH:MM format)
        
        Args:
            hours: Timer (0-23)
            minutes: Minutter (0-59)
        
        Returns:
            True hvis vellykket
        """
        # Formater tid som HH:MM
        time_str = f"{hours:02d}:{minutes:02d}"
        
        # Klokkefarger - gradient fra blå til oransje basert på tid på døgnet
        # Hvert siffer får sin egen farge
        if 0 <= hours < 6:
            # Natt (midnatt til 06:00): Mørke kalde farger
            digit_colors = [
                (20, 40, 150),   # Mørk blå
                (80, 20, 120),   # Lilla
                (20, 100, 150),  # Cyan-blå
                (100, 40, 150)   # Lys lilla
            ]
            colon_color = (150, 40, 150)  # Lilla/magenta kontrast
        elif 6 <= hours < 12:
            # Morgen (06:00 til 12:00): Friske morgenfarger
            blend = (hours - 6) / 6
            digit_colors = [
                (50, 150, 255),   # Lys blå
                (100, 200, 200),  # Turkis
                (200, 220, 100),  # Gul-grønn
                (255, 200, 50)    # Gul
            ]
            colon_color = (255, 100, 150)  # Rosa kontrast
        elif 12 <= hours < 18:
            # Ettermiddag (12:00 til 18:00): Varme solfarger
            digit_colors = [
                (255, 200, 0),    # Gul
                (255, 150, 0),    # Oransje
                (255, 100, 50),   # Rød-oransje
                (255, 200, 100)   # Lys oransje
            ]
            colon_color = (0, 200, 255)  # Cyan kontrast
        else:
            # Kveld (18:00 til midnatt): Solnedgangsfarger
            digit_colors = [
                (255, 100, 0),    # Oransje
                (200, 50, 100),   # Rød-lilla
                (150, 100, 200),  # Lilla-blå
                (100, 150, 255)   # Blå
            ]
            colon_color = (150, 255, 100)  # Lime grønn kontrast
        
        # Lag canvas
        canvas = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        
        # Tegn tiden - kompakt layout for 24 bred display
        # HH:MM = 2 siffer + kolon + 2 siffer
        # Layout: 5 bred siffer + kolon 1 bred + 5 bred siffer
        # Total: 5 + 5 + 1 + 5 + 5 = 21 bred (med 3 piksler marger totalt)
        
        start_y = (self.height - 7) // 2
        x_offset = 2  # Start x-posisjon (sentrert: (24-21)/2 ≈ 1.5)
        digit_index = 0  # Teller for hvilken farge vi skal bruke
        
        for i, char in enumerate(time_str):
            if char == ':':
                # Tegn kolon (to prikker) - 1 piksel bred
                # Øvre prikk
                canvas[start_y + 2][x_offset] = colon_color
                # Nedre prikk
                canvas[start_y + 4][x_offset] = colon_color
                x_offset += 1  # 1 piksel kolon
            elif char in DIGIT_FONT:
                digit = DIGIT_FONT[char]
                current_color = digit_colors[digit_index % len(digit_colors)]
                
                # Tegn siffer (full 5 piksel bredde)
                for y, row in enumerate(digit):
                    for x in range(len(row)):  # Alle 5 piksler
                        if row[x] == 1:
                            canvas_y = start_y + y
                            canvas_x = x_offset + x
                            if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
                                canvas[canvas_y][canvas_x] = current_color
                
                x_offset += 5  # 5 piksler siffer (ingen mellomrom)
                digit_index += 1  # Neste farge for neste siffer
        
        return self.show_pattern(canvas)
    
    def clear(self) -> bool:
        """
        Sletter displayet (alle LEDs av)
        
        Returns:
            True hvis vellykket
        """
        black_pattern = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        return self.show_pattern(black_pattern)
