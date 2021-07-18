from py_gitfix.state import State
import time


class StartState(State):
    """
    The starting state.
    """

    def __init__(self):
        super().__init__()
        self.options = ["Fix a change", "Find what is lost"]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Fix a change":
            return CommitedQuestionState()
        elif choice == "Find what is lost":
            return LostNFoundState()
        else:
            return self

    def describe(self):
        title = (
            "Are you trying to find that which is lost or fix a change that was made?"
        )
        body = """Due to previous activities, you may have lost some work which you \
would like to find and restore. Alternatively, you may have made some changes which \
you would like to fix. Fixing includes updating, rewording, and deleting or \
discarding."""
        return title, body


class CommitedQuestionState(State):
    """
    The "have you committed yet" state.
    """

    def __init__(self):
        super().__init__()
        self.options = [
            "I am in the middle of a bad merge",
            "I am in the middle of a bad rebase",
            "Yes, commits were made",
            "No, I have not yet committed",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "I am in the middle of a bad merge":
            return BadMergeState()
        elif choice == "I am in the middle of a bad rebase":
            return BadRebaseState()
        elif choice == "Yes, commits were made":
            return CommittedState()
        elif choice == "No, I have not yet committed":
            return UncommittedState()
        else:
            return self

    def describe(self):
        title = "Have you committed?"
        body = """If you have not yet committed that which you do not want, git \
does not know anything about what you have done yet, so it is pretty easy to \
undo what you have done."""
        return title, body


class LostNFoundState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class BadMergeState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Recovering from a broken merge"
        body = """So, you were in the middle of a merge, have encountered one \
or more conflicts, and you have now decided that it was a big mistake and want \
to get out of the merge.

The fastest way out of the merge is `git merge --abort`"""
        return title, body


class BadRebaseState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Recovering from a broken rebase"
        body = """So, you were in the middle of a rebase, have encountered one \
or more conflicts, and you have now decided that it was a big mistake and want \
to get out of the rebase.

The fastest way out of the rebase is `git rebase --abort`"""
        return title, body


class CommittedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = [
            "No, I have no changes/working directory is clean",
            "Yes, I have bad changes/working directory is dirty: discard it",
            "Yes, I have good changes/working directory is dirty: save it",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Do you have uncommitted stuff in your working directory?"
        body = """So you have committed. However, before we go about fixing or \
removing whatever is wrong, you should first ensure that any uncommitted changes \
are safe, by either committing them (`git commit`) or by stashing them (`git stash \
save "message"`) or getting rid of them.

`git status` will help you understand whether your working directory is clean or \
not. It should report nothing for perfect safety ("Untracked files" only are \
sometimes safe.)"""
        return title, body


class UncommittedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class CommittedReallyState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class UncommittedEverythingState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class UncommittedCommitState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class PushedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class UnpushedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class DiscardAllUnpushedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ReplaceAllUnpushedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class FixUnpushedState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ChangeLastState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class RemoveLastState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class UndoTipState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ChangeDeepState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class PushedRestoreFileState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class RemoveLastState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class MoveCommitState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class UpdateLastState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class RemoveDeepState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ModifyDeepState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class UncommittedSomethingsState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class BulkRewriteHistoryState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ChangeSingleDeepState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ChangeSingleDeepMergeState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class ChangeSingleDeepSimpleState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class PushedNewSimpleState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class PushedFixitState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class BranchOverlayMergeState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class PushedOldState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class FilterBranchState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body


class BfgState(State):
    """
    State.
    """

    def __init__(self):
        super().__init__()
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        return self

    def describe(self):
        title = "Not yet implemented"
        body = ""
        return title, body
