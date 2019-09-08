import numpy as np
f = np.arange(9*1280).reshape(1280,9).astype(np.float32)
np.save('test.npy', f)
print(np.load('test.npy'))

f2 = np.arange(9*1280).reshape(1280,9).astype(np.float32)
np.savez_compressed('test2.npz', array_1=f, array_2=f2)

loaded_array = np.load('test2.npz')
print(loaded_array['array_1'])
