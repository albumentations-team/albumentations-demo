import albumentations
import cv2
import numpy as np
import streamlit as st
from control import param2func
from utils.constants import STATUS_CODE_LOAD_ERROR, STATUS_CODE_NO_IMAGE, STATUS_CODE_OK
from utils.helpers import get_images_list, load_image, upload_image


def select_image(path_to_images: str, interface_type: str = "Simple") -> tuple[int, int | np.ndarray]:
    """Show interface to choose the image, and load it
    Args:
        path_to_images: path to folder with images
        interface_type: mode to the interface used
    Returns:
        (status, image)
        status (int):
            0 - if everything is ok
            1 - if there is error during loading of image file
            2 - if user hasn't uploaded photo yet
    """
    image_names_list = get_images_list(path_to_images)
    if len(image_names_list) < 1:
        return STATUS_CODE_LOAD_ERROR, 0

    if interface_type == "Professional":
        image_names_list += ["Upload my image"]
        image_name = st.sidebar.selectbox(
            "Select an image:",
            image_names_list,
        )
    else:
        image_name = st.sidebar.selectbox("Select an image:", image_names_list)

    if image_name != "Upload my image":
        try:
            image = load_image(image_name, path_to_images)
            return STATUS_CODE_OK, image  # noqa: TRY300
        except cv2.error:
            return STATUS_CODE_LOAD_ERROR, 0
    else:
        try:
            image = upload_image()
            return STATUS_CODE_OK, image  # noqa: TRY300
        except cv2.error:
            return STATUS_CODE_LOAD_ERROR, 0
        except AttributeError:
            return STATUS_CODE_NO_IMAGE, 0


def show_transform_control(
    transform_params: list[dict[str, list[int] | str | int]],
    n_for_hash: int,
) -> dict[str | int, float | tuple[int]]:
    param_values: dict[str | int, float | tuple[int]] = {"p": 1.0}
    if len(transform_params) == 0:
        st.sidebar.text("Transform has no parameters")
    else:
        for param in transform_params:
            control_function = param2func[param["type"]]
            if isinstance(param["param_name"], list):
                returned_values = control_function(**param, n_for_hash=n_for_hash)
                for name, value in zip(
                    param["param_name"],
                    returned_values,
                    strict=False,
                ):
                    param_values[name] = value
            else:
                param_values[param["param_name"]] = control_function(
                    **param,
                    n_for_hash=n_for_hash,
                )
    return param_values


def get_transformations_params(
    transform_names: list[str],
    augmentations: dict[str, list[dict[str, list[int] | str | int]]],
) -> list[albumentations.augmentations.transforms]:
    transforms = []
    for i, transform_name in enumerate(transform_names):
        # select the params values
        st.sidebar.subheader("Params of the " + transform_name)
        param_values = show_transform_control(augmentations[transform_name], i)
        transforms.append(getattr(albumentations, transform_name)(**param_values))
    return transforms


def show_docstring(obj_with_ds: albumentations.augmentations.transforms) -> None:
    st.markdown("* * *")
    st.subheader("Docstring for " + obj_with_ds.__class__.__name__)
    st.text(obj_with_ds.__doc__)
