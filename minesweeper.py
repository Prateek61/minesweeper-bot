import itertools
import random

from typing import List, Set

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
        self.cells: set = set(cells)
        self.count: int = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        try:
            self.cells.remove(cell)
        except:
            pass


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height: int = height
        self.width: int = width

        # Keep track of which cells have been clicked on
        self.moves_made: set = set()

        # Keep track of cells known to be safe or mines
        self.mines: set = set()
        self.safes: set = set()

        # List of sentences about the game known to be true
        self.knowledge: List[Sentence] = list()

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

    def is_cell_valid(self, cell) -> bool:
        x, y = cell
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return False
        
        return True

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

        # Mark the cell as a move that has been made
        self.moves_made.add(cell)
        # Mark the cell as safe
        self.mark_safe(cell)

        # Add new sentence to knowledgebase
        x, y = cell
        cells = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if self.is_cell_valid((x + i, y + j)):
                    if (x + i, y + j) in self.mines:
                        count -= 1
                    elif (x + i, y + j) not in self.moves_made:
                        cells.add((x + i, y + j))
        
        self.knowledge.append(Sentence(cells, count))

        # Mark any additional cells as sage or as mines
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            for cell in known_mines:
                self.mark_mine(cell)
            known_safes = sentence.known_safes()
            for cell in known_safes:
                self.mark_safe(cell)

        # Removes unwanted sets
        length: int = len(self.knowledge)
        i: int = 0
        while i < length:
            if len(self.knowledge[i].cells) == 0:
                del self.knowledge[i]
                length -= 1
                continue

            j = i
            while j < length:
                if not i == j:
                    if self.knowledge[i].cells == self.knowledge[j].cells:
                        del self.knowledge[j]
                        length -= 1
                        continue
                
                j += 1
            i += 1

        # Add any new sentences to the AI's knowledge base
        new_knowledges: List[Sentence] = list()

        for i, s1 in enumerate(self.knowledge):
            s1_len = len(s1.cells)

            if s1_len == 0:
                continue
            for j, s2 in enumerate(self.knowledge[i:]):
                s2_len = len(s2.cells)
                if s2_len == 0:
                    continue
                if s1_len > s2_len and s2.cells.issubset(s1.cells):
                    new_knowledges.append(Sentence(s1.cells.difference(s2.cells), s1.count - s2.count))   
                elif s2_len > s1_len and s1.cells.issubset(s2.cells):
                    new_knowledges.append(Sentence(s2.cells.difference(s1.cells), s2.count - s1.count))
        
        self.knowledge.extend(new_knowledges)



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        for safe_move in self.safes:
            if safe_move not in self.moves_made:
                return safe_move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(0, self.height):
            for j in range(0, self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    return (i, j)
