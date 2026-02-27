# ml/astar/pathfinder.py
"""
A* (A-Star) Pathfinding Algorithm
Used to reroute MEP (pipes/wires) around shifted structural elements.
"""

import heapq
import time
from typing import List, Tuple, Optional


class Node:
    """A single cell in the grid"""
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.g = float('inf')   # Cost from start
        self.h = 0              # Heuristic (estimated cost to end)
        self.f = float('inf')   # g + h
        self.parent: Optional['Node'] = None

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.col == other.col and self.row == other.row

    def __hash__(self):
        return hash((self.col, self.row))

    def to_dict(self):
        return {"col": self.col, "row": self.row}


class AStarPathfinder:
    """
    Grid-based A* pathfinder for MEP rerouting.

    Grid = 2D map of the construction floor plan.
    Obstacles = positions of shifted structural elements.
    Finds shortest collision-free path from Point A to Point B.
    """

    def __init__(self, cols: int = 20, rows: int = 10):
        self.cols = cols
        self.rows = rows
        self.grid: List[List[int]] = [[0] * cols for _ in range(rows)]
        # 0 = free, 1 = obstacle

    def set_obstacle(self, col: int, row: int):
        """Mark a grid cell as blocked (shifted pillar/beam)"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1

    def set_obstacles_from_list(self, obstacles: List[dict]):
        """Mark multiple obstacle nodes"""
        for obs in obstacles:
            self.set_obstacle(obs["col"], obs["row"])

    def _heuristic(self, a: Node, b: Node) -> float:
        """Manhattan distance heuristic — optimal for grid movement"""
        return abs(a.col - b.col) + abs(a.row - b.row)

    def _get_neighbors(self, node: Node) -> List[Node]:
        """
        Get valid adjacent cells.
        4-directional movement (up/down/left/right).
        For pipe routing, diagonal is not allowed.
        """
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neighbors = []
        for dc, dr in directions:
            nc, nr = node.col + dc, node.row + dr
            if 0 <= nc < self.cols and 0 <= nr < self.rows:
                if self.grid[nr][nc] == 0:  # not an obstacle
                    neighbors.append(Node(nc, nr))
        return neighbors

    def find_path(
        self,
        start_col: int, start_row: int,
        end_col: int, end_row: int
    ) -> dict:
        """
        Run A* algorithm.
        Returns: path (list of nodes), nodes_explored, compute_ms
        """
        start_time = time.time()
        start = Node(start_col, start_row)
        end = Node(end_col, end_row)

        start.g = 0
        start.h = self._heuristic(start, end)
        start.f = start.g + start.h

        open_set: list = []
        heapq.heappush(open_set, start)

        closed_set = set()
        node_map = {(start.col, start.row): start}
        nodes_explored = 0

        while open_set:
            current = heapq.heappop(open_set)
            nodes_explored += 1

            if current == end:
                # Reconstruct path
                path = []
                node = current
                while node is not None:
                    path.append(node.to_dict())
                    node = node.parent
                path.reverse()

                compute_ms = round((time.time() - start_time) * 1000, 2)
                return {
                    "success": True,
                    "path": path,
                    "nodes_explored": nodes_explored,
                    "path_length": len(path),
                    "compute_ms": compute_ms,
                    "message": f"Optimal path found: {len(path)} steps, {nodes_explored} nodes explored in {compute_ms}ms"
                }

            closed_set.add((current.col, current.row))

            for neighbor in self._get_neighbors(current):
                if (neighbor.col, neighbor.row) in closed_set:
                    continue

                tentative_g = current.g + 1
                key = (neighbor.col, neighbor.row)

                if key not in node_map:
                    node_map[key] = neighbor
                elif tentative_g >= node_map[key].g:
                    continue

                node = node_map[key]
                node.g = tentative_g
                node.h = self._heuristic(node, end)
                node.f = node.g + node.h
                node.parent = current
                heapq.heappush(open_set, node)

        compute_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": False,
            "path": [],
            "nodes_explored": nodes_explored,
            "path_length": 0,
            "compute_ms": compute_ms,
            "message": "No path found — check obstacles or grid boundaries."
        }

    def get_obstacle_nodes_from_mismatch(
        self, detected_x: int, detected_y: int,
        img_width: int = 640, img_height: int = 640
    ) -> List[dict]:
        """
        Convert pixel coordinates of a shifted element
        to grid obstacle nodes.
        """
        cell_w = img_width / self.cols
        cell_h = img_height / self.rows

        col = int(detected_x / cell_w)
        row = int(detected_y / cell_h)

        # Mark a 3x5 block as obstacle (pillar footprint)
        obstacles = []
        for dc in range(-1, 3):
            for dr in range(-2, 6):
                obstacles.append({"col": col + dc, "row": row + dr})
        return obstacles


# Convenience function for direct use
def compute_reroute(
    obstacle_nodes: List[dict],
    start: dict = None,
    end: dict = None,
    cols: int = 20,
    rows: int = 10
) -> dict:
    """
    Main entry: given obstacle positions, compute new MEP route.
    Default: pipe goes from left-center to right-center of floor plan.
    """
    pf = AStarPathfinder(cols, rows)
    pf.set_obstacles_from_list(obstacle_nodes)

    s = start or {"col": 0, "row": rows // 2}
    e = end   or {"col": cols - 1, "row": rows // 2}

    return pf.find_path(s["col"], s["row"], e["col"], e["row"])
