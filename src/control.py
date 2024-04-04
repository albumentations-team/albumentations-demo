import streamlit as st
from streamlit.elements.widgets.slider import SliderReturn


def select_num_interval(
    param_name: str,
    limits_list: list[list[int]],
    defaults: list[int],
    n_for_hash: int,
    step: float | None = None,
    **_: int,
) -> SliderReturn:
    return st.sidebar.slider(
        param_name,
        limits_list[0],
        limits_list[1],
        defaults,
        step=step,
        key=hash(param_name + str(n_for_hash)),
    )


def select_several_nums(
    param_name: str,
    subparam_names: list[str],
    limits_list: list[list[int]],
    defaults_list: list[int],
    n_for_hash: int,
    **_: int,
) -> tuple[SliderReturn]:
    st.sidebar.subheader(param_name)
    result = []

    for name, limits, defaults in zip(
        subparam_names,
        limits_list,
        defaults_list,
        strict=False,
    ):
        result.append(
            st.sidebar.slider(
                name,
                limits[0],
                limits[1],
                defaults,
                key=hash(param_name + name + str(n_for_hash)),
            ),
        )
    return tuple(result)


def select_min_max(
    param_name: str,
    limits_list: list[list[int]],
    defaults_list: list[int],
    n_for_hash: int,
    min_diff: int = 0,
    **_: int,
) -> tuple[SliderReturn]:
    result = list(
        select_num_interval(
            " & ".join(param_name),
            limits_list,
            defaults_list,
            n_for_hash,
        ),
    )
    if result[1] - result[0] < min_diff:
        diff = min_diff - result[1] + result[0]
        if result[1] + diff <= limits_list[1]:
            result[1] = result[1] + diff
        elif result[0] - diff >= limits_list[0]:
            result[0] = result[0] - diff
        else:
            result = limits_list
    return tuple(result)


def select_rgb(param_name: str, n_for_hash: int, **_: int) -> tuple[SliderReturn]:
    result = select_several_nums(
        param_name,
        subparam_names=["Red", "Green", "Blue"],
        limits_list=[[0, 255], [0, 255], [0, 255]],
        defaults_list=[0, 0, 0],
        n_for_hash=n_for_hash,
    )
    return tuple(result)


def replace_none(string: str) -> str | None:
    if string == "None":
        return None
    return string


def select_radio(param_name: str, options_list: list[int], n_for_hash: int, **_: int) -> str | None:
    st.sidebar.subheader(param_name)
    result = st.sidebar.radio("", options_list, key=hash(param_name + str(n_for_hash)))
    return replace_none(result)


def select_checkbox(param_name: str, defaults: list[int], n_for_hash: int, **_: int) -> bool:
    st.sidebar.subheader(param_name)
    return st.sidebar.checkbox("True", defaults, key=hash(param_name + str(n_for_hash)))


# dict from param name to function showing this param
param2func = {
    "num_interval": select_num_interval,
    "several_nums": select_several_nums,
    "radio": select_radio,
    "rgb": select_rgb,
    "checkbox": select_checkbox,
    "min_max": select_min_max,
}
