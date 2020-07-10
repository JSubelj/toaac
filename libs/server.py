import json
import time
import os
import libs.settings as settings
import libs.transcode as ffmpeg
from pymediainfo import MediaInfo
import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from multiprocessing import Process, Lock

def write_log():
    json.dump(log, open("log.json", "w"), sort_keys=True, indent=4)

log = {}
try:
    log = json.load(open("log.json","r"))
except:
    write_log()

def is_correct_name(file):
    if not file.endswith(".mkv"):
        print("dosen't end in mkv")
        return False
    return True
def check_if_all_tracks_unsupported(file):
    info = MediaInfo.parse(file)
    # check if ac3 or aac in maybe it will play and don't need transcode
    # check if TrueHD audio needs transcoding
    audio_tracks = []
    for track in info.tracks:
        if track.track_type == 'Audio':
            audio_tracks.append(track.format)

    # TODO: add to config
    FORBIDDEN_AUDIO_TRACKS = ["DTS"]
    ALLOWED_AUDIO_TRACKS = ["AAC", "AC-3"]

    for at in audio_tracks:
        if at in ALLOWED_AUDIO_TRACKS:
            print(os.path.basename(file),"Has allowed track")
            log_end(file,file)
            return False

    remaining = [x for x in audio_tracks if x not in FORBIDDEN_AUDIO_TRACKS]
    if len(remaining) > 0:
        log_maybe_will_work(file, audio_tracks)
        return False

    return True



def log_maybe_will_work(full_path, audio_tracks):
    log[os.path.basename(full_path)] = {
        "1. status": "maybe",
        "2. start": str(datetime.datetime.now()),
        "3. source": full_path,
        "6. audio tracks": audio_tracks
    }
    write_log()

def log_beginning(full_path):
    log[os.path.basename(full_path)] = {
        "1. status": "running",
        "2. start": str(datetime.datetime.now()),
        "3. source": full_path
    }
    write_log()

def log_started_watching(full_path):
    log[os.path.basename(full_path)] = {
        "1. status": "running",
        "1.1 started_watching":str(datetime.datetime.now()),
        "3. source": full_path
    }
    write_log()

def log_end(full_path, dst):
    l = log[os.path.basename(full_path)]
    l["1. status"]="done"
    l["4. end"] = str(datetime.datetime.now())
    l["5. destination"] = dst
    write_log()



def watcher(file):
    old_time_modified = os.stat(file).st_mtime
    while True:
        time.sleep(10)
        try:
            new_time_modified = os.stat(file).st_mtime
            if old_time_modified == new_time_modified:
                # check
                # start process
                print(os.path.basename(file), "didn't change in 10s")
                if check_if_all_tracks_unsupported(file):
                    log_beginning(file)
                    dst = ffmpeg.transcode(file)
                    log_end(file, dst)
                return
            old_time_modified = new_time_modified
        except:
            return

def create_watcher_process(file):
    print("Started WATCHING",os.path.join(os.path.dirname(os.path.realpath(file)),os.path.basename(file)))
    log_started_watching(file)
    p = Process(target=watcher, args=(file,))
    p.start()
    return p



class _Handler(FileSystemEventHandler):
    watchers ={}
    @staticmethod
    def on_any_event(event):


        keys_to_delete = []
        for key, watcher in _Handler.watchers.items():
            if not watcher.is_alive():
                print("Removed watcher for ",os.path.basename(key))
                watcher.join()
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del _Handler.watchers[key]

        if event.is_directory:
            return None

        elif event.event_type != 'deleted':
            path = event.src_path if event.event_type != "moved" else event.dest_path
            print(event.event_type, os.path.basename(path))
            if is_correct_name(path):
                if path not in _Handler.watchers.keys():
                    _Handler.watchers[path] = create_watcher_process(path)







def watch():
    config = settings.get_settings()
    observer = Observer()
    event_handler = _Handler()

    observer.schedule(event_handler,os.path.abspath(config.watch_dir),recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except:
        observer.stop()
    observer.join()


if __name__=="__main__":
    watch()