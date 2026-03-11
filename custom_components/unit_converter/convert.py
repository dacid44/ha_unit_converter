from fractions import Fraction

from pint import DimensionalityError, Quantity, UndefinedUnitError, Unit, UnitRegistry
from text_to_num import alpha2digit
from num2words import num2words

MAX_FLOAT_DIGITS = 4
MAX_DENOMINATOR = 32
MAX_DENOMINATOR_EPSILON = 10**-MAX_FLOAT_DIGITS

PRE_REPLACEMENTS = {
    "-": " ",
    "\u00bc": "1/4",
    "\u00bd": "1/2",
    "\u00be": "3/4",
    "\u2044": "/",
    "quarter": "fourth",
}

IGNORED_WORDS = ("of",)

REPLACEMENTS = (
    {
        "a": 1,
        "an": 1,
        "half": Fraction(1, 2),
        "halfs": Fraction(1, 2),
        "halves": Fraction(1, 2),
    }
    | {
        num2words(i, to="ordinal_num"): Fraction(1, i)
        for i in range(3, MAX_DENOMINATOR + 1)
    }
    | {
        num2words(i, to="ordinal_num") + "s": Fraction(1, i)
        for i in range(3, MAX_DENOMINATOR + 1)
    }
)

VOWELS = ("a", "e", "i", "o", "u")

ureg = UnitRegistry()


def convert_units(input: str, target: str) -> str:
    quantity = parse_input(input)
    try:
        target_unit = ureg(target.replace(" ", "_")).units
    except UndefinedUnitError as e:
        raise ConvertException(error_message_from_unknown_units(e.unit_names))

    result = try_convert(quantity, target_unit)

    return f"{format_quantity(quantity)} is {format_quantity(result)}"


def how_many(smaller: str, larger: str) -> str:
    try:
        smaller_unit = ureg(smaller.replace(" ", "_")).units
    except UndefinedUnitError as e:
        raise ConvertException(error_message_from_unknown_units(e.unit_names))
    try:
        larger_unit = ureg(larger.replace(" ", "_")).units
    except UndefinedUnitError as e:
        raise ConvertException(error_message_from_unknown_units(e.unit_names))

    result = format_quantity(try_convert(1 * larger_unit, smaller_unit))
    larger_unit_name = str(larger_unit).replace("_", " ")
    if larger_unit_name[0] in VOWELS:
        return f"there are {result} in an {larger_unit_name}"
    else:
        return f"there are {result} in a {larger_unit_name}"


def parse_input(input: str) -> Quantity:
    input = input.strip()
    for s, replacement in PRE_REPLACEMENTS.items():
        input = input.replace(s, replacement)
    parts = [
        part
        for part in alpha2digit(input, "en", 0).split()
        if part not in IGNORED_WORDS
    ]

    if len(parts) == 0:
        raise ConvertException("I could not find any useful input.")

    new_parts = []
    for i in range(len(parts)):
        part = parts[i]
        if "/" in part:
            numerator, denominator = part.split("/")
            new_parts.append(int(numerator))
            new_parts.append(Fraction(1, int(denominator)))
            continue
        if part in REPLACEMENTS:
            new_parts.append(REPLACEMENTS[part])
            continue
        try:
            new_parts.append(Fraction(part))
        except ValueError:
            new_parts.append(part)
    parts = new_parts

    i = len(parts) - 1
    while i >= 0 and isinstance(parts[i], str):
        i -= 1
    if i == -1:
        raise ConvertException("I could not find any numbers in the input")
    if i == len(parts):
        raise ConvertException("I could not find any units in the input")

    unit = "_".join(parts[i + 1 :])
    try:
        unit = ureg(unit).units
    except UndefinedUnitError as e:
        raise ConvertException(error_message_from_unknown_units(e.unit_names))

    parts = parts[: i + 1]
    no_match = tuple(
        part
        for part in parts
        if not (
            isinstance(part, int)
            or isinstance(part, float)
            or isinstance(part, Fraction)
            or part in ("and", "&", "point")
        )
    )
    if len(no_match) > 0:
        raise ConvertException(f"I don't understand {no_match[0]}")
    string_parts = tuple(i for i, part in enumerate(parts) if isinstance(part, str))
    if len(string_parts) != 0 and string_parts != (1,):
        raise ConvertException("I don't understand the input")

    match parts:
        case [whole, "and" | "&", fraction]:
            number = whole + fraction
        case [whole, "and" | "&", numerator, denominator] | [
            whole,
            (int() | float() | Fraction()) as numerator,
            denominator,
        ]:
            number = whole + (numerator * denominator)
        case [whole, "point", decimal]:
            if (
                isinstance(whole, float)
                or (isinstance(whole, Fraction) and whole.denominator != 1)
                or isinstance(decimal, float)
                or (isinstance(decimal, Fraction) and decimal.denominator != 1)
            ):
                raise ConvertException("I don't understand the input")
            number = float(f"{int(whole)}.{int(decimal)}")
        case [number]:
            pass
        case [numerator, (int() | float() | Fraction()) as denominator]:
            number = numerator * denominator
        case _:
            raise ConvertException("I don't understand the input")

    return number * unit


def format_quantity(quantity: Quantity) -> str:
    number = Fraction(quantity.magnitude)
    number_estimate = number.limit_denominator(MAX_DENOMINATOR)
    if abs(number - number_estimate) < MAX_DENOMINATOR_EPSILON:
        number = number_estimate

    if number.denominator == 1:
        magnitude = num2words(number.numerator)
    elif number.denominator > MAX_DENOMINATOR:
        magnitude = f"{round(float(number), MAX_FLOAT_DIGITS)}"
    else:
        fraction = number % 1
        whole = int(number - fraction)

        if whole == 0:
            magnitude = f"{num2words(fraction.numerator)} "
        elif fraction.numerator == 1:
            magnitude = f"{num2words(whole)} and a "
        else:
            magnitude = f"{num2words(whole)} and {num2words(fraction.numerator)} "

        if fraction.denominator == 2:
            magnitude += "half"
        else:
            magnitude += num2words(fraction.denominator, to="ordinal")

        if fraction.numerator > 1:
            magnitude += "s"

    unit = str(quantity.units).replace("_", " ")

    if number == 1:
        return f"{magnitude} {unit}"
    elif number < 1:
        if unit[0] in VOWELS:
            return f"{magnitude} of an {unit}"
        else:
            return f"{magnitude} of a {unit}"
    else:
        return f"{magnitude} {unit}s"


def try_convert(quantity: Quantity, to: Unit) -> Quantity:
    try:
        return quantity.to(to)
    except DimensionalityError as e:
        unit1 = str(e.units1).replace("_", " ")
        unit2 = str(e.units2).replace("_", " ")
        raise ConvertException(f"I can't convert {unit1}s to {unit2}s")


def error_message_from_unknown_units(unit_names: tuple[str, ...]) -> str:
    match unit_names:
        case []:
            return "I don't know that unit"
        case [unit]:
            return f"I don't know the unit {unit}"
        case units:
            return f"I don't know the units {', '.join(units)}"


class ConvertException(Exception):
    pass
