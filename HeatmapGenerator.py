import png
import pandas as pd
import fnmatch
import os
import math
import numpy as np
import sys

#Variables that depends on the script argument
grain = 250
pathWidth = 50
borderX = borderY = 0

#Variables used during runtime
minX = minY = maxX = maxY = sizeX = sizeY = 0
maxPoints = secondBest = 0
filesAnalyzed = nbFiles = 0
per20 = per40 = per60 = per80 = 0

#Call this function to terminate the program and display a 'usage' error message
def usage():
    "Call this function to terminate the program and display a 'usage' error message"
    sys.exit("usage: python HeatmapGenerator.py [Grain as int > 0] [pathWidth as int > 0] [borderSize as int >= 0]")

#Returns a list containing the paths of all the CSV-type files
#in the same folder as the script. 'heatgrid.csv' is ignored.
def getAllCSVFiles():
    "Returns a list containing the paths of all the CSV-type files in the same folder as the script. 'heatgrid.csv' is ignored."
    result = []
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if fnmatch.fnmatch(file, '*.csv') and file != 'heatgrid.csv':
            result.append(os.path.dirname(os.path.abspath(__file__)) + "\\" + file)
    return result

#Returns a properly formatted pixel list compatible with the
#pyPNG module that represents the Heatmap.
#The parameter is the grid containing the heat value of each pixel. (1px = 1uu)
def getImgPixels(heatGrid):
    "Returns a properly formatted pixel list compatible with the pyPNG module that represents the Heatmap. The parameter is the grid containing the heat value of each pixel. (1px = 1uu)"
    result = []
    for y in range(0, sizeY):
        row = []
        for x in range(0, sizeX):
            if x >= borderX and y >= borderY and x < sizeX - borderX and y < sizeY - borderY:
                row += getColorFromHeat(int(heatGrid[y - borderY][x - borderX]))
            else:
                row += [0, 0, 0]
        result.append(row)
    return result

#Returns a properly formatted pixel list compatible with the
#pyPNG module that represents the Heatgrid.
#The parameter is the grid containing the number of points in each grid tile. (1px = 1uu)
def getGridPixels(refinedGrid):
    "Returns a properly formatted pixel list compatible with the pyPNG module that represents the Heatgrid. The parameter is the grid containing the number of points in each grid tile. (1px = 1uu)"
    result = []
    prevPercent = 0
    for y in range(0, sizeY):
        row = []
        for x in range(0, sizeX):
            if x >= borderX and y >= borderY and x < sizeX - borderX and y < sizeY - borderY:
                row += getColorFromPoints((x - borderX) // grain, (y - borderY) // grain, refinedGrid)
            else:
                row += [0, 0, 0]
        if int(y / sizeY * 100) % 25 == 0 and int(y / sizeY * 100) != prevPercent:
            print("%d%%" % (int(y / sizeY * 100)))
            prevPercent = int(y / sizeY * 100)
        result.append(row)
    return result

#Returns a grid that divides the heatmap in several tiles of height and width
#corresponding to the grain. Each value is set at the number of points contained in the tile.
def getRefinedGrid():
    "Returns a grid that divides the heatmap in several tiles of height and width corresponding to the grain. Each value is set at the number of points contained in the tile."
    grid = []
    for y in range((sizeY - 2 * borderY) // grain):
        row = []
        for x in range((sizeX - 2 * borderX) // grain):
            row.append(0)
        grid.append(row)
    for f in getAllCSVFiles():
        df = pd.read_csv(f)
        if 'X' in df.columns and 'Y' in df.columns:
            if df.X.dtype == 'float64' and df.Y.dtype == 'float64':
                filePos = list(zip(df.X, df.Y))
                for pair in filePos:
                    x = (int(pair[0]) - minX + borderX) // grain
                    y = (int(pair[1]) - minY + borderY) // grain
                    if x >= len(grid[0]):
                        x = len(grid[0]) - 1
                    if y >= len(grid):
                        y = len(grid) - 1
                    grid[y][x] += 1
    return grid

#Returns a two dimensional list containing one value for each pixel representing
#the heat of that pixel. Calls setHeatMap to fill this grid with the proper heat values.
def getHeatGrid():
    "Returns a two dimensional list containing one value for each pixel representing the heat of that pixel. Calls setHeatMap to fill this grid with the proper heat values."
    grid = []
    for y in range(sizeY - 2 * borderY):
        row = []
        for x in range(sizeX - 2 * borderX):
            row.append(0)
        grid.append(row)
    setHeatMap(grid, pathWidth)
    return grid

#Returns a [R, G, B] color value for pixels according to the heat,
#using the four values that respectively represent the value at which
#the heat should yield a blue, a light blue, a yellow and a red color.
def getColorFromHeat(heat, p1 = 51, p2 = 102, p3 = 153, p4 = 204):
    "Returns a [R, G, B] color value for pixels according to the heat, using the four values that respectively represent the value at which the heat should yield a blue, a light blue, a yellow and a red color."
    if heat <= p1:
        return [0, 0, int(heat / p1 * 255)]
    elif heat <= p2:
        return [0, int((heat - p1) / (p2 - p1) * 255), 255]
    elif heat <= p3:
        return [int((heat - p2) / (p3 - p2) * 255), 255, int(255 - (heat - p2) / (p3 - p2) * 255)]
    elif heat <= p4:
        return [255, int(255 - (heat - p3) / (p4 - p3) * 255), 0]
    else:
        return [255, 0, 0]

#Returns a [R, G, B] color value according to the point value at grid[y][x].
#grid should be the one containing the number of points per tile, got from getRefinedGrid().
def getColorFromPoints(x, y, grid):
    "Returns a [R, G, B] color value according to the point value at grid[y][x]. grid should be the one containing the number of points per tile, got from getRefinedGrid()."
    if x >= len(grid[0]):
        x = len(grid[0]) - 1
    if y >= len(grid):
        y = len(grid) - 1
    points = grid[y][x]
    if points != 0:
        return getColorFromHeat(points, per20, per40, per60, per80)
    else:
        return getColorFromHeat(0)

#Sets the global variables per20, per40, per60, per80 representing
#the percentiles of corresponding percentage in the number of points per tile list.
def getPercentile(refinedGrid):
    "Sets the global variables per20, per40, per60, per80 representing the percentiles of corresponding percentage in the number of points per tile list."
    global per20
    global per40
    global per60
    global per80
    heatList = []
    for row in refinedGrid:
        for value in row:
            if value != 0:
                heatList.append(value)
    per20 = np.percentile(heatList, 20)
    per40 = np.percentile(heatList, 40)
    per60 = np.percentile(heatList, 60)
    per80 = np.percentile(heatList, 80)
    
#Creates the 'heatgrid.csv' file with information from the Heatgrid.
def createCSV(refinedGrid):
    "Creates the 'heatgrid.csv' file with information from the Heatgrid."
    csvInfo = []
    for y in range((sizeY - 2 * borderY) // grain):
        for x in range((sizeX - 2 * borderX) // grain):
            csvInfo.append((x, y, refinedGrid[y][x], grain, \
                            refinedGrid[y][x] / maxPoints * 255, \
                            math.sqrt(refinedGrid[y][x] / maxPoints) * 255))
            if refinedGrid[y][x] > 0:
                csvInfo[len(csvInfo) - 1] += (math.log(refinedGrid[y][x]) / math.log(maxPoints) * 255, \
                                              (refinedGrid[y][x] * math.log(refinedGrid[y][x])) / (maxPoints * math.log(maxPoints)) * 255)
            else:
                csvInfo[len(csvInfo) - 1] += (0, 0)
    df = pd.DataFrame(data = csvInfo, columns = ['X', 'Y', 'Number of Points', 'Grid Grain', \
                                                 'Heat Value', 'Square Root', 'Logarithm', \
                                                 'n * log(n)'])
    df.to_csv('heatgrid.csv', index=False,header=True)
#Sets sizeX and sizeY, the size of the final PNG files. 1px = 1uu
def setImageSize(pairList):
    "Sets sizeX and sizeY, the size of the final PNG files. 1px = 1uu"
    global minX
    global maxX
    global minY
    global maxY
    global sizeX
    global sizeY
    for pair in pairList:
        if minX > int(pair[0]):
            minX = int(pair[0])
        if minY > int(pair[1]):
            minY = int(pair[1])
        if maxX < int(pair[0]):
            maxX = int(pair[0])
        if maxY < int(pair[1]):
            maxY = int(pair[1])
    sizeX = maxX - minX + 2 * borderX
    sizeY = maxY - minY + 2 * borderY

#Sets the heat value of each pixel in the grid generated in getHeatGrid().
def setHeatMap(heatGrid, radius):
    "Sets the heat value of each pixel in the grid generated in getHeatGrid()."
    global filesAnalyzed
    for f in getAllCSVFiles():
        filesAnalyzed += 1
        print("File %d out of %d: " % (filesAnalyzed, nbFiles) + f)
        df = pd.read_csv(f)
        if 'X' in df.columns and 'Y' in df.columns:
            if df.X.dtype == 'float64' and df.Y.dtype == 'float64':
                filePos = list(zip(df.X, df.Y))
                for pair in filePos:
                    x = int(pair[0]) - minX + borderX
                    y = int(pair[1]) - minY + borderY
                    for Yi in range(max(0, y - radius), min(sizeY - 2 * borderY, y + radius + 1)):
                        for Xi in range(max(0, x - radius), min(sizeX - 2 * borderX, x + radius + 1)):
                            distance = math.sqrt((x - Xi) ** 2 + (y - Yi) ** 2)
                            if (distance <= radius and heatGrid[Yi][Xi] < 255):
                                heatGrid[Yi][Xi] += 25.5 * secondBest / maxPoints * (1 - distance / radius)
                                if heatGrid[Yi][Xi] > 255:
                                    heatGrid[Yi][Xi] = 255

#Sets the values of maxPoints and secondBest, which respectively represents
#the highest and second highest number of points per tile.
def setPointValues(grid):
    "Sets the values of maxPoints and secondBest, which respectively represents the highest and second highest number of points per tile."
    global maxPoints
    global secondBest
    maxPoints = secondBest = 0
    for row in grid:
        for nb in row:
            if nb >= maxPoints:
                secondBest = maxPoints
                maxPoints = nb
            elif nb > secondBest:
                secondBest = nb

#Analyzes the values of the optional arguments and sets the global variables accordingly.
def setArgumentValues(argv):
    "Analyzes the values of the optional arguments and sets the global variables accordingly."
    global grain
    global pathWidth
    global borderX
    global borderY
    if len(argv) > 0:
        if argv[0].isdigit() and int(argv[0]) > 0:
            grain = int(argv[0])
        else:
            usage()
    if len(argv) > 1:
        if argv[1].isdigit() and int(argv[1]) > 0:
            pathWidth = int(argv[1])
        else:
            usage()
    if len(argv) > 2:
        if argv[2].isdigit() and int(argv[2]) >= 0:
            borderX = int(argv[2])
            borderY = int(argv[2])
        else:
            usage()

setArgumentValues(sys.argv[1:])
print("Files to analyze:")
for file in getAllCSVFiles():
    print(file)
    nbFiles += 1
    df = pd.read_csv(file)
    if 'X' in df.columns and 'Y' in df.columns:
        if df.X.dtype == 'float64' and df.Y.dtype == 'float64':
            setImageSize(list(zip(df.X, df.Y)))

refinedGrid = getRefinedGrid()
getPercentile(refinedGrid)
setPointValues(refinedGrid)
createCSV(refinedGrid)
image = png.Writer(sizeX, sizeY)

print("\nGenerating HeatMap: (It may take several minutes)")
map = open(os.path.dirname(os.path.abspath(__file__)) + '\\heatmap.png', 'w+b')
heatGrid = getHeatGrid()
pixels = getImgPixels(heatGrid)
image.write(map, pixels)
map.close()

print("\nGenerating HeatGrid: (It may take several minutes)")
grid = open(os.path.dirname(os.path.abspath(__file__)) + '\\heatgrid.png', 'w+b')
pixels = getGridPixels(refinedGrid)
image.write(grid, pixels)
grid.close()

print("---------------")
print("Image size: %d x %d" % (sizeX, sizeY))
print("Grid size: %d x %d" % (len(refinedGrid[0]), len(refinedGrid)))
print("Highest number of point: %d" % maxPoints)
print("Second best: %d" % secondBest)
print("Path radius: %dpx" % pathWidth)
print("Grid grain: %dpx" % grain)

print("\nDONE: heatmap.png and heatgrid.png were generated")

input("\nPress Enter to quit.")