"""
Show how affixes are computed.
"""

import matplotlib.pyplot as plt
import numpy as np

PREFIX = 2
SUFFIX = 1
SPLIT = 0.5

# "overlap", "split", or "final"
MODE = "final"


# Set axes bounds
plt.xlim(0, 10)
plt.ylim(0, 10)

plt.xlabel("Proximity")
plt.ylabel("Time")

x = np.linspace(0, 10, 100)
key1 = np.full_like(x, 3)
key2 = np.interp(x, [0, 10], [7, 3.5])

def plot_affixes(key):
    plt.fill_between(x, key-PREFIX, key, color="yellow", alpha=0.2)
    plt.fill_between(x, key, key+SUFFIX, color="blue", alpha=0.2)
    plt.plot(x, key-PREFIX, color="yellow", alpha=0.3)
    plt.plot(x, key+SUFFIX, color="blue", alpha=0.3)

if MODE in ("overlap", "split"):
    plot_affixes(key1)
    plot_affixes(key2)

x_start = np.argmax(key1+SUFFIX > key2-PREFIX)
x_overlap = x[x_start:]
k1_overlap = (key1+SUFFIX)[x_start:]
k2_overlap = (key2-PREFIX)[x_start:]

plt.plot(x, key1, color="black")
plt.plot(x, key2, color="black")

if MODE in ("split", "final"):
    split = k1_overlap*SPLIT + k2_overlap*(1-SPLIT)
    split = np.clip(split, key1[x_start:], key2[x_start:])
    plt.plot(x_overlap, split, color="green")

if MODE in ("overlap", "split"):
    # Draw overlap
    for color, alpha in (("white", 1), ("red", 0.5)):
        plt.fill_between(x_overlap, k1_overlap, k2_overlap, color=color, alpha=alpha)

if MODE == "final":
    plt.fill_between(x, key1-PREFIX, key1, color="yellow", alpha=0.2)
    plt.fill_between(x, key2, key2+SUFFIX, color="blue", alpha=0.2)

    full_split = key1 + SUFFIX
    full_split[-split.size:] = split
    plt.fill_between(x, key1, np.minimum(full_split, key1+SUFFIX), color="blue", alpha=0.2)
    plt.fill_between(x, np.maximum(full_split, key2-PREFIX), key2, color="yellow", alpha=0.2)

plt.show()
