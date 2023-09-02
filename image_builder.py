from PIL import Image, ImageDraw, ImageFont

from utils import get_font


class JacketBuilder:
    def __init__(self):
        self.width = 320
        self.height = 180
        self.font_size = 40
        self.margin = 10
        self.max_lines = 3
        self.bg_color = "rgb(214, 230, 245)"

    def make_image(self, title, song_type=2):
        size = (self.width, self.height)
        image = Image.new("RGB", size, color="black")
        size_inner = (size[0] - 4, size[1] - 4)
        image_inner = Image.new("RGB", size_inner, color=self.bg_color)
        image.paste(image_inner, (2, 2))

        self._draw_lines(image, title)
        self._draw_type(image, song_type)

        return image
    
    def _get_lines(self, title, font, width, max_lines):
        result = []
        while (len(title) > 0) and (len(result) < max_lines):
            i = 0
            while font.getsize(title[:i])[0] < width:
                i += 1
                if i > len(title):
                    break
            result.append(title[:i - 1])
            title = title[i - 1:]
        return result

    def _draw_lines(self, image, title):
        font_size = self.font_size
        draw = ImageDraw.Draw(image)

        font = get_font(font_size)
        font_color = "black"
        font_width = self.width - 2 * self.margin
        lines = self._get_lines(title, font, font_width, self.max_lines)
        y_text = (self.height - font_size * len(lines)) // 2
        for line in lines:
            draw.text((self.margin, y_text), line, fill=font_color, font=font)
            y_text += font_size

    def _draw_type(self, image, song_type):
        draw = ImageDraw.Draw(image)
        font = get_font(self.font_size // 2)
        font_color = "red"
        type_dict = {
            1: "Short",
            2: "",
            3: "Remix",
            4: "Full"
        }
        type_text = type_dict[song_type]
        x_text = self.width - font.getsize(type_text)[0] - self.margin
        draw.text((x_text, self.margin), type_text, fill=font_color, font=font)
