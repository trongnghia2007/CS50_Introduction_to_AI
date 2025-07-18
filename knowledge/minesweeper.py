import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count  # Số lượng mìn

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return set(self.cells)
        return set()  # set các ô được biết là mìn

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set()  # set các ô an toàn

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Kiểm tra ô đó có thuộc sentence không ?
        # Nếu có: xóa ô đó, nhưng vẫn thể hiện được ô đó là mìn
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Kiểm tra ô đó có thuộc sentence không ?
        # Nếu có: xóa ô đó, nhưng vẫn thể hiện được ô đó an toàn
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()  # cells: mines
        self.safes = set()  # cells: safes

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)  # ô được chọn
        self.safes.add(cell)  # ô an toàn

        new_cell_sentence = []
        i, j = cell

        for x in range(max(0, i - 1), min(self.height, i + 2)):
            for y in range(max(0, j - 1), min(self.width, j + 2)):
                adj = (x, y)
                if adj != cell and adj not in self.safes and adj not in self.mines:
                    # các ô kề an toàn được chọn và lan ra
                    new_cell_sentence.append(adj)

        # add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        new_sentence = Sentence(new_cell_sentence, count)
        self.knowledge.append(new_sentence)

        # mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            known_safes = sentence.known_safes()

            self.mines.update(known_mines)
            self.safes.update(known_safes)

        # add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        for mine in known_mines:
            for sen in self.knowledge:
                sen.mark_mine(mine)

        for safe in known_safes:
            for sen in self.knowledge:
                sen.mark_safe(safe)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # với ô trong các ô an toàn
        for move in self.safes:
            if move not in self.moves_made:
                # ô đó chưa được chọn thì chọn
                return move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Duyệt qua các ô trong bảng
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    # ô được lựa chọn không phải mìn thì chọn
                    return move

        return None


"""
def add_knowledge(self, cell, count):

        self.moves_made.add(cell)
        self.safes.add(cell)

        new_sentence_cells = []
        i, j = cell

        for x in range(max(0, i - 1), min(self.height, i + 2)):
            for y in range(max(0, j - 1), min(self.width, j + 2)):
                neighbor = (x, y)
                if neighbor != cell and neighbor not in self.safes and neighbor not in self.mines:
                    new_sentence_cells.append(neighbor)

        new_sentence = Sentence(new_sentence_cells, count)
        self.knowledge.append(new_sentence)

        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            known_safes = sentence.known_safes()

            self.mines.update(known_mines)
            self.safes.update(known_safes)

            for mine in known_mines:
                for s in self.knowledge:
                    s.mark_mine(mine)
            for safe in known_safes:
                for s in self.knowledge:
                    s.mark_safe(safe)

        # raise NotImplementedError

    def make_safe_move(self):

        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

        # raise NotImplementedError

    def make_random_move(self):

        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    return move
        return None

"""
