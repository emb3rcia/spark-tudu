# imports
import subprocess
import tomllib

from rich.text import Text

from textual.app import App, ComposeResult
from textual.binding import BindingType, Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, DirectoryTree, DataTable, ListItem, ListView, Label

from pathlib import Path

# app

PROJECT_DIR = Path.cwd()

IGNORED = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
}

MARKERS = [
    "TODO",
    "FIXME",
    "BUG",
    "HACK",
    "NOTE",
    "IDEA",
    "REVIEW",
    "SECURITY",
    "DOCS",
    "TEST",
    "PERF",
    "CLEANUP",
    "BLOCKED",
]

# used ai for hex code due to time spent for searching every one of them it would take
MARKER_COLORS = {
    "TODO": "#00ffff",
    "FIXME": "#ffff00",
    "BUG": "#ff0000",
    "HACK": "#ff00ff",
    "NOTE": "#0088ff",
    "IDEA": "#00ff88",
    "REVIEW": "#aa66ff",
    "SECURITY": "#3366ff",
    "DOCS": "#33cc66",
    "TEST": "#ff8800",
    "PERF": "#a86f32",
    "CLEANUP": "#66ff66",
    "BLOCKED": "#ff3333",
}

PRIORITIES = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
    "OPTIONAL",
]

PRIORITY_COLORS = {
    "CRITICAL": "#ff0000",
    "HIGH": "#ff8800",
    "MEDIUM": "#ffff00",
    "LOW": "#00ccff",
    "OPTIONAL": "#888888",
    "UNKNOWN": "#ffffff",
}

COMMENT_PREFIXES = {
    ".py": ["#"],
    ".pyi": ["#"],
    ".pyw": ["#"],
    ".pyx": ["#"],
    ".px": ["#"],
    ".pxi": ["#"],
    ".c": ["//", "/*", "*"],
    ".h": ["//", "/*", "*"],
    ".cpp": ["//", "/*", "*"],
    ".hpp": ["//", "/*", "*"],
    ".cc": ["//", "/*", "*"],
    ".hh": ["//", "/*", "*"],
    ".cxx": ["//", "/*", "*"],
    ".hxx": ["//", "/*", "*"],
    ".js": ["//", "/*", "*"],
    ".jsx": ["//", "/*", "*"],
    ".ts": ["//", "/*", "*"],
    ".tsx": ["//", "/*", "*"],
    ".md": ["#", "<!--"],
}

def get_config_editor():
    config_path = PROJECT_DIR / "spark-tudu.toml"

    if not config_path.exists():
        return {
            "command": ["code", "-g", "{file}:{line}"],
            "wait": False,
            "terminal": False
        }

    with open(config_path, "rb") as file:
        config = tomllib.load(file)

    return config.get("editor", {})     

def build_editor_command(command_template, file_path, line_number):
    return [
        part.replace("{file}", str(file_path)).replace("{line}", str(line_number)) for part in command_template
    ]

def open_in_editor(file_name, line_number):
    editor = get_config_editor()

    command_template = editor.get("command", ["code", "-g", "{file}:{line}"])
    wait = editor.get("wait", False)
    terminal = editor.get("terminal", False)

    file_path = PROJECT_DIR / file_name

    command = build_editor_command(command_template, file_path, line_number)

    if terminal:
        with app.suspend():
            subprocess.run(command)
    elif wait:
        subprocess.run(command)
    else:
        subprocess.Popen(command)

def scan():
    rows = [
        ("File", *MARKERS),
    ]

    data = {}

    for path in PROJECT_DIR.rglob("*"):
        if any(part in IGNORED for part in path.parts):
            continue

        if not path.is_file():
            continue

        if path.suffix not in COMMENT_PREFIXES:
            continue

        file_name = str(path.relative_to(PROJECT_DIR))
        counts = {marker: 0 for marker in MARKERS}
        file_items = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.readlines()
                for line_number, line in enumerate(content, start=1):
                    line_clean = line.strip()
                    prefixes = COMMENT_PREFIXES[path.suffix]

                    for prefix in prefixes:
                        if not line_clean.startswith(prefix):
                            continue

                        without_prefix = line_clean[len(prefix):].strip()

                        for marker in MARKERS:
                            if not without_prefix.startswith(marker + "/"):
                                continue

                            split_line = without_prefix.split("/", 3)

                            if len(split_line) < 4:
                                continue
                            
                            priority = split_line[1].strip().upper()
                            if priority not in PRIORITIES:
                                priority = "UNKNOWN"
                            comment = split_line[2]
                            deadline = split_line[3]
                            deadline = deadline.removesuffix("-->").strip()
                            deadline = deadline.removesuffix("*/").strip()

                            counts[marker] += 1
                            file_items.append((line_number, marker, priority, comment, deadline))

                if file_items:
                    data[file_name] = file_items
                    rows.append((file_name, *[counts[marker] for marker in MARKERS]))
        except Exception as e:
            print(e)
            quit()

    return rows, data


ROWS, DATA = scan()


def list_items_compose():
    list_items = []

    found_items = []

    for file_name, found in DATA.items():
        for line_number, found_type, found_priority, found_name, found_date in found:
            color = MARKER_COLORS.get(found_type, "white")
            color_priority = PRIORITY_COLORS.get(found_priority, "white")
            text = Text(f"{file_name}:{line_number}, ")
            text.append(found_priority, style=color_priority)
            text.append(" - ")
            text.append(found_type, style=color)
            text.append(f": {found_name}")
            list_items.append(
                ListItem(
                    Label(text)
                )
            )
            found_items.append(
                (file_name, line_number, found_type, found_priority, found_name.strip(), found_date.strip())
            )
    return list_items, found_items

list_items_composed = []
found_items_composed = []

# dark mode taken from textual docs as way of learning and starting the app
class TuduApp(App):

    TITLE = "spark-tudu"

    BINDINGS: list[BindingType] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("r", "rescan", "Rescan files"),
        Binding("o", "open_selected_marker", "Open selected marker"),
    ]

    CSS_PATH = "textual_css.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Horizontal(classes="height-one border-gray"):
                yield DirectoryTree(PROJECT_DIR, classes="width-two height-one border-gray")
                yield DataTable(classes="width-one height-one border-gray")
            with Horizontal(classes="height-one border-gray"):
                yield ListView(classes="width-two height-one border-gray",)
                yield Label("Four", classes="width-two height-one border-gray", id="details")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_rescan(self) -> None:
        global ROWS, DATA
        ROWS, DATA = scan()
        global list_items_composed, found_items_composed
        list_items_composed, found_items_composed = list_items_compose()
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_column("File")
        for marker in MARKERS:
            color = MARKER_COLORS.get(marker, "white")
            table.add_column(Text(marker, style=color))
        for row in ROWS[1:]:
            styled_row = [
                Text(str(cell)) for cell in row
            ]
            table.add_row(*styled_row)

        details = self.query_one("#details")

        list_view = self.query_one(ListView)
        list_view.clear()

        if not found_items_composed:
            details.update("No markers found!")
            return
        
        for list_item in list_items_composed:
            list_view.append(list_item)
        index_list = list_view.index

        if index_list is None:
            index_list = 0

        self.show_details(index_list)
        list_view.focus()

    def action_open_selected_marker(self) -> None:
        list_view = self.query_one(ListView)
        index_list = list_view.index
        if index_list is None:
            index_list = 0
        
        file_name, line_number, found_type, found_priority, comment, deadline = found_items_composed[index_list]

        open_in_editor(file_name, line_number)

    def on_list_view_selected(self, event: ListView.Selected) -> None:

        details = self.query_one("#details")

        if not found_items_composed:
            details.update("No markers found")
            return

        list_view = event.list_view
        index_list = list_view.index

        if index_list is None:
            index_list = 0

        self.show_details(index_list)

    def on_mount(self) -> None:
        self.action_rescan()

    def show_details(self, index: int) -> None:
        details = self.query_one("#details")

        file_name, line_number, found_type, found_priority, comment, deadline = found_items_composed[index]

        color = MARKER_COLORS.get(found_type, "white")
        color_priority = PRIORITY_COLORS.get(found_priority, "white")
        details_string = Text()
        details_string.append(f"File: {file_name}\n")
        details_string.append(f"Line: {line_number}\n")
        details_string.append(f"Type: ")
        details_string.append(found_type, style=color)
        details_string.append(f"\nPriority: ")
        details_string.append(found_priority, style=color_priority)
        details_string.append(f"\n\nComment: \n{comment}")
        if deadline:
            details_string.append(f"\n\nDeadline: \n{deadline}")

        details.update(details_string)


if __name__ == "__main__":
    app = TuduApp()
    app.run()
