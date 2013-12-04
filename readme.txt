== Binary version ==

I'm using cx_Freeze to convert the Python program to a binary. However, this only generates binaries for the system it's run on. Namely, mine is 64-bit Windows. If you are running a different system you'll have to run it from Python directly, or get somebody to generate a binary for you.

For the binary version, download the zip and extract it. Then run eu4cd.exe. If you're asked for the game directory, find your Europa Universalis IV directory (the one containing the exe). Save your creations to your mod folder.

== Python version ==

The Python version should be cross-platform, although you will need Python and some libraries. Specifically, you will need:

* Python 3.3. Some earlier 3.x might work too, but I haven't tested.
* pyqt5: http://www.riverbankcomputing.com/software/pyqt/download5
* pyyaml: https://bitbucket.org/xi/pyyaml
* cx_Freeze (only required if you want to generate a binary): http://cx-freeze.sourceforge.net/
