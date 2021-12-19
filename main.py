#!/usr/bin/python3
# TODO: refactor with Point implementation

from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw
import streamlit as st
from pydantic import BaseModel


class GridSettings(BaseModel):
    bg_color: str
    primary_color: str
    secondary_color: str
    approx_x: int
    approx_y: int
    spacing_x: int
    spacing_y: int
    line_width_primary: int
    line_width_secondary: int
    big_square_multiple: int = 5


def get_settings_from_gui():
    return GridSettings(
        bg_color=st.color_picker('Background color', '#FFFFFF'),
        primary_color=st.color_picker('Primary grid color', '#555555'),
        secondary_color=st.color_picker('Secondary grid color', '#000000'),
        spacing_x=st.number_input('X spacing', value=100),
        spacing_y=st.number_input('Y spacing', value=100),
        approx_x=st.number_input('Approx X', value=1024),
        approx_y=st.number_input('Approx Y', value=768),
        line_width_primary=st.number_input('Line width, primary', value=1),
        line_width_secondary=st.number_input('Line width, secondary', value=3),
        big_square_multiple=st.number_input('Length of large square, in small squares', value=2)
    )


class Grid:

    def __init__(self, conf: GridSettings):
        self.conf = conf
        # FYI I know this is horrible but I was rushing and didn't want to implement a proper Point class.

        self.big_square_spacing_x = self.conf.spacing_x * self.conf.big_square_multiple
        self.big_square_spacing_y = self.conf.spacing_y * self.conf.big_square_multiple

        self.x = self.conf.approx_x - (self.conf.approx_x % self.big_square_spacing_x)
        self.y = self.conf.approx_y - (self.conf.approx_y % self.big_square_spacing_y)

        self.num_of_squares_x = int(self.x/self.conf.spacing_x)
        self.num_of_squares_y = int(self.y/self.conf.spacing_y)

        self.num_of_big_squares_x = int(self.num_of_squares_x/self.conf.big_square_multiple)
        self.num_of_big_squares_y = int(self.num_of_squares_y/self.conf.big_square_multiple)

        self.im = Image.new("RGB", (self.x, self.y), self.conf.bg_color)
        self.draw = ImageDraw.Draw(self.im)

    def render(self):
        for i in range(1, self.num_of_squares_y):
            i *= self.conf.spacing_y
            self.draw.line((0, i, self.x, i), fill=self.conf.primary_color, width=self.conf.line_width_primary)
        for i in range(1, self.num_of_squares_x):
            i *= self.conf.spacing_x
            self.draw.line((i, 0, i, self.y), fill=self.conf.primary_color, width=self.conf.line_width_primary)
        for i in range(1, self.num_of_big_squares_y):
            i *= self.big_square_spacing_y
            self.draw.line((0, i, self.x, i), fill=self.conf.secondary_color, width=self.conf.line_width_secondary)
        for i in range(1, self.num_of_big_squares_x):
            i *= self.big_square_spacing_x
            self.draw.line((i, 0, i, self.y), fill=self.conf.secondary_color, width=self.conf.line_width_secondary)


def main():
    grid_settings = get_settings_from_gui()
    grid = Grid(grid_settings)
    grid.render()
    img_file_name = str(datetime.now()) + '.png'
    st.image(grid.im, caption='Preview')
    png_bytes = BytesIO()
    grid.im.save(png_bytes, format='PNG')
    st.download_button(label="Download grid image", data=png_bytes, file_name=img_file_name)


if __name__ == '__main__':
    main()
