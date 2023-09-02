from PIL import ImageFont

from config import PATH_FONT


def get_font(size):
    return ImageFont.truetype(PATH_FONT, size=size)
