import random
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def CreateGrid(x, y):
  grid = np.zeros((x, y))
  X_start, Y_start = SetStartPosition(grid, x, y)
  X_target, Y_target = SetTargetPosition(grid, x, y)

  ComputeFastestPath(grid, X_start, Y_start, X_target, Y_target)
  DrawLineBetweenPoints(grid, X_start, Y_start, X_target, Y_target)

  plt.figure(figsize=(6, 6))
  ax = sns.heatmap(
      grid,
      cmap="plasma",
      cbar=False,
      linewidths=1,
      linecolor="gray",
      xticklabels=True,
      yticklabels=True,
  )
  ax.invert_yaxis()
  plt.show()


def SetStartPosition(grid, x, y):
  X_start = random.randint(0, x - 1)
  Y_start = random.randint(0, y - 1)
  grid[X_start, Y_start] = 1
  print(f"Starting position is {X_start}, {Y_start}")
  return X_start, Y_start


def SetTargetPosition(grid, x, y):
  X_target = random.randint(0, x - 1)
  Y_target = random.randint(0, y - 1)
  grid[X_target, Y_target] = 5
  print(f"Target position is {X_target}, {Y_target}")
  return X_target, Y_target


def ComputeFastestPath(grid, X_start, Y_start, X_target, Y_target):
  dy = Y_target - Y_start
  dx = X_target - X_start
  manhattan_distance = abs(dx) + abs(dy)
  print(f"Delta X: {dx}, Delta Y: {dy}, Manhattan Distance: {manhattan_distance}")


def DrawLineBetweenPoints(grid, X_start, Y_start, X_target, Y_target):
  # Draw a simple line or path between start (1) and target (5)
  if X_target != X_start:
    m = (Y_target - Y_start) / (X_target - X_start)
    c = Y_start - m * X_start
    for x in range(min(X_start, X_target), max(X_start, X_target) + 1):
      y = int(round(m * x + c))
      if 0 <= y < grid.shape[1] and grid[x, y] == 0:
        grid[x, y] = 2  # Mark path
  else:
    for y in range(min(Y_start, Y_target), max(Y_start, Y_target) + 1):
      if grid[X_start, y] == 0:
        grid[X_start, y] = 2

  # Re-apply start and target markers
  grid[X_start, Y_start] = 1
  grid[X_target, Y_target] = 5


# Run the grid generation
CreateGrid(20, 20)
