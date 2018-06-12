import os
from tkinter import *
import arcpy
from arcpy import env
from arcpy.sa import *
from PIL import Image, ImageTk
import tkMessageBox

#Setting up the different functions that are needed for the application
def idwHelp():
    tkMessageBox.showinfo("Inverse Weighted Distance", "Information about Inverse Weighted Distance")

def censusHelp():
    tkMessageBox.showinfo("Census Units Help", "Information about the different Census units")

def idw():
    #Setting up the workspace
    arcpy.env.workspace = "C:\\MAMP\\htdocs\\cancerAnalysis\\files\\well_nitrate"
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")
    # status["text"] = "Running IDW..."

    #Setting up the variables
    inPoint = "well_nitrate.shp"
    zField = "nitr_ran"
    power = float(powerEntry.get())
    print power
    searchRadius = RadiusVariable(10, 150000)

    #Run IDW
    idwOutPut = Idw(inPoint, zField, "", power, searchRadius)

    #Save the output raster
    idwOutPut.save("C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\idw.tif")

    #Update the mxd to include the IDW raster
    mxd = arcpy.mapping.MapDocument(r"C:\\MAMP\\htdocs\\cancerAnalysis\\idwMap.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

    #Change the symbology of the IDW raster
    idwTiff = arcpy.mapping.Layer(r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\idw.tif")
    idwSymbology = r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\idwSymbology.lyr"
    arcpy.ApplySymbologyFromLayer_management(idwTiff, idwSymbology)

    #Add newly changed IDW raster to the map
    arcpy.mapping.AddLayer(dataFrame, idwTiff, "BOTTOM")

    #Export the map
    arcpy.mapping.ExportToPNG(mxd, "C:\\MAMP\\htdocs\\cancerAnalysis\\idwResults.png")
    # status["text"] = "Completed IDW..."

def displayIDW():
    image2 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\idwResults.png")
    mapDisplay.configure(image=image2)
    mapDisplay.image = image2
    Image.ANTIALIAS

#Setting up the workspace
env.workspace = "U:\School\Geog777\Project1\Workspace"

#Creating the GUI window
root = Tk()
root.title("Relationship between Cancer and Nitrate Levels")
# root.resizable(width = FALSE, height = FALSE)
root.geometry("1250x800")

#Split the root into 2 different frames
top = Frame(root)
bottom = Frame(root)
top.pack(side=TOP)
bottom.pack(side=BOTTOM, fill=BOTH)

#Section for the map display
imagePath = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\test.png")
mapDisplay = Label(root, image=imagePath, bg="black")
mapDisplay.pack(side=TOP, padx=10, pady=10)
Image.ANTIALIAS

#Create a new frame
execute = Frame(bottom, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="gray")
execute.pack(side=LEFT, padx=10, pady=10)

#Title for the execution frame
executeTitle = Text(execute, width=20, height=1, wrap=WORD)
executeTitle.insert(INSERT, "Execute Analysis")
executeTitle.pack(padx=5,pady=1)

#Instructions for the user
executeLabel = Label(execute, text="Enter a Power Value:")
executeLabel.pack()

#Create the power entry box
powerEntry = Entry(execute, bg="red")
powerEntry.pack(pady=1)

#Create the buttons to either run the analysis or get help about the analysis
# executeButton = Button(execute, text="Run", width=5)
executeHelp = Button(execute, text="Help", command=idwHelp)
# executeButton.pack(side=LEFT)

#Pack the buttons under the entry box
# executeHelp = Button(execute, text="Help", width=10)
# executeButton.pack(side=LEFT, fill=X, padx=25)
executeHelp.pack(padx=5)

#Create a new frame for the spatial unit
units = Frame(bottom, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="gray")
units.pack(padx=10, pady=10)

#Title for the spatial units frame
unitsTitle = Text(units, width=25, height=1, wrap=WORD)
unitsTitle.insert(INSERT, "Choose a Spatial Unit:")
unitsTitle.pack(padx=5, pady=1)

#Create the radiobuttons
var = IntVar()
tracts = Radiobutton(units, text="Census Tracts", variable=var, value=1)
blocks = Radiobutton(units, text="Census Block", variable=var, value=2, width=10)
unitsHelp = Button(units, text="Help", command=censusHelp)
tracts.pack()
blocks.pack()
unitsHelp.pack()

#Create a new frame for the different map displays
displays = Frame(bottom, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="gray")
displays.pack(side=RIGHT, pady=10)

#Title for the map displays
displaysTitle = Text(displays, width=25, height=1, wrap=WORD)
displaysTitle.insert(INSERT, "Choose a map display:")
displaysTitle.pack(padx=5, pady=1)

#Create the buttons to determine the map display
idwDisplay = Button(displays, text="IDW", command=displayIDW)
olsDisplay = Button(displays, text="Regression", command=idw)
idwDisplay.pack()
olsDisplay.pack(side=LEFT)

root.mainloop()
