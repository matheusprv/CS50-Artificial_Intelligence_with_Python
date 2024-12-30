import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus: dict, page: str, damping_factor: float):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    n = len(corpus.keys())

    # Se nao tem links para outras paginas, todas devem ter a mesma probabildiade
    if len(corpus[page]) == 0:
        return {k:  damping_factor / n for k in corpus.keys()}

    # caclulando a probabildiade de ir para as paginas que a pagina atual conhece 
    # mais a chance de ir para outras diferentes
    start_probability = (1 - damping_factor) / n
    output = {
        #  Paginas que a atual conhece | multiplicando por falso (0) ou true (1) 
        curr_page: (damping_factor / len(corpus[page])) * 
        (curr_page in corpus[page]) + start_probability
        for curr_page in corpus.keys()
    }

    return output


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    pages_counting = {k: 0 for k in corpus.keys()}

    page = random.choice(list(corpus.keys()))
    for _ in range(n):
        tm = transition_model(corpus, page, damping_factor)
        page = random.choices(list(tm.keys()), weights=tm.values())[0]
        pages_counting[page] += 1

    pages = {page: pages_counting[page]/n for page in corpus.keys()}

    return pages


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    target = 0.001
    N = len(corpus)

    # Paginas que nao possuem links terão links para todas e para elas mesmas
    for page in corpus:
        if not corpus[page]:
            corpus[page] = set(corpus.keys())

    page_rank = {page: 1 / N for page in corpus}
    
    not_converged = True
    while not_converged:
        previous_page_rank = page_rank.copy()

        for page in corpus:
            pr = (1 - damping_factor) / N

            for other_page in corpus:
                if page in corpus[other_page]:
                    pr += (damping_factor * 
                           (previous_page_rank[other_page] / len(corpus[other_page])))

            page_rank[page] = pr

        not_converged = any(
            abs(page_rank[page] - previous_page_rank[page]) > target
            for page in corpus
        )

    return page_rank


if __name__ == "__main__":
    main()
