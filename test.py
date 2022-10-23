from unittest import TestCase
from io import BytesIO
from os import path

from PIL import Image as PilImage, ImageDraw as PilDraw
from wand.image import Image as WandImage

import dhash


IMGDIR = path.dirname(__file__)


def pil_to_wand(image, format='png'):
    with BytesIO() as fd:
        image.save(fd, format=format)
        fd.seek(0)
        return WandImage(file=fd)


class TestDHash(TestCase):
    def test_get_grays_pil(self):
        with PilImage.open(path.join(IMGDIR, 'dhash-test.jpg')) as image:
            self._test_get_grays(image, delta=1)

    def test_get_grays_wand(self):
        image = WandImage(filename=path.join(IMGDIR, 'dhash-test.jpg'))
        self._test_get_grays(image, delta=2)

    def _test_get_grays(self, image, delta):
        result = dhash.get_grays(image, 9, 9)[:18]

        expected = [
            93, 158, 210, 122, 93, 77, 74, 74, 77,
            95, 117, 122, 111, 92, 74, 81, 80, 77,
        ]  # fmt: skip

        self.assertEqual(len(result), len(expected))
        for r, e in zip(result, expected):
            self.assertAlmostEqual(r, e, delta=delta)

    def test_fill_transparency(self):
        "Ensure transparent colors in PIL Images are ignored in hashes"

        # greyscale image, completely white and also completely transparent
        im1 = PilImage.new('LA', (100, 100), (0xff, 0))

        im2 = im1.copy()
        # replace most of it with "transparent black"
        PilDraw.Draw(im2).rectangle((10, 10, 90, 90), (0, 0))

        # delta=n means difference <= n
        self.assertAlmostEqual(dhash.dhash_row_col(im1), dhash.dhash_row_col(im2), delta=1)

        # same with Wand version of images
        pm1, pm2 = pil_to_wand(im1), pil_to_wand(im2)
        self.assertAlmostEqual(dhash.dhash_row_col(pm1), dhash.dhash_row_col(pm2), delta=1)


if __name__ == '__main__':
    import unittest
    unittest.main()
