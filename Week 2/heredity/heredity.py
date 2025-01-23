import csv
import itertools
import sys
import math

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1

    def calculate_number_of_genes(person): 
        return 2 if person in two_genes else 1 if person in one_gene else 0
    
    def check_has_traits(person): 
        return person in have_trait
    
    # Se o pai/mae nao possui o gene, entao so pode ser passado por mutacao. Se possui 1, entao é 50% de chance, caso contrario ele vai passar a nao ser que sofra mutacao
    def parent_probability(number_of_genes): 
        return PROBS['mutation'] if number_of_genes == 0 else 0.5 if number_of_genes == 1 else 1 - PROBS['mutation']

    for person in people.keys():
        number_of_genes = calculate_number_of_genes(person)
        has_trait = check_has_traits(person)

        # Caso não seja informado o pai e a mãe da pessoa
        if people[person]["mother"] is None:
            probability *= (PROBS["gene"][number_of_genes] * 
                            PROBS["trait"][number_of_genes][has_trait])

        else:
            father = people[person]["father"]
            father_number_of_genes = calculate_number_of_genes(father)
            father_probability = parent_probability(father_number_of_genes)

            mother = people[person]["mother"]
            mother_number_of_genes = calculate_number_of_genes(mother)
            mother_probability = parent_probability(mother_number_of_genes)
            
            if number_of_genes == 0:
                probability *= (1 - mother_probability) * (1 - father_probability)
            elif number_of_genes == 1:
                probability *= ((1 - mother_probability) * father_probability 
                                + mother_probability * (1 - father_probability))
            else:
                probability *= mother_probability * father_probability
            
            probability *= PROBS["trait"][number_of_genes][has_trait]

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    def calculate_number_of_genes(person): 
        return 2 if person in two_genes else 1 if person in one_gene else 0
    
    def check_has_traits(person): 
        return person in have_trait
    
    for person in probabilities:
        number_of_genes = calculate_number_of_genes(person)
        has_trait = check_has_traits(person)
        probabilities[person]["gene"][number_of_genes] += p
        probabilities[person]["trait"][has_trait] += p

    
def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for gene_trait in probabilities[person]:
            total = sum(probabilities[person][gene_trait].values())
            for key in probabilities[person][gene_trait]:
                probabilities[person][gene_trait][key] /= total


if __name__ == "__main__":
    main()
