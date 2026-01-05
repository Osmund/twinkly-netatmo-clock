#!/usr/bin/env python3
"""
Test script for å identifisere panel-rekkefølgen
Lyser opp senteret av hvert panel, ett om gangen
"""
import os
import time
from dotenv import load_dotenv
from twinkly_client import TwinklySquare


def test_panels():
    """Test hvert panel individuelt"""
    print("=" * 50)
    print("Twinkly Panel Test")
    print("=" * 50)
    
    # Last inn miljøvariabler
    load_dotenv()
    twinkly_ip = os.getenv('TWINKLY_IP')
    
    print("\nKobler til Twinkly...")
    twinkly = TwinklySquare(ip_address=twinkly_ip)
    
    if not twinkly.connect():
        print("✗ Kunne ikke koble til Twinkly")
        return
    
    if not twinkly.set_mode_rt():
        print("✗ Kunne ikke sette realtime modus")
        return
    
    print("\n" + "=" * 50)
    print("Vi har 6 paneler totalt (3 bredt x 2 høyt)")
    print("Hver panel er 8x8 piksler")
    print("=" * 50)
    
    # Definer senterpunkt for hvert teoretisk panel
    # Layout: 3 paneler bredt (0-7, 8-15, 16-23) x 2 paneler høyt (0-7, 8-15)
    panels = [
        {"navn": "Panel 1", "x": 4, "y": 4},      # Øvre venstre (0-7, 0-7)
        {"navn": "Panel 2", "x": 12, "y": 4},     # Øvre midten (8-15, 0-7)
        {"navn": "Panel 3", "x": 20, "y": 4},     # Øvre høyre (16-23, 0-7)
        {"navn": "Panel 4", "x": 4, "y": 12},     # Nedre venstre (0-7, 8-15)
        {"navn": "Panel 5", "x": 12, "y": 12},    # Nedre midten (8-15, 8-15) - KONTROLLPANEL
        {"navn": "Panel 6", "x": 20, "y": 12},    # Nedre høyre (16-23, 8-15)
    ]
    
    print("\nTester hvert panel. Vent...")
    print("(En hvit piksel vil lyse i senteret av hvert panel)")
    print()
    
    try:
        for i, panel in enumerate(panels, 1):
            # Lag tomt canvas
            canvas = [[(0, 0, 0) for _ in range(24)] for _ in range(16)]
            
            # Tenn en hvit piksel i senteret av panelet
            x, y = panel["x"], panel["y"]
            
            # Lag et lite kryss (5 piksler) for bedre synlighet
            canvas[y][x] = (255, 255, 255)  # Senter
            if x > 0:
                canvas[y][x-1] = (255, 255, 255)  # Venstre
            if x < 23:
                canvas[y][x+1] = (255, 255, 255)  # Høyre
            if y > 0:
                canvas[y-1][x] = (255, 255, 255)  # Opp
            if y < 15:
                canvas[y+1][x] = (255, 255, 255)  # Ned
            
            print(f"\n{'='*50}")
            print(f"Viser: {panel['navn']}")
            print(f"  Teoretisk posisjon: x={panel['x']}, y={panel['y']}")
            print(f"{'='*50}")
            
            twinkly.show_pattern(canvas)
            
            if i < len(panels):
                print("\nSkriv hvilket panel dette er i ditt oppsett:")
                print("  (f.eks: 'øvre venstre', 'nedre midten', etc.)")
                panel_pos = input("  >> ").strip()
                panel["faktisk_posisjon"] = panel_pos
        
        # Sammendrag
        print("\n" + "=" * 50)
        print("SAMMENDRAG AV PANEL-MAPPING:")
        print("=" * 50)
        for panel in panels:
            faktisk = panel.get("faktisk_posisjon", "Ikke oppgitt")
            print(f"{panel['navn']} (x={panel['x']}, y={panel['y']}): {faktisk}")
        
    except KeyboardInterrupt:
        print("\n\nAvbrutt av bruker")
    finally:
        print("\nRenser display...")
        twinkly.clear()
        print("✓ Ferdig!")


if __name__ == "__main__":
    test_panels()
