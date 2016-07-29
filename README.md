# PathTracer
A plugin UE4 and a python script to help you track your players and actors during play tests, but also generate heat maps and grids to visualise their movement and the most used paths.

After you've installed the plugin in your UE4 project, add "PathTracer" to the build.cs file's public dependencies.
If you want to use the Movement tracker, you have to attach it to an Actor:

Add an include "MovementTracker.h" to your actor/pawn's header file, and create a UMovementTracker for it while making it editable in the editor, as such:

UPROPERTY(EditAnywhere)
	class UMovementTracker* MovementTracker;

And initialize it in the cpp file:
MovementTracker = CreateDefaultSubobject<UMovementTracker>(TEXT("MoveTracker"));

Once the projet is compiled, you should see "MovementTracker" in the actor's components; you now have access to four options for reading and writing paths.

Play around with them, but here's the basic overview:

In Write Options:
* Track Actor Path: Enables the recording of paths by recording a series of positions
* Time Interval: The amount of time in seconds between each position recorded

In Read Options:
* Display Tracked Path: Displays the different paths recorded with this actor
* Time Interval: The interval of time between the end and the beginning of the path in seconds. (Zero or less makes the path displayed from its beginning position)

All the paths are recorded as CSV files in "YourProject/Data/MovementTracker/" you can use them as you see fit outside of the plugin.
You are also provided with a HeatmapGenerator.py script. just copy/paste it in the Data/MovementTracker folder and run it to generate three files:

* heatmap.png: the heatmap of all the recorded paths
* heatgrid.png: the heatgrid that represents the heat of sections of the map
* heatgrid.csv: a data version of the grid usable outside of the script

You also have some argument you can pass to the script, which are, in order:
* python HeatmapGenerator.py [grain] [pathWidth] [borderWidth]

A quick overview:
* grain: (default: 250) is the height and width in pixels of the different sections of the heatgrid.
* pathWidth: (default 50) is the radius, in pixels, of the paths displayed in the heatmap.
* borderWidth: (default 0) is the width in pixels of black border that you can put around the heatmap and heatgrid images to make them a bit more readable.

Note that the PNG files have a resolution representing the size of all recorded paths, where 1 pixel is equal to 1 Unreal Unit.
