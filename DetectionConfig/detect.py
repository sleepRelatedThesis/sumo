from dataclasses import dataclass


@dataclass
class DetectionInstructions:
    detection_id: str
    edf_absolute_path: str
    channel: str
    configuration: dict


@dataclass
class SpindleResult:
    id: int
    start_seconds: float
    end_seconds: float


@dataclass
class CustomSpindleResult(SpindleResult):
    # add any custom property you will need.
    pass


def detect_spindles(dto: DetectionInstructions) -> list[CustomSpindleResult]:
    import pyedflib

    edf_reader = pyedflib.EdfReader(dto.edf_absolute_path)
    signal_data = edf_reader.readSignal(edf_reader.getSignalLabels().index(dto.channel))
    sampling_frequency = edf_reader.getSampleFrequencies()[
        edf_reader.getSignalLabels().index(dto.channel)
    ]

    from DetectionConfig.sumo_infrastructure import SumoDetector

    detector = SumoDetector()
    results = detector.detect_segments(sampling_frequency, signal_data)

    results = [
        CustomSpindleResult(
            id=i,
            start_seconds=start / sampling_frequency,
            end_seconds=end / sampling_frequency,
        )
        for i, (start, end) in enumerate(results)
    ]
    return results
