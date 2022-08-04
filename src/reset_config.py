from paths import CONFIG_PATH, DEFAULT_CONFIG_PATH
import shutil


def reset_config() -> bool:
    try:
        shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    if reset_config():
        print(f"{CONFIG_PATH} reset")
