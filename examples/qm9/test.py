import dask
import np


def func(data):
    result = np.histogram(data)
    return result


def func_partition(data, additional_args):
    result = data.apply(func, args=(bsifilter, ), axis=1)
    return result

if __name__ == '__main__':
    dask.set_options(get=dask.multiprocessing.get)
    n = 30000
    df = pd.DataFrame({'image': [(np.random.random((180, 64)) * 255).astype(np.uint8) for i in np.arange(n)],
                   'n1': np.arange(n),
                   'n2': np.arange(n) * 2,
                   'n3': np.arange(n) * 4
                   }
                  )


    ddf = dd.from_pandas(df, npartitions=MAX_PROCESSORS)
    dhists = ddf.map_partitions(func_partition, bfilter, meta=pd.Series(dtype=np.ndarray))
    print('Delayed dhists = \n', dhists)
    hists = pd.Series(dhists.compute())
