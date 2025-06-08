# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name
import json
import numpy as np
from scipy.optimize import minimize

def map_distances_to_3d(distances):

    def objective_function(coords):
        coords = coords.reshape((4, 3))
        dists = np.linalg.norm(coords[:, np.newaxis] - coords[np.newaxis, :], axis=-1)
        return np.sum((dists - distances) ** 2)

    initial_guess =  np.array([
        [0.59266219, 0.4879774,  0.29526902],
        [0.74651822, 0.14567955, 0.70959896],
        [0.79550913, 0.85019913, 0.67938143],
        [0.10097802, 0.16379639, 0.94126657]
    ])
    result = minimize(objective_function, initial_guess.flatten(), method='L-BFGS-B')

    if result.success:
        return result.x.reshape((4, 3))
    raise ValueError("Optimization failed to find a solution.")

def distance_between_points(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

assert distance_between_points([0, 0, 0], [1, 1, 1]) == np.sqrt(3)

def map_point_to_3d(distance_to_control_points, control_points):
    # This function maps a point to 3D space based on its distances to control points.
    def objective_function(point):
        point = np.array(point)
        dists = np.array([distance_between_points(point, cp) for cp in control_points])
        return np.sum((dists - distance_to_control_points) ** 2)
    initial_guess = np.mean(control_points, axis=0)
    result = minimize(objective_function, initial_guess, method='L-BFGS-B')
    if result.success:
        return result.x
    raise ValueError("Optimization failed to find a solution.")

# Parse the control points from the file zamytaeus-anomaly.json
with open('data/zamytaeus-anomaly.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

control_point_names = {}
for system in data.keys():
    system_data = data[system]
    if "control_point" in system_data:
        control_point_names[system_data["control_point"]] = system

# Get distances between control points
distances_between_control_points = []
for cp in control_point_names.items():
    cp_name = cp[1]
    if "distances" in data[cp_name]:
        distances = [
            data[cp_name]["distances"].get(other_cp, 0)
            for other_cp in control_point_names.values()
        ]
        distances_between_control_points.append(distances)

control_points = map_distances_to_3d(distances_between_control_points)

print("node, x, y, z")
for system in data.keys():
    system_data = data[system]
    if "distances" in system_data:
        distances = [0,0,0,0]
        for cp in control_point_names.items():
            distances[cp[0]] = system_data["distances"].get(cp[1], 0)
        mapped_point = map_point_to_3d(distances, control_points)
        print(f"{system}, {mapped_point[0]:.2f}, {mapped_point[1]:.2f}, {mapped_point[2]:.2f}")
