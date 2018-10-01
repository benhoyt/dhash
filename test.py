from unittest import TestCase

import PIL.Image
import PIL.ImageDraw

from dhash import dhash_row_col


class TestDHash(TestCase):
    def test_fill_transparency_pil(self):
        "Ensure transparent colors in PIL Images are ignored in hashes"

        # greyscale image, completely white and also completely transparent
        im1 = PIL.Image.new('LA', (100, 100), (0xff, 0))

        im2 = im1.copy()
        # replace most of it with "transparent black"
        PIL.ImageDraw.Draw(im2).rectangle((10, 10, 90, 90), (0, 0))

        self.assertEqual(dhash_row_col(im1), dhash_row_col(im2))
