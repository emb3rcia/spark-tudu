# imports
import subprocess
import tomllib
import datetime
import json
import argparse

from rich.text import Text

from textual.app import App, ComposeResult
from textual.binding import BindingType, Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, DirectoryTree, DataTable, ListItem, ListView, Label
from textual.screen import ModalScreen

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

CURRENT_FILTER = None

FILTER_CYCLING = [
    None,
    *MARKERS
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

PRIORITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "OPTIONAL": 4,
    "UNKNOWN": 5,
}

DEFAULT_EDITOR = {
    "command": ["code", "-g", "{file}:{line}"],
    "wait": False,
    "terminal": False,
}

DEFAULT_COMMENT_PREFIXES = {
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

EDITOR = DEFAULT_EDITOR.copy()
COMMENT_PREFIXES = DEFAULT_COMMENT_PREFIXES.copy()

def get_config():
    config_path = PROJECT_DIR / "spark-tudu.toml"

    editor = DEFAULT_EDITOR.copy()
    comment_prefixes = DEFAULT_COMMENT_PREFIXES.copy()

    if not config_path.exists():
        return editor, comment_prefixes

    with open(config_path, "rb") as file:
        config = tomllib.load(file)

    editor.update(config.get("editor", {}))

    configured_prefixes = (
        config.get("files", {})
        .get("comment_prefixes", {})
    )

    if not isinstance(configured_prefixes, dict):
        raise ValueError("files.comment_prefixes must be a TOML table")

    for extension, prefixes in configured_prefixes.items():
        if not isinstance(extension, str) or not extension.startswith("."):
            raise ValueError(
                f"Invalid file extension in comment prefixes: {extension!r}"
            )

        if not isinstance(prefixes, list) or not all(
            isinstance(prefix, str) and prefix
            for prefix in prefixes
        ):
            raise ValueError(
                f"Comment prefixes for {extension!r} must be an array of non-empty strings"
            )

    comment_prefixes.update(configured_prefixes)

    return editor, comment_prefixes

def build_editor_command(command_template, file_path, line_number):
    return [
        part.replace("{file}", str(file_path)).replace("{line}", str(line_number)) for part in command_template
    ]

def open_in_editor(file_name, line_number, app):
    command_template = EDITOR.get("command", ["code", "-g", "{file}:{line}"])
    wait = EDITOR.get("wait", False)
    terminal = EDITOR.get("terminal", False)

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

    markers_total_count = {marker: 0 for marker in MARKERS}

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
                            markers_total_count[marker] += 1
                            file_items.append((line_number, marker, priority, comment, deadline))

                if file_items:
                    data[file_name] = file_items
                    rows.append((file_name, *[counts[marker] for marker in MARKERS]))
        except Exception as e:
            print(e)
            quit()

    rows.insert(1, ("TOTAL", *[markers_total_count[marker] for marker in MARKERS]))

    return rows, data


ROWS = []
DATA = {}


def list_items_compose():
    list_items = []

    found_items = []

    for file_name, found in DATA.items():
        for line_number, found_type, found_priority, found_name, found_date in found:
            if CURRENT_FILTER != None and found_type != CURRENT_FILTER:
                continue
            found_items.append(
                (file_name, line_number, found_type, found_priority, found_name.strip(), found_date.strip())
            )
    
    found_items.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(item[3], 999),
            item[0],
            item[1],
        )
    )
    for file_name, line_number, found_type, found_priority, found_name, found_date in found_items:
        color = MARKER_COLORS.get(found_type, "white")
        color_priority = PRIORITY_COLORS.get(found_priority, "white")
        text = Text(f"{file_name}:{line_number} [")
        text.append(found_priority, style=color_priority)
        text.append("] - ")
        text.append(found_type, style=color)
        text.append(f": {found_name}")
        list_items.append(
            ListItem(
                Label(text)
            )
        )

    return list_items, found_items

list_items_composed = []
found_items_composed = []

class ShowPopup(ModalScreen):
    BINDINGS: list[BindingType] = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close"),
        Binding("space", "dismiss", "Close"),
    ]
    def __init__(self, string: str) -> None:
        super().__init__()
        self.string = str(string)

    def compose(self) -> ComposeResult:
        yield Label(self.string, id="popup")

    def action_dismiss(self) -> None:
        self.dismiss()


# dark mode taken from textual docs as way of learning and starting the app
class TuduApp(App):

    TITLE = f"spark-tudu | Filter: {str(CURRENT_FILTER)}" if CURRENT_FILTER != None else f"spark-tudu | Filter: All"

    BINDINGS: list[BindingType] = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("r", "rescan", "Rescan files"),
        Binding("o", "open_selected_marker", "Open selected marker"),
        Binding("m", "export_md", "Export in MD format"),
        Binding("j", "export_json", "Export in JSON format"),
        Binding("c", "cycle_filter", "Cycle filter"),
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

    def action_cycle_filter(self) -> None:
        global CURRENT_FILTER, FILTER_CYCLING
        if CURRENT_FILTER in FILTER_CYCLING:
            index = FILTER_CYCLING.index(CURRENT_FILTER)
        else:
            index = 0

        index += 1

        if index >= len(FILTER_CYCLING):
            index = 0

        CURRENT_FILTER = FILTER_CYCLING[index]
        self.title = f"spark-tudu | Filter: {str(CURRENT_FILTER)}" if CURRENT_FILTER != None else f"spark-tudu | Filter: All"
        global list_items_composed, found_items_composed
        list_items_composed, found_items_composed = list_items_compose()
        list_view = self.query_one(ListView)
        list_view.clear()

        details = self.query_one("#details")

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

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_rescan(self) -> None:
        global ROWS, DATA, EDITOR, COMMENT_PREFIXES
        EDITOR, COMMENT_PREFIXES = get_config()
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
        if found_items_composed:
            file_name, line_number, found_type, found_priority, comment, deadline = found_items_composed[index_list]

            open_in_editor(file_name, line_number, self)
    
    def action_export_md(self) -> None:
        if found_items_composed:
            string_to_export = f"# spark-tudu export {str(datetime.datetime.now())[0:19]}\n\n"
            for file_name, line_number, found_type, found_priority, comment, deadline in found_items_composed:
                string_to_export += f"## {file_name}:{line_number} [{found_priority}] {found_type}\nFile name: {file_name}\nLine: {line_number}\nPriority:{found_priority}\n\nComment:\n{comment}\n\nDeadline:\n{deadline}\n\n"
            with open(f"spark-tudu-export-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md", "w+", encoding="utf-8") as file:
                file.writelines(string_to_export)
            self.push_screen(ShowPopup("Exported to Markdown"))
        else:
            self.push_screen(ShowPopup("No markers to export"))

    def action_export_json(self) -> None:
        if found_items_composed:
            to_export = {
                "exported_at": str(datetime.datetime.now())[0:19],
                "items": {}
            }
            for file_name, line_number, found_type, found_priority, comment, deadline in found_items_composed:
                to_export["items"][f"{file_name}:{line_number}"] = {
                    "file_name": file_name,
                    "line_number": line_number,
                    "type": found_type,
                    "priority": found_priority,
                    "comment": comment,
                    "deadline": deadline,
                }
            with open(f"spark-tudu-export-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w+", encoding="utf-8") as file:
                json.dump(to_export, file, indent=4)
            self.push_screen(ShowPopup("Exported to JSON"))
        else:
            self.push_screen(ShowPopup("No markers to export"))


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
            try:
                deadline_composed = datetime.datetime.strptime(deadline, "%d.%m.%Y").date()
                present = datetime.datetime.now().date()
                if present > deadline_composed:
                    delta = present-deadline_composed
                    details_string.append(f"\n\nDeadline:\nOverdue by {delta.days} days!")
                else:
                    delta = deadline_composed-present
                    if delta.days:
                        details_string.append(f"\n\nDeadline:\nDue in {delta.days} days")
                    else:
                        details_string.append(f"\n\nDeadline:\nDue today!")
            except Exception as e:
                details_string.append(f"\n\nDeadline: \n{deadline}")

        details.update(details_string)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spark-tudu",
        description="Scan a project for structured comment markers.",
        epilog="Marker syntax documentation: https://github.com/emb3rcia/spark-tudu#syntax",
    )

    parser.add_argument(
        "project_dir",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        metavar="PROJECT_DIR",
        help="Directory to scan. Defaults to the current working directory.",
    )

    return parser

def resolve_project_dir(parser: argparse.ArgumentParser, path: Path) -> Path:
    project_dir = path.expanduser().resolve()
    if not project_dir.exists():
        parser.error(f"Project directory doesn't exist: {project_dir}")

    if not project_dir.is_dir():
        parser.error(f"Project path is not a directory: {project_dir}")
    
    return project_dir

def main() -> None:
    global PROJECT_DIR, EDITOR, COMMENT_PREFIXES

    parser = build_parser()
    args = parser.parse_args()

    PROJECT_DIR = resolve_project_dir(parser, args.project_dir)

    EDITOR, COMMENT_PREFIXES = get_config()

    app = TuduApp()
    app.run()
