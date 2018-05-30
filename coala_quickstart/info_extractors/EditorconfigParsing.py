"""
Contains code for parsing ".editorconfig" files. Taken from
https://github.com/editorconfig/editorconfig-core-py library with some
minor modifications. Licensed under PSF License (see below)

PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
--------------------------------------------

1. This LICENSE AGREEMENT is between the Python Software Foundation
("PSF"), and the Individual or Organization ("Licensee") accessing and
otherwise using this software ("Python") in source or binary form and
its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
analyze, test, perform and/or display publicly, prepare derivative works,
distribute, and otherwise use Python alone or in any derivative version,
provided, however, that PSF's License Agreement and PSF's notice of copyright,
i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010
Python Software Foundation; All Rights Reserved" are retained in Python alone or
in any derivative version prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on
or incorporates Python or any part thereof, and wants to make
the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to Python.

4. PSF is making Python available to Licensee on an "AS IS"
basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any
relationship of agency, partnership, or joint venture between PSF and
Licensee.  This License Agreement does not grant permission to use PSF
trademarks or trade name in a trademark sense to endorse or promote
products or services of Licensee, or any third party.

8. By copying, installing or otherwise using Python, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.


BEOPEN.COM LICENSE AGREEMENT FOR PYTHON 2.0
-------------------------------------------

BEOPEN PYTHON OPEN SOURCE LICENSE AGREEMENT VERSION 1

1. This LICENSE AGREEMENT is between BeOpen.com ("BeOpen"), having an
office at 160 Saratoga Avenue, Santa Clara, CA 95051, and the
Individual or Organization ("Licensee") accessing and otherwise using
this software in source or binary form and its associated
documentation ("the Software").

2. Subject to the terms and conditions of this BeOpen Python License
Agreement, BeOpen hereby grants Licensee a non-exclusive,
royalty-free, world-wide license to reproduce, analyze, test, perform
and/or display publicly, prepare derivative works, distribute, and
otherwise use the Software alone or in any derivative version,
provided, however, that the BeOpen Python License is retained in the
Software, alone or in any derivative version prepared by Licensee.

3. BeOpen is making the Software available to Licensee on an "AS IS"
basis.  BEOPEN MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, BEOPEN MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE SOFTWARE WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

4. BEOPEN SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF THE
SOFTWARE FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS
AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THE SOFTWARE, OR ANY
DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

5. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

6. This License Agreement shall be governed by and interpreted in all
respects by the law of the State of California, excluding conflict of
law provisions.  Nothing in this License Agreement shall be deemed to
create any relationship of agency, partnership, or joint venture
between BeOpen and Licensee.  This License Agreement does not grant
permission to use BeOpen trademarks or trade names in a trademark
sense to endorse or promote products or services of Licensee, or any
third party.  As an exception, the "BeOpen Python" logos available at
http://www.pythonlabs.com/logos.html may be used according to the
permissions granted on that web page.

7. By copying, installing or otherwise using the software, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.


CNRI LICENSE AGREEMENT FOR PYTHON 1.6.1
---------------------------------------

1. This LICENSE AGREEMENT is between the Corporation for National
Research Initiatives, having an office at 1895 Preston White Drive,
Reston, VA 20191 ("CNRI"), and the Individual or Organization
("Licensee") accessing and otherwise using Python 1.6.1 software in
source or binary form and its associated documentation.

2. Subject to the terms and conditions of this License Agreement, CNRI
hereby grants Licensee a nonexclusive, royalty-free, world-wide
license to reproduce, analyze, test, perform and/or display publicly,
prepare derivative works, distribute, and otherwise use Python 1.6.1
alone or in any derivative version, provided, however, that CNRI's
License Agreement and CNRI's notice of copyright, i.e., "Copyright (c)
1995-2001 Corporation for National Research Initiatives; All Rights
Reserved" are retained in Python 1.6.1 alone or in any derivative
version prepared by Licensee.  Alternately, in lieu of CNRI's License
Agreement, Licensee may substitute the following text (omitting the
quotes): "Python 1.6.1 is made available subject to the terms and
conditions in CNRI's License Agreement.  This Agreement together with
Python 1.6.1 may be located on the Internet using the following
unique, persistent identifier (known as a handle): 1895.22/1013.  This
Agreement may also be obtained from a proxy server on the Internet
using the following URL: http://hdl.handle.net/1895.22/1013".

3. In the event Licensee prepares a derivative work that is based on
or incorporates Python 1.6.1 or any part thereof, and wants to make
the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to Python 1.6.1.

4. CNRI is making Python 1.6.1 available to Licensee on an "AS IS"
basis.  CNRI MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, CNRI MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON 1.6.1 WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

5. CNRI SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
1.6.1 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON 1.6.1,
OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. This License Agreement shall be governed by the federal
intellectual property law of the United States, including without
limitation the federal copyright law, and, to the extent such
U.S. federal law does not apply, by the law of the Commonwealth of
Virginia, excluding Virginia's conflict of law provisions.
Notwithstanding the foregoing, with regard to derivative works based
on Python 1.6.1 that incorporate non-separable material that was
previously distributed under the GNU General Public License (GPL), the
law of the Commonwealth of Virginia shall govern this License
Agreement only as to issues arising under or with respect to
Paragraphs 4, 5, and 7 of this License Agreement.  Nothing in this
License Agreement shall be deemed to create any relationship of
agency, partnership, or joint venture between CNRI and Licensee.  This
License Agreement does not grant permission to use CNRI trademarks or
trade name in a trademark sense to endorse or promote products or
services of Licensee, or any third party.

8. By clicking on the "ACCEPT" button where indicated, or by copying,
installing or otherwise using Python 1.6.1, Licensee agrees to be
bound by the terms and conditions of this License Agreement.

        ACCEPT


CWI LICENSE AGREEMENT FOR PYTHON 0.9.0 THROUGH 1.2
--------------------------------------------------

Copyright (c) 1991 - 1995, Stichting Mathematisch Centrum Amsterdam,
The Netherlands.  All rights reserved.

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the name of Stichting Mathematisch
Centrum or CWI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior
permission.

STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
import re


def parse_editorconfig_file(fname, file_content):
    """
    Parses the given .editorconfig file. Modified from ini.py file
    distributed with https://github.com/editorconfig/editorconfig-core-py
    library.

    :param fname:   Name of the file
    :param content: Contents of the file in the form of string.
    :return:        A nested dictionary with the section name as
                    primary key, and the configuration settings as
                    secondary key-value pairs.
    """
    # Regular expressions for parsing section header.
    SECTRE = re.compile(
        r"""

        \s *                                # Optional whitespace
        \[                                  # Opening square brace

        (?P<header>                         # One or more chars excluding
            ( [^\#;] | \\\# | \\; ) +       # unescaped # and ; characters
        )

        \]                                  # Closing square brace

        """, re.VERBOSE
    )
    # Regular expression for parsing option name/values.
    OPTRE = re.compile(
        r"""

        \s *                                # Optional whitespace
        (?P<option>                         # One or more chars excluding
            [^:=\s]                         # : a = characters (and first
            [^:=] *                         # must not be whitespace)
        )
        \s *                                # Optional whitespace
        (?P<vi>
            [:=]                            # Single = or : character
        )
        \s *                                # Optional whitespace
        (?P<value>
            . *                             # One or more characters
        )
        $

        """, re.VERBOSE
    )

    in_section = False
    current_section = None
    config = {}
    with open(fname, encoding='utf-8') as fp:
        line = fp.readline()
        if line.startswith(str('\ufeff')):
            line = line[1:]  # Strip UTF-8 BOM

        while True:
            # a section header or option header?
            match_object = SECTRE.match(line)
            if match_object:
                section_name = match_object.group('header')
                config[section_name] = {}
                current_section = section_name
                in_section = True
                optname = None
            else:
                match_object = OPTRE.match(line)
                if match_object:
                    optname, vi, optval = match_object.group(
                        'option', 'vi', 'value')
                    if ';' in optval or '#' in optval:
                        # ';' and '#' are comment delimiters only if
                        # preceeded by a spacing character
                        mo = re.search('(.*?) [;#]', optval)
                        if mo:
                            optval = mo.group(1)
                    optval = optval.strip()
                    # allow empty values
                    if optval == '""':
                        optval = ''
                    optname = optname.rstrip().lower()
                    if in_section:
                        config[current_section][optname] = optval
                else:
                    # unrecognized line type.
                    pass
            line = fp.readline()
            if not line:
                break
            # comment or blank line?
            while line.strip() == '' or line[0] in '#;':
                line = fp.readline()

    return config


def translate_editorconfig_section_to_regex(pat, nested=False):
    """
    Translates the editorconfig section pattern to a regular
    expression. Taken exactly from fnmatch.py file distributed with
    https://github.com/editorconfig/editorconfig-core-py library.
    """

    LEFT_BRACE = re.compile(
        r"""

        (?: ^ | [^\\] )     # Beginning of string or a character besides "\"

        \{                  # "{"

        """, re.VERBOSE
    )

    RIGHT_BRACE = re.compile(
        r"""

        (?: ^ | [^\\] )     # Beginning of string or a character besides "\"

        \}                  # "}"

        """, re.VERBOSE
    )

    NUMERIC_RANGE = re.compile(
        r"""
        (               # Capture a number
            [+-] ?      # Zero or one "+" or "-" characters
            \d +        # One or more digits
        )

        \.\.            # ".."

        (               # Capture a number
            [+-] ?      # Zero or one "+" or "-" characters
            \d +        # One or more digits
        )
        """, re.VERBOSE
    )

    index, length = 0, len(pat)  # Current index and length of pattern
    brace_level = 0
    in_brackets = False
    result = ''
    is_escaped = False
    matching_braces = (len(LEFT_BRACE.findall(pat)) ==
                       len(RIGHT_BRACE.findall(pat)))
    numeric_groups = []
    while index < length:
        current_char = pat[index]
        index += 1
        if current_char == '*':
            pos = index
            if pos < length and pat[pos] == '*':
                result += '.*'
            else:
                result += '[^/]*'
        elif current_char == '?':
            result += '.'
        elif current_char == '[':
            if in_brackets:
                result += '\\['
            else:
                pos = index
                has_slash = False
                while pos < length and pat[pos] != ']':
                    if pat[pos] == '/' and pat[pos-1] != '\\':
                        has_slash = True
                        break
                    pos += 1
                if has_slash:
                    result += '\\[' + pat[index:(pos + 1)] + '\\]'
                    index = pos + 2
                else:
                    if index < length and pat[index] in '!^':
                        index += 1
                        result += '[^'
                    else:
                        result += '['
                    in_brackets = True
        elif current_char == '-':
            if in_brackets:
                result += current_char
            else:
                result += '\\' + current_char
        elif current_char == ']':
            result += current_char
            in_brackets = False
        elif current_char == '{':
            pos = index
            has_comma = False
            while pos < length and (pat[pos] != '}' or is_escaped):
                if pat[pos] == ',' and not is_escaped:
                    has_comma = True
                    break
                is_escaped = pat[pos] == '\\' and not is_escaped
                pos += 1
            if not has_comma and pos < length:
                num_range = NUMERIC_RANGE.match(pat[index:pos])
                if num_range:
                    numeric_groups.append(map(int, num_range.groups()))
                    result += '([+-]?\d+)'
                else:
                    inner_result, inner_groups = (
                            translate_editorconfig_section_to_regex(
                                pat[index:pos],
                                nested=True))
                    result += '\\{%s\\}' % (inner_result,)
                    numeric_groups += inner_groups
                index = pos + 1
            elif matching_braces:
                result += '(?:'
                brace_level += 1
            else:
                result += '\\{'
        elif current_char == ',':
            if brace_level > 0 and not is_escaped:
                result += '|'
            else:
                result += '\\,'
        elif current_char == '}':
            if brace_level > 0 and not is_escaped:
                result += ')'
                brace_level -= 1
            else:
                result += '\\}'
        elif current_char == '/':
            if pat[index:(index + 3)] == '**/':
                result += '(?:/|/.*/)'
                index += 3
            else:
                result += '/'
        elif current_char != '\\':
            result += re.escape(current_char)
        if current_char == '\\':
            if is_escaped:
                result += re.escape(current_char)
            is_escaped = not is_escaped
        else:
            is_escaped = False
    if not nested:
        result += '\Z(?ms)'
    return result, numeric_groups
