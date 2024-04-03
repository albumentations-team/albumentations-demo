from pathlib import Path

import albumentations
import streamlit as st
from utils.constants import STATUS_CODE_LOAD_ERROR, STATUS_CODE_NO_IMAGE
from utils.helpers import (
    get_arguments,
    get_placeholder_params,
    load_augmentations_configs_from_folder,
    render_ga_code,
    select_transformations,
    show_random_params,
)
from visuals import get_transformations_params, select_image, show_docstring

st.set_page_config(
    page_title="Albumentations Demo",
    page_icon="docs/albumentations_logo.png",
    menu_items={
        "Get help": None,
        "Report a bug": "https://github.com/albumentations-team/albumentations-demo/issues/new",
        "About": "- Main page: [albumentations.ai](https://albumentations.ai) \n"
        "- Documentation: [albumentations.ai/docs](https://albumentations.ai/docs) \n"
        "- Github: [github.com/albumentations](https://github.com/albumentations-team/albumentations)",
    },
)


def main() -> None:
    # get CLI params: the path to images and image width
    path_to_images, width_original, ga_tracking_id = get_arguments()

    if not Path(path_to_images).is_dir():
        st.title("There is no directory: " + path_to_images)
    else:
        # select interface type
        interface_type = st.sidebar.radio(
            "Select the interface mode",
            ["Simple", "Professional"],
        )

        # select image
        status, image = select_image(path_to_images, interface_type)
        if status == STATUS_CODE_LOAD_ERROR:
            st.title("Can't load image")
        if status == STATUS_CODE_NO_IMAGE:
            st.title("Please, upload the image")
        else:
            # image was loaded successfully
            placeholder_params = get_placeholder_params(image)

            # load the config
            augmentations = load_augmentations_configs_from_folder(
                placeholder_params,
                "configs",
            )

            # get the list of transformations names
            transform_names = select_transformations(augmentations, interface_type)

            # get parameters for each transform
            transforms = get_transformations_params(transform_names, augmentations)

            try:
                # apply the transformation to the image
                data = albumentations.ReplayCompose(transforms)(image=image)
                error = 0
            except ValueError:
                error = 1
                st.title(
                    "The error has occurred. Most probably you have passed wrong set of parameters. \
                Check transforms that change the shape of image.",
                )

            # proceed only if everything is ok
            if error == 0:
                augmented_image = data["image"]
                # show title
                st.markdown("# [Demo of Albumentations](https://albumentations.ai/)")

                # show the images
                width_transformed = int(
                    width_original / image.shape[1] * augmented_image.shape[1],
                )

                st.image(image, caption="Original image", width=width_original)
                st.image(
                    augmented_image,
                    caption="Transformed image",
                    width=width_transformed,
                )

                # comment about refreshing
                st.write("*Press 'R' to refresh*")

                # random values used to get transformations
                show_random_params(data, interface_type)

                # print additional info
                for transform in transforms:
                    show_docstring(transform)
                    st.code(str(transform))
    render_ga_code(ga_tracking_id)


if __name__ == "__main__":
    main()
