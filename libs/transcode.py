import subprocess
import os
import libs.settings as settings
from pymediainfo import MediaInfo
import time
import datetime

def _get_path_names(ifile, ofile, config):
    assert ifile.endswith(".mkv")





    if ofile == None:
        name = os.path.basename(ifile)
        name_a = name.split(".")
        name_a.insert(-1, config.name_addition)
        tmp = []
        for p in name_a:
            if p.lower() != "dts":
                tmp.append(p)


        name = ".".join(tmp)
        if config.target_dir == None:
            path = os.path.dirname(os.path.abspath(ifile))
        else:
            path = os.path.abspath(config.target_dir)




        ofile = os.path.join(path, name)

    else:
        ofile = os.path.abspath(ofile)
    return ifile, ofile


def transcode(ifile: str, ofile: str = None):
    config = settings.get_settings()

    ifile, ofile = _get_path_names(ifile, ofile, config)

    frame_count = -1
    for i in range(0,5):
        try:
            mi = MediaInfo.parse(ifile)

            for track in mi.tracks:
                if track.track_type == "Video":
                    frame_count = track.frame_count
                    break
        except Exception as e:
            time.sleep(1)


    args = [
        config.ffmpeg_exe, "-y",
        "-i", ifile,
        "-map", "0",
        "-c:v", "copy",
        "-c:s", "copy",
        "-c:a", "aac",
        "-b:a", "384k",
        "-progress", "-",
        ofile]
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as p:
        while True:
            line = p.stdout.readline()
            if len(line) == 0:
                break
            l = line.decode("utf-8")
            if l.startswith("frame"):
                current_frame = int(l.split("=")[1])
                string = ["["]
                perc_done = 100*current_frame/int(frame_count)
                for i in range(100):
                    if i < perc_done:
                        string.append("#")
                    else:
                        string.append(" ")
                string.append("]")
                print(str(datetime.datetime.now()),"Converting", os.path.basename(ifile),"".join(string), perc_done, "%")



        # for l in p.stderr.readline():
        #
        #     print("tvoja mtka, ",l)
        # if l.startswith("progress"):
        #     if "end" == l.split("=")[1]:
        #         print("100%")

    p.wait()
    print()

    return ofile


if __name__ == "__main__":
    transcode("..\\test.dts.mkv", "test2.mkv")
