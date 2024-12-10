from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Nao pode ser knight e knave ao mesmo tempo
    Or(
        And(AKnight, Not(AKnave)),
        And(Not(AKnight), AKnave)
    ),
    # Ou ele é knight e nave ao mesmo tempo
    # Ou ele é knave e nao é knight e knave
    Or(
        And(AKnight, AKnave), 
        And(AKnave, Not(And(AKnight, AKnave)))
    ),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Nao pode ser knight e knave ao mesmo tempo
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    Or(And(BKnight, Not(BKnave)), And(Not(BKnight), BKnave)),

    # Se o A é knave, entao e mentira que ambos sao knave
    Implication(AKnave, Not(And(AKnave, BKnave))),
    Implication(AKnight, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
mesmo_tipo = Or(And(AKnight, BKnight), And(AKnave, BKnave))
diferentes_tipos = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    Or(And(BKnight, Not(BKnave)), And(Not(BKnight), BKnave)),

    # O que A disse
    # Se for verdade, entao eles sao do mesmo tipo
    # Se for mentira, eles sao de tipos diferentes
    Implication(AKnight, mesmo_tipo),
    Implication(AKnave, diferentes_tipos),

    # O que B disse
    # Se for verdade, implica que sao de tipos diferentes
    # Se for mentira, sao do mesmo tipo
    Implication(BKnight, diferentes_tipos),
    Implication(BKnave, mesmo_tipo)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(And(AKnight, Not(AKnave)), And(Not(AKnight), AKnave)),
    Or(And(BKnight, Not(BKnave)), And(Not(BKnight), BKnave)),
    Or(And(CKnight, Not(CKnave)), And(Not(CKnight), CKnave)),

    # Se o A falou que e knight, ou ele é knight e disse a verdade ou é kanve e ta mentindo
    # Se o A falou que e kanve, ele nao pode ser knight, pois knight nao mente
    # e ele nao pode ser kanve pois o kanve falaria que ele e um knight
    Implication(Or(AKnight, AKnave), AKnight),

    # B disse que o A falou que era kane e falou que o C era knave
    Implication(BKnight, And(AKnave, CKnave)),
    Implication(BKnave, And(AKnight, CKnight)),

    # C disse que o A é knight
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight)),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
