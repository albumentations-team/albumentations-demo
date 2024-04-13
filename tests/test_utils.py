# test

import albumentations as A
import numpy as np

from src.utils.helpers import get_images_list, load_augmentations_configs_from_folder, load_image


def test_get_images_list():
    images_list = get_images_list("images")
    assert isinstance(images_list, list)
    assert len(images_list) > 0
    assert isinstance(images_list[0], str)


def test_load_image():
    images_list = get_images_list("images")
    for image_name in images_list:
        image = load_image(image_name, path_to_folder="images", bgr2rgb=True)
        assert len(image.shape) == 3, f"error in {image_name}"
        assert image.shape[2] == 3, f"error in {image_name}"
        assert image.max() <= 255, f"error in {image_name}"
        assert image.min() >= 0, f"error in {image_name}"


def test_load_augmentations_config():
    rng = np.random.default_rng(seed=42)
    image = rng.integers(low=0, high=255, size=(100, 100, 3)).astype(np.uint8)
    placeholder_params = {
        "image_width": image.shape[1],
        "image_height": image.shape[0],
        "image_half_width": int(image.shape[1] / 2),
        "image_half_height": int(image.shape[0] / 2),
    }
    augmentations = load_augmentations_configs_from_folder(placeholder_params, directory="configs")

    for transform_name in augmentations.keys():
        param_values = dict(p=1.0)
        size = (10, 10)

        match transform_name:
            case "CenterCrop" | "RandomCrop" | "Resize":
                param_values.update(height=10, width=10)
            case "CropAndPad":
                param_values.update(px=10)
            case "RandomResizedCrop":
                param_values.update(size=size)
            case "RandomSizedCrop":
                param_values.update(size=size, min_max_height=(50, 50))
            case "Crop":
                param_values.update(x_max=10, y_max=10)
            case _:
                ...

        transform = getattr(A, transform_name)(**param_values)
        transformed_image = transform(image=image)["image"]

        assert_msg = f"error in {str(transform)}"
        assert len(transformed_image.shape) == 3, assert_msg
        assert transformed_image.shape[2] == 3, assert_msg
        assert transformed_image.max() <= 255, assert_msg
        assert transformed_image.min() >= 0, assert_msg
