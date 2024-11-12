
#See https://en.wikipedia.org/wiki/ANSI_escape_code#Select_Graphic_Rendition_parameters

RESET = "\33[0m"
BOLD = "\33[1m"
ITALIC = "\33[3m"
UNDER = "\33[4m"


def fg(color):
    """
    See https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
    """
    return f"\33[38:5:{color}m"


def bg(color):
    """
    See https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
    """
    return f"\33[48:5:{color}m"
