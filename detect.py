from pydantic import BaseModel


class DetectionInstructions(BaseModel):
    edf_absolute_path: str
    channel: str


class DetectionConfiguration(BaseModel):
    pass


class SpindleResult(BaseModel):
    id: str
    start_seconds: float
    end_seconds: float


class CustomSpindleResult(SpindleResult):
    # add any custom property you will need.
    pass


class DetectionResult(BaseModel):
    spindles: list[CustomSpindleResult]


def detect_spindles(
    dto: DetectionInstructions, configuration: DetectionConfiguration
) -> DetectionResult:
    import pyedflib

    edf_reader = pyedflib.EdfReader(dto.edf_absolute_path)
    signal_data = edf_reader.readSignal(edf_reader.getSignalLabels().index(dto.channel))
    sampling_frequency = edf_reader.getSampleFrequencies()[
        edf_reader.getSignalLabels().index(dto.channel)
    ]

    from sumo_infrastructure import SumoDetector

    detector = SumoDetector()
    results = detector.detect_segments(sampling_frequency, signal_data)

    results = [
        CustomSpindleResult(
            id=str(i),
            start_seconds=start / sampling_frequency,
            end_seconds=end / sampling_frequency,
        )
        for i, (start, end) in enumerate(results)
    ]
    return DetectionResult(spindles=results)


if __name__ == "__main__":
    detect_spindles(
        DetectionInstructions(
            edf_absolute_path="path/to/edf/files",
            channel="EEG Fpz-Cz",
        ),
        DetectionConfiguration(),
    )
