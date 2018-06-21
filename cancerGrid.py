import os
from tkinter import *
import arcpy
from arcpy import env
from arcpy.sa import *
from PIL import Image, ImageTk
import tkMessageBox, tkFileDialog, tkFont

#Setting up the different functions that are needed for the application
def idwHelp():
    tkMessageBox.showinfo("Inverse Weighted Distance", "Inverse Weighted Distance (IDW) is the most widely used interpolation." +
    "\n\nIDW uses the theory of close things are more related than distant things most explicitly." +
    "\n\nIDW assigns weights quantitatively based on distance from a known point." +
    "\n\nThe power you enter will determine how quickly locations are no longer considered close." +
    "\n\nTypically the power value should be between 1.5 and 2.5")

def censusHelp():
    tkMessageBox.showinfo("Census Units Help", "Information about the different Census units")

def idw():
    #Determine which spatial unit the user chose
    selection = unitVar.get()

    #Setting up the workspace
    arcpy.env.workspace = "C:\\MAMP\\htdocs\\cancerAnalysis\\files"
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")

    #Setting up the variables for the IDW tool
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
    del mxd

    #Update the county mxd to include the IDW raster
    mxd2 = arcpy.mapping.MapDocument(r"C:\\MAMP\\htdocs\\cancerAnalysis\\countyIDWMap.mxd")
    dataFrame2 = arcpy.mapping.ListDataFrames(mxd2, "Layers")[0]
    arcpy.mapping.AddLayer(dataFrame2, idwTiff, "BOTTOM")
    arcpy.mapping.ExportToPNG(mxd2, "C:\\MAMP\\htdocs\\cancerAnalysis\\countyIDWResults.png")
    idwDisplay.config(state=NORMAL)
    tkMessageBox.showinfo("Completed IDW", "Completed IDW interpolation...")

    #Setting up the process for the two different spatial units
    if selection == 1:
        #Allow overwriting
        arcpy.env.overwriteOutput = True

        #Setting up the variables for the Zonal Statistics tool
        inZone = "cancer_tracts.shp"
        zone = "GEOID10"
        rasterValue = idwTiff
        table = "zonalStatistics.dbf"

        #Run the Zonal Statistics tool
        outZoneStat = ZonalStatisticsAsTable(inZone, zone, rasterValue, table, "NODATA", "MEAN")

        #Join the Zonal Statistics table with the census tracts
        try:
            #Setting up the variables
            inFeatures = "cancer_tracts.shp"
            layerName = "cancer_tracts"
            joinTable = "zonalStatistics.dbf"
            joinField = "GEOID10"
            outputFeature = r"C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\joinedCensus"

            #Make a feature layer from the cancer tracts
            arcpy.MakeFeatureLayer_management(inFeatures, layerName)

            #Join the feature to the table
            arcpy.AddJoin_management(layerName, joinField, joinTable, joinField, "KEEP_COMMON")

            #Create a copy of the joined layer
            arcpy.CopyFeatures_management(layerName, outputFeature)
            tkMessageBox.showinfo("Completed Zonal Statistics", "Completed Zonal Statistics...")
        except Exception, e:
            import traceback, sys
            tb = sys.exc_info()[2]
            print "Line %i" % tb.tb_lineno
            print e.message

        #Run linear regression on the results
        try:
            #Set the environment to allow to overwrite existing data
            arcpy.env.overwriteOutput = True

            #Create the tool to run Ordinary Least Squares
            ordLeastSq = arcpy.OrdinaryLeastSquares_stats("C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\joinedCensus",
            "cancer_tracts_ID", "C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\olsResults", "cancer_tracts_canrate",
            "zonalStatistics_MEAN", "", "C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\olsTable.pdf")
        except:
            print (arcpy.GetMessages())

        #Get the mxd
        olsMXD = arcpy.mapping.MapDocument("C:\\MAMP\\htdocs\\cancerAnalysis\\OLSmap.mxd")
        olsDF = arcpy.mapping.ListDataFrames(olsMXD, "Layers")[0]

        #Add the OLS output to an mxd and apply symbology
        olsResults = arcpy.mapping.Layer(r"C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\olsResults")
        olsSymbology = r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\olsSymbology.lyr"
        arcpy.ApplySymbologyFromLayer_management(olsResults, olsSymbology)
        arcpy.mapping.AddLayer(olsDF, olsResults, "AUTO_ARRANGE")

        #Add the legend to the map
        olsLegend = arcpy.mapping.ListLayoutElements(olsMXD, "LEGEND_ELEMENT", "Legend")[0]
        olsLegend.autoAdd = True

        #Export the mxd
        arcpy.mapping.ExportToPNG(olsMXD, "C:\\MAMP\\htdocs\\cancerAnalysis\\olsResults.png")
        tkMessageBox.showinfo("Completed OLS", "Completed Ordinary Least Squares..." + "\n\nYou can now view and download the maps")
        olsDisplay.config(state=NORMAL)
        downloadButton.config(state=NORMAL)
        image3 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\olsResults.png")
        mapDisplay.configure(image=image3)
        mapDisplay.image = image3
        Image.ANTIALIAS
    else:
        #Allow overwriting
        arcpy.env.overwriteOutput = True

        #Setting up the variables for the Zonal Statistics tool
        inZone = "cancer_county.shp"
        zone = "GEOID10"
        rasterValue = idwTiff
        table = "zonalStatistics.dbf"

        #Run the Zonal Statistics tool
        outZoneStat = ZonalStatisticsAsTable(inZone, zone, rasterValue, table, "NODATA", "MEAN")

        #Join the Zonal Statistics table with the census tracts
        try:
            #Setting up the variables
            inFeatures = "cancer_county.shp"
            layerName = "cancer_county"
            joinTable = "zonalStatistics.dbf"
            joinField = "GEOID10"
            outputFeature = r"C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\joinedCounty"

            #Make a feature layer from the cancer tracts
            arcpy.MakeFeatureLayer_management(inFeatures, layerName)

            #Join the feature to the table
            arcpy.AddJoin_management(layerName, joinField, joinTable, joinField, "KEEP_COMMON")

            #Create a copy of the joined layer
            arcpy.CopyFeatures_management(layerName, outputFeature)
            tkMessageBox.showinfo("Completed Zonal Statistics", "Completed Zonal Statistics...")
        except Exception, e:
            import traceback, sys
            tb = sys.exc_info()[2]
            print "Line %i" % tb.tb_lineno
            print e.message

        #Run linear regression on the results
        try:
            #Set the environment to allow to overwrite existing data
            arcpy.env.overwriteOutput = True

            #Create the tool to run Ordinary Least Squares
            ordLeastSq = arcpy.OrdinaryLeastSquares_stats("C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\joinedCounty",
            "zonalStatistics_ZONE_CODE", "C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\countyOLSResults", "cancer_county_canrate",
            "zonalStatistics_MEAN", "", "C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\countyOLSTable.pdf")
        except:
            print (arcpy.GetMessages())

        #Get the mxd
        olsMXD = arcpy.mapping.MapDocument("C:\\MAMP\\htdocs\\cancerAnalysis\\OLSmap.mxd")
        olsDF = arcpy.mapping.ListDataFrames(olsMXD, "Layers")[0]

        #Add the OLS output to an mxd and apply symbology
        olsResults = arcpy.mapping.Layer(r"C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\countyOLSResults")
        olsSymbology = r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\olsSymbology.lyr"
        arcpy.ApplySymbologyFromLayer_management(olsResults, olsSymbology)
        arcpy.mapping.AddLayer(olsDF, olsResults, "AUTO_ARRANGE")

        #Add the legend to the map
        olsLegend = arcpy.mapping.ListLayoutElements(olsMXD, "LEGEND_ELEMENT", "Legend")[0]
        olsLegend.autoAdd = True

        #Export the mxd
        arcpy.mapping.ExportToPNG(olsMXD, "C:\\MAMP\\htdocs\\cancerAnalysis\\countyOLSResults.png")
        olsDisplay.config(state=NORMAL)
        downloadButton.config(state=NORMAL)
        tkMessageBox.showinfo("Completed OLS", "Completed Ordinary Least Squares..." + "\n\nYou can now view and download the maps")
        image3 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\countyOLSResults.png")
        mapDisplay.configure(image=image3)
        mapDisplay.image = image3
        Image.ANTIALIAS

def displayIDW():
    selection = unitVar.get()
    if selection == 1:
        image2 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\idwResults.png")
        mapDisplay.configure(image=image2)
        mapDisplay.image = image2
        Image.ANTIALIAS
    else:
        image2 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\countyIDWResults.png")
        mapDisplay.configure(image=image2)
        mapDisplay.image = image2
        Image.ANTIALIAS

def displayOLS():
    selection = unitVar.get()
    if selection == 1:
        image4 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\olsResults.png")
        mapDisplay.configure(image=image4)
        mapDisplay.image = image4
        Image.ANTIALIAS
    else:
        image4 = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\countryOLSResults.png")
        mapDisplay.configure(image=image4)
        mapDisplay.image = image4
        Image.ANTIALIAS

def downloadMaps():
    #User enter the path for the downloaded maps
    dirName = tkFileDialog.askdirectory(parent=root, initialdir="/")

    #Get the two mxds
    mxd = arcpy.mapping.MapDocument(r"C:\\MAMP\\htdocs\\cancerAnalysis\\idwMap.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

    #Change the symbology of the IDW raster
    idwTiff = arcpy.mapping.Layer(r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\idw.tif")
    idwSymbology = r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\idwSymbology.lyr"
    arcpy.ApplySymbologyFromLayer_management(idwTiff, idwSymbology)

    #Add newly changed IDW raster to the map
    arcpy.mapping.AddLayer(dataFrame, idwTiff, "BOTTOM")

    #Export the map
    location = os.path.join(dirName, "idwResults.pdf")
    arcpy.mapping.ExportToPDF(mxd, location)

    #Get the OLS mxd
    olsMXD = arcpy.mapping.MapDocument("C:\\MAMP\\htdocs\\cancerAnalysis\\OLSmap.mxd")
    olsDF = arcpy.mapping.ListDataFrames(olsMXD, "Layers")[0]

    #Add the OLS output to an mxd and apply symbology
    olsResults = arcpy.mapping.Layer(r"C:\\MAMP\\htdocs\\cancerAnalysis\\files\\Result_Testing.gdb\\olsResults")
    olsSymbology = r"C:\\MAMP\\htdocs\\cancerAnalysis\\project1\\olsSymbology.lyr"
    arcpy.ApplySymbologyFromLayer_management(olsResults, olsSymbology)
    arcpy.mapping.AddLayer(olsDF, olsResults, "AUTO_ARRANGE")

    #Add the legend to the map
    olsLegend = arcpy.mapping.ListLayoutElements(olsMXD, "LEGEND_ELEMENT", "Legend")[0]
    olsLegend.autoAdd = True

    #Export the mxd
    location2 = os.path.join(dirName, "olsResults.pdf")
    arcpy.mapping.ExportToPDF(olsMXD, location2)

    #Message to say that the download is complete
    tkMessageBox.showinfo("Download Complete", "The map download has completed. Navigate to the selected folder to see the results.")


#Creating the GUI window
root = Tk()
root.title("Relationship between Cancer and Nitrate Levels")
root.geometry("1050x800")
root.configure(background="papaya whip")

# #Section for the map display
imagePath = ImageTk.PhotoImage(file="C:\\MAMP\\htdocs\\cancerAnalysis\\nitrateWells.png")
mapDisplay = Label(root, image=imagePath, bg="black")
mapDisplay.grid(columnspan=4,padx=50)
Image.ANTIALIAS

# #Create a new frame
execute = Frame(root, highlightbackground="black", highlightcolor="black", highlightthickness=1, bg="gray72")
execute.grid(row=5, column=0, sticky=W, padx=50, pady=20)


# #Title for the execution frame
executeTitle = Text(execute, width=20, height=1, wrap=WORD)
executeTitle.insert(INSERT, "Execute Analysis")
executeTitle.config(state=DISABLED)
executeTitle.configure(font=("Baskerville Old Face", "13"))
executeTitle.grid(row=6, column=0, sticky=W)

# #Instructions for the user
executeLabel = Label(execute, text="Enter a Power Value:", font=("Baskerville Old Face", "10"))
executeLabel.grid(row=7, column=0)

# #Create the power entry box
powerEntry = Entry(execute, bg="white")
powerEntry.grid(row=8, columnspan=2)

# #Create the buttons to either run the analysis or get help about the analysis
executeHelp = Button(execute, text="Help", command=idwHelp)
executeHelp.grid(row=9)

# #Create a new frame for the spatial unit
units = Frame(root, highlightbackground="black", highlightcolor="black", highlightthickness=1, bg="gray72")
units.grid(row=5, column=1, sticky=W, padx=50, pady=20)

# #Title for the spatial units frame
unitsTitle = Text(units, width=25, height=1, wrap=WORD)
unitsTitle.insert(INSERT, "Choose a Spatial Unit:")
unitsTitle.config(state=DISABLED)
unitsTitle.configure(font=("Gill Sans", "11"))
unitsTitle.grid(row=6, column=1)

# #Create the radiobuttons
unitVar = IntVar()
unitVar.set(1)
tracts = Radiobutton(units, text="Census Tracts", font=("Garamond", "10"), variable=unitVar, value=1)
blocks = Radiobutton(units, text="Counties", variable=unitVar, value=2, width=10)
unitsHelp = Button(units, text="Help", command=censusHelp)
tracts.grid(row=7, column=1)
blocks.grid(row=8, column=1)
unitsHelp.grid(row=9, columnspan=3)


# #Create a new frame for the different map displays
displays = Frame(root, highlightbackground="black", highlightcolor="black", highlightthickness=1, bg="gray72")
displays.grid(row=5, column=2, padx=50, pady=20)

# #Title for the map displays
displaysTitle = Text(displays, width=25, height=1, wrap=WORD)
displaysTitle.insert(INSERT, "Choose a map display:")
displaysTitle.config(state=DISABLED)
displaysTitle.configure(font=("Baskerville Old Face", "13"))
displaysTitle.grid(row=6, column=2)

# #Create the buttons to determine the map display
idwDisplay = Button(displays, text="IDW", command=displayIDW)
olsDisplay = Button(displays, text="Regression", command=displayOLS)
idwDisplay.config(state=DISABLED)
olsDisplay.config(state=DISABLED)
idwDisplay.grid(row=7, columnspan=3)
olsDisplay.grid(row=8, columnspan=3)

# #Create the buttons to run the script and to download the map
run = Frame(root, highlightbackground="black", highlightcolor="black", bg="papaya whip")
run.grid(row=5, column=3)
runButton = Button(run, text="Run", command=idw)
runButton.grid(row=5)
downloadButton = Button(run, text="Download", command=downloadMaps)
downloadButton.config(state=DISABLED)
downloadButton.grid(row=6)


root.mainloop()
