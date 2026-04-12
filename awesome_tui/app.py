from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, ListView, ListItem, Label, Static, Button, Input
from textual.containers import Container, Vertical, Horizontal
import httpx
import asyncio


class AwesomeList:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url


class AwesomeTUI(App):
    """Browse awesome lists in the terminal."""

    COLORS = {
        "paper": "#2d353b",
        "paper2": "#343f44",
        "panel": "#374247",
        "ink": "#d3c6aa",
        "stone": "#9da9a0",
        "ash": "#859289",
        "sage": "#a7c080",
        "teal": "#7fbbb3",
        "rose": "#e67e80",
        "violet": "#d699b6",
        "selection": "#425047",
    }

    CSS = f"""
    Screen {{
        background: {COLORS["paper"]};
    }}

    #toolbar {{
        height: 3;
        background: {COLORS["panel"]};
        border-bottom: solid {COLORS["stone"]};
        padding: 0 1;
    }}

    #toolbar Button {{
        margin: 0 1;
    }}

    #main_container {{
        layout: horizontal;
        height: 1fr;
    }}

    #sidebar {{
        width: 25%;
        border-right: solid {COLORS["stone"]};
        background: {COLORS["panel"]};
    }}

    #content_container {{
        width: 75%;
        padding: 1 2;
        background: {COLORS["paper"]};
    }}

    #shortcuts_bar {{
        height: 3;
        background: {COLORS["panel"]};
        border-top: solid {COLORS["stone"]};
        padding: 0 2;
    }}

    Tree {{
        background: {COLORS["panel"]};
        color: {COLORS["ink"]};
    }}

    Tree > .tree--highlight {{
        background: {COLORS["selection"]};
    }}

    ListView {{
        background: {COLORS["paper2"]};
    }}

    ListItem {{
        padding: 0 1;
    }}

    ListItem:hover {{
        background: {COLORS["selection"]};
    }}

    ListItem:focus {{
        background: {COLORS["selection"]};
    }}

    ListItem:focus {{
        background: {COLORS["sage"]};
        color: {COLORS["paper"]};
    }}

    Label {{
        margin: 0 0;
    }}

    Static {{
        overflow-y: scroll;
    }}

    Button {{
        background: {COLORS["paper2"]};
        color: {COLORS["ink"]};
    }}

    Button:hover {{
        background: {COLORS["sage"]};
        color: {COLORS["paper"]};
    }}

    Input {{
        margin: 1 0;
    }}

    .title {{
        color: {COLORS["teal"]};
        text-style: bold;
    }}

    .category {{
        color: {COLORS["sage"]};
        text-style: bold;
    }}

    .item {{
        color: {COLORS["ink"]};
    }}

    .description {{
        color: {COLORS["ash"]};
    }}

    .url {{
        color: {COLORS["teal"]};
        text-style: italic;
    }}

    .header-title {{
        color: {COLORS["ink"]};
        text-style: bold;
    }}

    .badge {{
        color: {COLORS["paper"]};
        background: {COLORS["sage"]};
        padding: 0 1;
    }}
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("o", "open_url", "Open URL"),
        ("/", "focus_search", "Search"),
    ]

    POPULAR_LISTS = [
        AwesomeList("awesome-ai", "https://raw.githubusercontent.com/awesome-orgs/awesome-ai/main/README.md"),
        AwesomeList("awesome-ai-gateways", "https://raw.githubusercontent.com/12britz/awesome-ai-gateways/main/README.md"),
        AwesomeList("awesome-llms", "https://raw.githubusercontent.com/Hannibal046/Awesome-LLM/main/README.md"),
        AwesomeList("awesome-selfhosted", "https://raw.githubusercontent.com/awesome-selfhosted/awesome-selfhosted/main/README.md"),
        AwesomeList("awesome-go", "https://raw.githubusercontent.com/avelino/awesome-go/main/README.md"),
        AwesomeList("awesome-python", "https://raw.githubusercontent.com/vinta/awesome-python/main/README.md"),
        AwesomeList("awesome-rust", "https://raw.githubusercontent.com/rust-unofficial/awesome-rust/main/README.md"),
        AwesomeList("awesome-tui", "https://raw.githubusercontent.com/12britz/awesome-tui/main/README.md"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="toolbar"):
            yield Input(placeholder="Search awesome lists...", id="search-input")
        with Container(id="main_container"):
            with Vertical(id="sidebar"):
                yield Label("Awesome Lists", classes="title")
                yield Tree("Popular Lists", id="list_tree")
            with Vertical(id="content_container"):
                yield Static("Select a list to view", id="content")
        with Container(id="shortcuts_bar"):
            yield Static("o: open url  |  /: search  |  r: refresh  |  q: quit", classes="description")
        yield Footer()

    def on_mount(self) -> None:
        self.list_tree = self.query_one("#list_tree", Tree)
        self.content = self.query_one("#content", Static)
        self.search_input = self.query_one("#search-input", Input)

        self.current_data = {}
        self.load_lists()

    def load_lists(self) -> None:
        self.list_tree.clear()
        root = self.list_tree.root
        for lst in self.POPULAR_LISTS:
            root.add(f"[{lst.name}]", data=lst)
        self.list_tree.root.expand_all()

    def on_tree_node_selected(self, event: "Tree.NodeSelected") -> None:
        lst = event.node.data
        if isinstance(lst, AwesomeList):
            asyncio.create_task(self.load_list_content(lst))

    async def load_list_content(self, lst: AwesomeList) -> None:
        self.content.update(f"Loading {lst.name}...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(lst.url, timeout=30.0)
                if response.status_code == 200:
                    content = self.parse_readme(response.text)
                    self.content.update(content)
                    self.current_data = {"type": "readme", "content": content}
                else:
                    self.content.update(f"Failed to load: {response.status_code}")
        except Exception as e:
            self.content.update(f"Error: {str(e)}")

    def parse_readme(self, text: str) -> str:
        lines = text.split("\n")
        output = []
        in_category = False
        category_name = ""

        for line in lines:
            if line.startswith("## "):
                in_category = True
                category_name = line.replace("## ", "").replace(" ##", "")
                output.append(f"\n{COLORS['sage']}{category_name}{COLORS['ink']}\n")
            elif line.startswith("### ") and not in_category:
                output.append(f"\n{COLORS['teal']}{line.replace('### ', '')}{COLORS['ink']}\n")
            elif line.startswith("- ["):
                parts = line.split("](")
                if len(parts) == 2:
                    name = parts[0].replace("- [", "").replace("]", "").replace("*", "")
                    url = parts[1].replace(")", "").replace("#readme)", "")
                    output.append(f"  {COLORS['teal']}#{COLORS['ink']} {name} {COLORS['ash']}({url}){COLORS['ink']}\n")
                else:
                    output.append(f"  {COLORS['ink']}{line}\n")
            elif line.startswith("- "):
                output.append(f"  {COLORS['ink']}{line}\n")
            elif line.startswith("> "):
                output.append(f"{COLORS['ash']}{line}{COLORS['ink']}\n")
            elif line.strip():
                output.append(f"{COLORS['ink']}{line}\n")

        return "".join(output)

    def action_refresh(self) -> None:
        self.load_lists()
        self.content.update("Select a list to view")

    def action_open_url(self) -> None:
        import subprocess
        if self.current_data.get("type") == "readme":
            subprocess.run(["open", "https://github.com"])

    def action_focus_search(self) -> None:
        self.search_input.focus()

    def on_input_submitted(self, event: "Input.Submitted") -> None:
        query = event.value.lower()
        if query:
            self.tree.clear()
            root = self.tree.root
            for lst in self.POPULAR_LISTS:
                if query in lst.name.lower():
                    root.add(f"[{lst.name}]", data=lst)
            self.tree.root.expand_all()


def main():
    app = AwesomeTUI()
    app.run()


if __name__ == "__main__":
    main()
