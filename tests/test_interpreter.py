import pytest
import io
from contextlib import redirect_stdout
from bioLOLPython.interpreter import handle_line, reset_bio_vars, bio_vars


@pytest.fixture(autouse=True)
def clean_state():
    """Reset bio_vars before each test."""
    reset_bio_vars()
    yield
    reset_bio_vars()


def capture_output(line, dialect_name="lolcat"):
    """Run handle_line and capture stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        handle_line(line, dialect_name=dialect_name)
    return buf.getvalue().strip()


def run_script(lines, dialect_name="lolcat"):
    """Run multiple lines and capture stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        for line in lines:
            handle_line(line.strip(), dialect_name=dialect_name)
    return buf.getvalue()


# ---- Lolcat dialect (default) ----

class TestDNADeclaration:
    def test_basic(self):
        handle_line('DNA GO X ITZ "ATGC"')
        assert "X" in bio_vars
        assert str(bio_vars["X"]) == "ATGC"

    def test_multiple(self):
        handle_line('DNA GO A ITZ "AAAA"')
        handle_line('DNA GO B ITZ "CCCC"')
        assert str(bio_vars["A"]) == "AAAA"
        assert str(bio_vars["B"]) == "CCCC"

    def test_invalid_sequence(self):
        out = capture_output('DNA GO X ITZ "XYZLOL"')
        assert "Invalid" in out
        assert "X" not in bio_vars


class TestReverseComplement:
    def test_reverse(self):
        handle_line('DNA GO X ITZ "ATGC"')
        handle_line("REVERSE THAT X")
        assert str(bio_vars["X"]) == "GCAT"

    def test_undefined_var(self):
        out = capture_output("REVERSE THAT NOPE")
        assert "not defined" in out


class TestGCBomb:
    def test_output(self):
        handle_line('DNA GO X ITZ "ATGC"')
        out = capture_output("GC BOMB X")
        assert "50.00%" in out

    def test_all_at(self):
        handle_line('DNA GO X ITZ "AATT"')
        out = capture_output("GC BOMB X")
        assert "0.00%" in out


class TestTranscribe:
    def test_dna_to_rna(self):
        handle_line('DNA GO X ITZ "ATGC"')
        handle_line("TRANSCRIBE X")
        assert str(bio_vars["X"]) == "AUGC"


class TestTranslate:
    def test_basic(self):
        handle_line('DNA GO X ITZ "ATGGAA"')
        handle_line("TRANSLATE X")
        assert str(bio_vars["X"]) == "ME"


class TestVisible:
    def test_print_variable(self):
        handle_line('DNA GO X ITZ "ATGC"')
        out = capture_output("VISIBLE X")
        assert "ATGC" in out

    def test_string_concatenation(self):
        handle_line('DNA GO X ITZ "ATGC"')
        out = capture_output('VISIBLE "seq: " + X')
        assert out == "seq: ATGC"

    def test_multiple_concat(self):
        handle_line('DNA GO X ITZ "ATGC"')
        out = capture_output('VISIBLE "a" + X + "b"')
        assert out == "aATGCb"


class TestMutation:
    def test_mutation_changes_one_base(self):
        handle_line('DNA GO X ITZ "AAAA"')
        original = str(bio_vars["X"])
        handle_line("I CRAVE VIOLENCE X")
        mutated = str(bio_vars["X"])
        diffs = sum(1 for a, b in zip(original, mutated) if a != b)
        assert diffs == 1


class TestAlignment:
    def test_identical(self):
        handle_line('DNA GO A ITZ "ATGC"')
        handle_line('DNA GO B ITZ "ATGC"')
        out = capture_output("ALIGN A WIT B")
        assert "SCOREZ" in out

    def test_missing_var(self):
        handle_line('DNA GO A ITZ "ATGC"')
        out = capture_output("ALIGN A WIT MISSING")
        assert "not defined" in out


class TestHAI:
    def test_greeting(self):
        out = capture_output("HAI GENZOME 1.0")
        assert "bioLOLCODE" in out


class TestNewCommands:
    def test_how_long(self):
        handle_line('DNA GO X ITZ "ATGC"')
        out = capture_output("HOW LONG X")
        assert "4" in out

    def test_complement(self):
        handle_line('DNA GO X ITZ "ATGC"')
        handle_line("COMPLEMENT X")
        assert str(bio_vars["X"]) == "TACG"

    def test_find_orf(self):
        handle_line('DNA GO X ITZ "AAATGCCCCCCTAAGG"')
        out = capture_output("FIND ORF X")
        assert "ORF found" in out
        assert "ATG" in out

    def test_find_orf_missing(self):
        handle_line('DNA GO X ITZ "CCCCCC"')
        out = capture_output("FIND ORF X")
        assert "No ORF" in out

    def test_motif_hunt(self):
        handle_line('DNA GO X ITZ "ATGCATGC"')
        out = capture_output('MOTIF HUNT X FOR "ATG"')
        assert "2 match" in out

    def test_motif_hunt_no_match(self):
        handle_line('DNA GO X ITZ "AAAA"')
        out = capture_output('MOTIF HUNT X FOR "GGG"')
        assert "No matches" in out


class TestResetBioVars:
    def test_reset(self):
        handle_line('DNA GO X ITZ "ATGC"')
        assert "X" in bio_vars
        reset_bio_vars()
        assert len(bio_vars) == 0


class TestComments:
    def test_btw_ignored(self):
        out = capture_output("BTW this is a comment")
        assert out == ""

    def test_empty_line_ignored(self):
        out = capture_output("")
        assert out == ""


# ---- Gen Z dialect ----

class TestGenZDialect:
    def test_declare_and_gc(self):
        handle_line('NO CAP X IS "ATGC"', dialect_name="gen_z")
        assert "X" in bio_vars
        out = capture_output("VIBE CHECK X", dialect_name="gen_z")
        assert "50.00%" in out

    def test_reverse(self):
        handle_line('NO CAP X IS "ATGC"', dialect_name="gen_z")
        handle_line("UNO REVERSE X", dialect_name="gen_z")
        assert str(bio_vars["X"]) == "GCAT"

    def test_translate(self):
        handle_line('NO CAP X IS "ATGGAA"', dialect_name="gen_z")
        handle_line("GLOW UP X", dialect_name="gen_z")
        assert str(bio_vars["X"]) == "ME"

    def test_transcribe(self):
        handle_line('NO CAP X IS "ATGC"', dialect_name="gen_z")
        handle_line("MAIN CHARACTER X", dialect_name="gen_z")
        assert str(bio_vars["X"]) == "AUGC"

    def test_print(self):
        handle_line('NO CAP X IS "ATGC"', dialect_name="gen_z")
        out = capture_output('SPILL "seq: " + X', dialect_name="gen_z")
        assert out == "seq: ATGC"

    def test_greeting(self):
        out = capture_output("YO ITS GIVING GENOME", dialect_name="gen_z")
        assert "bestie" in out

    def test_end_to_end(self):
        script = [
            "YO ITS GIVING GENOME",
            'NO CAP X IS "ATGCATGC"',
            "VIBE CHECK X",
            "PERIODT",
        ]
        out = run_script(script, dialect_name="gen_z")
        assert "50.00%" in out


# ---- Brainrot dialect ----

class TestBrainrotDialect:
    def test_declare_and_gc(self):
        handle_line('SIGMA X RIZZ "ATGC"', dialect_name="brainrot")
        assert "X" in bio_vars
        out = capture_output("AURA CHECK X", dialect_name="brainrot")
        assert "50.00%" in out

    def test_reverse(self):
        handle_line('SIGMA X RIZZ "ATGC"', dialect_name="brainrot")
        handle_line("FANUM TAX X", dialect_name="brainrot")
        assert str(bio_vars["X"]) == "GCAT"

    def test_translate(self):
        handle_line('SIGMA X RIZZ "ATGGAA"', dialect_name="brainrot")
        handle_line("LOOKSMAX X", dialect_name="brainrot")
        assert str(bio_vars["X"]) == "ME"

    def test_print(self):
        handle_line('SIGMA X RIZZ "ATGC"', dialect_name="brainrot")
        out = capture_output('HAWK TUAH "seq: " + X', dialect_name="brainrot")
        assert out == "seq: ATGC"

    def test_greeting(self):
        out = capture_output("SKIBIDI GENOME", dialect_name="brainrot")
        assert "SKIBIDI" in out

    def test_mutate(self):
        handle_line('SIGMA X RIZZ "AAAA"', dialect_name="brainrot")
        original = str(bio_vars["X"])
        handle_line("ONLY IN OHIO X", dialect_name="brainrot")
        mutated = str(bio_vars["X"])
        diffs = sum(1 for a, b in zip(original, mutated) if a != b)
        assert diffs == 1

    def test_end_to_end(self):
        script = [
            "SKIBIDI GENOME",
            'SIGMA X RIZZ "ATGCATGC"',
            "AURA CHECK X",
            "MOGGER OUT",
        ]
        out = run_script(script, dialect_name="brainrot")
        assert "50.00%" in out


# ---- End-to-end workflows ----

class TestEndToEnd:
    def test_gc_workflow(self):
        script = [
            "HAI GENZOME 1.0",
            'DNA GO X ITZ "ATGCATGC"',
            "GC BOMB X",
            "KTHXBYE",
        ]
        out = run_script(script)
        assert "50.00%" in out

    def test_translate_workflow(self):
        script = [
            "HAI GENZOME 1.0",
            'DNA GO Y ITZ "ATGGAGGAG"',
            "TRANSLATE Y",
        ]
        run_script(script)
        assert str(bio_vars["Y"]) == "MEE"

    def test_transcribe_and_print(self):
        script = [
            "HAI GENZOME 1.0",
            'DNA GO MRNA ITZ "ATGCGTACG"',
            "TRANSCRIBE MRNA",
            "VISIBLE MRNA",
        ]
        out = run_script(script)
        assert "AUGCGUACG" in out

    def test_visible_concatenation(self):
        script = [
            'DNA GO X ITZ "ATGC"',
            'VISIBLE "result: " + X + " done"',
        ]
        out = run_script(script)
        assert "result: ATGC done" in out
