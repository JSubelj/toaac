import json

from dataclasses import dataclass


@dataclass
class Config:
    ffmpeg_exe: str = "ffmpeg-20200628-4cfcfb3-win64-static\\bin\\ffmpeg.exe"
    watch_dir: str = "test_dir"
    name_addition: str = "AAC.encode"
    remove_old: bool = False
    target_dir: str = None  # same as source

    def to_dict(self):
        return {
            "ffmpeg_exe": self.ffmpeg_exe,
            "watch_dir": self.watch_dir,
            "name_addition": self.name_addition,
            "remove_old": self.remove_old,
            "target_dir": self.target_dir
        }


def get_settings():
    config = Config()
    try:
        jsonconf = json.load(open("config.json", "r"))
        config = Config(
            ffmpeg_exe=jsonconf["ffmpeg_exe"],
            watch_dir=jsonconf["watch_dir"],
            name_addition=jsonconf["name_addition"],
            remove_old=jsonconf["remove_old"],
            target_dir=jsonconf["target_dir"]
        )
    except:
        json.dump(config.to_dict(), open("config.json", "w"), sort_keys=True, indent=4)

    return config
