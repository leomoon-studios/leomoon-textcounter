# LeoMoon TextCounter for Blender

## Introduction

LeoMoon TextCounter is an easy to use text animation plugin for Blender that can be used to make GUI simulations, scoreboards, timers, HUDs, and data-driven titles.

More info / download: https://leomoon.com/downloads/plugins/leomoon-textcounter/

## Features

- **Animated mode** - keyframe the counter value directly on any Text object
- **Dynamic mode** - drive the counter from a Python expression (supports `bpy`, `mathutils`, `math`, and more); object/data references are auto-rewritten to use the evaluated depsgraph
- **Number formatting** - integer/decimal display, leading-zero padding, digit grouping (comma, period, space), configurable decimal separator, prefix/suffix
- **Abbreviation** - compact K / M / B / T / Q suffixes with optional lowercase and decimal precision
- **Time formatting** - display as `SS`, `MM:SS`, `HH:MM:SS`, or `DD:HH:MM:SS` with configurable modulo and separators
- **Text file source** - override the counter with a line from a Blender text data-block; optionally re-parse the line as a number
- **Live preview** - counter updates instantly on property change without needing to scrub the timeline
- **Copy / Paste settings** - copy all counter settings from one Text object and paste to one or more selected Text objects
- **Bundled presets** - Currency USD, Currency EUR, Percentage, Stopwatch MM:SS, Timecode HH:MM:SS:FF, Padded Score, Abbreviated Large Numbers
- **Error display** - expression evaluation errors shown inline in the panel

## Changelog

- 2.0.0 - 2026-04-03:
    - Ported to Blender 5.1+ modern extension format
    - Dynamic expression evaluator with safe sandboxed namespace
    - Live property updates (no timeline scrub required)
    - Copy/paste settings between Text objects
    - Bundled presets
- 1.4.0 - 2023-03-09: Fixed expression and animation lag when rendering
- 1.3.6 - 2021-06-03: Fixed compatibility issue for Blender 2.93 and 3.0
- 1.3.5: Fixed text grouping bug
- 1.3.4: Fixed dynamic section not updating while rendering
- 1.3.3: Fixed animation not updating while rendering
- 1.3.2: Fixed Blender 2.80 API warnings
- 1.3.1: Added support for Blender 2.8 and bug fixes
- 1.3.0: Improved abbreviation support with decimals
- 1.2.0: Time counter with many options
- 1.1.0: Overriding counter with lines from text file
- 1.0.0: First public release

## Usage

> **Blender 5.1+ (extension format):** Always install from the [Releases page](https://github.com/leomoon-studios/leomoon-textcounter/releases). Do **not** use the green "Code → Download ZIP" button. That downloads the source, not the installable extension.

1. Download `leomoon-textcounter-X.Y.Z_blender-A.B.C.zip` from the Releases page.
2. In Blender, open `Edit → Preferences → Get Extensions`.
3. Click the **▼ dropdown arrow** in the **top-right corner** of the panel (next to the **Repositories** selector) and choose **Install from Disk…**.
4. Select the downloaded `.zip`. The extension is enabled automatically and appears under the **Installed** section.
5. Create a **Text** object and go to the **Properties → Object Data** tab (the "a" icon).
6. The **TextCounter** panel appears at the top of that tab.
7. Enable the counter with the toggle in the panel header, choose a mode, and configure formatting.

## Compatibility

Tested with Blender 5.1.1

## Development

```bash
make venv     # create .venv with ruff + pytest
make check    # ruff lint + pytest
make build    # build dist/leomoon-textcounter-<ver>_blender-<min>.zip
make install  # build and install into the Blender user profile
make tag      # create an annotated git tag from the manifest version
```

Override the Blender binary if it isn't on `PATH`:

```bash
make build BLENDER=/path/to/blender
```
