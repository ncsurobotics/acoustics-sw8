from tdoa_sim import TDOASim
import numpy as np
class Multilateration(TDOASim):
    # Assumptions: Three hydrophones forming a right angle in the xz plane
    # Hydrophones 1 and 2 form the horizontal pair, and 2 and 3 form the vertical

    # https://en.wikipedia.org/wiki/Multilateration - cartesian solution
    def calculate_xyz(self, pinger_loc):
        relative_toas = self.calc_tdoas(pinger_loc) + .01 # Add 1 to eliminate div by 0 - this needs a much better implementation
        x1, y1, z1 = self.hydrophones[0]
        t1 = relative_toas[0]
        c = self.v_sound
        lhs = []
        rhs = []
        for i in range(1, 4):
            xm, ym, zm = self.hydrophones[i]
            tm = relative_toas[i]

            A = (2 * xm) / (c * tm) - (2 * x1) / (c * t1)
            B = (2 * ym) / (c * tm) - (2 * y1) / (c * t1)
            C = (2 * zm) / (c * tm) - (2 * z1) / (c * t1)
            D = c*tm - c*t1 - (xm ** 2 + ym ** 2 +zm ** 2)/(c * tm) + (x1 ** 2 + y1 ** 2 + z1 ** 2)/(c * t1)
            
            lhs.append([A, B, C])
            rhs.append(-D)

        lhs = np.array(lhs)
        rhs = np.array(rhs)

        return np.linalg.solve(lhs, rhs)

    def calculate_bearing(self, pinger_loc):
        x, y, z = self.calculate_xyz(pinger_loc)
        return (np.rad2deg(np.arctan2(y, x)), np.rad2deg(np.arctan2(np.sqrt(x ** 2 + y ** 2), z)))


