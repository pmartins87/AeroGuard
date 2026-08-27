import numpy as np
import pytest

from aeroguard.detectors.yolox_opencv import (
    LetterboxMeta,
    YOLOXConfig,
    decode_yolox_output,
    letterbox_top_left,
    make_yolox_blob,
)


def test_top_left_letterbox_preserves_aspect_and_padding():
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    padded, meta = letterbox_top_left(image, input_width=640, input_height=640, pad_value=114)

    assert padded.shape == (640, 640, 3)
    assert meta.scale == pytest.approx(3.2)
    assert (meta.resized_width, meta.resized_height) == (640, 320)
    assert np.all(padded[:320] == 0)
    assert np.all(padded[320:] == 114)


def test_blob_contract_is_bgr_float32_without_normalization():
    image = np.zeros((10, 20, 3), dtype=np.uint8)
    image[:, :, 0] = 10  # B
    image[:, :, 1] = 20  # G
    image[:, :, 2] = 30  # R
    blob, _ = make_yolox_blob(image, YOLOXConfig(input_width=20, input_height=20))

    assert blob.shape == (1, 3, 20, 20)
    assert blob.dtype == np.float32
    assert blob[0, 0, 0, 0] == pytest.approx(10.0)
    assert blob[0, 1, 0, 0] == pytest.approx(20.0)
    assert blob[0, 2, 0, 0] == pytest.approx(30.0)


def test_decode_maps_boxes_back_and_performs_class_aware_nms():
    labels = ("Bolt", "Rock")
    meta = LetterboxMeta(
        original_width=200,
        original_height=100,
        input_width=640,
        input_height=640,
        resized_width=640,
        resized_height=320,
        scale=3.2,
    )
    # columns: cx cy w h objectness class0 class1
    output = np.array(
        [[[
            320.0, 160.0, 64.0, 64.0, 0.9, 0.9, 0.1
        ], [
            322.0, 162.0, 64.0, 64.0, 0.8, 0.9, 0.1
        ], [
            320.0, 160.0, 64.0, 64.0, 0.85, 0.1, 0.9
        ]]],
        dtype=np.float32,
    )

    detections = decode_yolox_output(
        output,
        labels,
        meta,
        image_id="frame-1",
        confidence_threshold=0.25,
        nms_threshold=0.45,
    )

    assert len(detections) == 2  # one Bolt after NMS + overlapping Rock retained
    bolt = next(box for box in detections if box.label == "Bolt")
    rock = next(box for box in detections if box.label == "Rock")
    assert bolt.score == pytest.approx(0.81)
    assert rock.score == pytest.approx(0.765)
    assert bolt.xmin == pytest.approx(90.0)
    assert bolt.ymin == pytest.approx(40.0)
    assert bolt.xmax == pytest.approx(110.0)
    assert bolt.ymax == pytest.approx(60.0)


def test_decode_accepts_transposed_output():
    labels = ("Bolt", "Rock")
    meta = LetterboxMeta(100, 100, 100, 100, 100, 100, 1.0)
    row = np.array([[50.0, 50.0, 20.0, 20.0, 1.0, 0.8, 0.2]], dtype=np.float32)
    output = row.T[None, :, :]

    detections = decode_yolox_output(
        output,
        labels,
        meta,
        image_id="x",
        confidence_threshold=0.5,
    )
    assert len(detections) == 1
    assert detections[0].label == "Bolt"


def test_low_confidence_and_invalid_width_are_ignored():
    labels = ("Bolt",)
    meta = LetterboxMeta(100, 100, 100, 100, 100, 100, 1.0)
    output = np.array(
        [[
            [50.0, 50.0, 20.0, 20.0, 0.2, 0.9],
            [50.0, 50.0, -1.0, 20.0, 1.0, 1.0],
        ]],
        dtype=np.float32,
    )
    assert decode_yolox_output(output, labels, meta, image_id="x", confidence_threshold=0.25) == []


def test_config_validation():
    with pytest.raises(ValueError, match="input dimensions"):
        YOLOXConfig(input_width=0).validate()
    with pytest.raises(ValueError, match="confidence_threshold"):
        YOLOXConfig(confidence_threshold=2.0).validate()
