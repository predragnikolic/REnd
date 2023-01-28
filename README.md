# REnd

REnd is a Sublime Text plugin for folding/unfolding region/endregion comments.

[Screencast from 2023-01-28 20-41-46.webm](https://user-images.githubusercontent.com/22029477/215287679-fd825ba9-bec7-4fc7-a6dc-0ab216e5e46e.webm)

When opening a file,
if there are region/endregion comments,
this extension will automatically fold those regions.

The following commands are available:

| command         | Keybinding                                           | Command Palette 				    |
|-----------------|------------------------------------------------------|----------------------------------|
| rend_fold       | `ctrl+shift+[` (Linux, Windows), `super+alt+[` (OSX) | /                                |
| rend_unfold     | `ctrl+shift+]` (Linux, Windows), `super+alt+]` (OSX) | /                                |
| rend_fold_all   | UNBOUND                                              | REnd: Fold All                   |
| rend_unfold_all | UNBOUND                                              | REnd: Unfold All                 |


> NOTE: `rend_unfold` / `rend_unfold` will only be triggered when the cursor in the region/endregion comment.