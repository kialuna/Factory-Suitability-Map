# -*- coding: utf-8 -*-
"""
Project: Prgramming Assignment 2 - Factory Suitability Map 
File: app.py
Github Repository: https://github.com/kialuna/Factory-Suitability-Map
-----
File Created: Sunday, 5th May 2022 2:35:02 pm
Student Number: 201578549
-----
License: MIT

"""

import csv
import numpy as np
import numpy.ma as ma
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import LinearSegmentedColormap


class arrayMap:
    """
    Three imported arrays maps of geology, transportation and population in the U.K 
    are overlayed using relative user assigned weights. 
    The most suitable 10% of the U.K is shown as a mask of the rest of the country.
    """

    def __init__(self, geo_weight=1, pop_weight=1, trans_weight=1):
        """
        Initialises the main attributes of the class, including the three contributing maps,
        the initial overlay map, and the initial top 10%.
        
        Parameters
        ----------
        geo_weight : Weight given to geology map. The default is 1.
        pop_weight : Weight given to population map. The default is 1.
        trans_weight : weight given to transport map. The default is 1.


        """
        # Import geology map 
        self.geology = self.import_csv('geology.txt')
        
        # Create land mask
        self.landmasked = self.landmask()
        
        # reverse polarity of geology values 
        self.geology = self.reverse(self.geology)
        
        # Import transport map
        self.transport = self.import_csv('transport.txt')
        
        # Reverse polarity of transport values
        self.transport = self.reverse(self.transport)
        
        # Import population map
        self.population = self.import_csv('population.txt')
        
        # Create overlay map 
        self.overlayMap = self.overlay(geo_weight, pop_weight, trans_weight)
        
        # Create masked map of top 10% of U.K
        self.top10 = self.top10func(self.overlayMap)

    def import_csv(self, file):
        """
        Import text file arrays from current directory and return them as python array.

        Parameters
        ----------
        file : filename.txt

        Returns
        -------
        array : Python array

        """
        # CITATION: Code for this function was reused from assignment 1. 
        
        reader = csv.reader(open(file, newline=''),
                            quoting=csv.QUOTE_NONNUMERIC)
        array = []
        for row in reader:
            rowlist = []
            for value in row:
                rowlist.append(value)
            array.append(rowlist)
        return array

    def reverse(self, array):
        """
        Reverse the polarity of the values in an array with range of values of 0-255. 
        High values become low values, and low values become high values. 

        Parameters
        ----------
        array : array to be reversed

        Returns
        -------
        reversedArray : Array with reversed polarity and range 0-255.

        """
        # Multiply by landmask so that sea values are np.nan
        reversedArray = np.multiply(array, self.landmasked)   
        
        # Multiply by -1          
        reversedArray = np.multiply(reversedArray, -1)   
         
        # Scale to 0-255      
        reversedArray=self.scaling(reversedArray)     
        
        # Set nan values back to zero                 
        reversedArray = np.where(np.isnan(reversedArray), 0, reversedArray) 
        
# =============================================================================
#         # TEST - Shows reversed arrays and max and min of 0 and 255
#         print(np.min(reversedArray),np.max(reversedArray))
#         fig, (ax1, ax2) = plt.subplots(1, 2)
#         ax1.imshow(array)
#         ax2.imshow(reversedArray)
#         plt.show()
# =============================================================================       
        return reversedArray

    def landmask(self):
        """
        Create a land mask of the U.K where land values are 1 and sea 
        values are 0, using the geology map as this had the least zero
        values over the land.

        Returns
        -------
        landmask : Array of nan and 1.

        """
        # Convert geology array to numpy array
        geology = np.array(self.geology)      
        
        # Set 0 values to nan and the rest to 1                         
        landmask = np.where(geology > 0, 1, np.nan)  
                           
# =============================================================================
#         # TEST - prints landmask
#         plt.imshow(landmask)
#         plt.show()
# =============================================================================
        return landmask

    def overlay(self, geo_weight, pop_weight, trans_weight):
        """
        Create an overlay map of geology, population and transport benefits 
        using their relative weights.

        Parameters
        ----------
        geo_weight : Weight given to geology map. 
        pop_weight : Weight given to population map. 
        trans_weight : weight given to transport map. 

        Returns
        -------
        overlay : Overlay array map.

        """
        # If all the weights are zero, set them all to 1 
        if (geo_weight+pop_weight+trans_weight == 0):                           
            geo_weight = pop_weight = trans_weight = 1
            
        # Multiply each array by it's weight    
        geo_weighted = np.multiply(self.geology, geo_weight)                    
        pop_weighted = np.multiply(self.population, pop_weight)
        trans_weighted = np.multiply(self.transport, trans_weight)

        # Add weighted arrays
        overlay = geo_weighted + pop_weighted + trans_weighted                  
        
# =============================================================================
#         # TEST - test for any cell, default is [400][200]
#         def overlay_test(y=400,x=200):
#             print('Initial arrays',self.geology[y][x],self.population[y][x],self.transport[y][x])
#             print('Weights',geo_weight,pop_weight,trans_weight)
#             print('Weighted',geo_weighted[y][x],pop_weighted[y][x],trans_weighted[y][x])
#             print('Total:',overlay[y][x])
#         overlay_test()
# =============================================================================

        # Scale array back to 0-255
        overlay = self.scaling(overlay)  
                                              
        return overlay

    def scaling(self, array):
        """
        Scale array values to 0-255.

        Parameters
        ----------
        array : An array

        Returns
        -------
        An array with values between 0-255
        
        
        >>> arrayMap().scaling([100,105,125])
        array([  0.,  51., 255.])
        >>> arrayMap().scaling([100,305,510])
        array([  0. , 127.5, 255. ])

        """
        scaled=((array-np.nanmin(array))/(np.nanmax(array)-np.nanmin(array)))*255
        
# =============================================================================
#         # TEST - shows arrays being rescaled using histograms - takes a little while
#         # DON'T LEAVE THIS UNCOMMENTED WHEN RUNNING DOCTESTS
#         fig, (ax1,ax2)=plt.subplots(1,2)
#         ax1.hist(array)
#         ax2.hist(scaled)
#         plt.show()
# =============================================================================
        return scaled

    def top10func(self, array, percentile=90):                                  
        """
        By default produces a masked array of the top 10% of cells in an array. 
        The bottom 90% is masked. The percentage can be changed. 

        Parameters
        ----------
        array : Input array
        percentile : The bottom percentile to mask. The default is 90.

        Returns
        -------
        Masked array.

        """
        # Multiply by land mask to set sea values to zero
        land = np.multiply(self.landmasked, array)   
           
        # find 90th percentile of array        
        limit = np.nanpercentile(land, percentile) 
        
        # Mask array where values are less than the 90th percentile                 
        top10 = ma.masked_where(array < limit, array)                           
            
# =============================================================================
#         # TEST top10func
#         landcount = np.count_nonzero(~np.isnan(self.landmasked))
#         maskcount = top10.count()
#         print('\n Count of masked cells:',maskcount, 
#               '\n Count of land cells:',landcount,
#               '\n Portion of land masked:',
#               maskcount/landcount,
#               '\n Cut-off value:',limit,
#               '\n Minimum value of masked area:',top10.min())
# =============================================================================
        return top10


class GUI:
    """
    Tkinter GUI class. 
    
    """

    def __init__(self, window, arrayMap):
        """
        Initialises all of the attributes and widgets of the Tkinter window.

        Parameters
        ----------
        window : Tkinter window in which to display everything.
        arrayMap : 'arrayMap' class to instantiate and use within GUI class.


        """

        window.title("Factory Location Suitability Map")                    
        
        # Instantiate 'arrayMap' class
        self.arrayMap = arrayMap     

        # Create frame for title
        self.title_frame = tk.Frame(window)
        
        # Make frame span two columns across first row
        self.title_frame.grid(column=0, row=0, columnspan=2)
        
        # Write title and add to frame
        self.labelTitle = tk.Label(
            self.title_frame, text="Interactive Suitability Map for Rock Aggregate Factory U.K. ", font=("Arial", 18))
        self.labelTitle.pack(side='top', pady=10)

        # Create matplotlib figure for map
        self.figure, self.ax = plt.subplots(figsize=(10, 10))
        
        # Custom colormap for top 10 area
        self.newcmp = LinearSegmentedColormap.from_list(
            'newcmp', colors=["#252abe", "#f2d3ed"])

        # Create heatmap image from overlay array with legend
        self.imGray = self.ax.imshow(arrayMap.overlayMap, cmap='gray')
        self.legend = self.figure.colorbar(
            self.imGray, shrink=0.4, location='bottom', ticks=[0, 250])
        self.legend.ax.set_xticklabels(['Least Suitable', 'Most Suitable'])
        
        # Create heatmap from top 10% array and set invisible
        self.imBlue = self.ax.imshow(arrayMap.top10, cmap=self.newcmp)
        self.imBlue.set_visible(False)
        
        # Create frame for map canvas and set in second row and second column of grid
        self.map_frame = tk.Frame(window)
        self.map_frame.grid(column=1, row=1)

        # Create Tkinter canvas widget for figure and add to map frame 
        self.canvas = FigureCanvasTkAgg(self.figure, self.map_frame)
        self.canvas.get_tk_widget().pack(side='top', expand=True)
        
        # Create options_frame for sliders and buttons and add to first column second row
        self.options_frame = tk.Frame(window)
        self.options_frame.grid(column=0, row=1)
        
        # Create label and add to options_frame
        self.labelSliders = tk.Label(self.options_frame, wraplength=200,
                                     text="Use the sliders below to set the relative weight of the three parameters:")
        self.labelSliders.pack(side='top', expand=True)

        # Create sliders for each weight
        self.geoSlider = self.slider("Geology")
        self.popSlider = self.slider("Population")
        self.transSlider = self.slider("Transport")
        
        # Set sliders to 50 and add to options_frame 
        self.sliderReset()
        
        # Create slider reset button and add to options_frame 
        self.buttonReset = tk.Button(
            self.options_frame, text="Reset Sliders", command=self.sliderReset)
        self.buttonReset.pack(pady=20, side='top', expand=True)

        # Create label and add to options_frame
        self.labelToggle = tk.Label(self.options_frame, wraplength=200,
                                    text="To view the 10% most suitable area of the U.K, use the toggle button below:")
        self.labelToggle.pack(side='top', expand=True)

        # Create button to toggle top 10% area
        self.buttonTop = tk.Button(
            self.options_frame, text="Toggle Top 10%", command=self.toggle)
        self.buttonTop.pack(pady=20, side='top', expand=True)
        
        # Create label and add to options_frame
        self.labelSave = tk.Label(self.options_frame, wraplength=200,
                                    text="To save the map as a CSV to the same directory as the code click below:")
        self.labelSave.pack(side='top', expand=True)

        # Create button to save map as CSV
        self.buttonSave = tk.Button(
            self.options_frame, text="Save", command=self.write)
        self.buttonSave.pack(pady=20)

    def update(self, value):
        """
        Function which updates map when sliders are moved. 

        Parameters
        ----------
        value : value from slider. Not utilised within the function. 


        """
        # Reset overlayMap array using function from arrayMap class and weights from sliders
        arrayMap.overlayMap = self.arrayMap.overlay(
            self.geoSlider.get(), self.popSlider.get(), self.transSlider.get())
        
        # Reset array in heatmap
        self.imGray.set_array(arrayMap.overlayMap)
        
        # Do the same to the the top10 array 
        arrayMap.top10 = self.arrayMap.top10func(arrayMap.overlayMap)
        self.imBlue.set_array(arrayMap.top10)
        
        # Refresh tk canvas with new arrays
        self.canvas.draw()

    def slider(self, name):
        """
        Creates a Tkinter slider within options_frame, with values from 0-100, 
        oriented horizontally, which triggers the update() function.

        Parameters
        ----------
        name : Label given to slider.

        Returns
        -------
        Tkinter slider.
        """
        return tk.Scale(self.options_frame, from_=0, to=100, label=name, 
                        orient=tk.HORIZONTAL, command=self.update, activebackground='#ff7373')

    def sliderReset(self):
        """
        Resets slider values to 50 and packs them. 

        """
        for i in [self.geoSlider, self.popSlider, self.transSlider]:
            i.set(50)
            i.pack(padx=20, side='top', expand=True)

    def toggle(self):
        """
        Switches visibility of top 10% image triggered by the toggle button.        

        """
        # If the top 10% image is visible, set it to invisible and set the button relief to "raised"
        if self.imBlue.get_visible():
            self.buttonTop.config(relief="raised")
            self.imBlue.set_visible(False)
            self.canvas.draw()
        # If not visible, do the opposite    
        else:    
            self.buttonTop.config(relief="sunken")
            self.imBlue.set_visible(True)
            self.canvas.draw()

        
            

    def write(self):
        """
        Save the overlay map to CSV in the current directory. 
        Filename: suitability_map.csv 

        """
        with open('suitability_map.csv', 'w', newline='') as f:
            mywriter = csv.writer(f, delimiter=',')
            mywriter.writerows(arrayMap.overlayMap)


# Create Tkinter window
window = tk.Tk()
# initiate GUI class using window and arrayMap() class
gui = GUI(window, arrayMap())
# Run application
window.mainloop()
