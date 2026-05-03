from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path


# Encapsulation: extension parsing stays private
class FileItem:

    def __init__(self, path):
        self._path = path
        self._ext = path.suffix.lstrip(".").lower()

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path.name

    def get_extension(self):
        return self._ext


# Abstraction: defines the interface every rule must follow
class BaseRule(ABC):

    @abstractmethod
    def get_category(self, extension):
        pass

    @property
    @abstractmethod
    def category_names(self):
        pass


# Inheritance: concrete implementation of BaseRule
class DefaultRule(BaseRule):

    _GROUPS = {
        "Images":      "jpg jpeg png gif webp bmp svg",
        "Documents":   "pdf doc docx txt xls xlsx csv ppt pptx",
        "Videos":      "mp4 mkv avi mov wmv",
        "Audio":       "mp3 wav flac aac ogg",
        "Archives":    "zip rar 7z tar gz",
        "Code":        "py js ts html css cpp c sh json yaml",
        "Executables": "exe msi dmg apk",
    }
    _MAP = {ext: cat for cat, exts in _GROUPS.items() for ext in exts.split()}

    def get_category(self, extension):
        return self._MAP.get(extension, "Others")

    @property
    def category_names(self):
        return list(self._GROUPS.keys()) + ["Others"]


# Polymorphism: overrides get_category to apply renamed folder labels
class CustomRule(DefaultRule):

    def __init__(self, rename_map):
        self._rename = rename_map

    def get_category(self, extension):
        raw = super().get_category(extension)
        return self._rename.get(raw, raw)

    @property
    def category_names(self):
        return [self._rename.get(c, c) for c in super().category_names]


# Polymorphism: overrides get_category to skip certain extensions
class FilterRule(DefaultRule):

    def __init__(self, ignore):
        self._ignore = {e.lstrip(".").lower() for e in ignore}

    def get_category(self, extension):
        if extension in self._ignore:
            return None  # signals Organizer to skip this file
        return super().get_category(extension)


# Abstraction: Only class allowed to interact with the file system
class FileManager:

    def ensure_dir(self, path):
        path.mkdir(parents=True, exist_ok=True)

    def move(self, source, dest_dir):
        dest = dest_dir / source.name
        n = 1
        while dest.exists():
            dest = dest_dir / f"{source.stem}_{n}{source.suffix}"
            n += 1
        source.rename(dest)

    def list_files(self, directory):
        # skip hidden files like .DS_Store or .gitignore
        return [p for p in directory.iterdir() if p.is_file() and not p.name.startswith(".")]


# Coordinates scanning, categorizing, and moving files
class Organizer:

    def __init__(self, rule, file_manager):
        self._rule = rule
        self._fm = file_manager

    def organize(self, target_dir):
        summary = defaultdict(int)
        known = set(self._rule.category_names)

        for path in self._fm.list_files(target_dir):
            item = FileItem(path)
            category = self._rule.get_category(item.get_extension())

            if category is None or item.name in known:
                continue

            dest = target_dir / category
            self._fm.ensure_dir(dest)
            self._fm.move(item.path, dest)
            summary[category] += 1

        return dict(summary)


# Manages the menu and user input
class CLIHandler:

    LINE = "─" * 40

    def run(self):
        print(f"\n{self.LINE}\n    📂  File Organizer\n{self.LINE}")
        while True:
            print("\n  1. Organize a folder")
            print("  2. Organize with custom folder names")
            print("  3. Exit\n")
            choice = input("  Select: ").strip()

            if choice == "3":
                print("\n  Goodbye!\n")
                break
            elif choice in ("1", "2"):
                self._handle(use_custom=(choice == "2"))
            else:
                print("\n  ⚠  Enter 1, 2, or 3.\n")

    def _handle(self, use_custom):
        path = self._prompt_path()
        if path is None:
            return

        if use_custom:
            rule = self._build_custom_rule()
        else:
            raw = input("  Extensions to ignore (e.g. tmp log), or Enter to skip: ").split()
            rule = FilterRule(raw) if raw else DefaultRule()

        try:
            summary = Organizer(rule, FileManager()).organize(path)
        except PermissionError:
            print("\n  ⚠  Permission denied.\n")
            return

        self._print_summary(summary)

    def _prompt_path(self):
        hint = Path.home() / "Downloads"
        raw = input(f"\n  Folder path (e.g. {hint})\n  or Enter for current folder: ").strip()
        path = Path(raw).expanduser().resolve() if raw else Path.cwd()

        if not path.is_dir():
            print(f"\n  ⚠  Not a valid folder: {path}\n")
            return None
        return path

    def _build_custom_rule(self):
        print("\n  Rename categories (Enter to keep default):\n")
        rename_map = {}
        for name in DefaultRule().category_names:
            new = input(f"    {name} → ").strip()
            if new and new != name:
                rename_map[name] = new
        return CustomRule(rename_map)

    def _print_summary(self, summary):
        total = sum(summary.values())
        print(f"\n{self.LINE}\n  ✅  Done!\n{self.LINE}")
        if not summary:
            print("  No files to organize.")
        else:
            for cat, n in sorted(summary.items()):
                print(f"  {cat + '/':<22} {n} file{'s' if n != 1 else ''}")
            print(self.LINE)
            print(f"  {'Total':<22} {total} file{'s' if total != 1 else ''}")
        print()


if __name__ == "__main__":
    CLIHandler().run()