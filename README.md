# tsto-mayhemids
Dump of Mayhem Id's to prepare to dump of tsto saves before shutdown on Jan 24th 2025

Please pull request any mayhem id's you have got from your tsto world or world's in the settings/info/about page in game into this repo from your/an fork in mayhemids.txt
or run the grab_mayhemids.py script on your computer with an range of applicationUserId's as such which is under https://github.com/nutterthanos/tsto-mayhemids/blob/main/grab_mayhemids.py#L10 and https://github.com/nutterthanos/tsto-mayhemids/blob/main/grab_mayhemids.py#L11 and then if it finds any of the mayhemid's from it then add to the list then pull request it thanks.

the script saves the found mayhem id's under applicationUserId_{applicationUserId}_mayhemId_{MayhemId}.xml in the current folder
so you could get the mayhem id from the filename or you can get it after the /users path in the files

note the script does dump the mayhemid from the server response into an file under applicationuserid_*_mayhemid_*.XML so in case you use the script you might want to delete the files afterwards or something 
