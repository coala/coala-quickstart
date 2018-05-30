import textwrap
from coala_quickstart.Strings import COALA_BEAR_LOGO, WELCOME_MESSAGES


def print_side_by_side(printer,
                       left=[],
                       right=[],
                       left_color='white',
                       right_color='blue',
                       limit=80):
    """
    Prints the the given lines side by side. Example usage:

    >>> from pyprint.ConsolePrinter import ConsolePrinter
    >>> printer = ConsolePrinter()
    >>> print_side_by_side(
    ...     printer,
    ...     ["Text content on the left",
    ...      "side of the text."],
    ...     ["Right side should contain",
    ...      "this."],
    ...     left_color=None,
    ...     right_color=None,
    ...     limit=80)
    Text content on the left Right side should contain
    side of the text.        this.

    If either side is longer than the other, empty lines will
    be added to the shorter side.

    :param printer:
        A ``ConsolePrinter`` object used for console interaction.
    :param left:
        The lines for the left portion of the text.
    :param right:
        The lines for the right portion of the text.
    :param left_color:
        The color to use for the left side of the text.
    :parm right_color:
        The color to use for the right side of the text.
    :param limit:
        The maximum line length limit.
    """
    max_left_length = len(max(left, key=len))

    for line in range(len(left) - len(right)):
        right.append('')
    for line in range(len(right) - len(left)):
        left.append('')

    for left_line, right_line in zip(left, right):
        printer.print(left_line, color=left_color, end='')
        printer.print(
            ' ' * (max_left_length - len(left_line) + 1),
            end='')
        printer.print(right_line, color=right_color)


def print_welcome_message(printer):
    """
    Prints the coala bear logo with a welcome message side by side.

    :param printer:
        A ``ConsolePrinter`` object used for console interaction.
    """
    max_length = 80 - len(max(COALA_BEAR_LOGO, key=len))
    text_lines = ['']
    for welcome_message in WELCOME_MESSAGES:
        text_lines += ['']
        text_lines += textwrap.wrap(welcome_message, max_length)

    print_side_by_side(
        printer,
        left=COALA_BEAR_LOGO,
        right=text_lines,
        limit=80)
