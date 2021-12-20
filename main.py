#!/usr/bin/python3
# TODO: refactor with Point implementation

from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw
import streamlit as st
from pydantic import BaseModel


class Point:
    x: int
    y: int 


class GridSettings(BaseModel):
    bg_color: str
    primary_color: str
    secondary_color: str
    approx_dims_x: int
    approx_dims_y: int
    spacing_x: int
    spacing_y: int
    line_width_primary: int
    line_width_secondary: int
    grid_ratio: int

    @classmethod
    def from_gui(cls):
        return cls(
            bg_color=st.color_picker('Background color', '#FFFFFF'),
            primary_color=st.color_picker('Primary grid color', '#000000'),
            secondary_color=st.color_picker('Secondary grid color', '#555555'),
            spacing_x=st.number_input('X spacing', value=100),
            spacing_y=st.number_input('Y spacing', value=100),
            approx_dims_x=st.number_input('Approx X', value=1024),
            approx_dims_y=st.number_input('Approx Y', value=768),
            line_width_primary=st.number_input('Line width, primary', value=3),
            line_width_secondary=st.number_input('Line width, secondary', value=1),
            grid_ratio=st.number_input('Length of large square, in small squares', value=2)
        )


class DrawGrids:
    conf: GridSettings

    def __init__(self, conf: GridSettings):
        self.conf = conf
        # FYI I know this is horrible but I was rushing and didn't want to implement a proper Point class.

        # Calculate amount of spacing to put between the lines on the primary grid (grid1)
        self.spacing_grid1_x = self.conf.spacing_x * self.conf.grid_ratio
        self.spacing_grid1_y = self.conf.spacing_y * self.conf.grid_ratio

        self.x = self.conf.approx_dims_x - (self.conf.approx_dims_x % self.spacing_grid1_x)
        self.y = self.conf.approx_dims_y - (self.conf.approx_dims_y % self.spacing_grid1_y)

        self.num_squares_x = int(self.x / self.conf.spacing_x)
        self.num_squares_y = int(self.y / self.conf.spacing_y)

        self.square_num_grid1_x = int(self.num_squares_x / self.conf.grid_ratio)
        self.square_num_grid1_y = int(self.num_squares_y / self.conf.grid_ratio)

        self.im = Image.new("RGB", (self.x, self.y), self.conf.bg_color)
        self.canvas = ImageDraw.Draw(self.im)

    def draw_grid2(self):
        """ The secondary grid is the small, usually lighter colored grid intended to measure smaller units. """
        for i in range(1, self.num_squares_y):
            i *= self.conf.spacing_y
            self.canvas.line((0, i, self.x, i), fill=self.conf.secondary_color, width=self.conf.line_width_secondary)
        for i in range(1, self.num_squares_x):
            i *= self.conf.spacing_x
            self.canvas.line((i, 0, i, self.y), fill=self.conf.secondary_color, width=self.conf.line_width_secondary)

    def draw_grid1(self):
        """ The primary grid is the larger, usually darker colored grid intended to measure larger units. """
        for i in range(1, self.square_num_grid1_y):
            i *= self.spacing_grid1_y
            self.canvas.line((0, i, self.x, i), fill=self.conf.primary_color, width=self.conf.line_width_primary)
        for i in range(1, self.square_num_grid1_x):
            i *= self.spacing_grid1_x
            self.canvas.line((i, 0, i, self.y), fill=self.conf.primary_color, width=self.conf.line_width_primary)

    def draw(self):
        # draw order is important -- we want to make sure primary grid shows up on top, so we draw it last
        self.draw_grid2()
        self.draw_grid1()


def main():
    grid_settings = GridSettings.from_gui()
    grid = DrawGrids(grid_settings)
    grid.draw()
    img_file_name = str(datetime.now()) + '.png'
    st.image(grid.im, caption='Preview')
    png_bytes = BytesIO()
    grid.im.save(png_bytes, format='PNG')
    st.download_button(label="Download grid image", data=png_bytes, file_name=img_file_name)


if __name__ == '__main__':
    main()
