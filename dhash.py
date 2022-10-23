"""Calculate difference hash (perceptual hash) for a given image, useful for detecting duplicates.

For example usage, see README.rst.

This code is licensed under a permissive MIT license -- see LICENSE.txt.

The dhash project lives on GitHub here:
https://github.com/benhoyt/dhash
"""

from __future__ import division

import sys

# Allow library to be imported even if neither wand or PIL are installed
try:
    import wand.image
    import wand.color
except ImportError:
    wand = None

try:
    import PIL.Image
    try:
        _resample = PIL.Image.Resampling.LANCZOS
    except AttributeError:
        _resample = PIL.Image.ANTIALIAS
except ImportError:
    PIL = None


__version__ = '1.4'

IS_PY3 = sys.version_info.major >= 3


def _get_grays_pil(image, width, height, fill_color='white'):
    if image.mode in ('RGBA', 'LA') and fill_color is not None:
        cleaned = PIL.Image.new(image.mode[:-1], image.size, fill_color)
        cleaned.paste(image, image.split()[-1])
        image = cleaned

    image = image.convert('L')
    image = image.resize((width, height), _resample)

    return list(image.getdata())


def _get_grays_wand(image, width, height, fill_color='white'):
    # we don't want to mutate the caller's image
    with image.clone() as clone:
        if clone.alpha_channel and fill_color is not None:
            clone.background_color = wand.color.Color(fill_color)
            clone.alpha_channel = 'background'

        clone.resize(width, height)

        blob = clone.make_blob(format='GRAY')

    if IS_PY3:
        return list(blob)

    return [ord(c) for c in blob]


def get_grays(image, width, height, fill_color='white'):
    """Convert image to grayscale, downsize to width*height, and return list
    of grayscale integer pixel values (for example, 0 to 255).

    >>> get_grays([0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9], 5, 5)
    [0, 0, 1, 1, 1, 0, 1, 1, 3, 4, 0, 1, 6, 6, 7, 7, 7, 7, 7, 9, 8, 7, 7, 8, 9]
    """
    if isinstance(image, (tuple, list)):
        if len(image) != width * height:
            raise ValueError(
                'image sequence length ({}) not equal to width*height ({})'.format(
                    len(image), width * height))
        return image

    if wand is None and PIL is None:
        raise ImportError('must have wand or Pillow/PIL installed to use dhash on images')

    if wand is not None and isinstance(image, wand.image.Image):
        return _get_grays_wand(image, width, height, fill_color)
    elif PIL is not None and isinstance(image, PIL.Image.Image):
        return _get_grays_pil(image, width, height, fill_color)
    else:
        raise ValueError('image must be a wand.image.Image or PIL.Image instance')


def dhash_row_col(image, size=8):
    """Calculate row and column difference hash for given image and return
    hashes as (row_hash, col_hash) where each value is a size*size bit
    integer.

    >>> image = [0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9]
    >>> row, col = dhash_row_col(image, 4)
    >>> format(row, '016b')
    '0100101111010001'
    >>> format(col, '016b')
    '0101001111111001'
    """
    width = size + 1
    grays = get_grays(image, width, width)

    row_hash = 0
    col_hash = 0
    for y in range(size):
        for x in range(size):
            offset = y * width + x
            row_bit = grays[offset] < grays[offset + 1]
            row_hash = row_hash << 1 | row_bit

            col_bit = grays[offset] < grays[offset + width]
            col_hash = col_hash << 1 | col_bit

    return (row_hash, col_hash)


def dhash_int(image, size=8):
    """Calculate row and column difference hash for given image and return
    hashes combined as a single 2*size*size bit integer (row_hash in most
    significant bits, col_hash in least).

    >>> image = [0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9]
    >>> dhash_int(image, size=4)
    1272009721
    """
    row_hash, col_hash = dhash_row_col(image, size=size)
    return row_hash << (size * size) | col_hash


def get_num_bits_different(hash1, hash2):
    """Calculate number of bits different between two hashes.

    >>> get_num_bits_different(0x4bd1, 0x4bd1)
    0
    >>> get_num_bits_different(0x4bd1, 0x5bd2)
    3
    >>> get_num_bits_different(0x0000, 0xffff)
    16
    """
    return bin(hash1 ^ hash2).count('1')


def format_bytes(row_hash, col_hash, size=8):
    """Format dhash integers as binary string of size*size//8 bytes (row_hash
    and col_hash concatenated, big endian).

    >>> hash_bytes = format_bytes(19409, 14959, size=4)
    >>> type(hash_bytes) is bytes
    True
    >>> [hex(b) for b in hash_bytes] if IS_PY3 else [hex(ord(b)) for b in hash_bytes]
    ['0x4b', '0xd1', '0x3a', '0x6f']

    >>> hash_bytes = format_bytes(1, 2, size=4)
    >>> type(hash_bytes) is bytes
    True
    >>> [hex(b) for b in hash_bytes] if IS_PY3 else [hex(ord(b)) for b in hash_bytes]
    ['0x0', '0x1', '0x0', '0x2']
    """
    bits_per_hash = size * size
    full_hash = row_hash << bits_per_hash | col_hash
    if IS_PY3:
        return full_hash.to_bytes(bits_per_hash // 4, 'big')
    else:
        return '{0:0{1}x}'.format(full_hash, bits_per_hash // 2).decode('hex')


def format_hex(row_hash, col_hash, size=8):
    """Format dhash integers as hex string of size*size//2 total hex digits
    (row_hash and col_hash concatenated).

    >>> format_hex(19409, 14959, size=4)
    '4bd13a6f'
    >>> format_hex(1, 2, size=4)
    '00010002'
    """
    hex_length = size * size // 4
    return '{0:0{2}x}{1:0{2}x}'.format(row_hash, col_hash, hex_length)


def format_matrix(hash_int, bits='01', size=8):
    """Format dhash integer as matrix of bits.

    >>> row, col = dhash_row_col([0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9], size=4)
    >>> print(format_matrix(row, bits='.*', size=4))
    .*..
    *.**
    **.*
    ...*
    >>> print(format_matrix(col, size=4))
    0101
    0011
    1111
    1001
    """
    output = '{:0{}b}'.format(hash_int, size * size)
    if IS_PY3:
        output = output.translate({ord('0'): bits[0], ord('1'): bits[1]})
    else:
        output = unicode(output).translate({ord('0'): unicode(bits[0]), ord('1'): unicode(bits[1])})
        output = type(bits[0])(output)
    width = size * len(bits[0])
    lines = [output[i:i + width] for i in range(0, size * width, width)]
    return '\n'.join(lines)


def format_grays(grays, size=8):
    r"""Format grays list as matrix of gray values.

    >>> image = [0,0,1,1,1, 0,1,1,3,4, 0,1,6,6,7, 7,7,7,7,9, 8,7,7,8,9]
    >>> out = format_grays(image, size=4)
    >>> print('\n'.join(line.strip() for line in out.splitlines()))
    0   0   1   1   1
    0   1   1   3   4
    0   1   6   6   7
    7   7   7   7   9
    8   7   7   8   9
    """
    width = size + 1
    lines = []
    for y in range(width):
        line = []
        for x in range(width):
            gray = grays[y * width + x]
            line.append(format(gray, '4'))
        lines.append(''.join(line))
    return '\n'.join(lines)


def force_pil():
    """If both wand and Pillow/PIL are installed, force the use of Pillow/PIL."""
    global wand
    if PIL is None:
        raise ValueError('Pillow/PIL library must be installed to use force_pil()')
    wand = None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--size', type=int, default=8,
                        help='width and height of dhash image size, default %(default)d')
    parser.add_argument('-f', '--format', default='hex', choices=['hex', 'decimal', 'matrix', 'grays'],
                        help='hash output format, default %(default)s')
    parser.add_argument('-p', '--pil', action='store_true',
                        help='if both wand and Pillow/PIL installed, force use of Pillow/PIL')
    parser.add_argument('filename', nargs='*',
                        help='name of image file to hash (or two to calculate the delta)')
    args = parser.parse_args()

    if args.pil:
        try:
            force_pil()
        except ValueError:
            sys.stderr.write('You must have Pillow/PIL installed to use --pil\n')
            sys.exit(1)

    def load_image(filename):
        if wand is not None:
            return wand.image.Image(filename=filename)
        elif PIL is not None:
            return PIL.Image.open(filename)
        else:
            sys.stderr.write('You must have wand or Pillow/PIL installed to use the dhash command\n')
            sys.exit(1)

    if len(args.filename) == 0:
        # NOTE: doctests require "wand" to be installed
        import doctest
        failure_count, _ = doctest.testmod()
        if failure_count:
            sys.exit(1)

    elif len(args.filename) == 1:
        image = load_image(args.filename[0])
        if args.format == 'grays':
            grays = get_grays(image, args.size + 1, args.size + 1)
            print(format_grays(grays, size=args.size))
        else:
            row_hash, col_hash = dhash_row_col(image, size=args.size)
            if args.format == 'hex':
                print(format_hex(row_hash, col_hash, size=args.size))
            elif args.format == 'decimal':
                print(row_hash, col_hash)
            else:
                bits = ['. ', '* ']
                print(format_matrix(row_hash, bits=bits, size=args.size))
                print()
                print(format_matrix(col_hash, bits=bits, size=args.size))

    elif len(args.filename) == 2:
        image1 = load_image(args.filename[0])
        image2 = load_image(args.filename[1])
        hash1 = dhash_int(image1, size=args.size)
        hash2 = dhash_int(image2, size=args.size)
        num_bits_different = get_num_bits_different(hash1, hash2)
        print('{} {} out of {} ({:.1f}%)'.format(
                num_bits_different,
                'bit differs' if num_bits_different == 1 else 'bits differ',
                args.size * args.size * 2,
                100 * num_bits_different / (args.size * args.size * 2)))

    else:
        parser.error('You must specify one or two filenames')
