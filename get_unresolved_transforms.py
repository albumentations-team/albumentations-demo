import inspect
import albumentations

from src.utils import load_augmentations_configs_from_folder

IGNORED_CLASSES = {
    "BasicTransform",
    "BasicIAATransform",
    "DualIAATransform",
    "DualTransform",
    "ImageOnlyIAATransform",
    "ImageOnlyTransform",
}

if __name__ == "__main__":
    configs = load_augmentations_configs_from_folder({}, "configs")
    resolved_transforms = set(configs.keys())

    albu_transforms = set()
    for name, cls in inspect.getmembers(albumentations):
        if inspect.isclass(cls) and issubclass(cls, albumentations.BasicTransform) and name not in IGNORED_CLASSES:
            if "DeprecationWarning" in inspect.getsource(cls) or "FutureWarning" in inspect.getsource(cls):
                continue
            albu_transforms.add(name)

    for i, name in enumerate(albu_transforms - resolved_transforms):
        print(i, name)
