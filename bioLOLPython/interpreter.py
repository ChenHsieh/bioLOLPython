#!/usr/bin/env python

"""
# 
# Additional features by Chen Hsieh (2025):
# - Updated codebase to Python 3
# - Meme-style biological sequence interpreter ("bioLOLCODE")
# - Commands added: DNA GO ..., REVERSE THAT ..., GC BOMB ..., TRANSCRIBE, TRANSLATE
# - Fun science ops: ALIGN A WIT B, I CRAVE VIOLENCE, etc.
# - Uses Biopython under the hood
# 
# Inspired by LOLCODE and Gen Z chaos, powered by 🧬
# 
# Project repo: https://github.com/ChenHsieh/bioLOLPython


 Implementation of the LOLPython language.
 Converts from LOLPython to Python then optionally runs the Python.

 This package depends on PLY -- http://www.dabeaz.com/ply/

 Written by Andrew Dalke <dalke@dalkescientific.com>
 Dalke Scientific Software, LLC
 1 June 2007, Gothenburg, Sweden
 
 This software is in the public domain.  For details see:
 http://creativecommons.org/licenses/publicdomain/


"""


import sys
import keyword
import os
import types
from io import StringIO
from ply import lex
from bioLOLPython.bio.sequence import BioSeq
import codecs
import re
import random

bio_vars = {}  # Store sequences by name, e.g., BRRRR
__NAME__ = "lolpython"
__VERSION__ = "1.0"

# Translating LOLPython tokens to Python tokens
# This could be cleaned up.  For example, some of
# these tokens could be merged into one.

tokens = (
    "NAME",      # variable names
    "RESERVED",  # Used for Python reserved names
    "NUMBER",    # Integers and floats
    "STRING",
    "OP",        # Like the Python OP
    "CLOSE",     # Don't really need this..

    "COMMENT",
    "AUTOCALL",  # write t.value then add '('
    "INLINE",    # write t.value directly
    "FUTURE",    # for the "I FUTURE CAT WITH" statement
    "PRINT",     # VISIBLE -> stdout or COMPLAIN -> stderr

    "ENDMARKER",
    "COLON",
    "WS",
    "NEWLINE",
)


# Helper functions for making given token types
def OP(t, value):
    t.type = "OP"
    t.value = value
    return t

def RESERVED(t, value):
    t.type = "RESERVED"
    t.value = value
    return t

def AUTOCALL(t, value):
    t.type = "AUTOCALL"
    t.value = "tuple"
    t.lexer.paren_stack.append(")")
    return t

def INLINE(t, value):
    t.type = "INLINE"
    t.value = value
    return t

#####

# ply uses a large regex for token detection, and sre is limited to
# 100 groups.  This grammar pushes the limit.  I use (?:non-grouping)
# parens to keep the count down.


def t_ASSIGN(t):  # cannot be a simple pattern because it must
    r'CAN[ ]+HA[SZ]\b'  # come before the t_NAME definition
    return OP(t, "=")

def t_SINGLE_QUOTE_STRING(t):
    r"'([^\\']+|\\'|\\\\)*'"  # I think this is right ...
    t.type = "STRING"
    t.value = codecs.decode(t.value[1:-1], "unicode_escape")
    return t

def t_DOUBLE_QUOTE_STRING(t):
    r'"([^\\"]+|\\"|\\\\)*"'
    t.type = "STRING"
    t.value = codecs.decode(t.value[1:-1], "unicode_escape")
    return t

# and LOL quoted strings!  They end with /LOL
# No way to have "/LOL" in the string.
def t_LOL_STRING(t):
    r"LOL[ ]*((?!/LOL).|\n)*[ ]*/LOL"
    t.type = "STRING"
    t.value = t.value[3:-4].strip(" ")
    return t

# Aliases for the same thing - for extra cuteness
def t_LSQUARE(t):
    r"(?:SOME|LOOK[ ]AT|LET[ ]+THE)\b"
    t.lexer.paren_stack.append(']')
    return OP(t, "[")

def t_LPAREN(t):
    r"(?:WIT|THEZ)\b"
    t.lexer.paren_stack.append(')')
    return OP(t, "(")

def t_LBRACE(t):
    r"BUCKET\b"
    t.lexer.paren_stack.append("}")
    return OP(t, "{")

def t_CLOSE(t):
    r"(?:OK(!+|\b)|!+)"
    stack = t.lexer.paren_stack
    if t.value.startswith("OK"):
        num_closes = len(t.value)-1  # OK -> 1, OK! -> 2, OK!!->3
    else:
        num_closes = len(t.value)  # ! -> 1, !! -> 2
    # Which close is this?  I use "OK" to match (, [ and {
    if len(stack) < num_closes:
        raise AssertionError("not enough opens on the stack: line %d"
                             % (t.lineno,))
    t.value = "".join(stack[-num_closes:][::-1])
    del stack[-num_closes:]
    return t

def t_EQ(t):
    r"KINDA[ ]+LIKE\b"
    return OP(t, "==")

def t_NE(t):
    r"(?:KINDA[ ]+)?NOT[ ]+LIKE\b"
    return OP(t, "!=")

def t_is(t):
    r"KINDA[ ]+IS\b"
    return RESERVED(t, "is")

def t_GT(t):
    r"ATE[ ]+MORE[ ]+CHEEZBURGERS?[ ]+THAN\b"
    return OP(t, ">")

def t_LT(t):
    r"ATE[ ]+FEWER[ ]+CHEEZBURGERS?[ ]+THAN\b"
    return OP(t, "<")

def t_GTE(t):
    r"BIG[ ]+LIKE\b"
    return OP(t, ">=")

def t_LTE(t):
    r"SMALL[ ]+LIKE\b"
    return OP(t, "<=")

def t_RETURN(t):
    r"U[ ]+TAKE\b"
    return RESERVED(t, "return")

def t_yield(t):
    r"U[ ]+BORROW\b"
    return RESERVED(t, "yield")

def t_ELIF(t):
    r"OR[ ]+IZ\b"
    return RESERVED(t, "elif")

def t_ELSE(t):
    r"(?:(?:I[ ]+GIVE[ ]+UP|IZ[ ]+KEWL|ALL[ ]+DONE)|NOPE)\b"
    return RESERVED(t, "else")

def t_COLON(t):
    r"\?"
    t.value = ":"
    return t

def t_FROM(t):
    r"IN[ ]+MAI\b"
    return RESERVED(t, "from")

def t_EXCEPT(t):
    r"O[ ]+NOES\b"
    return RESERVED(t, "except")

def t_PLUS(t):
    r"ALONG[ ]+WITH\b"
    return OP(t, "+")
def t_MINUS(t):
    r"TAKE[ ]+AWAY\b"
    return OP(t, "-")

def t_PLUS_EQUAL(t):
    r"GETZ[ ]+ANOTHR\b"
    return OP(t, "+=")

def t_MINUS_EQUAL(t):
    r"THROW[SZ]?[ ]+AWAY\b"
    return OP(t, "-=")

def t_DIV(t):
    r"SMASHES[ ]+INTO\b"
    return OP(t, "/")
    
def t_DIV_EQUAL(t):
    r"SMASHES[ ]+INTO[ ]+HAS\b"
    return OP(t, "/=")
    
def t_TRUEDIV(t):
    r"SMASHES[ ]+NICELY[ ]+INTO\b"
    return OP(t, "//")

def t_MUL(t):
    r"OF[ ]THOSE\b"
    return OP(t, "*")

def t_MUL_EQUAL(t):
    r"COPIES[ ]+(?:HIM|HER|IT)SELF[ ]+BY\b"
    return OP(t, "*=")

def t_POW(t):
    r"BY[ ]+GRAYSKULL[ ]+POWER"
    return OP(t, "**")

def t_IN(t):
    r"IN[ ]+(?:UR|THE|THIS)\b"
    return OP(t, "in")

def t_del(t):
    r"DO[ ]+NOT[ ]+WANT\b"
    return RESERVED(t, "del")

def t_and(t):
    r"\&"
    return RESERVED(t, "and")

def t_or(t):
    r"OR[ ]+MABEE\b"
    return RESERVED(t, "or")

def t_pass(t):
    r"I[ ]+IZ[ ]+CUTE\b"
    return RESERVED(t, "pass")

def t_forever(t):
    r"WHILE[ ]+I[ ]+CUTE\b"
    return INLINE(t, "while 1")

def t_def(t):
    r"SO[ ]+IM[ ]+LIKE\b"
    return RESERVED(t, "def")

def t_class(t):
    r"ME[ ]+MAKE[ ]\b"
    return RESERVED(t, "class")

def t_future(t):
    r"I[ ]+FUTURE[ ]+CAT[ ]+WITH\b"
    t.type = "FUTURE"
    return t

def t_assert(t):
    r"SO[ ]+GOOD\b"
    return RESERVED(t, "assert")

def t_assert_not(t):
    r"AINT[ ]+GOOD\b"
    return INLINE(t, "assert not ")

def t_for(t):
    r"GIMME[ ]+EACH\b"
    return RESERVED(t, "for")

def t_list(t):
    r"ALL[ ]+OF\b"
    return AUTOCALL(t, "tuple")

RESERVED_VALUES = {
    "EASTERBUNNY": ("NUMBER", "0"),
    "CHEEZBURGER": ("NUMBER", "1"),
    "CHOKOLET": ("NUMBER", "-1"),
    "TWIN": ("NUMBER", "2"),
    "TWINZ": ("NUMBER", "2"),
    "TWINS": ("NUMBER", "2"),
    "EVILTWIN": ("NUMBER", "-2"),
    "EVILTWINZ": ("NUMBER", "-2"),
    "EVILTWINS": ("NUMBER", "-2"),
    "ALLFINGERZ": ("NUMBER", "10"),
    "TOEZ": ("NUMBER", "-10"),
    "ONE": ("NUMBER", "1"),
    "ONCE": ("NUMBER", "1"),
    "TWO": ("NUMBER", "2"),
    "TWICE": ("NUMBER", "2"),
    "THR33": ("NUMBER", "3"),
    "FOUR": ("NUMBER", "4"),
    "FIV": ("NUMBER", "5"),
    "SIKS": ("NUMBER", "6"),
    "SEVN": ("NUMBER", "7"),
    "ATE": ("NUMBER", "8"),
    "NINE": ("NUMBER", "9"),
    "MEH": ("NAME", "False"),
    "YEAH": ("NAME", "True"),
    "VISIBLE": ("PRINT", "stdout"),
    "COMPLAIN": ("PRINT", "stderr"),
    "AND": ("OP", ","),
    "BLACKHOLE": ("RESERVED", "ZeroDivisionError"),
    "DONOTLIKE": ("AUTOCALL", "AssertionError"),

    "ANTI": ("OP", "-"),
    "IZ": ("RESERVED", "if"),
    "GIMME": ("RESERVED", "import"),
    "LIKE": ("RESERVED", "as"),
    "OWN": ("OP", "."),

    "PLZ": ("RESERVED", "try"),
    "HALP": ("RESERVED", "raise"),
    "WHATEVER": ("RESERVED", "finally"),
    "KTHX": ("RESERVED", "continue"),
    "KTHXBYE": ("RESERVED", "break"),
    
    "OVER": ("OP", "/"),

    "AINT": ("RESERVED", "not"),
    "ME": ("RESERVED", "self"),

    "STRING": ("AUTOCALL", "str"),
    "NUMBR": ("AUTOCALL", "int"),
    "BIGNESS": ("AUTOCALL", "len"),
    "NUMBRZ": ("AUTOCALL", "range"),
    "ADDED": ("AUTOCALL", ".append"),

    "ARGZ": ("INLINE", "_lol_sys.argv"),
    "THINGZ": ("INLINE", "()"),  # invisible tuple didn't sound right
    "THING": ("INLINE", "()"),   # sometimes it's better in singular form
    "MY": ("INLINE", "self."),
    "MYSELF": ("INLINE", "(self)"),

    "EVEN": ("INLINE", "% 2 == 0"),
    "ODD": ("INLINE", "% 2 == 1"),
    "WIF": ("RESERVED", "with"),
    "ITSLIKETHIS":("RESERVED","class")
    }

def t_FLOAT(t):
    r"""(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]? \d+)?"""
    t.value = t.value
    t.type = "NUMBER"
    return t

def t_INT(t):
    r"\d+"
    t.type = "NUMBER"
    return t

def t_INVISIBLE(t):
    r"INVISIBLE([ ]+(LIST|STRING|BUCKET))?\b"
    if "LIST" in t.value:
        t.type = "INLINE"
        t.value = "[]"
    elif "STRING" in t.value:
        t.type = "INLINE"
        t.value = '""'
    elif "BUCKET" in t.value:
        t.type = "INLINE"
        t.value = "{}"
    else:
        RESERVED(t, "None")
    return t

# Not consuming the newline.  Needed for "IZ EASTERBUNNY? BTW comment"
def t_COMMENT(t):
    r"[ ]*(?:BTW|WTF)[^\n]*"
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in RESERVED_VALUES:
        type, value = RESERVED_VALUES[t.value]
        t.type = type
        t.value = value
        if t.type == "AUTOCALL":
            t.lexer.paren_stack.append(")")
    return t

def t_WS(t):
    r' [ ]+ '
    if t.lexer.at_line_start and not t.lexer.paren_stack:
        return t
    

# Don't generate newline tokens when inside of parens
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = "NEWLINE"
    if not t.lexer.paren_stack:
        return t
    

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))



## I implemented INDENT / DEDENT generation as a post-processing filter

# The original lex token stream contains WS and NEWLINE characters.
# WS will only occur before any other tokens on a line.

# I have three filters.  One tags tokens by adding two attributes.
# "must_indent" is True if the token must be indented from the
# previous code.  The other is "at_line_start" which is True for WS
# and the first non-WS/non-NEWLINE on a line.  It flags the check so
# see if the new line has changed indication level.

# Python's syntax has three INDENT states
#  0) no colon hence no need to indent
#  1) "if 1: go()" - simple statements have a COLON but no need for an indent
#  2) "if 1:\n  go()" - complex statements have a COLON NEWLINE and must indent

NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line
def track_tokens_filter(lexer, tokens):
    lexer.at_line_start = at_line_start = True
    indent = NO_INDENT
    
    for token in tokens:
        token.at_line_start = at_line_start

        if token.type == "COLON":
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False
            
        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False

        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False

        elif token.type == "COMMENT":
            pass

        else:
            # A real token; only indent after COLON NEWLINE
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False

            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start

def _new_token(type, lineno):
    tok = lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.lexpos = -1
    return tok

# Synthesize a DEDENT tag
def DEDENT(lineno):
    return _new_token("DEDENT", lineno)

# Synthesize an INDENT tag
def INDENT(lineno):
    return _new_token("INDENT", lineno)


# Track the indentation level and emit the right INDENT / DEDENT events.
def indentation_filter(tokens):
    # A stack of indentation levels; will never pop item 0
    levels = [0]
    token = None
    depth = 0
    prev_was_ws = False
    for token in tokens:
##        if 1:
##            print "Process", token,
##            if token.at_line_start:
##                print "at_line_start",
##            if token.must_indent:
##                print "must_indent",
##            print
                
        # WS only occurs at the start of the line
        # There may be WS followed by NEWLINE so
        # only track the depth here.  Don't indent/dedent
        # until there's something real.
        if token.type == "WS":
            assert depth == 0
            depth = len(token.value)
            prev_was_ws = True
            # Don't forward WS to the parser
            continue

        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                # ignore blank lines
                continue
            # pass the other cases on through
            yield token
            continue

        if token.type == "COMMENT":
            yield token
            continue

        # then it must be a real token (not WS, not NEWLINE)
        # which can affect the indentation level

        prev_was_ws = False
        if token.must_indent:
            # The current depth must be larger than the previous level
            if not (depth > levels[-1]):
                raise IndentationError("expected an indented block")

            levels.append(depth)
            yield INDENT(token.lineno)

        elif token.at_line_start:
            # Must be on the same level or one of the previous levels
            if depth == levels[-1]:
                # At the same level
                pass
            elif depth > levels[-1]:
                raise IndentationError("indentation increase but not in new block")
            else:
                # Back up; but only if it matches a previous level
                try:
                    i = levels.index(depth)
                except ValueError:
                    raise IndentationError("inconsistent indentation")
                for _ in range(i+1, len(levels)):
                    yield DEDENT(token.lineno)
                    levels.pop()

        yield token

    ### Finished processing ###

    # Must dedent any remaining levels
    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            yield DEDENT(token.lineno)
    

# The top-level filter adds an ENDMARKER, if requested.
# Python's grammar uses it.
def token_filter(lexer, add_endmarker = True):
    token = None
    tokens = iter(lexer.token, None)
    tokens = track_tokens_filter(lexer, tokens)
    for token in indentation_filter(tokens):
        yield token

    if add_endmarker:
        lineno = 1
        if token is not None:
            lineno = token.lineno
        yield _new_token("ENDMARKER", lineno)

class LOLLexer(object):
    def __init__(self, debug=0, optimize=0, lextab='lextab', reflags=0):
        self.lexer = lex.lex(debug=debug, optimize=optimize,
                             lextab=lextab, reflags=reflags)
        self.token_stream = None
    def input(self, s, add_endmarker=True):
        self.lexer.paren_stack = []
        self.lexer.input(s)
        self.token_stream = token_filter(self.lexer, add_endmarker)
    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

# Helper class to generate logically correct indented Python code
class IndentWriter(object):
    def __init__(self, outfile):
        self.outfile = outfile
        self.at_first_column = True
        self.indent = 0
    def write(self, text):
        if self.at_first_column:
            self.outfile.write("    "*self.indent)
            self.at_first_column = False
        self.outfile.write(text)

# Split things up because the from __future__ statements must
# go before any other code.

HEADER = """# LOLPython to Python converter version 1.0
# Written by Andrew Dalke, who should have been working on better things.

"""

BODY = """
# sys is used for COMPLAIN and ARGZ
import sys as _lol_sys

"""

def to_python(s):
    L = LOLLexer()
    L.input(s)
    
    header = StringIO()
    header.write(HEADER)
    header_output = IndentWriter(header)

    body = StringIO()
    body.write(BODY)
    body_output = IndentWriter(body)

    write = body_output.write
    output = body_output

    for t in iter(L.token_stream):
        if t.type == "NAME":
            # Need to escape names which are Python variables Do that
            # by appending an "_".  But then I also need to make sure
            # that "yield_" does not collide with "yield".  And you
            # thought you were being clever trying to use a Python
            # variable.  :)
            name = t.value.rstrip("_")
            if name in keyword.kwlist:
                write(t.value + "_ ")
            else:
                write(t.value + " ")
            
        elif t.type in ("RESERVED", "OP", "NUMBER", "CLOSE"):
            # While not pretty, I'll put a space after each
            # term because it's the simplest solution.  Otherwise
            # I'll need to track the amount of whitespace between
            # the tokens in the original text.
            write(t.value+" ")

            # XXX escape names which are special in Python!
        elif t.type == "STRING":
            write(repr(t.value) + " ")
        
        elif t.type == "COMMENT":
            # Not enough information to keep comments on the correct
            # indentation level.  This is good enough.  Ugly though.
            # Maybe I need to fix the tokenizer.
            write("#"+ t.value[3:]+"\n")
            output.at_first_column = True

        elif t.type == "COLON":
            write(":")

        elif t.type == "INDENT":
            output.indent += 1
            pass
            
        elif t.type == "DEDENT":
            output.indent -= 1
            pass
            
        elif t.type == "NEWLINE":
            write(t.value)
            output.at_first_column = True
            output = body_output
            write = output.write
            
        elif t.type == "PRINT":
            if t.value == "stdout":
                write("print ")
            elif t.value == "stderr":
                write("print(..., file=_lol_sys.stderr) ")
            else:
                raise AssertionError(t.value)
                
        elif t.type == "AUTOCALL":
            write(t.value + "(")
        
        elif t.type == "INLINE":
            write(t.value)
        
        elif t.type == "ENDMARKER":
            write("\n# The end.\n")
        
        elif t.type == "WS":
            output.leading_ws = t.value
        
        elif t.type == "FUTURE":
            # Write to the header.  This is a hack.  Err, a hairball.
            output = header_output
            write = output.write
            write("from __future__ import ")
            
        else:
            raise AssertionError(t.type)
        
    return header.getvalue() + body.getvalue()


# API code for doing the translation and exec'ing the result

#####################################
# bioLOLCODE Extension Commands 🧬😹
# Added by Chen Hsieh, 2025
# - Meme-style DNA sequence tools
# - Dialect system for internet slang eras
#####################################
from bioLOLPython.dialects import get_dialect, list_dialects, dialect_names

_current_dialect_name = "lolcat"


def set_dialect(name):
    global _current_dialect_name
    get_dialect(name)  # validate it exists
    _current_dialect_name = name


def _get_var(name):
    if name not in bio_vars:
        print(f"❌ Variable '{name}' not defined.")
        return None
    return bio_vars[name]


def _parse_visible(msg):
    """Parse print message: split on +, strip quotes, resolve variables."""
    parts = msg.split("+")
    result = []
    for part in parts:
        part = part.strip()
        if (part.startswith('"') and part.endswith('"')) or \
           (part.startswith("'") and part.endswith("'")):
            result.append(part[1:-1])
        elif part in bio_vars:
            result.append(str(bio_vars[part]))
        else:
            result.append(part)
    return "".join(result)


def _score_rating(score):
    ratings = ("meh", "ok", "slay", "SHEEESH")
    return ratings[min(int(score) // 5, 3)]


def _execute_command(cmd_name, match, dialect):
    """Execute a bio command using dialect-specific response templates."""
    cmd_def = dialect["commands"][cmd_name]

    if cmd_name == "init":
        print(cmd_def.get("greeting", ""))
        return

    if cmd_name == "end":
        return

    if cmd_name == "declare":
        name = match.group("name")
        seq = match.group("seq")
        try:
            bio_vars[name] = BioSeq(seq)
        except ValueError as e:
            print(f"❌ {e}")
        return

    if cmd_name == "reverse":
        name = match.group("name")
        var = _get_var(name)
        if var:
            bio_vars[name] = BioSeq(var.reverse_complement())
        return

    if cmd_name == "gc_content":
        name = match.group("name")
        var = _get_var(name)
        if var:
            gc = var.gc_content()
            template = cmd_def.get("response", "GC content: {value:.2f}%")
            rating = _score_rating(gc / 10)  # 0-100% -> rating
            print(template.format(value=gc, rating=rating))
        return

    if cmd_name == "print":
        # The print pattern matches just the keyword; the rest of the line is the message
        keyword = cmd_def["pattern"]
        # Find where the keyword ends in the original line
        msg = match.string[match.end():].strip()
        if not msg:
            # Try getting everything after the keyword
            idx = match.string.upper().find(keyword.upper())
            if idx >= 0:
                msg = match.string[idx + len(keyword):].strip()
        print(_parse_visible(msg))
        return

    if cmd_name == "transcribe":
        name = match.group("name")
        var = _get_var(name)
        if var:
            bio_vars[name] = BioSeq(str(var.seq.transcribe()))
        return

    if cmd_name == "translate":
        name = match.group("name")
        var = _get_var(name)
        if var:
            bio_vars[name] = BioSeq(str(var.seq.translate()), validate=False)
        return

    if cmd_name == "align":
        try:
            from Bio.Align import PairwiseAligner
            name1 = match.group("a")
            name2 = match.group("b")
            if name1 not in bio_vars or name2 not in bio_vars:
                print("❌ One or both sequences not defined.")
                return
            seq1 = str(bio_vars[name1])
            seq2 = str(bio_vars[name2])

            aligner = PairwiseAligner()
            aligner.mode = "global"
            alignments = aligner.align(seq1, seq2)

            if not alignments:
                print("⚠️ No alignment found.")
                return

            print(alignments[0].format())
            score = alignments[0].score
            template = cmd_def.get("response", "Score: {score:.2f} {rating}")
            print(template.format(score=score, rating=_score_rating(score)))
        except Exception as e:
            print(f"❌ Error during alignment: {e}")
        return

    if cmd_name == "mutate":
        name = match.group("name")
        var = _get_var(name)
        if not var:
            return
        original = str(var)
        mutated = list(original)
        if not mutated:
            print("⚠️ sequence is empty, nothing to mutate")
            return
        index = random.randint(0, len(mutated) - 1)
        bases = "ACGTU"
        original_base = mutated[index]
        choices = [b for b in bases if b != original_base.upper()]
        mutated[index] = random.choice(choices)
        bio_vars[name] = BioSeq("".join(mutated))
        template = cmd_def.get("response", "mutated {name} at pos {pos}: {old} ➜ {new}")
        print(template.format(name=name, pos=index + 1, old=original[index], new=mutated[index]))
        return

    if cmd_name == "length":
        name = match.group("name")
        var = _get_var(name)
        if var:
            template = cmd_def.get("response", "{name} is {value} bases long")
            print(template.format(name=name, value=var.length()))
        return

    if cmd_name == "complement":
        name = match.group("name")
        var = _get_var(name)
        if var:
            bio_vars[name] = BioSeq(var.complement())
        return

    if cmd_name == "find_orf":
        name = match.group("name")
        var = _get_var(name)
        if var:
            orf = var.find_orf()
            if orf:
                template = cmd_def.get("orf_found", "ORF found: {orf} ({length} bp)")
                print(template.format(orf=orf, length=len(orf)))
            else:
                template = cmd_def.get("orf_missing", "No ORF found in {name}")
                print(template.format(name=name))
        return

    if cmd_name == "motif":
        name = match.group("name")
        pattern = match.group("pattern")
        var = _get_var(name)
        if var:
            matches = var.find_motif(pattern)
            if matches:
                template = cmd_def.get("found", "Found {count} match(es):")
                print(template.format(count=len(matches), pattern=pattern, name=name))
                pos_template = cmd_def.get("position", "   pos {start}-{end}")
                for start, end in matches:
                    print(pos_template.format(start=start, end=end))
            else:
                template = cmd_def.get("not_found", "No matches for '{pattern}' in {name}")
                print(template.format(pattern=pattern, name=name))
        return


def handle_line(line, dialect_name=None):
    """Process a single bioLOLPython command line using the specified dialect."""
    if dialect_name is None:
        dialect_name = _current_dialect_name

    if not line or line.startswith("BTW"):
        return

    dialect = get_dialect(dialect_name)

    for cmd_name, cmd_def in dialect["commands"].items():
        m = cmd_def["matcher"].match(line)
        if m:
            _execute_command(cmd_name, m, dialect)
            return

    # Check if this is an end command or comment — the regex might not match
    # partial lines, so also check the print command specially since it's a prefix match
    print_cmd = dialect["commands"].get("print")
    if print_cmd:
        keyword = print_cmd["pattern"]
        if line.startswith(keyword):
            msg = line[len(keyword):].strip()
            print(_parse_visible(msg))
            return
 
def reset_bio_vars():
    bio_vars.clear()

def execfile(infile, module_name="__lolmain__"):
    "file, module_name -- exec the lolpython file in a newly created module"
    if not hasattr(infile, "read"):
        with open(infile, "r") as f:
            s = f.read()
    else:
        s = infile.read()
    return execstring(s, module_name)

def execstring(s, module_name="__lolmain__"):
    "s, module_name -- exec the lolpython string in a newly created module"
    python_s = to_python(s)
    # Doing this bit of trickiness so I can have LOLPython code act
    # like __main__.  This fix is enough to fool unittest.
    m = types.ModuleType(module_name)
    sys.modules[module_name] = m
    exec(python_s, m.__dict__)
    return m

def convert_file(infile, outfile):
    "read LOLPython code from infile, write converted Python code to outfile"
    if not hasattr(outfile, "write"):
        outfile = open(outfile, "w")
    outfile.write(to_python(infile.read()))

def convert(filenames):
    "convert LOLPython filenames into corresponding Python '.py' files"
    if not filenames:
        convert_file(sys.stdin, sys.stdout)
    else:
        for filename in filenames:
            base, ext = os.path.splitext(filename)
            convert_file(open(filename, "r"), open(base+".py", "w"))

def help():
    print("""convert and run a lolpython program
Commands are:
    lolpython              Read a lolpython program from stdin and execute it
    lolpython --convert    Convert a lolpython program from stdin 
                                  and generate python to stdout
    lolpython --convert filename1 [filename....] 
                           Convert a list of lolpython files into Python files
    lolpython filename [arg1 [arg2 ...]]
                           Run a lolpython program using optional arguments
""")

def main(argv):
    if len(argv) >= 2:
        if argv[1] == "--convert":
            convert(argv[2:])
            return
        if argv[1] == "--help":
            help()
            return
        if argv[1] == "--version":
            print(__NAME__ + " " + __VERSION__)
            return

        # otherwise, run the lolpython program
        sys.argv = sys.argv[1:]
        filename = sys.argv[0]
        if filename.endswith(".lolz"):
            with open(filename, "r") as f:
                for line in f:
                    handle_line(line.strip())
            return
        execfile(filename, "__main__")
    else:
        # commands from stdin
        execfile(sys.stdin)
        
    

if __name__ == "__main__":
    main(sys.argv)
    
