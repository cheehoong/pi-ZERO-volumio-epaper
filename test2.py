print(__name__)

try:
    # Trying to find module in the parent package
    from .libz import epd2in13_V2
    print(epd2in13_V2.EPD_WIDTH)
    del epd2in13_V2
except ImportError:
    print('Relative import failed')

try:
    # Trying to find module on sys.path
    import epd2in13_V2
    print(epd2in13_V2.EPD_WIDTH)
except ModuleNotFoundError:
    print('Absolute import failed')