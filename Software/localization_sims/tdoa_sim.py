import numpy as np
import matplotlib.pyplot as plt
import sys

# All units are SI standard (meters and seconds)

class TDOASim:

    def __init__(self, hydrophones, v_sound=1533, dt=528e-9, error_std=0):
        
        self.hydrophones = hydrophones
        self.v_sound = v_sound
        self.dt = dt
        self.error_std = error_std

    def calc_toa(self, hydrophone, pinger):
        distance = np.linalg.norm(hydrophone - pinger)
        return distance / self.v_sound

    
    def calc_tdoas(self, pinger_loc):
        toas = [self.calc_toa(hydrophone, pinger_loc) for hydrophone in self.hydrophones]
        noise = np.random.normal(scale=self.error_std, size=len(self.hydrophones))
        toas_noise = toas + noise
        toas = np.array(toas_noise)
        
        if self.dt == 0:
            relative_toas = toas - np.min(toas)
        else:
            base = self.dt
            prec = 12
            rounded_toas = (base * (toas / base).round()).round(prec)
            relative_toas = rounded_toas - np.min(rounded_toas)
        
        return relative_toas

    def actual_bearing(self, pinger_loc):
        theta = np.arctan2(pinger_loc[1], pinger_loc[0])
        phi = np.arctan2(np.sqrt(pinger_loc[1] ** 2 + pinger_loc[0] ** 2), pinger_loc[2])
        return (np.rad2deg(theta), np.rad2deg(phi))
