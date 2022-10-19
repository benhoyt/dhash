from unittest import TestCase
from io import BytesIO
from os import path

from PIL import Image as PilImage, ImageDraw as PilDraw
from wand.image import Image as WandImage

import dhash


IMGDIR = path.dirname(__file__)


def pilToWand(image, format='png'):
    with BytesIO() as fd:
        image.save(fd, format=format)
        fd.seek(0)
        return WandImage(file=fd)


class TestDHash(TestCase):
    def test_get_grays(self):
        with PilImage.open(path.join(IMGDIR, 'dhash-test.jpg')) as image:
            # get the first two rows
            result = dhash.get_grays(image, 9, 9)[:18]

        expected = [
            93, 158, 210, 122, 93, 77, 74, 74, 77,
            95, 117, 122, 111, 92, 74, 81, 80, 77,
        ]  # fmt: skip

        self.assertEqual(result, expected)

    def test_dhash_row_col(self):
        image = [
            0, 0, 1, 1, 1,
            0, 1, 1, 3, 4,
            0, 1, 6, 6, 7,
            7, 7, 7, 7, 9,
            8, 7, 7, 8, 9,
        ]  # fmt: skip

        row, col = dhash.dhash_row_col(image, size=4)
        self.assertEqual(row, 0b0100101111010001)
        self.assertEqual(col, 0b0101001111111001)

    def test_fill_transparency(self):
        "Ensure transparent colors in PIL Images are ignored in hashes"

        # greyscale image, completely white and also completely transparent
        im1 = PilImage.new('LA', (100, 100), (0xff, 0))

        im2 = im1.copy()
        # replace most of it with "transparent black"
        PilDraw.Draw(im2).rectangle((10, 10, 90, 90), (0, 0))

        self.assertEqual(dhash.dhash_row_col(im1), dhash.dhash_row_col(im2))

        self.assertEqual(dhash.dhash_row_col(pilToWand(im1)), dhash.dhash_row_col(pilToWand(im2)))


if __name__ == '__main__':
    import unittest
    unittest.main()
