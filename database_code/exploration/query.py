import os
import sys
import numpy as np
import datetime

data = np.load(sys.argv[1])
# Earliest record (by day)
a = (data[:, 2]*30 + data[:, 3]).argmin()
r = data[a]
first_day = datetime.date(r[1], r[2], r[3])


