lx = 5.2  # in meters
# lx = 4.6 # in meters
ly = 5.2  # in meters
t = 300  # simulation time in seconds
dx = 0.05
dy = 0.05
nx = int(lx / dx)
ny = int(ly / dy)

# constants for the pml
w = 10
r0 = 1e-8
m = 3

#def speedtest1():
#    a = np.ones((100, 100))
#    b = np.zeros((100, 100))
#    b[:,10] = 1
#    b[23,34] = 5
#    for t in range(1000):
#        a += a + b

#def speedtest2():
#    a = np.ones((100, 100))
#    b = np.zeros((100, 10))
#    b[:,:] = 1
#    for t in range(1000):
#        a += a
#        a[:,:10] = a[:,:10] + b

#num = 1000
#time1 = timeit.timeit(speedtest1, number = num)
#time2 = timeit.timeit(speedtest2, number = num)
#print("same size:" ,time1)
#print("sparse:   ", time2)


