from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, ListView, ListItem, Label, Static, Input, ProgressBar
from textual.containers import Container, Vertical
import httpx
import asyncio
import re


class AwesomeList:
    def __init__(self, name: str, url: str, description: str = ""):
        self.name = name
        self.url = url
        self.description = description


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

    #main_container {{
        layout: horizontal;
        height: 1fr;
    }}

    #sidebar {{
        width: 30%;
        border-right: solid {COLORS["stone"]};
        background: {COLORS["panel"]};
    }}

    #content_container {{
        width: 70%;
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

    Label {{
        margin: 0 0;
    }}

    Static {{
        overflow-y: scroll;
    }}

    Input {{
        margin: 1 0;
    }}

    .title {{
        color: {COLORS["teal"]};
        text-style: bold;
    }}

    .section-title {{
        color: {COLORS["sage"]};
        text-style: bold;
    }}

    .description {{
        color: {COLORS["ash"]};
    }}

    .search-result {{
        color: {COLORS["ink"]};
    }}

    #progress {{
        height: 1;
    }}
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("/", "focus_search", "Search"),
        ("ctrl+s", "deep_search", "Deep Search"),
        ("o", "open_selected", "Open"),
        ("enter", "select_item", "Select"),
    ]

    POPULAR_LISTS = [
        # TUI-focused collections
        AwesomeList("awesome-tuis", "https://raw.githubusercontent.com/rothgar/awesome-tuis/main/README.md", "Curated list of TUI applications - 18k stars"),
        AwesomeList("awesome-ratatui", "https://raw.githubusercontent.com/ratatui/awesome-ratatui/main/README.md", "TUI apps and libraries built with Ratatui"),
        AwesomeList("awesome-textualize-projects", "https://raw.githubusercontent.com/oleksis/awesome-textualize-projects/main/README.md", "Projects related to Textualize (Textual, Rich)"),
        AwesomeList("toolleeo/awesome-cli-apps", "https://raw.githubusercontent.com/toolleeo/awesome-cli-apps-in-a-csv/master/README.md", "Largest collection of CLI/TUI tools - 2.4k stars"),
        
        # This app
        AwesomeList("awesome-tui", "https://raw.githubusercontent.com/12britz/awesome-tui/main/README.md", "Browse awesome lists in the terminal"),
        
        # AI & ML
        AwesomeList("awesome-ai", "https://raw.githubusercontent.com/awesome-orgs/awesome-ai/main/README.md", "Artificial Intelligence resources"),
        AwesomeList("awesome-ai-gateways", "https://raw.githubusercontent.com/12britz/awesome-ai-gateways/main/README.md", "LLM routing and gateway infrastructure"),
        AwesomeList("awesome-llms", "https://raw.githubusercontent.com/Hannibal046/Awesome-LLM/main/README.md", "Large Language Models resources"),
        AwesomeList("awesome-agents", "https://raw.githubusercontent.com/JoshuaOliphant/awesome-ai-agents/main/README.md", "AI Agents and Autonomous Systems"),
        AwesomeList("awesome-mlops", "https://raw.githubusercontent.com/visenger/awesome-mlops/main/README.md", "MLOps resources and tools"),
        
        # Programming Languages
        AwesomeList("awesome-python", "https://raw.githubusercontent.com/vinta/awesome-python/main/README.md", "Python resources"),
        AwesomeList("awesome-rust", "https://raw.githubusercontent.com/rust-unofficial/awesome-rust/main/README.md", "Rust resources"),
        AwesomeList("awesome-go", "https://raw.githubusercontent.com/avelino/awesome-go/main/README.md", "Go resources"),
        AwesomeList("awesome-nodejs", "https://raw.githubusercontent.com/sindresorhus/awesome-nodejs/main/readme.md", "Node.js resources"),
        AwesomeList("awesome-react", "https://raw.githubusercontent.com/enaqx/awesome-react/main/README.md", "React resources"),
        AwesomeList("awesome-vue", "https://raw.githubusercontent.com/vuejs/awesome-vue/main/README.md", "Vue.js resources"),
        
        # DevOps & Cloud
        AwesomeList("awesome-selfhosted", "https://raw.githubusercontent.com/awesome-selfhosted/awesome-selfhosted/main/README.md", "Self-hostable software"),
        AwesomeList("awesome-docker", "https://raw.githubusercontent.com/veggiemonk/awesome-docker/main/README.md", "Docker resources"),
        AwesomeList("awesome-kubernetes", "https://raw.githubusercontent.com/ramitsurana/awesome-kubernetes/main/README.md", "Kubernetes resources"),
        AwesomeList("awesome-terraform", "https://raw.githubusercontent.com/shuaibiyy/awesome-terraform/main/README.md", "Terraform resources"),
        AwesomeList("awesome-devops", "https://raw.githubusercontent.com/wmariuss/awesome-devops/main/README.md", "DevOps resources"),
        AwesomeList("awesome-sre", "https://raw.githubusercontent.com/dastergon/awesome-sre/main/README.md", "Site Reliability Engineering"),
        AwesomeList("awesome-aws", "https://raw.githubusercontent.com/donnemartin/awesome-aws/main/README.md", "AWS resources and tools"),
        
        # Tools & Productivity
        AwesomeList("awesome-cli", "https://raw.githubusercontent.com/awesome-shell/awesome-shell/main/README.md", "Command line tools"),
        AwesomeList("awesome-git", "https://raw.githubusercontent.com/dictcp/awesome-git/main/README.md", "Git resources"),
        AwesomeList("awesome-vim", "https://raw.githubusercontent.com/akrawchyk/awesome-vim/main/README.md", "Vim resources"),
        AwesomeList("awesome-terminal", "https://raw.githubusercontent.com/k4m4/awesome-terminal-music/main/README.md", "Terminal utilities"),
        
        # Databases
        AwesomeList("awesome-postgres", "https://raw.githubusercontent.com/dhamaniasad/awesome-postgres/main/README.md", "PostgreSQL resources"),
        AwesomeList("awesome-mongodb", "https://raw.githubusercontent.com/ramnes/awesome-mongodb/main/README.md", "MongoDB resources"),
        AwesomeList("awesome-redis", "https://raw.githubusercontent.com/JamzyWang/awesome-redis/main/README.md", "Redis resources"),
        
        # Security
        AwesomeList("awesome-security", "https://raw.githubusercontent.com/sbilly/awesome-security/main/README.md", "Security resources and tools"),
        AwesomeList("awesome-pentest", "https://raw.githubusercontent.com/enaqx/awesome-pentest/main/README.md", "Penetration testing resources"),
        AwesomeList("awesome-ctf", "https://raw.githubusercontent.com/apsdehal/awesome-ctf/main/README.md", "Capture The Flag resources"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="toolbar"):
            yield Input(placeholder="Search lists... (/ for deep search)", id="search-input")
        with Container(id="main_container"):
            with Vertical(id="sidebar"):
                yield Label("Awesome Lists", classes="title")
                yield ProgressBar(id="progress", show_percentage=False)
                yield Tree("All Lists", id="list_tree")
            with Vertical(id="content_container"):
                yield Static("Select a list to view\n\nPress / to search or Ctrl+S for deep GitHub search", id="content")
        with Container(id="shortcuts_bar"):
            yield Static("/: search  |  Ctrl+S: deep search  |  o: open  |  r: refresh  |  q: quit", classes="description")
        yield Footer()

    def on_mount(self) -> None:
        self.list_tree = self.query_one("#list_tree", Tree)
        self.content = self.query_one("#content", Static)
        self.search_input = self.query_one("#search-input", Input)
        self.progress = self.query_one("#progress", ProgressBar)

        self.all_lists = self.POPULAR_LISTS.copy()
        self.search_results = []
        self.load_lists()

    def load_lists(self) -> None:
        self.list_tree.clear()
        root = self.list_tree.root
        for lst in self.all_lists:
            root.add(f"{lst.name} - {lst.description[:40]}...", data=lst)
        self.list_tree.root.expand_all()

    def on_tree_node_selected(self, event: "Tree.NodeSelected") -> None:
        lst = event.node.data
        if isinstance(lst, AwesomeList):
            asyncio.create_task(self.load_list_content(lst))

    async def load_list_content(self, lst: AwesomeList) -> None:
        self.content.update(f"Loading {lst.name}...\n")
        self.progress.update(total=100, progress=0)
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(lst.url, timeout=60.0)
                if response.status_code == 200:
                    self.progress.update(progress=50)
                    content = self.parse_readme(response.text)
                    self.progress.update(progress=100)
                    self.content.update(content)
                else:
                    self.content.update(f"Failed to load: {response.status_code}")
        except Exception as e:
            self.content.update(f"Error: {str(e)}")

    def parse_readme(self, text: str) -> str:
        lines = text.split("\n")
        output = []
        current_section = ""

        for line in lines:
            if line.startswith("## "):
                current_section = line.replace("## ", "").strip()
                output.append(f"\n\033[1;38;2;167;192;128m◆ {current_section}\033[0m\n\n")
            elif line.startswith("- ["):
                match = re.match(r'- \[([^\]]+)\]\(([^)]+)\)', line)
                if match:
                    name, url = match.groups()
                    output.append(f"  \033[38;2;127;187;179m▸\033[0m {name}\n    \033[38;2;133;146;137m{url}\033[0m\n")
            elif line.startswith("- "):
                if not line.startswith("- [") and not line.startswith("- *"):
                    output.append(f"  \033[38;2;211;198;170m•\033[0m {line[2:]}\n")
            elif line.startswith("> "):
                output.append(f"\033[38;2;133;146;137m{line}\033[0m\n")
            elif line.strip() and len(line) > 10:
                if not line.startswith("#"):
                    output.append(f"{line}\n")

        return "".join(output)[:10000]

    def action_refresh(self) -> None:
        self.all_lists = self.POPULAR_LISTS.copy()
        self.search_results = []
        self.load_lists()
        self.content.update("Select a list to view")

    def action_focus_search(self) -> None:
        self.search_input.focus()

    async def action_deep_search(self) -> None:
        self.content.update("Searching GitHub for awesome lists...\n")
        self.progress.update(total=0, progress=0)

        query = self.search_input.value.strip() if self.search_input.value.strip() else "awesome"
        self.content.update(f"Deep searching GitHub for '{query}'...\n")

        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.github.com/search/repositories?q={query}+awesome+list+readme&sort=stars&order=desc&per_page=30"
                response = await client.get(url, headers={"Accept": "application/vnd.github.v3+json"}, timeout=30.0)

                if response.status_code == 200:
                    data = response.json()
                    repos = data.get("items", [])

                    if not repos:
                        self.content.update(f"No awesome lists found for '{query}'")
                        return

                    self.content.update(f"Found {len(repos)} awesome lists:\n\n")
                    self.search_results = []

                    for i, repo in enumerate(repos):
                        name = repo["full_name"]
                        url = repo.get("html_url", "")
                        description = repo.get("description", "No description")
                        stars = repo.get("stargazers_count", 0)

                        readme_url = f"https://raw.githubusercontent.com/{name}/main/README.md"
                        lst = AwesomeList(name, readme_url, description)
                        self.search_results.append(lst)

                        self.content.update(
                            f"\033[38;2;167;192;128m{name}\033[0m (\033[38;2;133;146;137m{stars:,} stars\033[0m)\n"
                            f"  {description}\n"
                            f"  {url}\n\n"
                        )
                        self.progress.update(total=len(repos), progress=i+1)

                    self.list_tree.clear()
                    root = self.list_tree.root
                    for lst in self.search_results:
                        root.add(f"★ {lst.name}", data=lst)
                    self.list_tree.root.expand_all()

                else:
                    self.content.update(f"GitHub API error: {response.status_code}")
        except Exception as e:
            self.content.update(f"Search error: {str(e)}")

    def action_open_selected(self) -> None:
        import subprocess
        selected = self.list_tree.selected_node
        if selected and isinstance(selected.data, AwesomeList):
            url = f"https://github.com/{selected.data.name}"
            subprocess.run(["open", url])

    def action_select_item(self) -> None:
        pass

    def on_input_submitted(self, event: "Input.Submitted") -> None:
        query = event.value.lower().strip()
        if not query:
            self.all_lists = self.POPULAR_LISTS.copy()
            self.load_lists()
            return

        self.list_tree.clear()
        root = self.list_tree.root

        results = [lst for lst in self.POPULAR_LISTS if query in lst.name.lower() or query in lst.description.lower()]

        if results:
            for lst in results:
                root.add(f"{lst.name}", data=lst)
            self.list_tree.root.expand_all()
            self.content.update(f"Found {len(results)} lists matching '{query}'")
        else:
            self.content.update(f"No lists found matching '{query}'\n\nPress Ctrl+S for deep GitHub search")


def main():
    app = AwesomeTUI()
    app.run()


if __name__ == "__main__":
    main()
