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
        # remove uma palavra do dominio de uma variavel quando a quantidade de letras for diferente do tamanho
        for v in self.crossword.variables:
            for x in self.domains[v].copy():
                if len(x) != v.length:
                    self.domains[v].remove(x)
        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlaps = self.crossword.overlaps[x, y]

        if overlaps is None: 
            # Se nao ha sobreposicao, entao nao ha conflitos, logo nao ha modificacoes
            return False

        i, j = overlaps

        revised = False
        for word_x in self.domains[x].copy():
            # Se para toda word_x nao ha uma word_y que nao da conflito, entao pode remover word_x
            if all(word_x[i] != word_y[j] for word_y in self.domains[y]):
                self.domains[x].remove(word_x)
                revised = True
        return revised

    def make_queue(self, arcs):
        queue = Queue()  # Importado na linha 5
        
        if arcs is not None:
            for arc in arcs:
                queue.put(arc)
            return queue
        
        for var in self.domains.keys():
            for neighbor in self.crossword.neighbors(var):
                queue.put((var, neighbor))
        
        return queue

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = self.make_queue(arcs)
        
        while not queue.empty():
            (x, y) = queue.get()
            if self.revise(x, y):
                # Se o dominio esta vazio, nao ha como satisfazer a restrição
                if len(self.domains[x]) == 0:
                    return False
                
                for z in self.crossword.neighbors(x) - set([y]):
                    queue.put((z, x))

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # assignment eh um dicinario que a chave eh uma variavel e o valor eh uma palavra qualquer
        # como eh chamada pela funcao backtracking, pode ser que ainda faltem variaveis
        # se uma variavel esta aqui, um valor foi atribuido para ela. entao deve-se verificar se todas
        #   as variaveis possuem um valor qualquer no assignmet
        return all(x in assignment.keys() for x in self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # all values are distinct
        if len(set(assignment.values())) != len(assignment):
            return False

        # every value is the correct length
        for var in assignment.keys():
            if len(assignment[var]) != var.length:
                return False

        # there are no conflicts between neighboring variables
        for var in assignment.keys():
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
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
        # Retorna a variavel que vai causar menos eliminações de outros dominios

        least_constraining = {}

        # O que ja foi atribuido nao pode ser modificado
        neighbors = set(self.crossword.neighbors(var)) - set(assignment)

        for word in self.domains[var]:
            eliminations = 0
            for neighbour in neighbors:
                overlap = self.crossword.overlaps[var, neighbour]
                if overlap is None:
                    continue

                i, j = overlap
                for neighbour_word in self.domains[neighbour]:
                    if word[i] != neighbour_word[j]:
                        eliminations += 1
            least_constraining[word] = eliminations

        # Ordena de forma ascendente, o least constraining vem primeiro
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
        
        # minimum remaining value in domain
        # Ordena pela menor quantidade de itens no dominio
        mnrm = sorted(unassigned, key=lambda x: len(self.domains[x]))
        # Pega todas as variaveis que tem a mesma quantidade de itens que a que tem menos
        mnrm = [x for x in mnrm if len(self.domains[x]) == len(self.domains[mnrm[0]])]

        if len(mnrm) == 1: 
            return mnrm[0]
        
        # Se ocorreu um empate, entao tem que olhar pela variavel com maior grau (mais vizinhos)
        return_variable = mnrm[0]
        highest_degree = self.crossword.neighbors(mnrm[0]) 

        for other in mnrm[1:]:
            degree = self.crossword.neighbors(mnrm[0]) 
            if degree > highest_degree:
                return_variable = other
                highest_degree = other

        return return_variable

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
