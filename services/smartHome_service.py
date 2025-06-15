import requests



# Common color names mapped to RGB values


# def main():
#     print("Color Control Options:")
#     print("1. HSV (Hue, Saturation, Value)")
#     print("2. RGB (Red, Green, Blue)")
#     print("3. Color by name")
#     print("4. Turning on and off")

#     choice = input("Choose option (1 - 4): ")
    
#     if choice == "1":
#         hue = input("Hue (0-360): ")
#         saturation = input("Saturation (0-100): ")
#         brightness = input("Brightness (0-100): ")
#         change_color(hue, saturation, brightness)
#     elif choice == "2":
#         red = input("Red (0-255): ")
#         green = input("Green (0-255): ")
#         blue = input("Blue (0-255): ")
#         brightness = input("Brightness (0-100): ")
#         set_rgb_color(int(red), int(green), int(blue), int(brightness))
#     elif choice == "3":
#         color_name = input("Color name (e.g. pink, blue, orange): ")
#         brightness = input("Brightness (0-100): ")
#         set_color_by_name(color_name, int(brightness))
#     elif choice == "4":
#         command = input("On or Off: ")
#         light_switch(command)
#     else:
#         print("Invalid choice")

class SmartHomeService():
    def __init__(self):
        self.domoticz_url = "http://127.0.0.1:8080/json.htm"
        self.idx = 4
        self.auth = ('admin', 'domoticz')
        self.COLOR_RGB = {
            "red":     (255, 0, 0),
            "green":   (0, 255, 0),
            "blue":    (0, 0, 255),
            "yellow":  (255, 234, 0),
            "cyan":    (0, 255, 255),
            "magenta": (255, 0, 255),
            "pink":    (255, 20, 147),
            "orange":  (255, 165, 0),
            "purple":  (128, 0, 128),
            "white":   (255, 255, 255),
            "black":   (0, 0, 0),
            "gray":    (128, 128, 128),
        }
        self.commands = {
            "on": self.light_switch,
            "off": self.light_switch,
            "toggle": self.light_switch,
            "set color": self.change_color,
            "set rgb": self.set_rgb_color,
            "set color": self.set_color_by_name,
        }
        
    def change_color(self,hue, saturation, brightness=100):
        """
        Change the color of Philips Hue lamp.
        
        Args:
            hue (int): Color hue (0-360)
            saturation (int): Color saturation (0-100)
            brightness (int): Brightness level (0-100), default 100
        """
        params = {
            "type": "command",
            "param": "setcolbrightnessvalue",
            "idx": self.idx,
            "hue": int(hue),
            "brightness": int(brightness),
            "saturation": int(saturation),
            "iswhite": "false"
        }

        try:
            response = requests.get(self.domoticz_url, params=params, auth=self.auth)
        except requests.RequestException as e:
            print(f"Error connecting to Domoticz: {e}")
            return
        
        print("Status code:", response.status_code)
        print(response.json())
        
        
    def set_color_by_name(self,color_name, brightness=100):
        """
        Set color using a common color name.
        """
        color_name = color_name.lower()
        if color_name in self.COLOR_RGB:
            red, green, blue = self.COLOR_RGB[color_name]
            self.set_rgb_color(red, green, blue, brightness)
        else:
            print(f"Color '{color_name}' not recognized. Available colors: {', '.join(self.COLOR_RGB.keys())}")
            
    def set_rgb_color(self, red, green, blue, brightness=100):
        """
        Set color using RGB values.
        
        Args:
            red (int): Red value (0-255)
            green (int): Green value (0-255) 
            blue (int): Blue value (0-255)
            brightness (int): Brightness level (0-100), default 100
        """
        # Convert RGB to HSV 
        r, g, b = red/255.0, green/255.0, blue/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Calculate hue
        if diff == 0:
            hue = 0
        elif max_val == r:
            hue = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            hue = (60 * ((b - r) / diff) + 120) % 360
        elif max_val == b:
            hue = (60 * ((r - g) / diff) + 240) % 360
        
        # Calculate saturation
        saturation = 0 if max_val == 0 else (diff / max_val) * 100
        self.change_color(int(hue), int(saturation), brightness)

    
    def light_switch(self,command):
        """
        Turn light on or off.
        
        Args:
            command (str): "On" or "Off"
        """
        
        params = {
            "type": "command",
            "param": "switchlight",
            "idx": self.idx,
            "switchcmd": command.strip().capitalize()
        }
        
        try:
            response = requests.get(self.domoticz_url, params=params, auth=self.auth)
        except requests.RequestException as e:
            print(f"Error connecting to Domoticz: {e}")
            return
        
        print("Status code:", response.status_code)
        print(response.json())
        
