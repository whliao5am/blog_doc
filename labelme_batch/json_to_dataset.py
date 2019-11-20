import os, argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="dir path of imamges")
args = parser.parse_args()

json_names = list(filter(lambda x: '.json' in x, os.listdir(args.path)))
os.chdir(args.path)
if not os.path.exists('../labels'):
    os.mkdir('../labels')

for n in json_names:
    os.system('labelme_json_to_dataset {} -o ../labels/{}'.format(n, os.path.splitext(n)[0]))

