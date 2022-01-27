import numpy as np
from Simulation import Ping
from Simulation import Pinger
import matplotlib.pyplot as plt

p = Ping(4e-3, 25000, 1, 1.24e-6)
p.generate_ping()

t = p.time
signal = p.ping_values

print(t)
print(signal)

plt.plot(t, signal)
plt.show()
