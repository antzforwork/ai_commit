# antz-skills

Personal Claude Code plugin marketplace: skills for code organization, git workflow and releases.

## Install

```bash
/plugin marketplace add <github-user>/antz-skills
/plugin install git-semantic-commit@antz-skills
```

Install only the plugins you need, or all of them:

| Plugin | What it does |
|---|---|
| `code-organization` | Decides where a function belongs (local / helper / formatter / validator / service / repository / domain) and which file it goes in. Frappe, Flutter and JS/TS mappings. |
| `git-clean-attribution` | Semantic commits plus MR/PR descriptions and work items with no AI attribution. Confirms before anything goes to a remote. |
| `git-semantic-commit` | `type(scope): description` commits with a 50-char title (details go in the body), no AI attribution, and a commit prompt after finishing a task. |
| `semantic-version-release` | Bumps semver, writes `changelogs/<version>/CHANGELOG.md` + `release-notes.txt` (Play Store / App Store), then commits, tags and pushes after you confirm. |

> `git-clean-attribution` and `git-semantic-commit` overlap: both trigger on commit requests. Install one of them if you don't want both firing.

## Layout

```
.claude-plugin/marketplace.json
plugins/<plugin>/
  .claude-plugin/plugin.json
  skills/<skill>/SKILL.md (+ references/, scripts/)
```

## Adding a skill

1. Create `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/skills/<name>/SKILL.md`.
2. Add an entry to `.claude-plugin/marketplace.json`.
3. Run `claude plugin validate .`.
4. Bump the `version` in both manifests when you change a skill, so installs pick up the update.
