import random
from .util import Colour


class MazeGenerator():
  def __init__(self, height=20, width=None, density=0.3):
    if not width:
      width = height

    self.height = height
    self.width = width
    self.len = height * width

    # Create the right number of walls to be shuffled for each new maze
    non_corner_size = height * width - 2
    population_count = int(non_corner_size * density)
    empty_squares = non_corner_size - population_count
    self.walls = ['1'] * population_count + ['0'] * empty_squares

    # Starting point is the bottom right corner
    self.bottom_right_corner = int('0' * (self.len - 1) + '1', base=2)

    # Edges for use in flood search
    self.not_left_edge, self.not_right_edge, \
      self.not_top_edge, self.not_bottom_edge = self._edges()

  def _edges(self):
    full_columns = '1' * (self.width - 1)
    not_left = int(('0' + full_columns) * self.height, base=2)
    not_right = int((full_columns + '0') * self.height, base=2)

    empty_row = '0' * self.width
    full_row = '1' * self.width
    full_rows = full_row * (self.height - 1)
    not_top = int(empty_row + full_rows, base=2)
    not_bottom = int(full_rows + empty_row, base=2)

    return not_left, not_right, not_top, not_bottom

  def maze_to_binary(self, maze):
    binary = bin(maze)[2:]
    return '0' * (self.len - len(binary)) + binary

  def print_maze(self, maze, labels):
    rows = []
    for i in range(self.height):
      row = maze[i]
      row = ''.join([str(row[i][0]) for i in range(self.width)])
      row = row.replace('0', '.').replace('1', '#')
      row = row[:i] + Colour.highlight(row[i], labels[i]) + row[i + 1:]
      rows.append(row)

    print('\n'.join(rows))

  def generate(self):
    random.shuffle(self.walls)
    return int('0' + ''.join(self.walls) + '0', base=2)

  def connected_squares(self, maze, start=None):
    """Find squares connected to the end square in the maze

    Uses a fast bitwise flood fill algorithm
    """

    empty_squares = ~maze
    current = None
    next = start or self.bottom_right_corner

    while current != next:
      current = next

      left = current << 1 & self.not_right_edge
      right = current >> 1 & self.not_left_edge
      up = current << self.width & self.not_bottom_edge
      down = current >> self.width & self.not_top_edge

      next = (current | left | right | up | down) & empty_squares

    return current

  def connected_diagonals(self, maze):
    assert self.height == self.width
    connected = self.maze_to_binary(self.connected_squares(maze))
    return [int(connected[(self.height + 1) * i]) for i in range(self.height)]

  def generate_labelled_mazes(self, batch_size):
    mazes = []
    labels = []
    for _ in range(batch_size):
      maze = self.generate()
      connected_diagonals = self.connected_diagonals(maze)
      mazes.append(self.maze_to_input(maze))
      labels.append(connected_diagonals)

    return mazes, labels

  def generate_mazes(self, batch_size):
    return [self.maze_to_input(self.generate()) for _ in range(batch_size)]

  def maze_to_input(self, maze):
    maze = self.maze_to_binary(maze)
    maze = [[[int(maze[i + j])] for j in range(self.width)]
            for i in range(0, self.height * self.width, self.width)]
    return maze
