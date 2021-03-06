#!/usr/bin/python3

import codecs
import os
import pickle
import re
import sys
from tqdm import tqdm

TO_SPLIT = ["To", "X-To", "Cc", "X-cc", "Bcc", "X-bcc"]
TO_DELETE = ["Message-ID", "X-Folder", "X-FileName", "X-Origin"]

x_regex = re.compile(r'([^,\s].+?) <.+?>')

def clean_dict(data_dict):
    for delete_key in TO_DELETE:
        del data_dict[delete_key]

    for split_key in TO_SPLIT:
        if split_key in data_dict:
            if '<' in data_dict[split_key]:
                data_dict[split_key] = x_regex.findall(data_dict[split_key])
            else:
                data_dict[split_key] = data_dict[split_key].split(', ')
            data_dict[split_key] = [name.strip() for name in data_dict[split_key]]
    return data_dict

def main():
    if len(sys.argv) != 3:
        print('Usage: parse.py maildir megadir')
        exit(1)

    root = sys.argv[1]
    megadir = sys.argv[2]
    os.makedirs(megadir, exist_ok=True)

    head_body_regex = re.compile(r"^(.*?\r\n\r\n)(.*)", flags=re.S)
    key_val_regex = re.compile(r"(.+?): (.*?)\r\n(?![ \t])", flags=re.S)

    for dirname, _, files in tqdm(os.walk(root), total=3500):
        for filename in files:
            path = os.path.join(dirname, filename)
            try:
                with codecs.open(path, 'r', 'cp1252') as f:
                    string = f.read()

                head_body_match = head_body_regex.match(string)
                head_string = head_body_match.group(1)
                body_string = head_body_match.group(2).replace('\r', '')

                data_dict = dict(key_val_regex.findall(head_string))
                if not data_dict:
                    print(f"Error in {path}: couldn't parse metadata")

                data_dict['Body'] = body_string

                data_dict = clean_dict(data_dict)

                new_path = os.path.join(megadir, path.replace('/', '-'))
                with open(new_path, 'wb') as f:
                    pickle.dump(data_dict, f)
            except Exception as e:
                print(f'{type(e).__name__} in {path}: {str(e)}')


if __name__ == "__main__":
    main()
