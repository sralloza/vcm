import csv

import matplotlib.pyplot as plt

ns = []
tfs = []

with open('performance.csv', 'rt', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    for line in reader:
        ns.append(int(line['n']))
        tfs.append(float(line['tf']))

min_tfs = min(tfs)
min_tfs = [min_tfs for x in ns]

plt.plot(ns, tfs)
plt.plot(ns, min_tfs, '--', c='g')
plt.scatter(ns, tfs, c='red', marker='x')
# plt.xticks(range(min(ns), max(ns) + 1, 5))
plt.xlabel('number of threads')
plt.ylabel('execution time in seconds')

plt.grid(True)
plt.show()
