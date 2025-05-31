import json
import numpy as np
import pandas as pd
from sklearn.manifold import MDS

# Load the data
with open('data/hub.json', 'r') as f:
    data = json.load(f)

# Get all unique node names
nodes = sorted(data.keys())
for v in data.values():
    for n in v:
        if n['neighbor'] not in nodes:
            nodes.append(n['neighbor'])
nodes = sorted(set(nodes))

# Build index mapping
node_idx = {node: i for i, node in enumerate(nodes)}
N = len(nodes)

# Initialize distance matrix with a large value
dist_matrix = np.full((N, N), np.inf)
np.fill_diagonal(dist_matrix, 0)

# Fill in known distances (make symmetric)
for node, neighbors in data.items():
    i = node_idx[node]
    for entry in neighbors:
        j = node_idx[entry['neighbor']]
        dist = entry['distance']
        dist_matrix[i, j] = dist
        dist_matrix[j, i] = dist  # ensure symmetry

# Replace inf with max finite distance * 2 (for disconnected pairs)
finite = dist_matrix[np.isfinite(dist_matrix)]
max_dist = finite.max() if finite.size > 0 else 1
dist_matrix[~np.isfinite(dist_matrix)] = max_dist * 2

# Run MDS
mds = MDS(n_components=3, dissimilarity='precomputed', random_state=42)
coords = mds.fit_transform(dist_matrix)

# Output as CSV
df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
df.insert(0, 'node', nodes)
df.to_csv('hub_mds_coords.csv', index=False)
print("Output written to hub_mds_coords.csv")