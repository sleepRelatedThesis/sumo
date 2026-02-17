from pathlib import Path
from typing import Union

import numpy as np
import pytorch_lightning as pl
import torch
from scipy.signal import resample_poly
from scipy.stats import zscore
from torch.utils.data import Dataset, DataLoader

from sumo.config import Config
from sumo.data import spindle_vect_to_indices
from sumo.model import SUMO


def downsample(data, sample_rate: int, resampling_frequency: int):
    if (sample_rate != int(sample_rate)) | (
        resampling_frequency != int(resampling_frequency)
    ):
        raise Exception(
            'parameters "sample_rate" and "resampling_frequency" have to be integers'
        )
    elif sample_rate < resampling_frequency:
        raise Exception(
            "the original sample frequency must not be lower than the resample frequency"
        )
    elif sample_rate == resampling_frequency:
        return data

    sample_rate = int(sample_rate)
    resampling_frequency = int(resampling_frequency)

    gcd = np.gcd(sample_rate, resampling_frequency)

    up = resampling_frequency // gcd
    down = sample_rate // gcd

    return resample_poly(data, up, down)


def get_model(path: Union[str, Path]):
    path = Path(path)
    model_file = path
    model_checkpoint = torch.load(model_file, map_location="cpu")
    config = Config("predict", create_dirs=False)
    model = SUMO(config)
    model.load_state_dict(model_checkpoint["state_dict"])
    return model


class SimpleDataset(Dataset):
    def __init__(self, data_vectors):
        super(SimpleDataset, self).__init__()
        self.data = data_vectors

    def __len__(self) -> int:
        return len(self.data)

    @staticmethod
    def preprocess(data):
        return zscore(data)

    def __getitem__(self, idx):
        data = self.preprocess(self.data[idx])
        return torch.from_numpy(data).float(), torch.zeros(0)


class SumoDetector:
    def __init__(self):
        script_dir = Path(__file__).parent
        model_path = script_dir / "output" / "final.ckpt"
        print(f"Loading model from: {model_path}")
        self.model = get_model(model_path)

    def detect_segments(self, sampling_frequency: int, data) -> list[tuple[int, int]]:
        sf = sampling_frequency
        resample_rate = 100
        signal_down = downsample(data, sf, resample_rate)
        dataset = SimpleDataset([signal_down])
        dataloader = DataLoader(dataset)
        trainer = pl.Trainer(num_sanity_val_steps=0, logger=False)
        predictions = trainer.predict(self.model, dataloader)
        if not predictions:
            raise ValueError("No predictions were made by the model.")
        spindle_segments = (
            []
        )  # list of (start, end) index, (not seconds) in original signal sampling frequency.
        for pred in predictions:
            spindle_vect = pred[0].numpy()
            spindles = spindle_vect_to_indices(spindle_vect) / resample_rate
            for sp in spindles:
                spindle_segment = (int(sp[0] * sf), int(sp[1] * sf))
                spindle_segments.append(spindle_segment)
        return spindle_segments
