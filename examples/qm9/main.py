import os
import io
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem
import dask.dataframe as dd
from dask.distributed import Client, LocalCluster
from distributed.protocol import dask_serialize, dask_deserialize

from .utils import download, extract_zip


rdBase.DisableLog('rdApp.*')

logging.basicConfig(format='%(asctime)s [%(process)d] %(levelname)-5.5s %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

raw_url = 'https://s3-us-west-1.amazonaws.com/deepchem.io/datasets/molnet_publish/qm9.zip'
raw_url2 = 'https://ndownloader.figshare.com/files/3195404'
processed_url = 'http://www.roemisch-drei.de/qm9.zip'

data_root = Path(os.environ.get("JHEEP_EXAMPLES_PATH"), ".data", "qm9")
raw_path = data_root.joinpath('raw')
raw_paths = [raw_path.joinpath(x) for x in ['gdb9.sdf', 'gdb9.sdf.csv', 'uncharacterized.txt']]


def download_qm9_data() -> None:
    logger.info("download qm9 data files ...")
    file_path = download(raw_url, raw_path)
    extract_zip(file_path, raw_path)
    Path(file_path).unlink()
    file_path = download(raw_url2, raw_path)
    Path(raw_path, '3195404').rename(Path(raw_path, 'uncharacterized.txt'))


def make_dataset(
    file_path: Path | str = data_root.joinpath("data"),
    manifest_file: str = "manifest.csv",
) -> None:
    if not raw_paths[0].exists():
        download_qm9_data()

    # read mol data
    """
    Molecules
    ---------
    For a subset of the GDB-9 database [1] consisting of 133885 neutral organic
    molecules composed from elements H,C,N,O,F, molecular geometries were relaxed
    and properties calculated at the DFT/B3LYP/6-31G(2df,p) level of theory.

    For a subset of 6095 isomers of C7O2H10, energetics were calculated
    at the G4MP2 [2] level of theory.

    For a validation set of 100 randomly drawn molecules from the 133885 molecules set,
    enthalpies of formation were additionally calculated at the
    DFT/B3LYP/6-31G(2df,p), G4MP2, G4 and CBS-QB3 levels of theory.

    Format
    ------
    Each molecule is stored in its own file, ending in ".xyz".
    The format is an ad hoc extension of the XYZ format [3].

    Line       Content
    ----       -------
    1          Number of atoms na
    2          Properties 1-17 (see below)
    3,...,na+2 Element type, coordinate (x,y,z) (Angstrom), and Mulliken partial charge (e) of atom
    na+3       Frequencies (3na-5 or 3na-6)
    na+4       SMILES from GDB9 and for relaxed geometry
    na+5       InChI for GDB9 and for relaxed geometry
    """
    logger.info("import qm9 mol files ...")
    supp = Chem.SDMolSupplier(str(raw_paths[0]), removeHs=True)
    mols = [{
        'mol_id': None if m is None else m.GetProp('_Name'),
        'smiles': None if m is None else Chem.MolToSmiles(m),
    } for m in supp]
    mols_df = pd.DataFrame.from_records(mols)

    # read targets
    """
        The properties stored in the second line of each file:

        I.  Property  Unit         Description
        --  --------  -----------  --------------
         1  tag       -            "gdb9"; string constant to ease extraction via grep
         2  index     -            Consecutive, 1-based integer identifier of molecule
         3  A         GHz          Rotational constant A
         4  B         GHz          Rotational constant B
         5  C         GHz          Rotational constant C
         6  mu        Debye        Dipole moment
         7  alpha     Bohr^3       Isotropic polarizability
         8  homo      Hartree      Energy of Highest occupied molecular orbital (HOMO)
         9  lumo      Hartree      Energy of Lowest occupied molecular orbital (LUMO)
        10  gap       Hartree      Gap, difference between LUMO and HOMO
        11  r2        Bohr^2       Electronic spatial extent
        12  zpve      Hartree      Zero point vibrational energy
        13  U0        Hartree      Internal energy at 0 K
        14  U         Hartree      Internal energy at 298.15 K
        15  H         Hartree      Enthalpy at 298.15 K
        16  G         Hartree      Free energy at 298.15 K
        17  Cv        cal/(mol K)  Heat capacity at 298.15 K

        I. = Property index (properties are given in this order)
        For the 6095 isomers, properties 12-16 were calculated at the G4MP2 level of theory.
        All other calculations were done at the DFT/B3LYP/6-31G(2df,p) level of theory.
    """
    logger.info("import qm9 labels ...")
    labels_df = pd.read_csv(raw_paths[1])
    labels_df = labels_df[[
        'mol_id',
        'mu', 'alpha', 'homo', 'lumo',
        'gap', 'r2', 'zpve',
        'u0', 'u298', 'h298', 'g298', 'cv',
    ]]
    df = pd.merge(mols_df, labels_df, how='right', on='mol_id')
    df.index += 1
    logger.info(df.head(20))

    # read wrong info
    """
    Notes
    -----
    3054 molecules from the 133885 GDB9 molecules failed a consistency check where the Corina generated
    Cartesian coordinates and the B3LYP/6-31G(2df,p) equilibrium geometry lead to different SMILES strings.

    Out of the 133885 molecules, geometries of the 11 molecules with indices
    21725, 87037, 59827, 117523, 128113, 129053, 129152, 129158, 130535, 6620, 59818
    were difficult to converge.
    Low threshold convergence was possible for 21725, 59827, 128113, 129053, 129152, 130535.
    Molecules 6620 and 59818 converged to very low-lying saddlepoints, with lowest frequency < 10i cm^-1.
    """
    logger.info("import qm9 unchar charts ...")
    with open(raw_paths[2], 'r') as f:
        lines = f.readlines()
        skip = [int(line.split()[0]) for line in lines[9:-1]]
    assert len(skip) == 3054
    ignore = set(skip)
    ignore.update([21725, 87037, 59827, 117523, 128113, 129053, 129152, 129158, 130535, 6620, 59818])
    df = df.drop(ignore, axis=0)
    df.dropna(how='any', inplace=True)

    logger.info("final manifest:", df.head(20))

    # write manifest
    manifest_path = file_path.joinpath(manifest_file)
    manifest_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    df.to_csv(manifest_path, index=False)


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


def make_fingerprint_feature(
    smiles: str,
    radius: int = 2,
    bitcount: int = 4096,
) -> np.array:
    if bitcount % 8 != 0:
        raise Exception("fingerprints length must be multiples of 8")
    mol = Chem.MolFromSmiles(smiles, sanitize=True)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, useChirality=True, radius=radius, nBits=bitcount)
    return fp.ToBase64()
    #return np.array(fp, dtype=np.uint8).tobytes()


if __name__ == "__main__":
    from timeit import default_timer as timer

    cluster = LocalCluster()
    cluster.adapt(minimum=1, maximum=8)
    client = Client(cluster)

    file_path: Path | str = data_root.joinpath("data")
    manifest_file: str = "manifest.csv"
    if not file_path.exists():
        make_dataset(file_path, manifest_file)

    manifest_path = file_path.joinpath(manifest_file)

    def pandas_worker():
        tqdm.pandas()
        df = pd.read_csv(manifest_path)
        results = df['smiles'].apply(make_fingerprint_feature)
        print(results)

    def dask_worker1():
        ddf = dd.read_csv(manifest_path)
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #    print(df.head(100))
        futures = client.map(make_fingerprint_feature, ddf.smiles)
        results = client.gather(futures)
        return results

    def dask_worker2():
        ddf = dd.read_csv(manifest_path)
        ddf = ddf.repartition(npartitions=4)

        def mff_wrapper(df):
            return df.smiles.apply(make_fingerprint_feature)

        results = ddf.map_partitions(mff_wrapper, meta=pd.Series(dtype=str)).compute()
        print(results)

    def dask_worker3():
        ddf = dd.read_csv(manifest_path)
        ddf = ddf.repartition(npartitions=4)

        def mff_wrapper(dfd):
            df = dfd.compute()
            return df['smiles'].apply(make_fingerprint_feature)

        futures = client.map(mff_wrapper, ddf.to_delayed())
        results = pd.concat(client.gather(futures))
        print(results)

    def dask_worker4():
        ddf = dd.read_csv(manifest_path)
        ddf = ddf.repartition(npartitions=8)
        futures = ddf.smiles.apply(make_fingerprint_feature, meta=pd.Series(dtype=str))
        results = futures.compute()
        print(results)


    t = timer()
    #results = pandas_worker()
    results = dask_worker3()
    et = timer() - t
    print(f"elapsed time: {et:.3f} secs")
