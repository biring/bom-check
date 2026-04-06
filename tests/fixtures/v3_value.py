"""
Typed fixtures for row and header field values used by BOM validators.

Provides reusable GOOD_/BAD_ lists for each field (model number, board name, stages, quantities, designators, etc.) aligned with the project’s centralized regex rules.

Example Usage:
    # Preferred within tests:
    from tests.fixtures import v3_value as fx
    assert "AB123" in fx.MODEL_NO_GOOD

    # Running the test suite (project root):
    python -m unittest discover -s tests

Dependencies:
    - Python >= 3.10
    - Standard Library: typing
    - Project: src.approve._constants (validation patterns and rule text)

Notes:
    - Lists are typed with Final[list[str]] and must not be mutated in tests.
    - Keep cases synchronized with src.approve._constants patterns and rule strings to prevent brittle tests.
    - Include both typical and boundary examples; prefer minimal strings that isolate each rule.
    - Values intentionally avoid locale/formatting pitfalls (e.g., commas in numbers) unless testing rejection.

License:
    - Internal Use Only
"""

from typing import Final

MODEL_NO_GOOD: Final[list[str]] = [
    "AB100",  # 2 letters + 3 digits
    "AB123EU",  # 2 letters + 3 digits + 2 trailing letters
    "ABC1234",  # 3 letters + 4 digits
    "AB123X",  # 2 letters + 3 digits + 1 trailing letter
    "ABC100ZZ",  # 3 letters + 3 digits + 2 trailing letters
    "AB123",  # 2 letters + 3 digits, no trailing letters
]
MODEL_NO_BAD: Final[list[str]] = [
    "100",  # does not start with 2–3 capital letters
    "123AB",  # starts with digits, not letters
    "AB",  # only 2 letters, missing digits
    "123",  # no leading letters
    "A_123",  # contains underscore, only A–Z allowed
    "AB-123",  # contains hyphen, not allowed
    "",  # empty string
    "   ",  # spaces only
    "X9Y",  # only 1 digit, needs 3–4
    "Model42X",  # lowercase letters not allowed
    "A1",  # 1 letter + 1 digit, too short
    "abc123xyz",  # lowercase letters, not allowed
]

BOARD_NAME_GOOD: Final[list[str]] = [
    "Power PCBA",  # starts with letter, ends with PCBA
    "Control PCBA",  # valid middle content, correct suffix
    "Brushless motor main PCBA",  # spaces and words allowed
    "Main board 2 PCBA",  # digits allowed in middle, valid ending
    "A PCBA",  # single letter prefix, ends correctly
]
BOARD_NAME_BAD: Final[list[str]] = [
    "Power",  # missing required 'PCBA' suffix
    "1Control PCBA",  # starts with digit, must start with letter
    "Control pcbA",  # wrong case on suffix, must be exact 'PCBA'
    "Control-PCBA",  # hyphen not allowed, only letters/digits/spaces
    "Control",  # missing 'PCBA' suffix
    " Control PCBA",  # starts with space, must start with letter
    "Power PCB left",  # does not end with 'PCBA'
    "",  # empty string
    "   ",  # spaces only
]

BOARD_SUPPLIER_GOOD: Final[list[str]] = [
    "ABC",  # 3 uppercase letters
    "Ab1",  # capital + lowercase + digit
    "Intel123",  # starts with capital, letters + digits
    "X9Y",  # capital + digit + letter
    "Sony 2025",  # contains space, valid format
    "General Electric",  # multiple words with spaces
    "Bosch Ltd",  # capitalized with space
    "A B C",  # multiple single-letter words, valid length
]
BOARD_SUPPLIER_BAD: Final[list[str]] = [
    "abc",  # starts with lowercase
    "12AB",  # starts with digit
    "AB",  # only 2 characters, too short
    "A1",  # only 2 characters, too short
    "-ABC",  # starts with non-letter
    " ab1",  # starts with space
    "",  # empty string
    "A_",  # contains underscore, not allowed
    "Bosch-Group",  # hyphen not allowed
    "Panasonic!",  # exclamation mark not allowed
]

BUILD_STAGE_GOOD: Final[list[str]] = [
    "P1",  # Pn form
    "P10.5",  # Pn.n form
    "EB2",  # EBn form
    "EB12.3",  # EBn.n form
    "MB",  # MB exact
    "MP",  # MP exact
    "FOT",  # FOT exact
    "TRA", # TRA exact
    "ECN",  # ECN with no digits (allowed)
    "ECN1",  # ECN with digits
    "ECN123",  # ECN with multiple digits
]
BUILD_STAGE_BAD: Final[list[str]] = [
    "P",  # missing digits
    "EB",  # missing digits
    "P1.",  # trailing dot without digits
    "EB2.",  # trailing dot without digits
    "ECN.1",  # dot not allowed after ECN
    "ecn1",  # lowercase not allowed
    "MP1",  # MP must be exact
    "MB2",  # MB must be exact
    "FOT1",  # FOT must be exact
    "TRA1", # TRA must be exact
    "",  # empty string
    " ",  # whitespace only
    "PX1",  # invalid prefix
]

BOM_DATE_GOOD: Final[list[str]] = [
    "2025-08-06",  # YYYY-MM-DD (zero-padded)
    "2025-8-6",  # YYYY-M-D (non-zero-padded)
    "06/08/2025",  # DD/MM/YYYY (zero-padded)
    "6/8/2025",  # D/M/YYYY (non-zero-padded)
    "08/06/2025",  # MM/DD/YYYY (zero-padded)
    "8/6/2025",  # M/D/YYYY (non-zero-padded)
    "2025-08-06T12:30",  # date + time w/ 'T'
    "2025-08-06 09:15",  # date + time w/ space
]
BOM_DATE_BAD: Final[list[str]] = [
    "2025.01.01",  # dots not allowed
    "2025/08/06",  # wrong separator for YYYY-MM-DD
    "06-08-2025",  # wrong separator for DD/MM/YYYY
    "2025-13-01",  # invalid month
    "2025-00-10",  # invalid month
    "2025-02-30",  # invalid day
    "not-a-date",  # junk
    "",  # empty
    "   ",  # whitespace only
]

COST_GOOD: Final[list[str]] = [
    "0",  # integer zero
    "0.00",  # zero with decimals
    "0.12",  # cents precision
    "12.5",  # single decimal
    "100",  # whole number
    "100.0",  # trailing .0 accepted
    ".5",  # leading decimal without integer
    "12.",  # trailing dot
]
COST_BAD: Final[list[str]] = [
    "-1",  # negative integer
    "-0.01",  # negative decimal
    ".",  # just a dot, no digits
    "abc",  # non-numeric
    "",  # empty string
    " ",  # whitespace only
    "1,000",  # comma not allowed
    "12.34.56",  # multiple decimals invalid
]

ITEM_GOOD: Final[list[str]] = [
    "",  # empty string
    "1",  # smallest positive integer
    "45",  # standard positive integer
    "9999",  # large positive integer
]
ITEM_BAD: Final[list[str]] = [
    "0",  # zero not allowed (not positive)
    "012",  # leading zero not allowed
    "-5",  # negative not allowed
    "3.14",  # decimal not allowed
    "abc",  # letters not allowed
    "   ",  # whitespace not allowed
]

COMP_TYPE_GOOD: Final[list[str]] = [
    "Fuse",  # simple alphabetic word
    "BJT",  # all caps letters
    "Battery Terminal",  # two words with space
    "Diode/SCR",  # with '/'
    "ALT",  # keyword only
    "ALT1",  # keyword + digit
    "ALT23",  # keyword + multiple digits
]
COMP_TYPE_BAD: Final[list[str]] = [
    "",  # empty string not allowed
    "123",  # digits only
    "ALTXYZ",  # ALT must be digits only
    "Fuse@",  # invalid char '@'
    "Battery-Terminal",  # hyphen not allowed
    " Diode",  # leading space not allowed
    "SCR ",  # trailing space not allowed
    "Diode//SCR",  # double '/' not allowed
    "ALT 1",  # space between ALT and digit not allowed
]

DEVICE_PACKAGE_GOOD: Final[list[str]] = [
    "",  # empty string allowed
    "0603",  # digits only
    "SMA",  # alphabets only
    "QFN32",  # letters + numbers, no dash
    "QFN-32",  # with dash
    "BGA-256-X",  # multiple dashes
    "10x12mm",  # dimensions using 'x'
    "10.9x12.8mm",  # dimensions with decimal points
    "P=15mm,L=3.5mm",  # key=value pairs with comma and decimals
]
DEVICE_PACKAGE_BAD: Final[list[str]] = [
    "X",  # single character not allowed
    "\\",  # symbol not allowed
    "QFN 32",  # space not allowed
    "-QFN32",  # cannot start with dash
    "QFN32-",  # cannot end with dash
    "QFN--32",  # consecutive dashes not allowed
    "QFN@32",  # special chars not allowed
    "QFN_32",  # underscore not allowed
]

DESCRIPTION_GOOD: Final[list[str]] = [
    "1k,1%,0.5W",  # alphanumeric + commas + percent
    "1uF,10%,50V",  # unit + tolerance + voltage
    "Rectifier,1A,50V",  # word + ratings
    "MOSFET,N-CH,30V,10A",  # multiple segments
    "IC,3.3V,100mA",  # includes dot and uppercase letters
]
DESCRIPTION_BAD: Final[list[str]] = [
    "",  # empty string not allowed
    "1k, 1%, 0.5W",  # space between values
    " 1uF,10%,50V",  # leading whitespace
    "1uF,10%,50V ",  # trailing whitespace
    "IC,\t3.3V,100mA",  # tab is whitespace
    "Rectifier,\n1A,50V",  # newline is whitespace
]

UNITS_GOOD: Final[list[str]] = [
    "",  # empty string allowed
    "PCS",  # all uppercase letters
    "Each",  # standard word
    "grams",  # lowercase letters
    "lb.",  # optional trailing dot
]
UNITS_BAD: Final[list[str]] = [
    "123",  # digits not allowed
    "g2",  # mix letters + digits not allowed
    "g.ram",  # dot only allowed at the end
    "PCS ",  # trailing space not allowed
    " Each",  # leading space not allowed
    "kg!",  # special character not allowed
]

CLASSIFICATION_GOOD: Final[list[str]] = [
    "A", "B", "C",
]
CLASSIFICATION_BAD: Final[list[str]] = [
    "",  # not allowed (must have one char)
    "a",  # lowercase not allowed
    "b",  # lowercase not allowed
    "c",  # lowercase not allowed
    "AB",  # more than one character
    "1",  # digit not allowed
    "#",  # special char not allowed
]

MFG_NAME_GOOD: Final[list[str]] = [
    "ST Microelectronics",  # letters + space
    "Delta Pvt. Ltd",  # with dot
    "Hewlett-Packard",  # with dash
    "Procter & Gamble",  # with ampersand
    "3M",  # digits + letters
    "TI-89",  # mix digits + dash + letters
]
MFG_NAME_BAD: Final[list[str]] = [
    "",  # cannot be empty
    " STMicro",  # cannot start with space
    "Intel ",  # cannot end with space
    "Nokia@",  # invalid symbol '@'
    "Micro_chip",  # underscore not allowed
]

MFG_PART_NO_GOOD: Final[list[str]] = [
    "LM358N",  # simple alphanumeric
    "SN74HC595N-TR",  # with dash
    "AT328P_U",  # with underscore
    "ADXL345.B",  # with dot
    "XC7Z010-1CLG400C",  # complex part number
    "BC547B",  # letters + digits
]
MFG_PART_NO_BAD: Final[list[str]] = [
    "",  # must not be empty
    "AT 328P",  # whitespace not allowed
    " LM358N",  # leading space
    "BC547B ",  # trailing space
    "Part*123",  # '*' not allowed
    "SN74HC595N@TR",  # '@' not allowed
    "LM358#N",  # '#' not allowed
]

UL_VDE_NO_GOOD: Final[list[str]] = [
    "",  # not allowed
    "E1234",  # 1 letter + digits
    "UL 567890",  # 2 letters + space + digits
    "VDE-12345678",  # 3 letters + dash + 8 digits
    "ULVD123",  # 4 letters + digits
    "UL12345678",  # 2 letters + 8 digits, no separator
]

UL_VDE_NO_BAD: Final[list[str]] = [
    "12345",  # must start with letters
    "ULVD",  # missing digits
    "ABCDE1234",  # >4 letters not allowed
    "UL123456789",  # >8 digits not allowed
    "UL--1234",  # only one separator allowed
    "UL_1234",  # underscore not allowed
    "UL- 1234",  # mixed separators not allowed
    " UL1234",  # cannot start with space
]

# GOOD validated-at strings (they satisfy the regex)
VALIDATED_AT_GOOD: Final[list[str]] = [
    "",  # empty allowed
    "P1",
    "P0",
    "P12.3",
    "EB0",
    "EB10.25",
    "ECN",
    "ECN123",
    "MB",
    "MP",
    "FOT",
    "P1/EB0/MP",
    "P2,ECN5,MB",
    "P10/EB2.1,ECN,MP/FOT",
    "P3.2,EB1/P0,ECN,MB/FOT",
]

# BAD validated-at strings
VALIDATED_AT_BAD: Final[list[str]] = [
    "/",  # only forward slash not allowed
    "P1 / EB0",  # whitespace not allowed
    "/P1",  # cannot start with separator
    "P1/",  # cannot end with separator
    "P1//EB0",  # consecutive separators not allowed
    "P1,,EB0",  # consecutive separators not allowed
    "P1,/EB0",  # empty token between separators
    "P1.EB0",  # '.' is not a valid separator
    "P",  # P must be followed by digits
    "P.1",  # must be digits then optional .digits
    "P1.2.3",  # only one optional decimal part
    "EB",  # EB must be followed by digits
    "EB1.",  # trailing dot not allowed
    "ECN-1",  # only digits allowed after ECN
    "ECN.1",  # dot not allowed after ECN
    "p1,eb0,ecn",  # tokens are case-sensitive
    "MB1",  # MB must be exact
    "MP0",  # MP must be exact
    "FOT1",  # FOT must be exact
    "PX1",  # invalid prefix
    "P1\tEB0",  # any whitespace is invalid
]

QUANTITY_GOOD: Final[list[str]] = [
    "0",  # smallest valid
    "2",  # simple integer
    "123",  # larger integer
    "0.34",  # decimal less than 1
    "10.5",  # decimal greater than 1
    "2500.125",  # long decimal
]
QUANTITY_BAD: Final[list[str]] = [
    "",  # must not be empty
    "-1",  # negatives not allowed
    "01",  # no leading zeros (except '0')
    ".",  # dot alone not allowed
    "5.",  # must have digits after dot
    ".25",  # must have leading digits
    "12A",  # letters not allowed
    "1 2",  # spaces not allowed
    "3 ",  # trailing space not allowed
]

DESIGNATOR_GOOD: Final[list[str]] = [
    "",  # allowed empty
    "R1",  # 1 letter + digit
    "ACL123",  # up to 5 letters + digits
    "ACL+",  # letters + '+'
    "V-",  # letters + '-'
    "ACN",  # letters only
    "ABCDE12345",  # 5 letters + 5 digits
    "R1,C2",  # two valid tokens with digits
    "R1,C1,M+",  # digits + digits + plus
    "U10,MT6,T-,Q500",  # mix of digits and signs
    "R1,ACN,C2",  # list with letters only
]
DESIGNATOR_BAD: Final[list[str]] = [
    "123",  # must start with letters
    "ABCDEF1",  # >5 letters
    "R123456",  # >5 digits
    "R1+",  # cannot have both digits and '+'
    "C2-",  # cannot have both digits and '-'
    "R++",  # only single '+' or '-' allowed
    "R1#",  # special chars not allowed
    " R1",  # leading space not allowed
    "C3 ",  # trailing space not allowed
    "R1,,C2",  # double comma → empty token
    "R1, C2",  # spaces not allowed unless regex updated
]

PRICE_GOOD: Final[list[str]] = [
    "0",  # smallest valid
    "2",  # simple integer
    "123",  # larger integer
    "0.34",  # decimal < 1
    "10.5",  # decimal > 1
    "2500.125",  # multi-digit decimal
]
PRICE_BAD: Final[list[str]] = [
    "",  # must not be empty
    "-1",  # negatives not allowed
    "01",  # no leading zeros (except '0')
    ".",  # dot alone not allowed
    "5.",  # must have digits after dot
    ".25",  # must have leading digits
    "12A",  # letters not allowed
    "1 2",  # spaces not allowed
    "3 ",  # trailing space not allowed
]
