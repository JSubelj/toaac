import libs.transcode as transcode
import argparse
import libs.server

parser = argparse.ArgumentParser(description="Transcode DTS audio to AAC")
parser.add_argument("-s","--src",type=str, help="Source file to transform", default=None)
parser.add_argument("-d","--dst",type=str, help="Destination file (default: same as src with appended as in config.json)", default=None, required=False)
parser.add_argument("-w","--watch", action="store_true")

if __name__=="__main__":
    args = parser.parse_args()
    if args.watch:
        libs.server.watch()
    elif args.src:
        transcode.transcode(args.src,args.dst)
