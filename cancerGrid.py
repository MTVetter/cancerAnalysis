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

#Setting up the workspace
env.workspace = "U:\School\Geog777\Project1\Workspace"

#Creating the GUI window
root = Tk()
root.title("Relationship between Cancer and Nitrate Levels")
root.geometry("1250x800")

# #Section for the map display
imagePath = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\test.png")
mapDisplay = Label(root, image=imagePath, bg="black").grid(columnspan=5,padx=50)
Image.ANTIALIAS

# #Create a new frame
execute = Frame(root, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="gray")
execute.grid(row=5, column=0, sticky=W, padx=50, pady=20)


# #Title for the execution frame
executeTitle = Text(execute, width=20, height=1, wrap=WORD)
executeTitle.insert(INSERT, "Execute Analysis")
executeTitle.grid(row=6, column=0, sticky=W)

# #Instructions for the user
executeLabel = Label(execute, text="Enter a Power Value:")
executeLabel.grid(row=7, column=0)

# #Create the power entry box
powerEntry = Entry(execute, bg="red")
powerEntry.grid(row=8, columnspan=2)

# #Create the buttons to either run the analysis or get help about the analysis
executeHelp = Button(execute, text="Help", command=idwHelp)
executeHelp.grid(row=9)

# #Create a new frame for the spatial unit
units = Frame(root, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="gray")
units.grid(row=5, column=1, sticky=W, padx=50, pady=20)

# #Title for the spatial units frame
unitsTitle = Text(units, width=25, height=1, wrap=WORD)
unitsTitle.insert(INSERT, "Choose a Spatial Unit:")
unitsTitle.grid(row=6, column=1)

# #Create the radiobuttons
var = IntVar()
tracts = Radiobutton(units, text="Census Tracts", variable=var, value=1)
blocks = Radiobutton(units, text="Census Block", variable=var, value=2, width=10)
unitsHelp = Button(units, text="Help", command=censusHelp)
tracts.grid(row=7, column=1)
blocks.grid(row=8, column=1)
unitsHelp.grid(row=9, columnspan=3)


# #Create a new frame for the different map displays
# displays = Frame(bottom, highlightbackground="gray", highlightcolor="gray", highlightthickness=.5, bg="gray")
# displays.pack(side=RIGHT, pady=10)

# #Title for the map displays
# displaysTitle = Text(displays, width=25, height=1, wrap=WORD)
# displaysTitle.insert(INSERT, "Choose a map display:")
# displaysTitle.pack(padx=5, pady=1)

# #Create the buttons to determine the map display
# idwDisplay = Button(displays, text="IDW")
# olsDisplay = Button(displays, text="Regression")
# idwDisplay.pack()
# olsDisplay.pack(side=LEFT)

root.mainloop()