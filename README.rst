dhash
=====

.. image:: https://img.shields.io/pypi/v/dhash.svg
   :target: https://pypi.org/project/dhash/
   :alt: dhash on PyPI (Python Package Index)

.. image:: https://github.com/benhoyt/dhash/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/benhoyt/dhash/actions/workflows/ci.yml
   :alt: GitHub Actions Tests

dhash is a Python library that generates a "difference hash" for a given image
-- a `perceptual hash`_ based on Neal Krawetz's dHash algorithm in `this
"Hacker Factor" blog entry`_.

The library is `on the Python Package Index (PyPI)`_ and works on both Python
3 and Python 2.7. To install it, fire up a command prompt, activate your
virtual environment if you're using one, and type:

::

    pip install dhash

The algorithm to create a difference hash is very simple:

* Convert the image to grayscale
* Downsize it to a 9x9 thumbnail (size=8 means an 8+1 by 8+1 image)
* Produce a 64-bit "row hash": a 1 bit means the pixel intensity is increasing
  in the x direction, 0 means it's decreasing
* Do the same to produce a 64-bit "column hash" in the y direction
* Combine the two values to produce the final 128-bit hash value

The library defaults to producing a size 8 dhash, but you can override this
easily by passing ``size=N`` as a keyword argument to most functions. For
example, you can produce a more accurate (but slower to work with) dhash of
512 bits by specifying ``size=16``.

I've found that dhash is great for detecting near duplicates (we
found dupes using a size 8 dhash with a maximum delta of 2
bits). But because of the simplicity of the algorithm, it's not great at
finding similar images or duplicate-but-cropped images -- you'd need a more
sophisticated image fingerprint if you want that. However, the dhash is good
for finding exact duplicates and near duplicates, for example, the same image
with slightly altered lighting, a few pixels of cropping, or very light
photoshopping.

To use the dhash library, you need either the `wand`_ ImageMagick binding or
the `Pillow (PIL)`_ library installed. Pick one and stick with it -- they will
produce slightly different dhash values due to differences in their grayscale
conversion and resizing algorithms.

If you have both libraries installed, dhash will use wand by default. To
override this and force use of Pillow/PIL, call ``dhash.force_pil()`` before
using the library.

To produce a dhash value using wand:

.. code:: python

    import dhash
    from wand.image import Image

    with Image(filename='dhash-test.jpg') as image:
        row, col = dhash.dhash_row_col(image)
    print(dhash.format_hex(row, col))

To produce a dhash value using Pillow:

.. code:: python

    import dhash
    from PIL import Image

    image = Image.open('dhash-test.jpg')
    row, col = dhash.dhash_row_col(image)
    print(dhash.format_hex(row, col))

If you have your own library to convert an image to grayscale and downsize it
to 9x9 (or 17x17 for size=16), you can pass ``dhash_row_col()`` a list of
integer pixel intensities (for example, from 0 to 255). For example:

.. code:: python

    >>> import dhash
    >>> row, col = dhash.dhash_row_col([0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9], size=4)
    >>> format(row, '016b')
    '0100101111010001'
    >>> format(col, '016b')
    '0101001111111001'

To produce the hash value as a 128-bit integer directly, use
``dhash_int(image, size=N)``. To format the hash value in various ways, use
the ``format_*`` functions:

.. code:: python

    >>> row, col = (13962536140006260880, 9510476289765573406)
    >>> dhash.format_bytes(row, col)
    b'\xc1\xc4\xe4\xa4\x84\xa0\x80\x90\x83\xfb\xff\xcc\x00@\x83\x1e'
    >>> dhash.format_hex(row, col)
    'c1c4e4a484a0809083fbffcc0040831e'

To compute the number of bits different (hamming distance) between two
hashes, you can use the ``get_num_bits_different(hash1, hash2)`` helper
function:

.. code:: python

    >>> import dhash
    >>> dhash.get_num_bits_different(0x4bd1, 0x5bd2)
    3

You can also use dhash to generate the difference hash for a specific image
from the command line:

::

    $ python -m dhash dhash-test.jpg
    c1c4e4a484a0809083fbffcc0040831e

    $ python -m dhash --format=decimal dhash-test.jpg
    13962536140006260880 9510476289765573406

    # show the 8x8 row and column grids
    $ python -m dhash --format=matrix dhash-test.jpg
    * * . . . . . * 
    * * . . . * . . 
    * * * . . * . . 
    * . * . . * . . 
    * . . . . * . . 
    * . * . . . . . 
    * . . . . . . . 
    * . . * . . . . 

    * . . . . . * * 
    * * * * * . * * 
    * * * * * * * * 
    * * . . * * . . 
    . . . . . . . . 
    . * . . . . . . 
    * . . . . . * * 
    . . . * * * * . 

    # compute the bit delta between two images
    $ python -m dhash dhash-test.jpg similar.jpg
    1 bit differs out of 128 (0.8%)

Read the code in `dhash.py`_ for more details – it's pretty small!

dhash was written by `Ben Hoyt`_ and is licensed with a
permissive MIT license (see `LICENSE.txt`_).


.. _perceptual hash: https://en.wikipedia.org/wiki/Perceptual_hashing
.. _on the Python Package Index (PyPI): https://pypi.python.org/pypi/dhash
.. _this "Hacker Factor" blog entry: http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
.. _wand: https://pypi.python.org/pypi/Wand
.. _Pillow (PIL): https://pypi.python.org/pypi/Pillow
.. _dhash.py: https://github.com/benhoyt/dhash/blob/master/dhash.py
.. _Ben Hoyt: http://benhoyt.com/
.. _LICENSE.txt: https://github.com/benhoyt/dhash/blob/master/LICENSE.txt
