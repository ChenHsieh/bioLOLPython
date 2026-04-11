# bioLOLPython/cli.py
import sys
from bioLOLPython.interpreter import handle_line, reset_bio_vars, set_dialect
from bioLOLPython.dialects import list_dialects, dialect_names, reload_dialects


def repl(dialect_name="lolcat"):
    """Interactive REPL mode."""
    set_dialect(dialect_name)
    print(f"🐾 bioLOL REPL v0.1 ({dialect_name} mode)")
    print(f"   Type bio commands. Ctrl+C or 'exit' to quit.\n")
    reset_bio_vars()
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if line.lower() in ("exit", "quit"):
                break
            if line:
                handle_line(line, dialect_name=dialect_name)
    except KeyboardInterrupt:
        pass
    print("\n👋 kthxbye!")


def print_dialects():
    """Print available dialects."""
    print("Available dialects:\n")
    for d in list_dialects():
        print(f"  {d['name']:12s} {d['era']:14s}  {d['description']}")
    print()


def do_update(force=False):
    """Fetch latest dialects from remote registry."""
    from bioLOLPython.dialects.remote import update_dialects
    print("🔄 Updating dialects from remote registry...")
    results = update_dialects(force=force)
    for name, status in results:
        icon = "✅" if status == "updated" else "📦" if status == "cached" else "❌"
        print(f"  {icon} {name}: {status}")
    reload_dialects()
    print(f"\n{len(dialect_names())} dialect(s) available.")


def main():
    dialect = "lolcat"
    args = sys.argv[1:]

    if "--list-dialects" in args:
        print_dialects()
        return

    if "--update" in args:
        force = "--force" in args
        do_update(force=force)
        return

    if "--dialect" in args:
        idx = args.index("--dialect")
        if idx + 1 < len(args):
            dialect = args[idx + 1]
            if dialect not in dialect_names():
                print(f"❌ Unknown dialect '{dialect}'.")
                print_dialects()
                return
            args = args[:idx] + args[idx + 2:]
        else:
            print("❌ --dialect requires a name argument.")
            print_dialects()
            return

    if not args:
        repl(dialect)
        return

    filename = args[0]
    reset_bio_vars()
    set_dialect(dialect)
    with open(filename) as f:
        for line in f:
            handle_line(line.strip(), dialect_name=dialect)


if __name__ == "__main__":
    main()
