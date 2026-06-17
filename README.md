# spark-tudu

# Navigation
- [About project](#about-project)
  - [Motivation for the project](#motivation-for-the-project)
  - [Learning outcomes](#learning-outcomes)
- [Project status](#project-status)
  - [Planned features](#planned-features)
- [Syntax](#syntax)
- [Installation and usage](#installation-and-usage)
- [Supported markers](#supported-markers)
- [Supported priorities](#supported-priorities)
- [Config](#config)
  - [Different editor presets](#different-editor-presets)
- [Dependencies](#dependencies)
- [Images](#images)
- [License](#license)

# About project
spark-tudu is simple TUI app written in Python to help you develop your projects. It searches for lines like TODO or FIXME in app's syntax ([about syntax](#syntax)) and provides it to you in one place in TUI written in Textual.

## Motivation for the project
Motivation for this project comes from both need for simple project when returning to coding, and from needing a simple program that puts all my TODOs from different files inside one space.

## Learning outcomes
I learned how to use Textual and how to make TUI apps.

# Project status
~~Minimum Viable Product is done. It was made in 3 hours. This isn't finished version yet, as project has more features planned.~~ As of 17.06.2026, app has been extended with colored output, opening file in editor at specific line, more prefixes and support for priorities. Planned features are available [here](#planned-features).

## Planned features
- Better deadline handling
- Filtering options
- Export of results
- Better table design
- Project summary screen
- Packaging it as binary for Linux and executable for Windows
- Uploading it to PyPI and the AUR

# Syntax
App detects comments with this syntax:

`language comment prefix marker/priority/comment/deadline`

Example:

`# TODO/HIGH/Add themes/22.10.2027`

# Installation and usage
Download `.py` file from GitHub Releases and run it through terminal of your choice using `python main.py` in project directory. You can also clone this project using `git clone https://github.com/emb3rcia/spark-tudu`

# Supported markers
Currently supported markers:
- TODO
- FIXME
- BUG
- HACK
- NOTE
- IDEA
- REVIEW
- SECURITY
- DOCS
- TEST
- PERF
- CLEANUP
- BLOCKED

# Supported priorities
Currently supported priorities:
- CRITICAL
- HIGH
- MEDIUM
- LOW
- OPTIONAL

# Config

spark-tudu supports a config file. The config file must be present in the directory from which you run the program.

If the config file does not exist, spark-tudu uses the default config made for VS Code.

The config file must be named `spark-tudu.toml` and can include these options:

```toml
[editor]
command = ["command", "arguments"]
wait = true/false
terminal = true/false
```
Default config:
```toml
[editor]
command = ["code", "-g", "{file}:{line}"]
wait = false
terminal = false
```

## Different editor presets
Here are presets for common editors:

**VS Code / Code OSS (default):**
```toml
[editor]
command = ["code", "-g", "{file}:{line}"]
wait = false
terminal = false
```
**VSCodium:**
```toml
[editor]
command = ["codium", "-g", "{file}:{line}"]
wait = false
terminal = false
```
**Nano:**
```toml
[editor]
command = ["nano", "+{line},1", "{file}"]
wait = true
terminal = true
```
**Vim:**
```toml
[editor]
command = ["vim", "+{line}", "{file}"]
wait = true
terminal = true
```
**Neovim:**
```toml
[editor]
command = ["nvim", "+{line}", "{file}"]
wait = true
terminal = true
```
**Sublime Text:**
```toml
[editor]
command = ["subl", "{file}:{line}"]
wait = false
terminal = false
```
**JetBrains IDE:**
```toml
[editor]
command = ["idea", "--line", "{line}", "{file}"]
wait = false
terminal = false
```

# Dependencies
- `textual`
- `rich`

Install with pip: 

`pip install textual rich`

Install command for Arch-based distributions:

`sudo pacman -S python-textual` 

(`python-rich` is installed as dependency of `pyt hon-textual`)

# Images
![dark mode](Images/dark.png)
![light mode](Images/light.png)

# License
All files are licensed under the Apache 2.0 License.

See `Licenses/Apache-2.0.txt` for full terms