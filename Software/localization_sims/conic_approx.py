from tdoa_sim import TDOASim
import numpy as np
class ConicApproximation(TDOASim):
    # Assumptions: Three hydrophones forming a right angle in the xz plane
    # Hydrophones 1 and 2 form the horizontal pair, and 2 and 3 form the vertical

    # Note - does not differentiate between directions
    # Can be improved by adding a fourth hydrophone and averaging
    def calculate_bearing(self, pinger_loc):
        relative_toas = self.calc_tdoas(pinger_loc)
        dx = np.linalg.norm(self.hydrophones[1] - self.hydrophones[0])
        dz = np.linalg.norm(self.hydrophones[2] - self.hydrophones[1])
        d1 = self.v_sound * (relative_toas[1] - relative_toas[0])
        d2 = self.v_sound * (relative_toas[2] - relative_toas[1])
        c1 = d1 ** 2 / (dx ** 2 - d1 ** 2)
        c2 = d2 ** 2 / (dz ** 2 - d2 ** 2)

        theta = np.arctan(np.sqrt((c1 + c1 * c2) / (1 - c1 * c2)))
        phi = np.arctan(np.sqrt((c1 + 1) / (c2 + c1 * c2)))

        return (90 - np.rad2deg(theta), np.rad2deg(phi))


