import multiprocessing
import string
import collections

from map_reduce import MapReduce

def file_to_words(filename):
    """Read a file and return a sequence of (word, occurances) values.
    """
    with open(filename, 'rb') as f:
        words = (word.lower() for word in f.read().split())
        return tuple(collections.Counter(words).items())


def count_words(item):
    """Convert the partitioned data for a word to a
    tuple containing the word and the number of occurances.
    """
    word, occurances = item
    return (word, sum(occurances))


def count_words_map_reduce():
    import operator
    import glob

    input_files = glob.glob('*.txt')

    mapper = MapReduce(file_to_words, count_words)
    word_counts = dict(mapper(input_files))
    res = collections.Counter()
    res.update(word_counts)
    for i in res.most_common(20):
        print(i)


if __name__ == '__main__':
    count_words_map_reduce()
