# Project Rules

## Git & Release

- **NEVER** commit, push, or create git tags unless explicitly asked by the user.
- **NEVER** run `git push`, `git commit`, or `git tag` on your own.
- The user will tell you when they want to commit or tag a release.
- You MAY stage files with `git add` to prepare a commit, but must stop and ask before running `git commit` or `git push`.

## Code Style

- No emojis in code or commit messages.
- Follow existing code conventions in the project.
- Run `ruff check` after making changes to Python files.