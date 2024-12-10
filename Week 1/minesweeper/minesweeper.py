import itertools
import random
from copy import deepcopy

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
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return set ()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set ()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
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
        self.mines = set()
        self.safes = set()

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


    def get_neighbors(self, cell):
        """
            Given a cell, return a set of neighbors
        """
        neighbors = set()
        cell_i, cell_j = cell
        start_i = max(0, cell_i - 1)
        end_i = min(self.height, cell_i + 2)
        start_j = max(0, cell_j - 1)
        end_j = min(self.width, cell_j + 2)

        for i in range(start_i, end_i):
            for j in range(start_j, end_j):
                if not(i == cell_i and j == cell_j) and (i, j) not in self.safes and (i, j) not in self.mines:
                    neighbors.add((i,j))
        return neighbors
    
    def aditional_safe_or_mines(self):
        knowlege_changed = True
        while knowlege_changed:
            knowlege_changed = False
            safes = set()
            mines = set()

            for sentence in self.knowledge:
                safes.update(sentence.known_safes())
                mines.update(sentence.known_mines())

            for safe in safes - self.safes:
                self.mark_safe(safe)
                knowlege_changed = True

            for mine in mines - self.mines:
                self.mark_mine(mine)
                knowlege_changed = True

            self.knowledge = [s for s in self.knowledge if s.cells]
        
    def new_rules_from_inference(self):
        knowledge_changed = False
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)

                    if new_sentence not in self.knowledge:
                        print("Novo conhecimento inferido")
                        self.knowledge.append(new_sentence)
                        knowledge_changed = True
        return knowledge_changed
                        

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
        # 1 
        self.moves_made.add(cell)

        # 2 
        self.mark_safe(cell)

        # 3
        # Gerando mais uma base de conhecimento de acordo tendo
        # as celulas vizinhas e quantas possiveis bombas tem ali
        neighbors = self.get_neighbors(cell)
        sentence = Sentence(neighbors, count)
        self.knowledge.append(sentence)
        
        knowledge_changed = True
        while knowledge_changed:
            # 4
            # Agora tendo mais uma base de conhecimento, verificamos se 
            # da para verificar se uma outra celula é segura sem nem ter
            # clicado nela. O mesmo vale para uma mina 
            self.aditional_safe_or_mines()

            # 5
            # Fazendo novas inferencias
            # Se set1 eh um subconjunto de s2, uma nova sentenca pode ser feita
            knowledge_changed = self.new_rules_from_inference()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes - self.moves_made
        print(safe_moves)
        if len(safe_moves) > 0:
            return list(safe_moves)[0]
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = {(x, y) for x in range(self.height) for y in range(self.width)}
        valid_moves = possible_moves - self.moves_made - self.mines

        if len(valid_moves) > 0:
            return random.choice(list(valid_moves))
