# Introduction #

Power users can use the interactive python console to control the behavior of Cinemol, by typing interactive commands or by running scripts and plugins.


# Starting the console #

From the Cinemol windows select the menu `Window->Show Console`

# Commands #

Commands are preceded with "`cm.`".

## center ##

Shifts the center of rotation and viewing.

Examples:

#### Center view about an absolute point ####
`>>> cm.center([1.0, 0.0, 0.3])`

#### Center view on the middle of all atoms ####
`>>> cm.center("*")`

## refresh ##

Used in script files to redraw the image.

Example:

`>>> cm.refresh()`