# Show Cultural and Religious Advances
Some cultures and religions offer unique advances that are super strong, giving you a reason to switch.

Currently, the only way to check them is when you select countries at the start of the game. There is no way of checking what unique advances each culture and religion offer in game.

## Features
- This mod provides such detail when you go to your culture/religion tooltip under the culture/religion breakdown tab. This includes all culture/religion, within/outside of your country. 
- The embedded tooltip is also present for each of the advances so you can see what each of them do. The screenshots should give you quite a good idea.
- Note that the tooltip only shows unique advances available to this culture/religion, without any further requirements. Specific unique advances that require you to be of specific culture AND religion for example, will not be shown.
- The current tag you are playing as is also not considered. Specific advances requiring a specific culture AND tag for example, will also not be shown, even if you're playing as the said tag.

## Compatibility
- Supported game version: **1.3.x** 
- The list of matching advances are created according to the current version, so if this mod is not updated later, then:
  - When a culture/religion is added in later versions, , they will not have the extra tooltip.
  - When the respective unique advances are changed in later versions, they will still have the unupdated tooltip. 
  - Your game shouldn't break though. You can rebuild the mod for the current version yourself by running: 
```sh
python3 build_catalogue.py "/path/to/Europa Universalis V"
```
`build_catalogue.py` is available in the mod files.
- For total conversion mods, the list needs to be build given the alterations.
- Save-game compatible.
- UI-only: no gameplay data is changed.
- The mod replaces `in_game/gui/culture_lateral_view.gui` and `in_game/gui/shared/religion_tooltips.gui`. Other mods also replacing those may conflict.
- Changes the checksum.

## Potential Issue
In age VI, there is an advance that unlocks the **Unify Culture Group** cabinet action, which, well, unifies your culture group. This creates a new culture that inherits the unique advances of your previous main culture. The list of matching advance does not update this, so I tried a workaround which may or may not update this. Let me know if you actually went through this and what happened.

## Feedback
If you encounter an issue or have a suggestion, please leave a comment on the Workshop page.
