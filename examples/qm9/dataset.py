import os
import logging
from pathlib import Path
from typing import Sequence

import pandas as pd
from rdkit import Chem, rdBase

from utils import download, extract_zip


rdBase.DisableLog('rdApp.*')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

data_root = Path(os.environ.get("JHEEP_EXAMPLES_PATH"), ".data", "qm9")
download_path = data_root.joinpath('download')
process_path = data_root.joinpath("process")


"""
class SingletonClass(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance
"""


class BaseDataset:

    def __init__(self, manifest_path: Path):
        self._manifest_path = manifest_path
        self._manifest: pd.DataFrame | None = None
        self._manifest_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

    def preprocess(self) -> None:
        pass

    def _make_manifest(self) -> Sequence:
        ...

    @property
    def manifest(self) -> Sequence:
        if self._manifest is not None:
            return self._manifest
        elif Path(self._manifest_path).exists():
            logger.info(f"loading manifest from {self._manifest_path}")
            self._manifest = pd.read_csv(self._manifest_path)
            return self._manifest
        else:
            self.preprocess()
            logger.info(f"generating manifest")
            return self._make_manifest()

    def __len__(self) -> int:
        return len(self.manifest)


class QM9Dataset(BaseDataset):

    def __init__(
        self,
        download_path = data_root.joinpath('download'),
        manifest_path = data_root.joinpath("process", "manifest.csv"),
    ):
        super().__init__(manifest_path)
        self._download_path = download_path

    def preprocess(self) -> None:
        if Path(self._download_path).exists():
            return

        raw_url = 'https://s3-us-west-1.amazonaws.com/deepchem.io/datasets/molnet_publish/qm9.zip'
        raw_url2 = 'https://ndownloader.figshare.com/files/3195404'
        processed_url = 'http://www.roemisch-drei.de/qm9.zip'

        logger.info("download qm9 data files ...")
        file_path = download(raw_url, self._download_path)
        extract_zip(file_path, self._download_path)
        Path(file_path).unlink()

        file_path = download(raw_url2, self._download_path)
        Path(self._download_path, '3195404').rename(Path(self._download_path, 'uncharacterized.txt'))

    def _make_manifest(self) -> pd.DataFrame:
        download_files = ['gdb9.sdf', 'gdb9.sdf.csv', 'uncharacterized.txt']
        download_paths = [self._download_path.joinpath(f) for f in download_files]

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
        supp = Chem.SDMolSupplier(str(download_paths[0]), removeHs=True)
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
        labels_df = pd.read_csv(download_paths[1])
        labels_df = labels_df[[
            'mol_id',
            'mu', 'alpha', 'homo', 'lumo',
            'gap', 'r2', 'zpve',
            'u0', 'u298', 'h298', 'g298', 'cv',
        ]]
        df = pd.merge(mols_df, labels_df, how='right', on='mol_id')
        df.index += 1
        logger.info(f"total len of original dataset: {len(df)}")

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
        with open(download_paths[2], 'r') as f:
            lines = f.readlines()
            skip = [int(line.split()[0]) for line in lines[9:-1]]
        assert len(skip) == 3054
        ignore = set(skip)
        ignore.update([21725, 87037, 59827, 117523, 128113, 129053, 129152, 129158, 130535, 6620, 59818])
        logger.info(f"ignore uncharacterized indices: {len(ignore)}")
        df = df.drop(ignore, axis=0)

        ignored = len(df)
        df.dropna(how='any', inplace=True)
        logger.info(f"dropped rows with na: {ignored - len(df)}")

        logger.info(f"final len of dataset: {len(df)}")

        # write manifest to file
        df.to_csv(self._manifest_path, index=False)
        df.reset_index(drop=True, inplace=True)

        return df
