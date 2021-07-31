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
            return CommitedQuestionState(self)
        elif choice == "Find what is lost":
            return LostNFoundState(self)
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

    def __init__(self, parent):
        super().__init__(
            parent,
            options=[
                "I am in the middle of a bad merge",
                "I am in the middle of a bad rebase",
                "Yes, commits were made",
                "No, I have not yet committed",
            ],
        )

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "I am in the middle of a bad merge":
            return BadMergeState(self)
        elif choice == "I am in the middle of a bad rebase":
            return BadRebaseState(self)
        elif choice == "Yes, commits were made":
            return CommittedState(self)
        elif choice == "No, I have not yet committed":
            return UncommittedState(self)
        elif choice == "Parent":
            return self.parent
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
    The lost and found state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        else:
            return self

    def describe(self):
        title = "I have lost some commits I know I made"
        body = """First make sure that it was not on a different branch. Try \
`git log -Sfoo --all` where `foo` is replaced with something unique in the \
commits you made. You can also search with `gitk --all --date-order` to see \
if anything looks likely.

Check your stashes, `git stash list`, to see if you might have stashed instead \
of committing. You can also visualize what the stashes might be associated with via:

`gitk --all --date-order $(git stash list | awk -F: '{print $1};')`

Next, you should probably look in other repositories you have lying around \
including ones on other hosts and in testing environments, and in your backups.

Once you are fully convinced that it is well and truly lost, you can start \
looking elsewhere in git. Specifically, you should first look at the reflog \
which contains the history of what happened to the tip of your branches for \
the past two weeks or so. You can of course say `git log -g` or `git reflog` \
to view it, but it may be best visualized with:

`gitk --all --date-order $(git reflog --pretty=%H)`

Next you can look in git's lost and found. Dangling commits get generated \
for many good reasons including resets and rebases. Still those activities \
might have mislaid the commits you were interested in. These might be best \
visualized with:

 `gitk --all --date-order $(git fsck | grep "dangling commit" | awk '{print $3;}')`

The last place you can look is in dangling blobs. These are files which have \
been git added but not attached to a commit for some (usually innocuous) \
reason. To look at the files, one at a time, run:

```
git fsck | grep "dangling blob" | while read x x s; do
  git show $s | less;
done
```

Once you find the changes you are interested in, there are several ways you \
can proceed. You can `git reset --hard SHA` your current branch to the history \
and current state of that SHA (probably not recommended for stashes), you can \
`git branch newbranch SHA` to link the old history to a new branch name (also \
not recommended for stashes), you can `git stash apply SHA` (for the non-index \
commit in a git-stash), you can `git stash merge SHA` or `git cherry-pick SHA` \
(for either part of a stash or non-stashes), etc."""
        return title, body


class BadMergeState(State):
    """
    The bad merge state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
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

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
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

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "No, I have no changes/working directory is clean",
            "Yes, I have bad changes/working directory is dirty: discard it",
            "Yes, I have good changes/working directory is dirty: save it",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "No, I have no changes/working directory is clean":
            return CommittedReallyState(self)
        elif choice == "Yes, I have bad changes/working directory is dirty: discard it":
            return UncommittedEverythingState(self)
        elif choice == "Yes, I have good changes/working directory is dirty: save it":
            return UncommittedCommitState(self)
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

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Discard everything",
            "Discard some thingsI want to save my changes",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Discard everything":
            return UncommittedEverythingState(self)
        elif choice == "Discard some things":
            return UncommittedSomethingsState(self)
        elif choice == "I want to save my changes":
            return UncommittedCommitState(self)
        return self

    def describe(self):
        title = "Discard everything or just some things?"
        body = (
            "So you have not yet committed, the question is now whether you want to"
            " undo everything which you have done since the last commit or just some"
            " things, or just save what you have done?"
        )
        return title, body


class CommittedReallyState(State):
    """
    The committed really state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = ["Yes, pushes were made", "No pushes"]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Yes, pushes were made":
            return PushedState(self)
        elif choice == "No pushes":
            return UnpushedState(self)
        return self

    def describe(self):
        title = "Have you pushed?"
        body = """So you have committed, the question is now whether you have \
made your changes (or at least the changes you are interesting in "fixing") \
publicly available or not. Publishing history has a big impact on others working \
on the same repository.

If you are dealing with commits someone else made, then this question covers \
whether they have pushed, and since you have their commits, the answer is almost \
certainly "yes".

Please note in any and all events, the recipes provided here will typically only \
modify the current branch you are on  (only one exception which will self-notify). \
Specifically, any tags or branches involving the commit you are changing or a child \
of that commit will not be modified. You must deal with those separately. Look at \
`gitk --all --date-order` to help visualize what other git references might also \
need to be updated.

Also note that these commands will fix up the referenced commits in your repository. \
There will be reflog'd and dangling commits holding the state you just corrected. \
This is normally a good thing and it will eventually go away by itself, but if for \
some reason you want to cut your seat belts, you can expire the reflog now and \
garbage collect with immediate pruning."""
        return title, body


class UncommittedEverythingState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "How to undo all uncommitted changes"
        body = """So you have not yet committed and you want to undo everything.\
 Well, best practice is for you to stash the changes in case you were mistaken \
and later decide that you really wanted them after all. \
`git stash save "description of changes"`. You can revisit those stashes later \
`git stash list` and decide whether to `git stash drop` them after some time \
has passed. Please note that untracked and ignored files are not stashed by \
default. See `--include-untracked` and `--all` for stash options to handle \
those two cases.

However, perhaps you are confident enough to know for sure that you will \
never ever want the uncommitted changes. If so, you can run `git reset --hard`\
, however please be quite aware that this is almost certainly a completely \
unrecoverable operation. Any changes which are removed here cannot be restored \
later. This will not delete untracked or ignored files. Those can be deleted \
with `git clean -nd` `git clean -ndX` respectively, or `git clean -ndx` for \
both at once. Well, actually those command do not delete the files. They \
show what files will be deleted. Replace the "n" in "-nd…" with "f" to \
actually delete the files. Best practice is to ensure you are not deleting \
what you should not by looking at the filenames first."""
        return title, body


class UncommittedCommitState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "How to save uncommitted changes"
        body = """There are five ways you can save your uncommitted change. \
I also suggest you read Pro Git as these are pretty basic git operations.

|Description|Command|
|:------------|:------|
|Commit them on the local branch.|`git commit -a -m "message"`|
|Commit them on another branch, no checkout conflicts.|`git checkout other_branch && git commit -am "message"`|
|Commit them on another branch, conflicts.|`git stash; git checkout other_branch; git stash apply; : "resolve conflicts"; git commit -am "message"`|
|Commit them on a new branch.|`git checkout -b new_branch; git commit -am "message"|
|Stash them for later|`git stash save "description"|
"""
        return title, body


class PushedState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Yes, I can make a new commit, but the bad commit trashed a particular file"
            " in error (among other good things I want to keep)",
            "Yes, I can make a new commit, and the bad commit is a merge commit I want"
            " to totally remove",
            "Yes, I can make a new commit, but the bad commit is a simple commit I want"
            " to totally remove",
            "Yes, I can make a new commit, and the bad commit has an error in it I want"
            " to fix",
            "Yes, I can make a new commit, but history is all messed up and I have a"
            " replacement branch",
            "No, I must rewrite published history and will have to inform others",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif (
            choice
            == "Yes, I can make a new commit, but the bad commit trashed a particular"
            " file in error (among other good things I want to keep)"
        ):
            return PushedRestoreFileState(self)
        elif (
            choice
            == "Yes, I can make a new commit, and the bad commit is a merge commit I"
            " want to totally remove"
        ):
            return PushedNewMergeState(self)
        elif (
            choice
            == "Yes, I can make a new commit, but the bad commit is a simple commit I"
            " want to totally remove"
        ):
            return PushedNewSimpleState(self)
        elif (
            choice
            == "Yes, I can make a new commit, and the bad commit has an error in it I"
            " want to fix"
        ):
            return PushedFixitState(self)
        elif (
            choice
            == "Yes, I can make a new commit, but history is all messed up and I have a"
            " replacement branch"
        ):
            return BranchOverlayMergeState(self)
        elif (
            choice
            == "No, I must rewrite published history and will have to inform others"
        ):
            return PushedOldState(self)

        return self

    def describe(self):
        title = (
            "Can you make a positive commit to fix the problem and what is the fix"
            " class?"
        )
        body = """Rewriting public history is a bad idea. It requires everyone \
else to do special things and you must publicly announce your failure. Ideally, \
you will create either a commit to just fix the problem, or a new `git revert` \
commit to create a new commit which undoes the changes made in a previous commit."""
        return title, body


class UnpushedState(State):
    """
    The unpushed state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Yes, I want to discard all unpushed changes",
            "Yes, and I want to make my branch identical to some non-upstream ref",
            "No, I want to fix some unpushed changes",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Yes, I want to discard all unpushed changes":
            return DiscardAllUnpushedState(self)
        elif (
            choice
            == "Yes, and I want to make my branch identical to some non-upstream ref"
        ):
            return ReplaceAllUnpushedState(self)
        elif choice == "No, I want to fix some unpushed changes":
            return FixUnpushedState(self)
        return self

    def describe(self):
        title = "Do you want to discard all unpushed changes on this branch?"
        body = """There is a shortcut in case you want to discard all changes made \
on this branch since you have last pushed or in any event, to make your local branch \
identical to "upstream". Upstream, for local tracking branches, is the place you \
get history from when you `git pull`: typically for master it might be origin/master. \
There is a variant of this option which lets you make your local branch identical \
to some other branch or ref."""
        return title, body


class DiscardAllUnpushedState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Discarding all local commits on this branch"
        body = """In order to discard all local commits on this branch, to \
make the local branch identical to the "upstream" of this branch, simply \
run `git reset --hard @{u}`
"""
        return title, body


class ReplaceAllUnpushedState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Replacing all branch history/contents"
        body = """If instead of discarding all local commits, you can make \
your branch identical to some other branch, tag, ref, or SHA that exists on \
your system.

The first thing you need to do is identify the SHA or ref of the good state \
of your branch. You can do this by looking at the output of `git branch -a; \
git tag`, `git log --all` or you can look graphically at \
`gitk --all --date-order`

Once you have found the correct state of your branch, you can get to that state by running:

`git reset --hard REF`

Replace `REF` with the reference or SHA you want to get back to."""
        return title, body


class FixUnpushedState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Yes, I want to change the most recent commit",
            "Yes, I want to discard the most recent commit(s)",
            "Yes, I want to undo the last git operation(s) affecting the HEAD/tip of my"
            " branch (most useful for rebase, reset, or --amend)",
            "No, I want to change an older commit",
            "No, I want to restore a older version of/deleted file as a new commit",
            "Either way, I want to move a commit from one branch to another",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Yes, I want to change the most recent commit":
            return ChangeLastState(self)
        elif choice == "Yes, I want to discard the most recent commit(s)":
            return RemoveLastState(self)
        elif (
            choice
            == "Yes, I want to undo the last git operation(s) affecting the HEAD/tip of"
            " my branch (most useful for rebase, reset, or --amend)"
        ):
            return UndoTipState(self)
        elif choice == "No, I want to change an older commit":
            return ChangeDeepState(self)
        elif (
            choice
            == "No, I want to restore a older version of/deleted file as a new commit"
        ):
            return PushedRestoreFileState(self)
        elif choice == "Either way, I want to move a commit from one branch to another":
            return MoveCommitState(self)
        return self

    def describe(self):
        title = "Is the commit you want to fix the most recent?"
        body = (
            "While the techniques mentioned to deal with deeper commits will work on"
            " the most recent, there are some convenient shortcuts you can take with"
            " the most recent commit."
        )
        return title, body


class ChangeLastState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "I want to remove the last commit",
            "I want to update the author/message/contents of the last commit",
            "I want to reorder, split, merge, or significantly rework the last"
            " commit(s)",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "I want to remove the last commit":
            return RemoveLastState(self)
        elif (
            choice == "I want to update the author/message/contents of the last commit"
        ):
            return UpdateLastState(self)
        elif (
            choice
            == "I want to reorder, split, merge, or significantly rework the last"
            " commit(s)"
        ):
            return ReworkLastState(self)
        return self

    def describe(self):
        title = (
            "Do you want to remove or change the commit message/contents of the last"
            " commit?"
        )
        body = ""
        return title, body


class RemoveLastState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Removing the last commit"
        body = """To remove the last commit from git, you can simply run \
`git reset --hard HEAD^` If you are removing multiple commits from the top, \
you can run `git reset --hard HEAD~2` to remove the last two commits. You can \
increase the number to remove even more commits.

If you want to "uncommit" the commits, but keep the changes around for \
reworking, remove the `--hard`: `git reset HEAD^` which will evict the \
commits from the branch and from the index, but leave the working tree around.

If you want to save the commits on a new branch name, then run \
`git branch newbranchname` before doing the `git reset`.
        """
        return title, body


class UndoTipState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Undoing the last few git operations affecting HEAD/my branch's tip"
        body = """Practically every git operation which affects the repository \
is recorded in the git reflog. You may then use the reflog to look at the \
state of the branches at previous times or even go back to the state of the \
local branch at the time.

While this happens for every git command affecting HEAD, it is usually most \
interesting when attempting to recover from a bad rebase or reset or an \
--amend'ed commit.

The first thing you need to do is identify the SHA of the good state of your \
branch. You can do this by looking at the output of `git log -g` or you can \
look graphically at `gitk --all --date-order $(git log -g --pretty=%H)`

Once you have found the correct state of your branch, you can get back to \
that state by running:

```
git reset --hard SHA
```

You could also link that old state to a new branch name using:

```
git checkout -b newbranch SHA
```

Replace `SHA` in both commands with the reference you want to get back to.

Note that any other commits you have performed since you did that "bad" \
operation will then be lost. You could `git cherry-pick` or \
`git rebase -p --onto` those other commits over.
        """
        return title, body


class ReworkLastState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Reworking the last commit"
        body = """WARNING: These techniques should only be used for non-merge \
commits. If you have a merge commit, you are better off deleting the merge \
and recreating it.

If you want to perform significant work on the last commit, you can simply \
`git reset HEAD^`. This will undo the commit and restore the index to the \
state it was in before that commit, leaving the working directory with the \
changes uncommitted, allowing you to fix whatever you need to fix and try again.

You can do this with multiple (non-merge) commits in a row (using `HEAD^^` \
or similar techniques), but then of course you lose the separation between \
the commits and are left with an undifferentiated working directory. If you \
are trying to squash all of the commits together, or rework which bits are \
in which commits, this may be what you want.
"""
        return title, body


class ChangeDeepState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Yes, I want to remove an entire commit",
            "No, I want to change an older commit",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Yes, I want to remove an entire commit":
            return RemoveDeepState(self)
        elif choice == "No, I want to change an older commit":
            return ModifyDeepState(self)
        return self

    def describe(self):
        title = "Do you want to remove an entire commit?"
        body = ""
        return title, body


class PushedRestoreFileState(State):
    """
    The pushed - restore file state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Making a new commit to restore a file deleted earlier"
        body = """The file may have been deleted or every change to that file in that \
commit (and all commits since then) should be destroyed. If so, you can simply \
checkout a version of the file which you know is good.

You must first identify the SHA of the commit containing the good version of the \
file. You can do this using `gitk --date-order` or using `git log --graph --decorate \
--oneline` or perhaps `git log --oneline -- filename` You are looking for the \
40 character SHA-1 hash ID (or the 7 character abbreviation). If you know the \
`^` or `~` shortcuts you may use those.

`git checkout SHA -- path/to/filename`

Obviously replace `SHA` with the reference that is good. You can then add and \
commit as normal to fix the problem."""
        return title, body


class RemoveLastState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Removing the last commit"
        body = """To remove the last commit from git, you can simply run \
`git reset --hard HEAD^` If you are removing multiple commits from the top, \
you can `run git reset --hard HEAD~2` to remove the last two commits. You \
can increase the number to remove even more commits.

If you want to "uncommit" the commits, but keep the changes around for \
reworking, remove the `--hard`: `git reset HEAD^ which will evict the commits \
from the branch and from the index, but leave the working tree around.

If you want to save the commits on a new branch name, then run \
`git branch newbranchname` before doing the `git reset`."""
        return title, body


class MoveCommitState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Moving a commit from one branch to another"
        body = """So, you have a commit which is in the wrong place and you \
want to move it from one branch to another. In order to do this, you will \
need to know the SHA of the first and last commit (in a continuous series of \
commits) you want to move (those values are the same if you are moving only \
one commit), the name of the branch you are moving the commit from, and the \
name of the branch you are moving the commit to. In the example below, these \
four values will be named $first, $last, $source, and $destination \
(respectively). Additionally, you will need to use a nonce branch as a \
placeholder. The nonce branch will be called "nonce" in the following \
example. However, you may use any branch name that is not currently in use. \
You can delete it immediately after you are done.

```
git branch nonce $last
git rebase -p --onto $destination $first^ nonce
```

Remember that when you substitute $first in the command above, leave the \
"^" alone, it is literal.

Use `gitk --all --date-order` to check to make sure the move looks correct \
(pretending that nonce is the destination branch). Please check very \
carefully if you were trying to move a merge, it may have been recreated \
improperly. If you don't like the result, you may delete the nonce branch \
(`git branch -D nonce`) and try again.

However, if everything looks good, we can move the actual destination branch \
pointer to where nonce is:

```
git checkout $destination
git reset --hard nonce
git branch -d nonce
```

If you double-checked with `gitk --all --date-order`, you would see that the \
destination branch looks correct. However, the commits are still on the \
source branch as well. We can get rid of those now:

```
git rebase -p --onto $first^ $last $source
```

Using `gitk --all --date-order` one last time, you should now see that the \
commits on the source branch have gone away. You have successfully moved the \
commits. Please check very carefully if merges occurred after the commits \
which were deleted. They may have been recreated incorrectly. If so you can \
either undo the delete or try to delete the bad merge and try to recreate it \
manually, or create a fake (--ours) merge from the same SHA so that git is \
aware that the merge occurred."""
        return title, body


class UpdateLastState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Updating the last commit's contents or commit message"
        body = """To update the last commit's contents, author, or commit \
message for a commit which you have not pushed or otherwise published, first \
you need to get the index into the correct state you wish the commit to \
reflect. If you are changing the commit message only, you need do nothing. \
If you are changing the file contents, typically you would modify the working \
directory and use git add as normal.

Note if you wish to restore a file to a known good state, you can use: \
```
git checkout GOODSHA -- path/to/filename
```

Once the index is in the correct state, then you can run `git commit --amend` \
to update the last commit. Yes, you can use `-a` if you want to avoid the \
`git add` suggested in the previous paragraph. You can also use `--author` \
to change the author information.
"""
        return title, body


class RemoveDeepState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Removing an entire commit"
        body = """You must first identify the SHA of the commit you wish to remove. You can do this using `gitk --date-order` or using `git log --graph --decorate --oneline` You are looking for the 40 character SHA-1 hash ID (or the 7 character abbreviation). Yes, if you know the `^` or `~` shortcuts you may use those.

```
git rebase -p --onto SHA^ SHA
```

Replace `SHA` with the reference you want to get rid of. The `^` in that command is literal.

However, please be warned. If some of the commits between SHA and the tip of your branch are merge commits, it is possible that `git rebase -p` will be unable to properly recreate them. Please inspect the resulting merge topology using `gitk --date-order HEAD ORIG_HEAD`  to ensure that git did want you wanted. If it did not, there is not really any automated recourse. You can reset back to the commit before the SHA you want to get rid of, and then cherry-pick the normal commits and manually re-merge the "bad" merges. Or you can just suffer with the inappropriate topology (perhaps by creating fake merges with `git merge --ours otherbranch` so that subsequent development work on those branches will be properly merged in with the correct merge-base)."""
        return title, body


class ModifyDeepState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Removing an entire commit"
        body = """You must first identify the SHA of the commit you wish to \
remove. You can do this using `gitk --date-order` or using \
`git log --graph --decorate --oneline` You are looking for the 40 character \
SHA-1 hash ID (or the 7 character abbreviation). Yes, if you know the `^` or \
`~` shortcuts you may use those.

```
git rebase -p --onto SHA^ SHA
```

Obviously replace "SHA" with the reference you want to get rid of. The `^` in \
that command is literal.

However, please be warned. If some of the commits between SHA and the tip of \
your branch are merge commits, it is possible that `git rebase -p` will be \
unable to properly recreate them. Please inspect the resulting merge topology \
`gitk --date-order HEAD ORIG_HEAD` and contents to ensure that git did want \
you wanted. If it did not, there is not really any automated recourse. You can \
reset back to the commit before the SHA you want to get rid of, and then \
cherry-pick the normal commits and manually re-merge the "bad" merges. Or you \
can just suffer with the inappropriate topology (perhaps creating fake merges \
`git merge --ours otherbranch` so that subsequent development work on those \
branches will be properly merged in with the correct merge-base)."""
        return title, body


class UncommittedSomethingsState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "How to undo some uncommitted changes"
        body = """So you have not yet committed and you want to undo some things.\
`git status` will tell you exactly what you need to do. For example:

```
# On branch master
# Changes to be committed:
#   (use "git reset HEAD <file>..." to unstage)
#
#       new file:   .gitignore
#
# Changes not staged for commit:
#   (use "git add <file>..." to update what will be committed)
#   (use "git checkout -- <file>..." to discard changes in working directory)
#
#       modified:   A
#
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#
#       C
```

However, the `git checkout` in file mode is a command that cannot be recovered \
from — the changes which are discarded most probably cannot be recovered. \
Perhaps you should run `git stash save -p "description"` instead, and select \
the changes you no longer want to be stashed, instead of permanently removing \
them.
"""
        return title, body


class BulkRewriteHistoryState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = [
            "Not just removing data (eg. re-arranging directory structure for all"
            " commits), or just wanting to use standard tools",
            "Want to only remove unwanted data (big files, private data, etc) and am"
            " willing to use a third party tool to do the job more quickly",
        ]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif (
            choice
            == "Not just removing data (eg. re-arranging directory structure for all"
            " commits), or just wanting to use standard tools"
        ):
            return FilterBranchState(self)
        elif (
            choice
            == "Want to only remove unwanted data (big files, private data, etc) and am"
            " willing to use a third party tool to do the job more quickly"
        ):
            return BfgState(self)
        return self

    def describe(self):
        title = "Changing all commits during all of git's history"
        body = (
            "You have not pushed but still somehow want to change all commits in all of"
            " git's history? Strange."
        )
        return title, body


class ChangeSingleDeepState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = ["Yes, a merge commit is involved", "No, only simple commits"]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Yes, a merge commit is involved":
            return ChangeSingleDeepMergeState(self)
        elif choice == "No, only simple commits":
            return ChangeSingleDeepSimpleState(self)
        return self

    def describe(self):
        title = "Is a merge commit involved?"
        body = (
            "If the commit you are trying to change is a merge commit, or if there is a"
            " merge commit between the commit you are trying to change and the tip of"
            " the branch you are on, then you need to do some special handling of the"
            " situation."
        )
        return title, body


class ChangeSingleDeepMergeState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Changing a single commit involving a merge"
        body = """Note, that this only applies if you have a merge commit. If a fast-forward (ff) merge occurred you only have simple commits, so should use other instructions.

Oh dear. This is going to get a little complicated. It should all work out, though. You will need to use a nonce branch as a placeholder. I will call the nonce branch "nonce" in the following example. However, you may use any branch name that is not currently in use. You can delete it immediately after you are done.

- Identify the SHA of the commit you wish to modify.

You can do this using `gitk --date-order` or using `git log --graph --decorate --oneline`. You are looking for the 40 character SHA-1 hash ID (or the 7 character abbreviation). Yes, if you know the "^" or "~" shortcuts you may use those.

- Remember the name of the branch you are currently on.

The line with a star on it in the `git branch` output is the branch you are currently on. I will use "$master" in this example, but substitute your branch name for "$master" in the following commands.

- Create and checkout a nonce branch pointing at that commit.

```
git checkout -b nonce SHA
```

Replace `SHA` with the reference you want to modify.

- Modify the commit

You need to get the index into the correct state you wish the commit to reflect. If you are changing the commit message only, you need do nothing. If you are changing the file contents, typically you would modify the working directory and use `git add` as normal.

Note if you wish to restore a file to a known good state, you can use `git checkout GOODSHA -- path/to/filename`.

Once the index is in the correct state, then you can run `git commit --amend` to update the last commit. Yes, you can use `-a` if you want to avoid the git add suggested in the previous paragraph.

If the commit you are updating is a merge commit, ensure that the log message reflects that.

- Put the remaining commits after the new one you just created

Remembering to substitute the correct branch name for $master

```
git rebase -p --onto $(git rev-parse nonce) HEAD^ $master
```

- Validate that the topology is still good

If some of the commits after the commit you changed are merge commits, please be warned. It is possible that `git rebase -p` will be unable to properly recreate them. Please inspect the resulting merge topology using `gitk --date-order HEAD ORIG_HEAD` to ensure that git did want you wanted. If it did not, there is not really any automated recourse. You can reset back to the commit before the SHA you want to get rid of, and then cherry-pick the normal commits and manually re-merge the "bad" merges. Or you can just suffer with the inappropriate topology (perhaps creating fake merges `git merge --ours otherbranch` so that subsequent development work on those branches will be properly merged in with the correct merge-base).

- Delete the nonce branch

You don't need it. It was just there to communicate an SHA between two steps in the above process. `git branch -d nonce`"""
        return title, body


class ChangeSingleDeepSimpleState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Changing a single commit involving only simple commits"
        body = """You must first identify the SHA of the commit you wish to remove. You can do this using `gitk --date-order` or using `git log --graph --decorate --oneline` You are looking for the 40 character SHA-1 hash ID (or the 7 character abbreviation). Yes, if you know the `^` or `~` shortcuts you may use those.

```
git rebase -i SHA^
```

Replace `SHA` with the reference you want to get rid of. The `^` in that command is literal.

You will be dumped in an editor with a bunch of lines starting with pick. The oldest commit, the one you are probably interested in changing, is first. You will want to change the "pick" to "reword" or "edit", or perhaps even "squash" depending on what your goal is.

When using "edit" to change contents or author, when you are dumped into the shell to make your change, make your change, `git add` as normal, and then run `git commit --amend` (including changing the author information with --author). When you are satisfied, you should run `git rebase --continue`."""
        return title, body


class PushedNewSimpleState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Reverting an old simple pushed commit"
        body = """To create an positive commit to remove the effects of a \
simple (non-merge) commit, you must first identify the SHA of the commit you \
want to revert. You can do this using `gitk --date-order` or using \
`git log --graph --decorate --oneline`. You are looking for the 40 character \
SHA-1 hash ID (or the 7 character abbreviation). If you know the `^` or `~` \
shortcuts you may use those.

`git revert SHA`

Obviously replace `SHA` with the reference you want to revert. If you want \
to revert multiple SHAs, you may specify a range or a list of SHAs."""
        return title, body


class PushedFixitState(State):
    """
    The pushed - fixit state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Making a new commit to fix an old commit"
        body = """If the problem in the old commit is just something was done \
incorrectly, go ahead and make a normal commit to fix the problem. Feel free to \
reference the old commit SHA in the commit message."""
        return title, body


class BranchOverlayMergeState(State):
    """
    The branch - overlay merge state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        return self

    def describe(self):
        title = "Rewriting an old branch with a new branch with a new commit"
        body = """If the state of a branch is contaminated beyond repair and \
you have pushed that branch or otherwise do not want to rewrite the existing \
history, then you can make a new commit which overwrites the original branch \
with the new one and pretends this was due to a merge. The command is a bit \
complicated, and will get rid of all ignored or untracked files in your working \
directory, so please be sure you have properly backed up everything.

In the following example, please replace `$destination` with the name of the \
branch whose contents you want to overwrite. `$source` should be replaced with \
the name of the branch whose contents are good.

You actually are being provided with two methods. The first set is more portable \
but generates two commits. The second knows about the current internal files git \
uses to do the necessary work in one commit. Only one command is different and a \
second command runs at a different time.

```
# Portable method to overwrite one branch with another in two commits
git clean -dfx
git checkout $destination
git reset --hard $source
git reset --soft ORIG_HEAD
git add -fA .
git commit -m "Rewrite $destination with $source"
git merge -s ours $source
```

or

```
# Hacky method to overwrite one branch with another in one commit
git clean -dfx
git checkout $destination
git reset --hard $source
git reset --soft ORIG_HEAD
git add -fA .
git rev-parse $source > .git/MERGE_HEAD
git commit -m "Rewrite $destination with $source"
```

"""
        return title, body


class PushedOldState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = ["Proceed with fixing the old commit"]

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        elif choice == "Proceed with fixing the old commit":
            return UnpushedState(self)
        else:
            return self

    def describe(self):
        title = "I am a bad person and must rewrite published history"
        body = """Hopefully you read the previous reference and fully understand \
why this is bad and what you have to tell everyone else to do in order to \
recover from this condition. Assuming this, you simply need to go to the parts \
of this document which assume that you have not yet pushed and do them as normal. \
Then you need to do a "force push" `git push -f` to thrust your updated history \
upon everyone else. As you read in the reference, this may be denied by default \
by your upstream repository (see `git config receive.denyNonFastForwards`, but \
can be disabled (temporarily I suggest) if you have access to the server. You \
then will need to send an email to everyone who might have pulled the history \
telling them that history was rewritten and they need to `git pull --rebase` \
and do a bit of history rewriting of their own if they branched or tagged from \
the now outdated history."""
        return title, body


class FilterBranchState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        else:
            return self

    def describe(self):
        title = "Arbitrarily changing all commits during all of git's history"
        body = """`git filter-branch` is a powerful, complex command that allows you to perform arbitary scriptable operations on all commits in git repository history. This flexibility can make it quite slow on big repos, and makes using the command quite difficult. See: https://git-scm.com/docs/git-filter-branch
        """
        return title, body


class BfgState(State):
    """
    State.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        else:
            return self

    def describe(self):
        title = (
            "Use The BFG to remove unwanted data, like big files or passwords, from Git"
            " repository history"
        )
        body = """https://rtyley.github.io/bfg-repo-cleaner/ is a simpler, faster alternative to `git filter-branch`, specifically designed for cleansing bad data out of your Git repository history - it operates over all branches and tags in your project to purge data you don't want retained anywhere. Some examples:

Remove all blobs bigger than 1 megabyte (to make your repo take up less space):

```
$ bfg --strip-blobs-bigger-than 1M  my-repo.git
```

Replace all passwords listed in a file with ***REMOVED*** wherever they occur in your repository :

```
$ bfg --replace-text passwords.txt  my-repo.git
```
"""
        return title, body


class PushedNewMergeState(State):
    """
    The pushed - new merge state.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.options = []

    def on_event(self, event):
        choice = self.parse_choice(event)
        if choice == "Parent":
            return self.parent
        else:
            return self

    def describe(self):
        title = "Reverting a merge commit"
        body = """Note, that this only applies if you have a merge commit. \
If a fast-forward (ff) merge occurred you only have simple commits, so should \
use another method.

Oh dear. This is going to get complicated.

To create an positive commit to remove the effects of a merge commit, you must \
first identify the SHA of the commit you want to revert. You can do this using \
`gitk --date-order` or using `git log --graph --decorate --oneline`. You are \
looking for the 40 character SHA-1 hash ID (or the 7 character abbreviation). \
Yes, if you know the `^` or `~` shortcuts you may use those.

Undoing the file modifications caused by the merge is about as simple as you \
might hope. `git revert -m 1 SHA`. (Obviously replace `SHA` with the reference \
you want to revert; `-m 1` will revert changes from all but the first parent, \
which is almost always what you want.) Unfortunately, this is just the tip of \
the iceberg. The problem is, what happens months later, long after you have \
exiled this problem from your memory, when you try again to merge these branches \
(or any other branches they have been merged into)? Because git has it tracked \
in history that a merge occurred, it is not going to attempt to remerge what it \
has already merged. Even worse, if you merge from the branch where you did the \
revert, you will undo the changes on the branch where they were made. (Imagine \
you revert a premature merge of a long-lived topic branch into master, and later \
merge master into the topic branch to get other changes for testing.)

One option is actually to do this reverse merge immediately, annihilating any \
changes before the bad merge, and then to "revert the revert" to restore them. \
This leaves the changes removed from the branch you mistakenly merged to, but \
present on their original branch, and allows merges in either direction without \
loss. This is the simplest option, and in many cases, can be the best.

A disadvantage of this approach is that `git blame` output is not as useful \
(all the changes will be attributed to the revert of the revert) and `git bisect` \
is similarly impaired. Another disadvantage is that you must merge all current \
changes in the target of the bad merge back into the source; if your development \
style is to keep branches clean, this may be undesirable, and if you rebase your \
branches (e.g. with `git pull --rebase`), it could cause complications unless you \
are careful to use `git rebase -p` to preserve merges.

In the following example, please replace `$destinatio`n with the name of the \
branch that was the destination of the bad merge, `$source` with the name of \
the branch that was the source of the bad merge, and `$sha` with the SHA-1 hash \
ID of the bad merge itself.

`git checkout $destination`
`git revert $sha`
# save the SHA-1 of the revert commit to un-revert it later
`revert="git rev-parse HEAD"`
`git checkout $source`
`git merge $destination`
`git revert $revert`

Another option is to abandon the branch you merged from, recreate it from the \
previous merge-base with the commits since then rebased or cherry-picked over, \
and use the recreated branch from now on. Then the new branch is unrelated and \
will merge properly. Of course, if you have pushed the donor branch, you cannot \
use the same name (that would be rewriting public history and is bad) so everyone \
needs to remember to use the new branch.

This approach has the advantage that the recreated donor branch will have cleaner \
history, but especially if there have been many commits (and especially merges) \
to the branch, it can be a lot of work. At this time, I will not walk you through \
the process of recreating the donor branch. \
See https://github.com/git/git/blob/master/Documentation/howto/revert-a-faulty-merge.txthowto/revert-a-faulty-merge.txt \
for more information."""
        return title, body
