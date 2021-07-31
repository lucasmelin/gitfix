"""CLI event loop and terminal printing functions."""
import re
import sys

from blessed import Terminal
from rich import box
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.table import Table

from gitfix import git_states


def parse_md(md):
    """Parse markdown and return a Rich markdown object."""
    table_re = r"(^|[^|]\n)((?:^\|[^\n]*\|(?:\n|$))+)([^|]|$)"
    md = re.sub(r"\n([\r\t ]*\n)+", r"\n\n", md, flags=re.MULTILINE)
    md = re.sub(r"^[\t ]*\|", r"|", md, flags=re.MULTILINE)
    md = re.sub(r"\|[\t ]*$", r"|", md, flags=re.MULTILINE)
    tables = []
    md = re.sub(
        table_re,
        lambda match: parse_md_table(match, tables),
        md,
        flags=re.MULTILINE | re.S,
    )
    console = Console()
    with console.capture() as capture:
        console.print(
            Markdown(md, inline_code_lexer="bash", inline_code_theme="monokai")
        )
    formated_text = capture.get()
    for i in range(len(tables)):
        formated_text = re.sub("<#MD-TABLE-" + str(i) + "#>", tables[i], formated_text)
    return re.sub(r"<br/?>", r"\n", formated_text).strip()


def parse_md_table(match, tables_memo):
    """Parse a markdown table and return a Rich markdown object."""
    [table_header, table_body, columns] = split_md_table(match.group(2))
    b = box.Box("    \n    \n══╪═\n    \n┈┈┼┈\n┈┈┼┈\n    \n    ")
    table = Table(
        box=b, show_header=False, show_edge=False, border_style=Style(color="#222222")
    )
    for col_align in columns:
        table.add_column(None, justify=col_align)
    sty_header = Style(bgcolor="yellow", color="#000000", bold=True)
    sty_odd = Style(bgcolor="#111111", color="white")
    sty_even = Style(bgcolor="#222222", color="white")
    for row in table_header:
        row = map(Align.center, row)
        table.add_row(*row, style=sty_header)
    for num, row in enumerate(table_body, start=1):
        style = sty_even if (num % 2 == 0) else sty_odd
        # Format any code blocks in table
        formatted_row = [
            Markdown(col, inline_code_lexer="bash", inline_code_theme="monokai")
            for col in row
        ]
        table.add_row(*formatted_row, style=style)

    console = Console()
    with console.capture() as capture:
        console.print(table)
    formated_text = "\n".join(capture.get().split("\n")[0:-1])
    before = "" if match.group(1) == "\n\n" else "\n"
    after = "  " if match.group(3) == "\n" else "  \n"
    tables_memo.append(before + formated_text)
    return f"{match.group(1)}<#MD-TABLE-{len(tables_memo) - 1}#>{after}{match.group(3)}"


def map_md_table_align_col(cell):
    """Map markdown table column alignments."""
    if re.match(r"^\s*:-+:\s*$", cell):
        return "center"
    elif re.match(r"^\s*-+:\s*$", cell):
        return "right"
    else:
        return "left"


def split_md_table(md_table):
    """Split a markdown table into header, body and columns."""
    md_table = re.sub(r"^\||\|$", "", md_table, flags=re.MULTILINE)
    table_header = []
    table_body = []
    columns = []
    table = list(
        map(
            lambda row: list(map(lambda cell: cell.strip(), row.split("|"))),
            md_table.strip().split("\n"),
        )
    )
    has_header = False
    for row in table:
        if re.match(r"^\s*:?-+:?\s*$", row[0]):
            has_header = True
    in_header = has_header
    for row in table:
        if in_header:
            if re.match(r"^\s*:?-+:?\s*$", row[0]):
                in_header = False
                columns = map(map_md_table_align_col, row)
            else:
                table_header.append(row)
        else:
            table_body.append(row)
    return [table_header, table_body, columns]


def clear_screen(term):
    """Clear the terminal."""
    print(term.home + term.black_on_black + term.clear)


def display_state(term, console, description):
    """Display the current state of the git fix walkthrough."""
    title, body = description[0], description[1]
    print(term.cyan(f"{title}"))
    print(parse_md(body))
    print()


def display_options(term, options):
    """Display the available options for the current state."""
    for idx, option in enumerate(options):
        print(term.yellow(f"{idx}: {option}"))


def main():
    """Main function, prompt loop."""
    term = Terminal()
    console = Console()
    with term.cbreak(), term.hidden_cursor():
        clear_screen(term)
        current_state = git_states.StartState()

        while True:
            print(term.home + term.clear + term.move_y(term.height // 2))
            display_state(term, console, current_state.describe())
            print(
                term.black_on_green(
                    term.center(
                        "Choose an option, press left arrow to go back, or press 'q' to quit."
                    )
                )
            )
            print()
            display_options(term, current_state.options)
            inp = term.inkey()
            if inp == "q":
                clear_screen(term)
                sys.exit(0)

            current_state = current_state.on_event(inp)


if __name__ == "__main__":
    main()
