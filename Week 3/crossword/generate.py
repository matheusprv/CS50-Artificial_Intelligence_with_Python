import sys

from crossword import *

from queue import Queue


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Percorre todas as variaveis e remove as palavras cujo tamanho seja diferente do tamanho da variavel
        for variable in self.domains.keys():
            var_length = variable.length
            words = [x for x in self.domains[variable] if len(x) == var_length]
            self.domains[variable] = set(words)
        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap = self.crossword.overlaps[x, y]

        # If no overlap occurs, then no revision must be done
        if overlap is None:
            return False
    
        revised = False
        i, j = overlap
        for word_x in set(self.domains[x]):
            if not any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                self.domains[x].remove(word_x)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = Queue()

        if arcs is not None:
            for arc in arcs: 
                queue.put(arc)
        else:
            for var in self.domains:
                for neighbor in self.crossword.neighbors(var):
                    if self.crossword.overlaps[(var, neighbor)] is not None:
                        queue.put((var, neighbor))

        while not queue.empty():
            X, Y = queue.get()
            if self.revise(X, Y):
                if len(self.domains[X]) == 0: 
                    return False
                
                for Z in self.crossword.neighbors(X) - set([Y]):
                    queue.put((Z, X))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Assignment is a dictionary where the keys are Variable objects and the values are strings representing the words those variables will take on.
        # An assignment is complete if every crossword variable is assigned to a value
        return all(variable in assignment for variable in self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # all values are distinct, every value is the correct length, and there are no conflicts between neighboring variables
        # A conflict in the context of the crossword puzzle is a square for which two variables disagree on what character value it should take on
        
        # All values are distinct
        if len(set(assignment.values())) != len(assignment):
            return False

        # every value is the correct length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # there are no conflicts between neighboring variables
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap is not None:
                        i, j = overlap
                        if assignment[var][i] != assignment[neighbor][j]:
                            return False
                
        return True       

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        least_constraining = {}

        neighbors = set(self.crossword.neighbors(var)) - set(assignment)

        # For each word in the var domain, check how many values it rules out among the neighbors.
        for word in self.domains[var]:
            eliminations = 0
            for neighbour in neighbors:
                overlap = self.crossword.overlaps[var, neighbour]
                if overlap is None:
                    continue

                x_over, y_over = overlap
                for neighbour_word in self.domains[neighbour]:  # Use neighbour (singular) here.
                    if word[x_over] != neighbour_word[y_over]:
                        eliminations += 1
            least_constraining[word] = eliminations

        # Sort values by their number of eliminations (least constraining first)
        return sorted(self.domains[var], key=lambda k: least_constraining[k])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        
        mnrm = sorted(unassigned, key=lambda x: len(self.domains[x]))
        mnrm = [x for x in mnrm if len(self.domains[x]) == len(self.domains[mnrm[0]])]

        if len(mnrm) == 1: 
            return mnrm[0]

        # A tie happenned. Then it must look for the variable with the highest degree
        result_value = mnrm[0]
        highest_degree = self.crossword.neighbors(mnrm[0]) 

        for other in mnrm[1:]:
            degree = self.crossword.neighbors(mnrm[0]) 
            if degree > highest_degree:
                result_value = other
                highest_degree = other

        return result_value

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment_copy = assignment.copy()
            assignment_copy[var] = value
            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)
                if result is not None:
                    return result
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
