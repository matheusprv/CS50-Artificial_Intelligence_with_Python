import random 
from minesweeper import Minesweeper, MinesweeperAI
random.seed(10)

def print_knowledge(ai):
    for sentence in ai.knowledge:
        print(str(sentence))
        print("\t", sentence.known_mines())

campoMinado = Minesweeper()
ai = MinesweeperAI()

campoMinado.print()


print("="*30)
celula = (5, 4)
count = campoMinado.nearby_mines(celula)
print(count)
ai.add_knowledge(celula, count)
print_knowledge(ai)

print("="*30)
celula = (6, 3)
count = campoMinado.nearby_mines(celula)
print(count)
ai.add_knowledge(celula, count)
print_knowledge(ai)

print("="*30)
celula = (6, 6)
count = campoMinado.nearby_mines(celula)
print(count)
ai.add_knowledge(celula, count)
print_knowledge(ai)

print("mines: " + str(ai.mines))
print("safes: " + str(ai.safes))