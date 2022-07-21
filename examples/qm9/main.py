import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error
import joblib

from dataset import QM9Dataset, data_root
from feature import FingerprintFeatureset


logging.basicConfig(format='%(asctime)s [%(process)d][%(levelname).1s] %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def prepare_data() -> Tuple[np.ndarray]:
    dataset = QM9Dataset()
    df = dataset.manifest
    logger.info(f"dataset manifest:\n{df}")

    featset = FingerprintFeatureset(dataset)
    return df, featset.result


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    #cluster = LocalCluster(host='127.0.0.1', scheduler_port=8786, dashboard_address=':8787')
    #cluster.adapt(minimum=1, maximum=8)
    #client = Client(cluster)
    #client = Client()

    raw_df, (trainset, testset) = prepare_data()

    model_path = data_root.joinpath("models", "svr.pkl")
    model_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
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
        # training
        search.fit(trainset.x.astype('f8'), trainset.y)
        pd.DataFrame(search.cv_results_)
        # save model
        joblib.dump(search, model_path, compress=('gzip', 9))
    else:
        # load model
        search = joblib.load(model_path)

    # test
    y_pred = search.predict(testset.x.astype('f8'))

    test_df = pd.DataFrame({'idx': testset.i, 'y_test': testset.y, 'y_pred': y_pred})
    test_df.set_index('idx', inplace=True)
    test_df['smiles'] = test_df.index.to_series().apply(lambda x: raw_df.loc[x, "smiles"])
    logger.info(f"test results:\n{test_df}")

    mae = mean_absolute_error(testset.y, y_pred)
    logger.info(f"test MAE: {mae:.4f}")
