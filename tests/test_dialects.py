import pytest
import tempfile
from pathlib import Path
import yaml

from bioLOLPython.dialects import (
    get_dialect,
    list_dialects,
    dialect_names,
    register_dialect,
    reload_dialects,
)
from bioLOLPython.dialects.base import (
    _compile_pattern,
    compile_dialect,
    validate_dialect,
    load_yaml_dialect,
    REQUIRED_COMMANDS,
    BUNDLED_DIR,
)


class TestDialectRegistry:
    def test_list_dialects(self):
        dialects = list_dialects()
        assert len(dialects) >= 3
        names = [d["name"] for d in dialects]
        assert "lolcat" in names
        assert "gen_z" in names
        assert "brainrot" in names

    def test_dialect_names(self):
        names = dialect_names()
        assert "lolcat" in names
        assert "gen_z" in names
        assert "brainrot" in names

    def test_get_dialect(self):
        d = get_dialect("lolcat")
        assert d["name"] == "lolcat"
        assert "commands" in d

    def test_unknown_dialect(self):
        with pytest.raises(ValueError, match="Unknown dialect"):
            get_dialect("doesntexist")

    def test_register_dialect(self):
        custom = {
            "name": "test_custom",
            "era": "~2099",
            "description": "test dialect",
            "commands": {
                cmd: {"pattern": f"TEST_{cmd.upper()} {{name}}"}
                if cmd not in ("init", "end", "print", "align", "declare", "motif")
                else (
                    {"pattern": "TEST_INIT"} if cmd == "init"
                    else {"pattern": "TEST_END"} if cmd == "end"
                    else {"pattern": "TEST_PRINT"} if cmd == "print"
                    else {"pattern": "TEST_ALIGN {a} WITH {b}"} if cmd == "align"
                    else {"pattern": 'TEST_DECLARE {name} AS {seq}'} if cmd == "declare"
                    else {"pattern": 'TEST_MOTIF {name} IN {pattern}'} if cmd == "motif"
                    else {"pattern": f"TEST_{cmd.upper()} {{name}}"}
                )
                for cmd in REQUIRED_COMMANDS
            },
        }
        register_dialect(custom)
        assert "test_custom" in dialect_names()
        d = get_dialect("test_custom")
        assert d["era"] == "~2099"
        # Cleanup
        reload_dialects()


class TestPatternCompiler:
    def test_simple_pattern(self):
        pattern = _compile_pattern("HELLO {name}")
        m = pattern.match("HELLO WORLD")
        assert m is not None
        assert m.group("name") == "WORLD"

    def test_two_vars(self):
        pattern = _compile_pattern("ALIGN {a} WIT {b}")
        m = pattern.match("ALIGN X WIT Y")
        assert m.group("a") == "X"
        assert m.group("b") == "Y"

    def test_seq_pattern(self):
        pattern = _compile_pattern("DNA GO {name} ITZ {seq}")
        m = pattern.match('DNA GO X ITZ "ATGC"')
        assert m.group("name") == "X"
        assert m.group("seq") == "ATGC"

    def test_trailing_text_allowed(self):
        pattern = _compile_pattern("HAI GENZOME")
        m = pattern.match("HAI GENZOME 1.0")
        assert m is not None

    def test_no_match(self):
        pattern = _compile_pattern("HELLO {name}")
        m = pattern.match("GOODBYE WORLD")
        assert m is None


class TestYAMLLoading:
    def test_bundled_yaml_files_exist(self):
        assert BUNDLED_DIR.is_dir()
        yaml_files = list(BUNDLED_DIR.glob("*.yaml"))
        assert len(yaml_files) >= 3

    def test_load_bundled_lolcat(self):
        path = BUNDLED_DIR / "lolcat.yaml"
        dialect = load_yaml_dialect(path)
        assert dialect["name"] == "lolcat"
        assert "matcher" in dialect["commands"]["init"]

    def test_load_from_temp_file(self):
        dialect_yaml = {
            "name": "temp_test",
            "era": "~2099",
            "description": "temp test dialect",
            "commands": {
                cmd: {"pattern": f"T_{cmd.upper()} {{name}}"}
                if cmd not in ("init", "end", "print", "align", "declare", "motif")
                else (
                    {"pattern": "T_INIT"} if cmd == "init"
                    else {"pattern": "T_END"} if cmd == "end"
                    else {"pattern": "T_PRINT"} if cmd == "print"
                    else {"pattern": "T_ALIGN {a} WITH {b}"} if cmd == "align"
                    else {"pattern": 'T_DECLARE {name} AS {seq}'} if cmd == "declare"
                    else {"pattern": 'T_MOTIF {name} IN {pattern}'}
                )
                for cmd in REQUIRED_COMMANDS
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(dialect_yaml, f)
            f.flush()
            dialect = load_yaml_dialect(f.name)
        assert dialect["name"] == "temp_test"
        assert "matcher" in dialect["commands"]["gc_content"]

    def test_invalid_yaml_missing_commands(self):
        bad_yaml = {"name": "bad", "era": "x", "description": "x", "commands": {}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_yaml, f)
            f.flush()
            with pytest.raises(ValueError, match="missing command"):
                load_yaml_dialect(f.name)


class TestValidation:
    def test_valid_dialect(self):
        d = get_dialect("lolcat")
        assert validate_dialect(d) is True

    def test_missing_name(self):
        with pytest.raises(ValueError, match="missing required field"):
            validate_dialect({"era": "x", "description": "x", "commands": {}})

    def test_missing_command(self):
        d = {
            "name": "bad",
            "era": "x",
            "description": "x",
            "commands": {"init": {"pattern": "HI"}},
        }
        with pytest.raises(ValueError, match="missing command"):
            validate_dialect(d)


class TestDialectCompleteness:
    """Ensure every dialect has all required commands."""

    @pytest.mark.parametrize("name", dialect_names())
    def test_all_commands_present(self, name):
        dialect = get_dialect(name)
        for cmd in REQUIRED_COMMANDS:
            assert cmd in dialect["commands"], f"Dialect '{name}' missing command '{cmd}'"

    @pytest.mark.parametrize("name", dialect_names())
    def test_all_commands_have_matcher(self, name):
        dialect = get_dialect(name)
        for cmd_name, cmd_def in dialect["commands"].items():
            assert "matcher" in cmd_def, f"Dialect '{name}' command '{cmd_name}' has no matcher"

    @pytest.mark.parametrize("name", dialect_names())
    def test_has_examples(self, name):
        dialect = get_dialect(name)
        assert "examples" in dialect, f"Dialect '{name}' has no examples"
        assert len(dialect["examples"]) > 0

    @pytest.mark.parametrize("name", dialect_names())
    def test_index_file_lists_dialect(self, name):
        index_path = BUNDLED_DIR / "index.txt"
        index_content = index_path.read_text()
        assert name in index_content
