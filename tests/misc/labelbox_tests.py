"""
Tests for the :mod:`fiftyone.utils.labelbox` module.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import unittest
from uuid import uuid4

import fiftyone as fo
import fiftyone.zoo as foz
import fiftyone.utils.labelbox as foul


@unittest.skip("Must be run manually")
def test_labelbox_image():
    # Image dataset
    _dataset = foz.load_zoo_dataset(
        "bdd100k", split="validation", shuffle=True, max_samples=10
    )
    dataset = fo.Dataset()
    dataset.add_samples(_dataset.take(10))

    _test_labelbox_image(dataset)


@unittest.skip("Must be run manually")
def test_labelbox_video_objects():
    # Video dataset with objects
    dataset = foz.load_zoo_dataset("quickstart-video", max_samples=10)

    _test_labelbox_video(dataset)


@unittest.skip("Must be run manually")
def test_labelbox_video_events():
    # Video dataset with events
    dataset = fo.Dataset()

    events = [
        {"label": "sunny", "frames": [1, 10]},
        {"label": "cloudy", "frames": [11, 20]},
        {"label": "sunny", "frames": [21, 30]},
    ]

    sample = fo.Sample(filepath="/path/to/road.mp4")

    for event in events:
        label = event["label"]
        frames = event["frames"]
        for frame_number in range(frames[0], frames[1] + 1):
            sample.frames[frame_number]["weather"] = fo.Classification(
                label=label
            )

    dataset.add_sample(sample)

    _test_labelbox_video(dataset)


def _test_labelbox_image(dataset):
    labelbox_export_path = "/tmp/labelbox-image-export.json"
    labelbox_import_path = "/tmp/labelbox-image-import.json"
    labelbox_id_field = "labelbox_id"

    # Generate fake Labelbox IDs, since we haven't actually uploaded there
    for sample in dataset:
        sample[labelbox_id_field] = str(uuid4())
        sample.save()

    # Export labels in Labelbox format
    foul.export_to_labelbox(
        dataset,
        labelbox_export_path,
        labelbox_id_field=labelbox_id_field,
        label_prefix="",  # all fields
    )

    # Convert to Labelbox import format
    foul.convert_labelbox_export_to_import(
        labelbox_export_path, labelbox_import_path
    )

    # Import labels from Labelbox
    foul.import_from_labelbox(
        dataset,
        labelbox_import_path,
        label_prefix="lb",
        labelbox_id_field=labelbox_id_field,
    )

    # Verify that we have two copies of the same labels
    session = fo.launch_app(dataset)
    session.wait()


def _test_labelbox_video(dataset):
    labelbox_export_dir = "/tmp/labelbox-video-export"
    labelbox_export_path = "/tmp/labelbox-video-export.json"
    labelbox_import_dir = "/tmp/labelbox-video-import"
    labelbox_import_path = "/tmp/labelbox-video-import.json"
    labelbox_id_field = "labelbox_id"

    # Video objects dataset
    dataset = foz.load_zoo_dataset("quickstart-video", max_samples=10)

    # Generate fake Labelbox IDs, since we haven't actually uploaded there
    for sample in dataset:
        sample[labelbox_id_field] = str(uuid4())
        sample.save()

    # Export labels in Labelbox format
    foul.export_to_labelbox(
        dataset,
        labelbox_export_path,
        video_labels_dir=labelbox_export_dir,
        labelbox_id_field=labelbox_id_field,
        frame_labels_prefix="",  # all fields
    )

    # Convert to Labelbox import format
    foul.convert_labelbox_export_to_import(
        labelbox_export_path,
        outpath=labelbox_import_path,
        video_outdir=labelbox_import_dir,
    )

    # Import labels from Labelbox
    foul.import_from_labelbox(
        dataset,
        labelbox_import_path,
        label_prefix="lb",
        labelbox_id_field=labelbox_id_field,
    )

    # Verify that we have two copies of the same labels
    session = fo.launch_app(dataset)
    session.wait()


if __name__ == "__main__":
    fo.config.show_progress_bars = False
    unittest.main(verbosity=2)
