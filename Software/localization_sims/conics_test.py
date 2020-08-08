import numpy as np
from conic_approx import ConicApproximation

bottom_left = [-0.0125, 0, -0.0125] # Channel 3
bottom_right = [0.0125, 0, -0.0125] # Channel 4
top_right = [0.0125, 0, 0.0125] # Channel 2
hydrophones = np.array([bottom_left, bottom_right, top_right])
c = ConicApproximation(hydrophones)