dhash
=====

dhash is a Python library that generates a "difference hash" for a given image
-- a `perceptual hash`_ based on Neal Krawetz's dHash algorithm in `this
"Hacker Factor" blog entry`_.

The library is `on the Python Package Index (PyPI)`_, so to install it, fire
up a command prompt, activate your virtualenv if you're using one, and type:

::

    pip install graphyte

The algorithm to create a difference hash is very simple:

* Convert the image to grayscale
* Downsize it to a 9x9 thumbnail (size=8 means 8+1 by 8+1)
* Produce a 64-bit "row hash", with 1 meaning pixel intensity is increasing in
  the x direction, 0 meaning it's decreasing
* Do the same to produce a 64-bit "column hash" in the y direction
* Combine the two values to produce the final 128-bit hash value

The library defaults to producing a "size 8" dhash, but you can override this
easily, for example, to produce a more accurate (but slower to work with)
"size 16" dhash of 512 bits.

I've found that the dhash is great for detecting near duplicates (at Jetsetter
we find dupes using a size=8 dhash with a maximum delta of 2 bits), but
because of the simplicity of the algorithm, it's not great at finding similar
images or duplicate-but-cropped images -- you'd need a more sophisticated
image fingerprint if you want that. However, the dhash is good for finding
exact duplicates and near duplicates, for example, the same image with
slightly altered lighting, a few pixels of cropping, or very light
photoshopping.

To use the dhash library, you need either the `wand`_ ImageMagick binding or
the `Pillow (PIL)`_ library installed. Pick one and stick with it -- they will
produce slightly different dhash values due to differences in their grayscale
conversion and resizing algorithms.

To produce a dhash value using wand:

.. code:: python

    import dhash
    from wand.image import Image

    with Image(filename='test.jpg') as image:
        row, col = dhash.dhash_row_col(image)
    print(dhash.format_hex(row, col))

To produce a dhash value using Pillow:

.. code:: python

    import dhash
    from PIL import Image

    image = Image.open('test.jpg')
    row, col = dhash.dhash_row_col(image)
    print(dhash.format_hex(row, col))

If you have your own library to convert an image to grayscale and downsize it
to 9x9 (or 17x17 for size=16), you can pass `dhash_row_col()` a list of
integer pixel intensities (for example, from 0 to 255). For example:

.. code:: python

    >>> row, col = dhash_row_col([0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9], size=4)
    >>> format(row, '016b')
    '0100101111010001'
    >>> format(col, '016b')
    '0101001111111001'

You can also use dhash to generate the difference hash for a specific image
from the command line:

::

    python -m dhash TODO

There are command line arguments to format the output in various ways, and to
produce the bit delta (hamming distance) between two images. Type
``python -m dhash --help`` for help.

Read the code in `dhash.py`_ for more details – it's pretty small!

dhash was written by `Ben Hoyt`_ for `Jetsetter`_ and is licensed with a
permissive MIT license (see `LICENSE.txt`_).


.. _perceptual hash: https://en.wikipedia.org/wiki/Perceptual_hashing
.. _on the Python Package Index (PyPI): https://pypi.python.org/pypi/dhash
.. _this "Hacker Factor" blog entry: http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
.. _wand: https://pypi.python.org/pypi/Wand
.. _Pillow (PIL): https://pypi.python.org/pypi/Pillow
.. _dhash.py: https://github.com/Jetsetter/dhash/blob/master/dhash.py
.. _Ben Hoyt: http://benhoyt.com/
.. _Jetsetter: http://www.jetsetter.com/
.. _LICENSE.txt: https://github.com/Jetsetter/dhash/blob/master/LICENSE.txt
