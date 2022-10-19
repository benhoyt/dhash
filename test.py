from unittest import TestCase

from io import BytesIO

import PIL.Image
import PIL.ImageDraw

import wand.image

from dhash import dhash_row_col


def pilToWand(image, format='png'):
    with BytesIO() as fd:
        image.save(fd, format=format)
        fd.seek(0)
        return wand.image.Image(file=fd)


class TestDHash(TestCase):
    def test_fill_transparency(self):
        "Ensure transparent colors in PIL Images are ignored in hashes"

        # greyscale image, completely white and also completely transparent
        im1 = PIL.Image.new('LA', (100, 100), (0xff, 0))

        im2 = im1.copy()
        # replace most of it with "transparent black"
        PIL.ImageDraw.Draw(im2).rectangle((10, 10, 90, 90), (0, 0))

        self.assertEqual(dhash_row_col(im1), dhash_row_col(im2))

        self.assertEqual(
            dhash_row_col(pilToWand(im1)),
            dhash_row_col(pilToWand(im2)))


if __name__ == '__main__':
    import unittest
    unittest.main()
