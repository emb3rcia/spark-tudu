# spark-tudu

# Navigation
- [About project](#about-project)
  - [Motivation for the project](#motivation-for-the-project)
  - [Learning outcomes](#learning-outcomes)
- [Project status](#project-status)
  - [Planned features](#planned-features)
- [Syntax](#syntax)
- [Scanned file extensions](#scanned-file-extensions)
- [Installation and usage](#installation-and-usage)
- [Supported markers](#supported-markers)
- [Supported priorities](#supported-priorities)
- [Config](#config)
  - [Different editor presets](#different-editor-presets)
- [Dependencies](#dependencies)
- [License](#license)

# About project
spark-tudu is a simple TUI app written in Python to help you develop your projects. It searches for lines like TODO or FIXME in app's syntax ([about syntax](#syntax)) and provides it to you in one place in TUI written in Textual.

## Motivation for the project
Motivation for this project comes from both the need for simple project when returning to coding, and from needing a simple program that puts all my TODOs from different files inside one space.

## Learning outcomes
I learned how to use Textual and how to make TUI apps.

# Project status
Project reached all requirements for 0.1.0 release. Currently app is fully functional. 0.1.1 added fixes for python 3.11 and 0.1.2 added more arguments to the config as well as arguments to command.

## Planned features
- Currently none

# Syntax
App detects comments with this syntax:

`language comment prefix marker/priority/comment/deadline`

Example:

`# TODO/HIGH/Add themes/22.10.2027`

**COMMENT MUST BE IN SEPARATE LINE THAN CODE**

# Scanned file extensions
spark-tudu scans only files with these extensions by default:
```
".py"
".pyi"
".pyw"
".pyx"
".px"
".pxi"
".c"
".h"
".cpp"
".hpp"
".cc"
".hh"
".cxx"
".hxx"
".js"
".jsx"
".ts"
".tsx"
".md"
```

These can be changed in config by adding for example this:

```
[files.comment_prefixes]
".py" = ["##"]

```
Above example makes it so .py files will be scanned only for comments starting with "##", empty lists can be made to disable scanning for given extension.

# Installation and usage
Use `pip install spark-tudu` or download Linux binary/Windows executable from [here](https://github.com/emb3rcia/spark-tudu/releases/tag/release) to install it. 

Use it by either running `spark-tudu` in directory you want to scan or by running downloaded binary/executable from there, depending on how you installed app.

You can also use `spark-tudu PROJECT_DIR` to scan given directory, as well as `spark-tudu -h` or `spark-tudu --help` to get more informations about the command

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

spark-tudu supports a config file. The config file must be present in the project directory being scanned.

If the config file does not exist, spark-tudu uses the default config made for VS Code.

The config file must be named `spark-tudu.toml` and can include these options:

```toml
[editor]
command = ["command", "arguments"]
wait = true/false
terminal = true/false

[files.comment_prefixes]
"file extension" = ["comment prefixes to scan"]

```
Default config:
```toml
[editor]
command = ["code", "-g", "{file}:{line}"]
wait = false
terminal = false

[files.comment_prefixes]
".py" = ["#"]
".pyi" = ["#"]
".pyw" = ["#"]
".pyx" = ["#"]
".px" = ["#"]
".pxi" = ["#"]
".c" = ["//", "/*", "*"]
".h" = ["//", "/*", "*"]
".cpp" = ["//", "/*", "*"]
".hpp" = ["//", "/*", "*"]
".cc" = ["//", "/*", "*"]
".hh" = ["//", "/*", "*"]
".cxx" = ["//", "/*", "*"]
".hxx" = ["//", "/*", "*"]
".js" = ["//", "/*", "*"]
".jsx" = ["//", "/*", "*"]
".ts" = ["//", "/*", "*"]
".tsx" = ["//", "/*", "*"]
".md" = ["#", "<!--"]
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

(`python-rich` is installed as dependency of `python-textual`)

# License
All files are licensed under the Apache 2.0 License.

See `LICENSE` for full terms