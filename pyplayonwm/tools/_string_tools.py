RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'

class ColoredString:
    
    def __init__(self, string):
        self.string = string

    def _color_string(self):
        return self.string
        
class RedString(ColoredString):

    def _color_string(self):
        return f"{RED}{self.string}{RESET}"
    
class YellowString(ColoredString):
    
    def _color_string(self):
        return f"{YELLOW}{self.string}{RESET}"
    
class GreenString(ColoredString):
        
    def _color_string(self):
        return f"{GREEN}{self.string}{RESET}"