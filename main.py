#!/usr/bin/python3
# TODO: refactor with Point implementation

from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw
import streamlit as st
from pydantic import BaseModel


class IntPoint:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)


class GridSettings(BaseModel):
    bg_color: str
    grid1_color: str
    grid2_color: str
    approx_dims: IntPoint
    spacing: IntPoint
    grid1_line_width: int
    grid2_line_width: int
    grid_ratio: int

    @classmethod
    def from_gui(cls):
        approximate_dimensions = IntPoint(st.number_input('Approx X', value=1024),
                                          st.number_input('Approx Y', value=768))
        spacing = IntPoint(st.number_input('X spacing', value=100),
                           st.number_input('Y spacing', value=100))
        return cls(
            bg_color=st.color_picker('Background color', '#FFFFFF'),
            grid1_color=st.color_picker('Primary grid color', '#000000'),
            grid2_color=st.color_picker('Secondary grid color', '#555555'),
            spacing=spacing,
            approx_dims=approximate_dimensions,
            grid1_line_width=st.number_input('Line width, primary', value=3),
            grid2_line_width=st.number_input('Line width, secondary', value=1),
            grid_ratio=st.number_input('Length of large square, in small squares', value=2)
        )

    class Config:
        arbitrary_types_allowed = True


class DrawGrids:
    conf: GridSettings

    def __init__(self, conf: GridSettings):
        self.conf = conf
        # FYI I know this is horrible but I was rushing and didn't want to implement a proper Point class.

        # Calculate amount of spacing to put between the lines on the primary grid (grid1)
        self.spacing_grid1 = IntPoint(self.conf.spacing.x * self.conf.grid_ratio,
                                      self.conf.spacing.y * self.conf.grid_ratio)
        self.size = IntPoint(self.conf.approx_dims.x - (self.conf.approx_dims.x % self.spacing_grid1.x),
                             self.conf.approx_dims.y - (self.conf.approx_dims.y % self.spacing_grid1.y))
        self.num_squares = IntPoint(self.size.x / self.conf.spacing.x, self.size.y / self.conf.spacing.y)
        self.square_num_grid1 = IntPoint(self.num_squares.x / self.conf.grid_ratio,
                                         self.num_squares.y / self.conf.grid_ratio)

        self.im = Image.new("RGB", (self.size.x, self.size.y), self.conf.bg_color)
        self.canvas = ImageDraw.Draw(self.im)

    def draw_grid(self, num_squares: IntPoint, spacing: IntPoint, grid_color: str, grid_line_width: int):
        for x in range(1, num_squares.x):
            x *= spacing.x
            self.canvas.line((x, 0, x, self.size.x), fill=grid_color, width=grid_line_width)
        for y in range(1, num_squares.y):
            y *= spacing.y
            self.canvas.line((0, y, self.size.x, y), fill=grid_color, width=grid_line_width)

    def draw_grid2(self):
        """ The secondary grid is the small, usually lighter colored grid intended to measure smaller units. """
        self.draw_grid(num_squares=self.num_squares,
                       spacing=self.conf.spacing,
                       grid_color=self.conf.grid2_color,
                       grid_line_width=self.conf.grid2_line_width)

    def draw_grid1(self):
        """ The primary grid is the larger, usually darker colored grid intended to measure larger units. """
        self.draw_grid(num_squares=self.square_num_grid1,
                       spacing=self.spacing_grid1,
                       grid_color=self.conf.grid1_color,
                       grid_line_width=self.conf.grid1_line_width)

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
