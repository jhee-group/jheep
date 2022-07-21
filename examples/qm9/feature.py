import logging
from pathlib import Path
from typing import Any, Sequence, Callable, NamedTuple, Tuple

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, rdFingerprintGenerator
from sklearn.model_selection import train_test_split
import h5py

import dask.dataframe as dd
from dask.distributed import Client, LocalCluster
from distributed.protocol import dask_serialize, dask_deserialize

from dataset import BaseDataset, data_root


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
@dask_serialize.register(np.ndarray)
def _serialize_ndarray(arr: np.ndarray) -> bytes:
    if isinstance(arr, np.ndarray):
        with io.BytesIO() as buf:
            np.save(buf, arr)
            return buf.getvalue()
    return arr


@dask_deserialize.register(np.ndarray)
def _deserialize_ndarray(val: bytes) -> np.ndarray:
    return np.load(io.BytesIO(val)) if isinstance(val, bytes) else val
"""


class BaseFeatureset:

    def __init__(
        self,
        dataset: BaseDataset,
        transport: Callable[..., np.ndarray],
    ):
        self._dataset = dataset
        self._transport = transport
        self._featset: Sequence | None = None

    @property
    def featset(self) -> Sequence:
        if self._featset is None:
            self.update()
        return self._featset

    def update(self):
        logger.info("transport data into featureset ...")
        manifest = self._dataset.manifest
        self._featset = self.batch_transport(manifest)

    def _wrapper_transport(self, x) -> np.ndarray:
        kwargs = x.to_dict()
        return self._transport(**kwargs)

    def transport(self, x: Any) -> np.ndarray:
        return self._wrapper_transport(x)

    def batch_transport(self, x: Sequence) -> np.ndarray:
        return x.apply(self._wrapper_transport, axis=1)


        """
        def dask_worker1():
            ddf = dd.read_csv(manifest_path)
            #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            #    print(df.head(100))
            futures = client.map(make_fingerprint_feature2, ddf.smiles)
            results = client.gather(futures)
            return results

        def dask_worker2():
            ddf = dd.read_csv(manifest_path)
            ddf = ddf.repartition(npartitions=4)

            def mff_wrapper(df):
                return df.smiles.apply(make_fingerprint_feature)

            results = ddf.map_partitions(mff_wrapper, meta=pd.Series(dtype=str)).compute()
            return results

        def dask_worker3():
            ddf = dd.read_csv(manifest_path)
            ddf = ddf.repartition(npartitions=4)

            def mff_wrapper(dfd):
                df = dfd.compute()
                return df['smiles'].apply(make_fingerprint_feature)

            futures = client.map(mff_wrapper, ddf.to_delayed())
            results = pd.concat(client.gather(futures))
            return results

        def dask_worker4():
            ddf = dd.read_csv(manifest_path)
            ddf = ddf.repartition(npartitions=8)
            futures = ddf.smiles.apply(make_fingerprint_feature, meta=pd.Series(dtype=str))
            results = futures.compute()
            return results

        def dask_worker5(ddf):
            ddf = ddf.repartition(npartitions=1)

            def mff_wrapper(dfd):
                df = dfd.compute()
                return df['smiles'].apply(make_fingerprint_feature2)

            futures = client.map(mff_wrapper, ddf.to_delayed())
            results = pd.concat(client.gather(futures))
            return results
        """


class Splitset(NamedTuple):
    i: np.ndarray
    x: np.ndarray
    y: np.ndarray | None


class OfflineFeatureset(BaseFeatureset):

    def __init__(
        self,
        dataset: BaseDataset,
        transport: Callable[..., np.ndarray],
        featset_path: Path,
    ):
        super().__init__(dataset, transport)
        self._featset_path = featset_path
        self._result: Tuple[NamedTuple] | None = None
        self._featset_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

    def _make_result(self):
        X = self.featset
        y = self._dataset.manifest.homo
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

        i_train = np.asarray(X_train.index)
        X_train = np.stack(X_train)
        y_train = np.stack(y_train)

        i_test = np.asarray(X_test.index)
        X_test = np.stack(X_test)
        y_test = np.stack(y_test)

        with h5py.File(self._featset_path, 'w') as store:
            comp_param = {
                'shuffle': True,
                'compression': 'gzip',
                'compression_opts': 9,
            }
            store.create_dataset("i_train", data=i_train, **comp_param)
            store.create_dataset("X_train", data=X_train, **comp_param)
            store.create_dataset("y_train", data=y_train, **comp_param)

            store.create_dataset("i_test", data=i_test, **comp_param)
            store.create_dataset("X_test", data=X_test, **comp_param)
            store.create_dataset("y_test", data=y_test, **comp_param)

        self._result = (
            Splitset(i_train, X_train, y_train),
            Splitset(i_test, X_test, y_test),
        )

    def _load_result(self):
        with h5py.File(self._featset_path, "r") as store:
            i_train = store["i_train"][:]
            X_train = store["X_train"][:]
            y_train = store["y_train"][:]

            i_test = store["i_test"][:]
            X_test = store["X_test"][:]
            y_test = store["y_test"][:]

        self._result = (
            Splitset(i_train, X_train, y_train),
            Splitset(i_test, X_test, y_test),
        )

    @property
    def result(self):
        if self._result is None:
            if self._featset_path.exists():
                self._load_result()
            else:
                self._make_result()
        return self._result


def make_fingerprint_feature(
    smiles: str,
    radius: int = 2,
    bitcount: int = 4096,
    **kwargs,
) -> np.array:
    if bitcount % 8 != 0:
        raise Exception("fingerprints length must be multiples of 8")
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles, sanitize=True))
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, useChirality=True, radius=radius, nBits=bitcount)
    #return fp.ToBase64()
    arr = np.asarray(fp)
    return arr


def make_fingerprint_feature2(
    smiles: str,
    radius: int = 2,
    bitcount: int = 4096,
    **kwargs,
) -> np.array:
    """
    https://github.com/rdkit/rdkit/pull/4523
    """
    if bitcount % 8 != 0:
        raise Exception("fingerprints length must be multiples of 8")
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles, sanitize=True))
    #rdFingerprintGenerator.GetRDKitFPGenerator,
    #rdFingerprintGenerator.GetMorganGenerator,
    #rdFingerprintGenerator.GetAtomPairGenerator,
    #rdFingerprintGenerator.GetTopologicalTorsionGenerator):
    fn = rdFingerprintGenerator.GetMorganGenerator
    gen = fn(includeChirality=True, radius=radius, fpSize=bitcount)
    #fp = gen.GetFingerprint(mol)
    #oarr = np.zeros((fp.GetNumBits(), ), 'u1')
    #DataStructs.ConvertToNumpyArray(fp, oarr)
    arr = gen.GetFingerprintAsNumPy(mol)
    #np.testing.assert_array_equal(oarr, arr)

    #cfp = gen.GetCountFingerprint(mol)
    #oarr = np.zeros((cfp.GetLength(), ), 'u4')
    #DataStructs.ConvertToNumpyArray(cfp, oarr)
    #arr = gen.GetCountFingerprintAsNumPy(mol)
    #np.testing.assert_array_equal(oarr, arr)
    return arr


class FingerprintFeatureset(OfflineFeatureset):

    def __init__(
        self,
        dataset,
        transport = make_fingerprint_feature2,
        featset_path = data_root.joinpath("feature", "featset.h5"),
    ):
        super().__init__(dataset, transport, featset_path)


"""
def make_feature(raw_df, feature_file):


    #t = timer()
    results = pandas_worker(raw_df)
    #results = dask_worker5(raw_ddf)
    #et = timer() - t
    #np.set_printoptions(threshold=sys.maxsize)
    #print(results[130185])
    #print(f"elapsed time: {et:.3f} secs")

    #logger.info(results.head(5))

    X = results
    y = df.homo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    i_train = np.asarray(X_train.index)
    X_train = np.stack(X_train)
    y_train = np.stack(y_train)
    i_test = np.asarray(X_test.index)
    X_test = np.stack(X_test)
    y_test = np.stack(y_test)

    with h5py.File(featset_path, 'w') as store:
        comp_param = {
            'shuffle': True,
            'compression': 'gzip',
            'compression_opts': 9,
        }
        store.create_dataset("i_train", data=i_train, **comp_param)
        store.create_dataset("X_train", data=X_train, **comp_param)
        store.create_dataset("y_train", data=y_train, **comp_param)

        store.create_dataset("i_test", data=i_test, **comp_param)
        store.create_dataset("X_test", data=X_test, **comp_param)
        store.create_dataset("y_test", data=y_test, **comp_param)

    else:
        with h5py.File(featset_path, "r") as store:
            i_train = store["i_train"][:]
            X_train = store["X_train"][:]
            y_train = store["y_train"][:]

            i_test = store["i_test"][:]
            X_test = store["X_test"][:]
            y_test = store["y_test"][:]


    model_file: str = "model.pkl"
    model_path = file_path.joinpath(model_file)

    logger.info(f"model_path: {model_path}")

    if not model_path.exists():
        param_space = {
            'C': np.logspace(-6, 6, 13),
            #'gamma': 'scale',
            #'tol': np.logspace(-4, -1, 4),
            #'epsilon': [0.08, 0.09, 0.1],
        }

        model = SVR(kernel='rbf')
        search = GridSearchCV(model, param_space, cv=5, verbose=10, scoring='neg_mean_absolute_error')
        search.fit(X_train.astype('f8'), y_train)

        pd.DataFrame(search.cv_results_)

        joblib.dump(search, model_path, compress=('gzip', 9))
    else:
        search = joblib.load(model_path)


    y_pred = search.predict(X_test.astype('f8'))

    test_df = pd.DataFrame({'idx': i_test, 'y_test': y_test, 'y_pred': y_pred})
    test_df.set_index('idx', inplace=True)
    test_df['smiles'] = test_df.index.to_series().apply(lambda x: raw_df.loc[x, "smiles"])
    logger.info(f"test results:\n{test_df}")

    mae = mean_absolute_error(y_test, y_pred)
    logger.info(f"test MAE: {mae:.4f}")
"""
