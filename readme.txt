== Installing ==

=== Binary version ===

Download the zip and extract it. Then run eu4cd.exe.

Currently 64-bit Windows only. I'm using cx_Freeze to convert the Python program to a binary. However, this only generates binaries for the system it's run on, namely, mine is 64-bit Windows. If you are running a different system you'll have to run it from Python directly, or get somebody with the same system as you to generate a binary for you by running freeze.py.

=== Python version ===

The Python version should be cross-platform, although you will need Python and some libraries. Specifically, you will need:

* Python 3.3. Some earlier 3.x might work too, but I haven't tested.
* pyqt5: http://www.riverbankcomputing.com/software/pyqt/download5
* pyyaml: https://bitbucket.org/xi/pyyaml
* cx_Freeze (only required if you want to generate a binary): http://cx-freeze.sourceforge.net/

To run the program use
> python eu4cd.py

To build a binary for your system in build/, use
> python freeze.py build

This requires cx_Freeze.

== How to use ==

If you're asked for the game directory, find your Europa Universalis IV directory (the one containing the exe). 
Save your creations to your mod folder. 
"Overwriting" a mod file will overwrite the current country in that mod, but will not affect other countries.

== Rating ==

There are no hard caps on what items you can pick. Instead the designer will give you a rating consisting of two parts:

=== National idea cost ===

Each bonus you pick for your national ideas has a cost in points. The cost is then totaled up and used to give your national idea group a rating:

7 or less: Cannot into relevant
7 to 9: Cannot into stronk
9 to 11: Normal
11 to 13: Stronk
13 to 15: Stronkest
More than 15: Überstronk

The average vanilla national idea group has a cost of 10; the highest cost in vanilla is about 15.

=== Penalties ===

You may also get yellow and red cards for various reasons, including (but not limited to):

* Having a high national idea cost.
* Upgrading technology group.
* Having empty ideas or ideas with negative cost.

Yellow cards represent bending the rules in minor ways, whereas red cards indicate a more major offense, or an ill-formed idea set.

=== Balance ===

Zero cards can be considered a "average" nation; one yellow card can be considered "fair" relative to vanilla. A red card or more than one yellow card is well beyond vanilla or indicates a ill-formed idea set.

How exploitable is the system? Very. I've set the points more towards the average strength of each bonus and so that existing sets can be reproduced, and less towards some idea of actual balance.
