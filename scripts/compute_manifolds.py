import os
import argparse
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
import pandas as pd
import tensorflow as tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
from activation_models.generators import get_activation_models
from custom_model_tools.manifold import (
    ManifoldStatisticsImageNet21k,
    ManifoldStatisticsImageNet,
    ManifoldStatisticsObject2Vec,
    ManifoldStatisticsMajajHong2015,
)

from utils import timed


@timed
def main(dataset, data_dir, pooling, additional, debug=False):
    save_path = f"results/manifolds|dataset:{dataset}|pooling:{pooling}.csv"
    if additional:
        save_path = save_path.replace(".csv", "|additional:True.csv")
    if os.path.exists(save_path):
        print(f"Results already exists: {save_path}")
        return

    manifold_statistics_df = pd.DataFrame()
    for model, layers in get_activation_models(additional=additional):
        manifold_statistics = get_manifold_statistics(dataset, data_dir, model, pooling)
        manifold_statistics.fit(layers)
        manifold_statistics_df = manifold_statistics_df.append(
            manifold_statistics.as_df()
        )
        if debug:
            break
    if not debug:
        manifold_statistics_df.to_csv(save_path, index=False)


def get_manifold_statistics(dataset, data_dir, activations_extractor, pooling):
    if dataset == "imagenet":
        return ManifoldStatisticsImageNet(
            activations_extractor=activations_extractor, pooling=pooling
        )
    elif dataset == "imagenet21k":
        return ManifoldStatisticsImageNet21k(
            data_dir=data_dir,
            activations_extractor=activations_extractor,
            pooling=pooling,
        )
    elif dataset == "imagenet21klarge":
        return ManifoldStatisticsImageNet21k(
            data_dir=data_dir,
            activations_extractor=activations_extractor,
            pooling=pooling,
            stimuli_identifier=dataset,
            num_classes=725,
            num_per_class=725,
        )
    elif dataset == "object2vec":
        return ManifoldStatisticsObject2Vec(
            data_dir=data_dir,
            activations_extractor=activations_extractor,
            pooling=pooling,
        )
    elif dataset == "majajhong2015":
        return ManifoldStatisticsMajajHong2015(
            activations_extractor=activations_extractor, pooling=pooling
        )
    else:
        raise ValueError(f"Unknown manifold dataset: {dataset}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute and store manifold statistics of models"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=[
            "imagenet",
            "imagenet21k",
            "imagenet21klarge",
            "object2vec",
            "majajhong2015",
        ],
        help="Dataset of concepts for which to compute manifold statistics",
    )
    parser.add_argument(
        "--data_dir", type=str, default=None, help="Data directory containing stimuli"
    )
    parser.add_argument(
        "--pooling",
        type=str,
        default="avg",
        choices=["max", "avg", "none"],
        help="Perform pooling prior to computing the manifold statistics",
    )
    parser.add_argument(
        "--additional_models",
        dest="additional",
        action="store_true",
        help="Run only additional models (AlexNet, VGG16, SqueezeNet)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Just run a single model to make sure there are no errors",
    )
    args = parser.parse_args()

    main(
        dataset=args.dataset,
        data_dir=args.data_dir,
        pooling=args.pooling,
        additional=args.additional,
        debug=args.debug,
    )
