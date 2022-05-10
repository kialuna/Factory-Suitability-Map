# -*- coding: utf-8 -*-
"""
Created on Mon May  9 20:40:19 2022

@author: kia
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
    This is a docstring
    """
    
    def __init__(self,geo_weight=1, pop_weight=1, trans_weight=1): 
        """
        

        Parameters
        ----------
        geo_weight : TYPE, optional
            DESCRIPTION. The default is 1.
        pop_weight : TYPE, optional
            DESCRIPTION. The default is 1.
        trans_weight : TYPE, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        None.

        """
        self.geology=self.import_csv('geology.txt')
        self.landmasked=self.landmask()
        self.geology=self.reverse(self.geology)
        self.transport=self.import_csv('transport.txt')
        self.transport=self.reverse(self.transport)
        self.population=self.import_csv('population.txt')
        
        
        self.overlayMap=self.overlay(geo_weight, pop_weight, trans_weight)
        self.top10=self.top10func(self.overlayMap)
        
    def import_csv(self,file,reverse=False) :
        """
        

        Parameters
        ----------
        file : TYPE
            DESCRIPTION.
        reverse : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        array : TYPE
            DESCRIPTION.

        """
        reader = csv.reader(open(file,newline=''),quoting=csv.QUOTE_NONNUMERIC)
        array=[]
        for row in reader:
            rowlist=[]
            for value in row:
                rowlist.append(value)
            array.append(rowlist)
        #array=np.array(array)    
        return array
    
    def reverse(self,array):
        reversedArray=np.multiply(array,self.landmasked)
        #array=np.array(array)
        
        reversedArray=np.multiply(reversedArray,-1)+255
        reversedArray=np.where(np.isnan(reversedArray),0,reversedArray)
        #plt.imshow(reversedArray)
        #plt.show()
        return reversedArray
    
    def landmask(self):
        geology=np.array(self.geology)
        landmask=np.where(geology>0,1,np.nan)
        plt.imshow(landmask)
        plt.show()
        return landmask
        
    
    def overlay(self,geo_weight,pop_weight,trans_weight):
        
        if (geo_weight+pop_weight+trans_weight==0):
            geo_weight=pop_weight=trans_weight=1
        
        geo_weighted=np.multiply(self.geology,geo_weight)
        pop_weighted=np.multiply(self.population,pop_weight)
        trans_weighted=np.multiply(self.transport,trans_weight)
        
        overlay= geo_weighted + pop_weighted + trans_weighted
        
        overlay=self.scaling(overlay)
        return overlay
    
    def scaling(self, array):
        
        return ((array-np.min(array))/(np.max(array)-np.min(array)))*255
    
    def top10func(self,array,percentile=90):
        land=np.multiply(self.landmasked,array)
        landcount=np.count_nonzero(~np.isnan(self.landmasked))
        limit=np.nanpercentile(land, percentile)
        top10=ma.masked_where(array<limit,array)
        maskcount=top10.count()
        
        
        print(maskcount,landcount,maskcount/landcount)
        return top10
    

class GUI:
    
    def __init__(self,window,arrayMap):
        

        window.title("Map")
    
        self.arrayMap=arrayMap

        self.title_frame=tk.Frame(window) 
        self.title_frame.grid(column=0,row=0,columnspan=2) 
        self.labelTitle=tk.Label(self.title_frame,text="Interactive Suitability Map for Rock Aggregate Factory U.K. ",font=("Arial", 18))

        self.labelTitle.pack(side='top', expand=True,pady=10)



        self.figure, self.ax = plt.subplots(figsize=(10,10))

        self.newcmp=LinearSegmentedColormap.from_list('newcmp', colors=["#252abe", "#f2d3ed"])

        self.imGray = self.ax.imshow(arrayMap.overlayMap, cmap='gray')
        self.legend = self.figure.colorbar(self.imGray,shrink=0.4,location='bottom',ticks=[0,250])
        self.legend.ax.set_xticklabels(['Least Suitable', 'Most Suitable'])
        self.imBlue = self.ax.imshow(arrayMap.top10, cmap=self.newcmp)
        self.imBlue.set_visible(False)
        
        self.map_frame=tk.Frame(window,bg='blue')      
        self.map_frame.grid(column=1,row=1)
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.map_frame)    
        self.canvas.get_tk_widget().pack(side='top', expand=True)
        
        
        self.options_frame=tk.Frame(window)
        self.options_frame.grid(column=0, row=1)
        
        
        self.labelSliders=tk.Label(self.options_frame, wraplength=200,text="Use the sliders below to set the relative weight of the three parameters:")
        self.labelSliders.pack(side='top', expand=True)
        
        self.geoSlider =self.slider("Geology")
        self.popSlider =self.slider("Population")
        self.transSlider =self.slider("Transport")
                
        self.sliderReset()
            
        self.buttonReset=tk.Button(self.options_frame, text="Reset Sliders", command=self.sliderReset)
        self.buttonReset.pack(pady=20,side='top', expand=True)
            
        self.labelToggle=tk.Label(self.options_frame, wraplength=200,text="To view the 10% most suitable area of the U.K, use the toggle button below:")
        self.labelToggle.pack(side='top', expand=True)
        
        self.buttonTop=tk.Button(self.options_frame, text="Toggle Top 10%", command=self.toggle)
        self.buttonTop.pack(pady=20,side='top', expand=True)
        
        self.labelToggle=tk.Label(self.options_frame, wraplength=200,text="To save the map as CSV to the same directory as the code click below:")
        self.labelToggle.pack(side='top', expand=True)

        self.buttonSave=tk.Button(self.options_frame,text="Save",command=self.write)
        self.buttonSave.pack(pady=20)

    def update(self,value):    
        arrayMap.overlayMap=self.arrayMap.overlay(self.geoSlider.get(), self.popSlider.get(), self.transSlider.get())
        self.imGray.set_array(arrayMap.overlayMap)
    
        arrayMap.top10=self.arrayMap.top10func(arrayMap.overlayMap)
        self.imBlue.set_array(arrayMap.top10)
        self.canvas.draw()
        

                
    def slider(self,name):
        return tk.Scale(self.options_frame, from_=0, to=100, label=name, orient=tk.HORIZONTAL,command=self.update,activebackground='#ff7373')
    
    def sliderReset(self):
        for i in [self.geoSlider,self.popSlider,self.transSlider]:
            i.set(50)
            i.pack(padx=20,side='top', expand=True) 
        


    def toggle(self):
        print(self.imBlue.get_visible())
        
        
        if not self.imBlue.get_visible():     
            self.buttonTop.config(relief="sunken")
            self.imBlue.set_visible(True)
            self.canvas.draw()
    
        else:          
            self.buttonTop.config(relief="raised")
            self.imBlue.set_visible(False)
            #barBlue.remove()
            self.canvas.draw()
            
    def write(self):
        with open('suitability_map.csv', 'w', newline='') as f:
            mywriter = csv.writer(f, delimiter=',')
            mywriter.writerows(arrayMap.overlayMap)
            print('done')
    


window = tk.Tk()
gui=GUI(window,arrayMap())
window.mainloop() 