import itertools
import collections
import multiprocessing


class MapReduce(object):
    """
    map_func: Function to map inputs to intermediate data. Takes as
              argument one input value and returns a tuple with the key
              and a value to be reduced.
    reduce_func: Function to reduce partitioned version of intermediate data
                 to final output. Takes as argument a key as produced by
                 map_func and a sequence of the values associated with that
                 key.
    num_workers: The number of workers to create in the pool. Defaults to the
                 number of CPUs available on the current host.
    """

    def __init__(self, map_func, reduce_func, pool=None):
        self.map_func = map_func
        self.reduce_func = reduce_func
        if pool is None:
            pool = multiprocessing.Pool()
        self.pool = pool

    def partition(self, mapped_values):
        """Organize the mapped values by their key.
        Returns an unsorted sequence of tuples with a key and a sequence of values.
        """
        partitioned_data = collections.defaultdict(list)
        for key, value in mapped_values:
            partitioned_data[key].append(value)
        return partitioned_data.items()

    def __call__(self, inputs, chunksize=1):
        """Process the inputs through the map and reduce functions given.

        inputs
          An iterable containing the input data to be processed.

        chunksize=1
          The portion of the input data to hand to each worker.  This
          can be used to tune performance during the mapping phase.
        """
        map_responses = self.pool.map(self.map_func, inputs, chunksize=chunksize)
        partitioned_data = self.partition(itertools.chain(*map_responses))
        reduced_values = self.pool.map(self.reduce_func, partitioned_data)
        return reduced_values


def map_reduce(mapf, reducef, inputs, pool=None, chuncksize=1):
    mr = MapReduce(mapf, reducef, pool=pool)
    return mr(inputs, chuncksize=chuncksize)
