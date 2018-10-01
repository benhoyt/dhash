from unittest import TestCase
from PIL import Image, ImageDraw

from dhash import dhash_row_col


class TestDHash(TestCase):
    def test_fill_transparency(self):
        "Ensure transparent colors are ignored in hashes"

        # greyscale image, completely white and also completely transparent
        im1 = Image.new('LA', (100, 100), (0xff, 0))

        im2 = im1.copy()
        # replace most of it with "transparent black"
        ImageDraw.Draw(im2).rectangle((10, 10, 90, 90), (0, 0))

        assert dhash_row_col(im1) == dhash_row_col(im2)
