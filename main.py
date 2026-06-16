#imports
from rich.text import Text

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static, DirectoryTree, DataTable

from pathlib import Path

#app
#TODO

PROJECT_DIR = Path.cwd()

def Scan():
    rows = [
        ("File", "TODO"),
    ]
    
    data = {}

    for path in PROJECT_DIR.iterdir():
        if not path.is_file():
            continue

        file_name = path.name
        todo = 0
        data[file_name] = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.readlines()
                
                for line in content:
                    if line.startswith("#TODO"):
                        todo += 1
                        splitted = line.split("/", 2)
                        try:
                            data[file_name].append((splitted[1], splitted[2]))
                        except Exception as e:
                            print(e)
                            quit()
                rows.append((file_name, todo))
        except Exception as e:
            print(e)
            quit()
        
    return rows, data

ROWS, DATA = Scan()

# dark mode taken from textual docs as way of learning and starting the app
class TuduApp(App):
    
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    CSS_PATH = "textual_css.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical():
            with Horizontal(classes="height-one border-gray"):
                yield DirectoryTree(PROJECT_DIR, classes="width-two height-one border-gray")
                yield DataTable(classes="width-one height-one border-gray")
            with Horizontal(classes="height-one border-gray"):
                yield DataTable(classes="width-two height-one border-gray")
                yield Static("Four", classes="width-one height-one border-gray")
                yield Static("Five", classes="width-one height-one border-gray")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        for row in ROWS[1:]:
            styled_row = [
                Text(str(cell)) for cell in row
            ]
            table.add_row(*styled_row)


if __name__ == "__main__":
    app = TuduApp()
    app.run()
