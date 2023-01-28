# REnd

REnd is a Sublime Text plugin for folding/unfolding region/endregion comments.

When opening a file,
if there are region/endregion comments,
this extension will fold those regions.

The following commands are available:

| command_name    | Keybinding                                           | Available in the Command Palette |
|-----------------|------------------------------------------------------|----------------------------------|
| rend_fold       | `ctrl+shift+[` (Linux, Windows), `super+alt+[` (OSX) | /                                |
| rend_unfold     | `ctrl+shift+]` (Linux, Windows), `super+alt+]` (OSX) | /                                |
| rend_fold_all   | UNBOUND                                              | REnd: Fold All                   |
| rend_unfold_all | UNBOUND                                              | REnd: Unfold All                 |


> NOTE: `rend_unfold` / `rend_unfold` will only be triggered when the cursor in the region/endregion comment.