import pickle
import numpy as np
import os

PICKLE_IN = 'similarity.pkl'
OUT = 'similarity_topk.npz'
K = 50

print('Loading similarity matrix...')
sim = pickle.load(open(PICKLE_IN, 'rb'))
print('Computing top', K, 'indices for each item...')

# If sim is sparse-like (has toarray), ensure numpy array
if hasattr(sim, 'toarray'):
    sim = sim.toarray()

n = sim.shape[0]
indices = np.zeros((n, K), dtype=np.int32)
values = np.zeros((n, K), dtype=np.float32)

for i in range(n):
    row = sim[i]
    # argsort descending
    topk = np.argsort(row)[::-1]
    # take top K (may include self at position 0)
    topk = topk[:K]
    indices[i, :len(topk)] = topk
    values[i, :len(topk)] = row[topk]

print('Saving compressed topk file to', OUT)
np.savez_compressed(OUT, indices=indices, values=values)
print('Done')
