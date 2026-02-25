import src.aerosol as aerosol
import logging
import numpy as np
import asyncio

from typing import List, Dict
from scipy.interpolate import CubicSpline 

class SMPSProcessor():
    

    def __init__(self, DMA_Type : str,
                 upscantime : int,
                 aerosol_flow_rate : int,
                 sheath_flow_rate : int):

        logging.basicConfig(filename="smps_postprocessing.log",level=logging.INFO)
        
        self._logger = logging.getLogger(__name__)
        self._upscantime = upscantime
        self._aerosol_flow_rate = aerosol_flow_rate
        self._sheath_flow_rate = sheath_flow_rate
        self._DMA_TYPE = DMA_Type
        
        self._initialize_SMPS_paramters()
        


    async def convert_to_size_distribution(self,
                                     data : List[Dict],
                                     minvoltage : int,
                                     maxvoltage : int) -> List[Dict]:
        

        #remove downscan time from data
        cut_data = data[:self._upscantime*10]
        self._logger.info(f"Removed data length from {len(data)} to {len(data)}")

        time = np.linspace(0,self._upscantime, len(cut_data))
        self._logger.info(f"Created time vector with max time = {max(time)} and len = {len(time)}")
        

        t_f = self._time_across_DMA
        t_d = self._time_classifier_cpc_connector
        self._logger.info(f"t_f = {t_f} s| t_d = {t_d} s")
        voltage = minvoltage * (maxvoltage/minvoltage) ** (
            (time -t_f - t_d ) / (self._upscantime - t_f - t_d)
            )
        
        

        diameter = self._voltage_to_diameter(voltage)
        data = []
        for (d,c) in zip(diameter, cut_data):
          data.append([float(d),c])
        return data
        
        



    def _initialize_SMPS_paramters(self):
        

        def cylinder_volume(r1,r2,l):
            return np.pi * l * (r2 ** 2 - r1 ** 2)
        
        self._logger.info(f"Setting DMA values for  ...")
        self._time_classifier_cpc_connector = cylinder_volume(0, 0.0025, 0.5) / self._aerosol_flow_rate

        match self._DMA_TYPE:
            
            case "3081":
                self._logger.info(f"Setting DMA values for 3081...")
                
                self._r1 = 0.937  / 100 # in meter
                self._r2 = 1.961 / 100 # in meter 
                self._L = 44.369 / 100 # in meter
                
                
                self._time_across_DMA = cylinder_volume(self._r1, self._r2, self._L) / self._sheath_flow_rate


                return


            case "3085":
                self._logger.info(f"Setting DMA values for 3085...")
                
                self._r1 = 0.937  / 100 # in meter
                self._r2 = 1.905 / 100 # in meter 
                self._L = 4.987 / 100 # in meter    
                
                self._time_across_DMA = cylinder_volume(self._r1, self._r2, self._L) / self._sheath_flow_rate

                return

            case _:
                
                self._logger.error(f"DMA Type not listed. Using Values for Type 3081")
                self._r1 = 0.937  / 100 # in meter
                self._r2 = 1.961 / 100 # in meter 
                self._L = 44.369 / 100 # in meter
                self._time_across_DMA = cylinder_volume(self._r1, self._r2, self._L) / self._sheath_flow_rate

                return


    def _voltage_to_diameter(self, voltage):
        
        ## set interpolation diameter range and calculate voltage for interpolation
        
        x_interp = np.logspace(-9, -6, 1000)
        cunningham = aerosol.cunningham_correction(x_interp)

        nom = 3 * 1.72e-6 * self._sheath_flow_rate * np.log( self._r2 / self._r1 )
        denom = 2 * 1.609e-19 * self._L
        fac = nom / denom
        
        V_interp = x_interp * fac / cunningham
        
        diameter = CubicSpline(V_interp, x_interp, extrapolate=True)(voltage)

        return diameter




#if __name__ == "__main__":
    

    # import matplotlib.pyplot as plt
    
    # smpsProc = SMPSProcessor("3085",120, 1.5/60000, 15/6000)
    # data = []
    # with open("test/test_smps_scan.txt") as f:
    #     lines = f.readlines()
    #     for l in lines:
    #         data.append(float(l.strip().replace('"', "" ).replace("\\r", "")))


    # data_arr = np.array(data)
    # x = np.linspace(0,len(data), len(data))
    
    # mu = 1e3
    # sigma = 0.01 * mu
    # data_arr = data + 10000 / ( sigma * ( 2 * np.pi) ** 0.5 ) * np.exp( -0.5 * (x - mu) ** 2 / (sigma)**2 )
    
    
    # data = asyncio.run(smpsProc.convert_to_size_distribution(data, 10,10000))
    
    
    # print(data)
    
    # plt.show()
    


