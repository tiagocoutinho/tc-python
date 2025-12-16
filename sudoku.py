def solve(grid):
    if (coords := find_empty(grid)) is None:
        return True
    row, col = coords
    for value in range(1, 10):
        if is_valid(grid, row, col, value):
            grid[row][col] = value
            if solve(grid):
                return True
            grid[row][col] = 0
    return False


def is_valid(grid, row, col, value):
    for x in range(9):
        if grid[row][x] == value:
            return False
    for y in range(9):
        if grid[y][col] == value:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == value:
                return False
    return True

def find_empty(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j


def print_grid(grid):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print('- - - - - - - - - - -')
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("| ", end="")
            print(f"{grid[i][j]} ", end="")
        print()

def main():
    grid = [
		[0, 3, 0, 0, 7, 0, 0, 0, 0],
		[0, 0, 0, 1, 3, 5, 0, 0, 0],
		[0, 0, 1, 0, 0, 0, 0, 5, 0],
		[1, 0, 0, 0, 6, 0, 0, 0, 3],
		[4, 0, 0, 8, 0, 3, 0, 0, 1],
		[7, 0, 0, 0, 2, 0, 0, 0, 6],
		[0, 0, 0, 0, 0, 0, 2, 1, 0],
		[0, 0, 0, 4, 1, 2, 0, 0, 5],
		[0, 0, 0, 0, 0, 0, 0, 7, 4],
	]
    print("Puzzle:")
    print_grid(grid)
    if solve(grid):
        print("Solved:")
        print_grid(grid)
    else:
        print("No solution exists")
        exit(1)

if __name__ == "__main__":
    main()
