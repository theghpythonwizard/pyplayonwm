from .tools._string_tools import *

class StringColor:

    def __init__(self):
        pass

    def red_string(self, string):
        return RedString(string)._color_string()
    
    def yellow_string(self, string):
        return YellowString(string)._color_string()
    
    def green_string(self, string):
        return GreenString(string)._color_string()