Python Script to reduce your commit count forcefully without changing contents.
Iterates through your commits, and summarizes commits during the same hour/minute (customizable) into one.

### You made way too many commits?
**Maybe you are using [Obsidian.md](https://obsidian.md) with something like [obsidian-git](https://github.com/denolehov/obsidian-git)...**
Or maybe you are using other automated commits, or your quick fixes have gotten too many, and now you decide to clean up the history?

That can be hard... Rebasing and Squash might help, but will likely run into thousands of merge conflicts.

I ended up writing a script, to do so. This helped me a lot.

---

Also to change name / email in git history:

You can add this alias:

git config --global alias.change-commits '!'"f() { VAR=\$1; OLD=\$2; NEW=\$3; shift 3; git filter-branch --env-filter \"if [[ \\\"\$\`echo \$VAR\`\\\" = '\$OLD' ]]; then export \$VAR='\$NEW'; fi\" \$@; }; f"
To change the author name:

git change-commits GIT_AUTHOR_NAME "old name" "new name"
or the email for only the last 10 commits:

git change-commits GIT_AUTHOR_EMAIL "old@email.com" "new@email.com" HEAD~10..HEAD
