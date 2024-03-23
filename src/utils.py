import argparse
import os
from pathlib import Path
from string import Template

import cv2
import numpy as np
import streamlit as st
from streamlit.components.v1 import html
import yaml


@st.cache_data
def get_arguments():
    """Return the values of CLI params"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_folder", default="images")
    parser.add_argument("--image_width", default=400, type=int)
    parser.add_argument("--ga_tracking_id", default="UA-158065353-1")

    args = parser.parse_args()
    return args.image_folder, args.image_width, args.ga_tracking_id


@st.cache_data
def get_images_list(path_to_folder: str) -> list:
    """Return the list of images from folder
    Args:
        path_to_folder (str): absolute or relative path to the folder with images
    """
    image_names_list = [x for x in os.listdir(path_to_folder) if x[-3:] in ["jpg", "peg", "png"]]
    return image_names_list


@st.cache_data
def load_image(image_name: str, path_to_folder: str, bgr2rgb: bool = True) -> np.ndarray:
    """Load the image
    Args:
        image_name (str): name of the image
        path_to_folder (str): path to the folder with image
        bgr2rgb (bool): converts BGR image to RGB if True
        read_mode (int): OpenCV read image format. Default: IMREAD_COLOR
    """
    path_to_image = os.path.join(path_to_folder, image_name)
    image = cv2.imread(path_to_image)
    if bgr2rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def upload_image(bgr2rgb: bool = True) -> np.ndarray:
    """Uoload the image
    Args:
        bgr2rgb (bool): converts BGR image to RGB if True
    """
    file = st.sidebar.file_uploader("Upload your image (jpg, jpeg, or png)", ["jpg", "jpeg", "png"])
    image = cv2.imdecode(np.fromstring(file.read(), np.uint8), 1)  # type: ignore
    if bgr2rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


@st.cache_data
def load_augmentations_config(placeholder_params: dict, path_to_config: str = "configs/augmentations.yml") -> dict:
    """Load the yaml config with params of all transforms
    Args:
        placeholder_params (dict): dict with values of placeholders
        path_to_config (str): path to the yaml config file
    """
    with open(path_to_config) as config_file:
        augmentations = yaml.safe_load(config_file)
    for _, params in augmentations.items():
        [fill_placeholders(param, placeholder_params) for param in params]
    return augmentations


@st.cache_data
def load_augmentations_configs_from_folder(placeholder_params: dict, directory: str = "configs") -> dict:
    """Load the yaml config with params of all transforms
    Args:
        placeholder_params (dict): dict with values of placeholders
        directory (str): path to the directory with yaml config files
    """
    result = {}
    for path in Path(directory).rglob("*.yml"):
        result.update(load_augmentations_config(placeholder_params, str(path)))
    return result


def fill_placeholders(params: dict, placeholder_params: dict) -> dict:
    """Fill the placeholder values in the config file
    Args:
        params (dict): original params dict with placeholders
        placeholder_params (dict): dict with values of placeholders
    """
    if "placeholder" in params:
        placeholder_dict = params["placeholder"]
        for k, v in placeholder_dict.items():
            if isinstance(v, list):
                params[k] = []
                for element in v:
                    if element in placeholder_params:
                        params[k].append(placeholder_params[element])
                    else:
                        params[k].append(element)
            else:
                if v in placeholder_params:
                    params[k] = placeholder_params[v]
                else:
                    params[k] = v
        params.pop("placeholder")
    return params


def get_params_string(param_values: dict) -> str:
    """Generate the string from the dict with parameters
    Args:
        param_values (dict): dict of "param_name" -> "param_value"
    """
    params_string = ", ".join([k + "=" + str(param_values[k]) for k in param_values.keys()])
    return params_string


def get_placeholder_params(image):
    return {
        "image_width": image.shape[1],
        "image_height": image.shape[0],
        "image_half_width": int(image.shape[1] / 2),
        "image_half_height": int(image.shape[0] / 2),
    }


def select_transformations(augmentations: dict, interface_type: str) -> list:
    # in the Simple mode you can choose only one transform
    if interface_type == "Simple":
        return [st.sidebar.selectbox("Select a transformation:", sorted(list(augmentations.keys())))]
    # in the professional mode you can choose several transforms
    # interface_type == "Professional":
    transform_names = [st.sidebar.selectbox("Select transformation №1:", sorted(list(augmentations.keys())))]
    while transform_names[-1] != "None":
        transform_names.append(
            st.sidebar.selectbox(
                f"Select transformation №{len(transform_names) + 1}:",
                ["None"] + sorted(list(augmentations.keys())),
            )
        )
    return transform_names[:-1]


def show_random_params(data: dict, interface_type: str = "Professional") -> None:
    """Shows random params used for transformation (from A.ReplayCompose)"""
    if interface_type == "Professional":
        st.subheader("Random params used")
        random_values = {}
        for applied_params in data["replay"]["transforms"]:
            random_values[applied_params["__class_fullname__"].split(".")[-1]] = applied_params["params"]
        st.write(random_values)


def render_ga_code(tracking_id):
    GA_CODE = Template(
        """
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=$tracking_id"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '$tracking_id');
        </script>
        """
    )
    return html(GA_CODE.substitute(tracking_id=tracking_id), height=0, width=0)
