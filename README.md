# Game Localization Studio

Development prototype for RPG Maker MV/MZ JSON. Import a source file, translate
individually addressed message lines, choices and selected database fields, check control tokens and
an explicitly supplied message-row limit, and export a new JSON file. The
original is never overwritten; a source changed or replaced during import is rejected. Drafts are local to the active Hermes profile.
List saved drafts to recover their IDs and translation counts without showing game text.

**At a glance**

- **Install:** `hermes plugins install flabanabba8/game-localization-studio`, then `hermes plugins enable game-localization-studio`.
- **Needs:** Hermes 0.22 or later and RPG Maker data files you are allowed to translate. Hermes itself does the translating; no key or model is required by the plugin.
- **Internet:** Nothing: no network calls, credentials or model calls of its own.
- **Limits:** Linux is the only platform checked. It handles RPG Maker message text only, protects control codes and row budgets, and writes translation drafts rather than editing your game in place. No game data is included.
- **Credits:** No third-party code or assets are bundled. Licence: GPL-3.0-or-later.
- **AI assistance:** Written with AI coding assistants (Anthropic Claude and OpenAI Codex agents) under the maintainer's direction; what was actually tested is listed in VERIFICATION.md.

This is not a complete game localization system yet. Other database fields,
scripts, images and pixel-accurate layout are not covered. A structural pass is
not proof of in-game rendering. The row limit is supplied by the user for the
actual game; if omitted, layout status is unknown. It applies to message-command groups, not system menus or messages. Empty message rows count, and system labels still need in-game layout review.

The plugin reads the explicitly selected JSON file and returns game text to
Hermes. It uses no network, credentials, or model calls of its own. No game data
is bundled. License: GPL-3.0-or-later.

Selected database coverage includes actor names/nicknames/profiles, class names,
skill names/descriptions/messages, item/equipment names/descriptions, enemy
names, state names/messages, the system title/currency, system terms and messages, and map display names. System terms cover the `basic`, `commands`, `params` and `messages` fields documented in [RPG Maker MV’s System::Terms format](https://rpgmakerofficial.com/product/MV_Help/page/03_52.html); `%1`-style message placeholders are preserved.
Internal notes, file names, variable names and numeric IDs are not translated. Optional `include_system_types` on `System.json` also exposes element, skill, equipment, weapon and armor type names; it is off by default because custom scripts or plugins may depend on original spellings. Inspect those scripts and test the game before using such translations. The [RPG Maker MV System format](https://rpgmakerofficial.com/product/MV_Help/page/03_50.html) identifies these arrays.

Choice translations also update matching branch labels. If an original branch
label differs, a branch is missing, or the choice block has no end, that choice
is blocked for manual review.
Control-token counts are preserved. Formatting and wait controls keep their
original order; supported variables, names, icons and positional placeholders
may move to accommodate grammar.

A CPU-only integration fixture used the official RPG Maker MV event interpreter with a stubbed message system: translated message lines and choices were consumed, and both choice branches behaved as expected. It did not launch a game or verify visual layout. The interpreter is not bundled with this plugin.

Exports are placed in a unique private directory under their original JSON filename so the correct RPG Maker database type is retained when reimporting. The plugin can reopen its own exports without allowing unrelated Hermes configuration files as sources.
On POSIX systems, new source copies, drafts and exports use owner-only file
permissions. Existing files are not retroactively changed.
Draft locking supports POSIX and Windows. Focused native Windows tests covered
synthetic system terms and choice branches; Windows ACLs, real games and visual
layout were not checked.

A separate CPU-only fixture used the [official MV TextManager source](https://github.com/rpgtkoolmv/corescript/blob/182e31449707ba7e406db0485c44c2a9d11e2dcd/js/rpg_managers/TextManager.js) to read translated synthetic system terms and a placeholder-bearing message. The source is not bundled; this is not an in-game or layout test.

## 0.2.0 (2026-11-11)

- `localize_inspect` returns `row_width_limit_chars` (widest original message row, or `message_columns`); `localize_validate` reports translated rows wider than that, ignoring control codes. A row-count check alone had let a Spanish row twice as wide as any original row pass.
- Skill: translate a message as a whole and put it back row by row.

## 0.2.1 (2026-11-11)

- Skill: list the working folder first and use the game file found there instead of asking for a path.
