import pytest
import dhash
from PIL import Image
from subprocess import check_output


size_sample = list(range(4, 17))


@pytest.fixture
def test_filename():
    return "dhash-test.jpg"


@pytest.fixture
def pil_image(test_filename):
    img = Image.open(test_filename)
    return img


# TODO
# @pytest.fixture
# def wand_image():
#    ...


@pytest.fixture
def known_hash():
    """The known hex format size 8 of dhash-test.jpg"""
    dhash = "c1c4e4a484a0809083fbffcc0040831e"
    return dhash


@pytest.mark.parametrize("size", size_sample)
def test_get_grays(pil_image, size):
    """get_grays(...) should convert an image to grayscale, downsize, and give integer values"""

    # GIVEN a sample image
    img = pil_image

    # WHEN calling get_grays(...)
    result = dhash.get_grays(img, size, size)

    # THEN return a list of grayscale ints 0-255
    assert isinstance(result, list), "get_grays(...) should return a list"

    for item in result:
        assert isinstance(item, int), "each item in the get_grays(...) list should be an int"
        assert item >= 0 and item <= 255, "each item in the get_grays(...) list should be between 0 and 255"

    expected_len = size * size
    assert len(result) == expected_len, "get_grays(...) should have be the expected_len"


@pytest.mark.parametrize("size", size_sample)
def test_dhash_row_col(pil_image, size):
    """dhash_row_col(...) should convert image to grayscale, downsize, and produce ints which will later be combined"""

    # GIVEN a sample image
    img = pil_image

    # WHEN calling dhash_row_col(...)
    result = dhash.dhash_row_col(img, size=size)

    # THEN return a tuple of two ints
    assert isinstance(result, tuple), "dhash_row_col(...) should return a tuple"
    assert len(result) == 2, "the dhash_row_col(...) tuple should have len of 2"

    for item in result:
        assert isinstance(item, int), "each item in the dhash_row_col(...) tuple should be an int"


@pytest.mark.parametrize("size", size_sample)
def test_dhash_int(pil_image, size):
    """dhash_int(...) should calculate combined hash and output an integer"""

    # GIVEN a sample image
    img = pil_image

    # WHEN calling dhash_int(...)
    result = dhash.dhash_int(img, size=size)

    # THEN return an int
    assert isinstance(result, int), "dhash_int(...) should return an int"


@pytest.mark.parametrize("size", size_sample)
def test_format_grays(pil_image, size):
    """format_grays(...) should a matrix graph of the gray values"""

    # GIVEN grays from a sample image
    img = pil_image
    grays = dhash.get_grays(pil_image, size, size)

    # WHEN calling format_grays(...)
    result = dhash.format_grays(grays, size=size - 1)

    # THEN
    assert isinstance(result, str), "dhash.format_grays(...) should return a str"

    lines = result.split("\n")

    assert len(lines) == size, "the matrix should be the specified size"

    for line in lines:

        values_in_line = list(filter(lambda x: x != "", line.lstrip().rstrip().split(" ")))

        assert len(values_in_line) == size, "all lines (non-whitespace) should be the specified size"

        for value in values_in_line:
            assert int(value) >= 0 and int(value) <= 255, "each value should be between 0 and 255"


@pytest.mark.parametrize("size", list(filter(lambda x: x % 2 == 0, size_sample)))
def test_format_bytes(pil_image, size):
    """format_bytes(...) should return a hash in bytes format"""

    # NOTE: This test fails on odd numbers

    # GIVEN the row and col hash from an image
    img = pil_image
    row_hash, col_hash = dhash.dhash_row_col(img, size=size)

    # WHEN calling format_bytes(...)
    result = dhash.format_bytes(row_hash, col_hash, size=size)

    # THEN return bytes
    assert isinstance(result, bytes), "format_bytes(...) should return bytes"


@pytest.mark.parametrize("size", size_sample)
def test_format_hex(pil_image, size):
    """format_hex(...) should return a hash in hex format"""

    # GIVEN the row and col hash from an image
    img = pil_image
    row_hash, col_hash = dhash.dhash_row_col(img, size=size)

    # WHEN calling format_hex(...)
    result = dhash.format_hex(row_hash, col_hash, size=size)

    # THEN return a hex str
    assert isinstance(result, str), "format_hex(...) should return a str"

    hex_characters = "0123456789abcdef"
    chars_are_hex_chars = list(map(lambda x: x in hex_characters, result))
    assert all(chars_are_hex_chars), "all character should be between 0-9 and a-f"


@pytest.mark.parametrize("size", size_sample)
def test_format_matrix(pil_image, size):
    """format_matrix(...) should a matrix graph of the pixel comparison"""

    # GIVEN the row and col hash from an image
    img = pil_image
    row_hash, col_hash = dhash.dhash_row_col(img, size=size)

    # WHEN calling dhash.format_matrix(...) on the row and col hashes
    bits = [". ", "* "]
    row_result = dhash.format_matrix(row_hash, bits=bits, size=size)
    col_result = dhash.format_matrix(col_hash, bits=bits, size=size)

    # THEN
    for result in [row_result, col_result]:

        assert isinstance(result, str), "dhash.format_matrix(...) should return a str"

        lines = result.split("\n")
        bit_chars = "".join(set("".join(bits)))

        assert len(lines) == size, "the matrix should be the specified size"

        for line in lines:

            assert len(line.replace(" ", "")) == size, "all lines (non-whitespace) should the specified size"

            chars_are_bit_chars = list(map(lambda x: x in bit_chars, line))
            assert all(chars_are_bit_chars), "all chars should be bit chars"


@pytest.mark.parametrize("hash1,hash2,expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)])
def test_get_num_bits_different(hash1, hash2, expected):
    """get_num_bits_different(...) should perform binary XOR and count 1s"""

    # GIVEN mock hashes
    # WHEN calling get_num_bits_different(...)
    result = dhash.get_num_bits_different(hash1, hash2)

    # THEN produce the expected XOR result
    assert result == expected


def test_force_pil():
    """force_pil() should overide wand to None"""

    # GIVEN wand as something other than None
    dhash.wand = 1

    # WHEN calling force_pil()
    dhash.force_pil()

    # THEN change dhash.wand to None
    assert dhash.wand is None


def test_dhash(test_filename, known_hash):
    """dhash(...) should perform the default configuartion of dhash"""
    # GIVEN a sample image
    # WHEN performing the default dhash
    result = dhash.dhash(test_filename)

    # THEN return a hex str of the known hash
    assert isinstance(result, str), "dhash(...) should return a str"

    hex_characters = "0123456789abcdef"
    chars_are_hex_chars = list(map(lambda x: x in hex_characters, result))
    assert all(chars_are_hex_chars), "all character should be between 0-9 and a-f"

    assert result == known_hash, "The result should match the known hash"


def test_dhash_diff(test_filename):
    """dhash(...) should provide an int of difference between two images"""

    # GIVEN the same image
    filename = test_filename

    # WHEN performing dhash_diff(...)
    result = dhash.dhash_diff(filename, filename)

    # THEN return a diff of zero
    assert isinstance(result, int), "dhash_diff(...) should return an int"
    assert result == 0, "The result should be zero"

    # GIVEN two different images
    filename180 = "dhash-test-180.jpg"

    # WHEN performing dhash_diff()
    result = dhash.dhash_diff(filename, filename180)
    assert isinstance(result, int), "dhash_diff(...) should return an int"
    assert result > 10, "The result should be zero"


def test_cli(pil_image, test_filename, known_hash):
    """dhash cli should produce hex format hash from size 8"""

    # GIVEN command line input for
    # dhash on the test image, no size or format specified
    cmd = f"python -m dhash {test_filename}"

    # WHEN executing on command line
    result = check_output(cmd, shell=True).decode().rstrip()

    # THEN dash, default at size 8 and return hex_format
    assert result == known_hash, "stdout should match expected output"
