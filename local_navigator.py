import heapq
import math

import numpy as np


def a_star(cost, start, goal, distance=None, heuristic=None):
    """A* on 8 neighbours, with no diagonal moves cutting through obstacle corners."""
    cost = np.asarray(cost, dtype=float)

    if cost.ndim != 2 or np.any(np.isfinite(cost) & (cost < 1)):
        raise ValueError("Cost must be a 2-D grid with finite values >= 1")

    height, width = cost.shape

    def valid(point):
        row, col = point
        return (
            0 <= row < height
            and 0 <= col < width
            and np.isfinite(cost[point])
        )

    if not valid(start) or not valid(goal):
        return None, math.inf

    distance = distance or (
        lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    )
    heuristic = heuristic or (
        lambda p: math.hypot(p[0] - goal[0], p[1] - goal[1])
    )

    best = {start: 0.0}
    parents = {}
    queue = [(heuristic(start), 0.0, start)]

    directions = (
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    )

    while queue:
        _, current_cost, current = heapq.heappop(queue)

        if current_cost != best.get(current):
            continue

        if current == goal:
            path = [current]

            while current in parents:
                current = parents[current]
                path.append(current)

            return path[::-1], current_cost

        row, col = current

        for dr, dc in directions:
            neighbour = (row + dr, col + dc)

            if not valid(neighbour):
                continue

            if dr and dc:
                if not valid((row + dr, col)):
                    continue
                if not valid((row, col + dc)):
                    continue

            edge_cost = (
                distance(current, neighbour)
                * (cost[current] + cost[neighbour])
                / 2
            )
            candidate = current_cost + edge_cost

            if candidate < best.get(neighbour, math.inf):
                best[neighbour] = candidate
                parents[neighbour] = current

                heapq.heappush(
                    queue,
                    (
                        candidate + heuristic(neighbour),
                        candidate,
                        neighbour,
                    ),
                )

    return None, math.inf