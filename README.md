# Game Localization Studio

Development prototype for RPG Maker MV/MZ JSON. Import a source file, translate
individually addressed message lines, choices and selected database fields, check control tokens and
an explicitly supplied message-row limit, and export a new JSON file. The
original is never overwritten; a source changed or replaced during import is rejected. Drafts are local to the active Hermes profile.
List saved drafts to recover their IDs and translation counts without showing game text.

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
Internal notes, file names, variable names and numeric IDs are not translated.

Choice translations also update matching branch labels. If an original branch
label differs, a branch is missing, or the choice block has no end, that choice
is blocked for manual review.
Control-token counts are preserved. Formatting and wait controls keep their
original order; supported variables, names, icons and positional placeholders
may move to accommodate grammar.

A CPU-only integration fixture used the official RPG Maker MV event interpreter with a stubbed message system: translated message lines and choices were consumed, and both choice branches behaved as expected. It did not launch a game or verify visual layout. The interpreter is not bundled with this plugin.

Exports are placed in a unique private directory under their original JSON filename so the correct RPG Maker database type is retained when reimporting. The plugin can reopen its own exports without allowing unrelated Hermes configuration files as sources.
