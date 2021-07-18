import sys
import time

from blessed import Terminal

from py_gitfix import git_states


def clear_screen(term):
    print(term.home + term.black_on_black + term.clear)


def display_state(term, description):
    title, body = description[0], description[1]
    print(term.cyan(f"{title}"))
    print(term.white(f"{body}"))
    print()


def display_options(term, options):
    for idx, option in enumerate(options):
        print(term.yellow(f"{idx}: {option}"))


def main():
    term = Terminal()
    with term.cbreak(), term.hidden_cursor():
        clear_screen(term)
        current_state = git_states.StartState()

        while True:
            print(term.home + term.clear + term.move_y(term.height // 2))
            display_state(term, current_state.describe())
            print(
                term.black_on_green(
                    term.center("Choose an option or press 'q' to quit.")
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
