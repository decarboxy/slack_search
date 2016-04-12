#!/usr/bin/env python

import sys
import json
import re
from datetime import datetime
from search import db, Message
import os

def parse_user_file(user_file_path):
  user_name_map = {}
  with open(user_file_path) as input_file:
    user_data = json.load(input_file)

  for user_record in user_data:
    user_name_map[user_record['id']] = user_record['name']

  return user_name_map


def replace_labeled_usernames(message_text):
  labeled_match = re.search('<@[A-Za-z0-9]*\|([A-Za-z0-9]*)>', message_text)
  if labeled_match:
    return message_text.replace(labeled_match.group(0), labeled_match.group(1))
  else:
    return message_text


def lookup_usernames(message_text, user_name_map):
  user_ids = re.findall('<@[A-Za-z0-9]*>', message_text)
  for user_id in user_ids:
    user_id_match = re.search('<@([A-Za-z0-9]*)>', message_text)
    if user_id_match:
      username = user_name_map[user_id_match.group(1)]
      message_text = message_text.replace(user_id_match.group(0), '@'+username)
  return message_text


def lookup_channels(message_text, channel_name_map):
  user_ids = re.findall('<#[A-Za-z0-9]*>', message_text)
  for user_id in user_ids:
    user_id_match = re.search('<#([A-Za-z0-9]*)>', message_text)
    if user_id_match:
      channel = channel_name_map[user_id_match.group(1)]
      message_text = message_text.replace(user_id_match.group(0), '#'+channel)
  return message_text


def load_messages_from_file(message_file_path, user_name_map, channel_name_map, channel):
  with open(message_file_path) as input_file:
    message_data = json.load(input_file)

  for message in message_data:
    try:
      username = user_name_map[message['user']]
      message_text = message['text']
      timestamp = datetime.utcfromtimestamp(float(message['ts']))
    except KeyError:
      pass
    else:
      message_text = replace_labeled_usernames(message_text)
      message_text = lookup_usernames(message_text, user_name_map)
      message_text = lookup_channels(message_text, channel_name_map)
      #print username, message_text, timestamp, channel
      db.session.add(Message(username, message_text, timestamp, channel))
  db.session.commit()


def walk_directory(dirpath, user_name_map, channel_name_map):
  excluded = ['channels.json', 'integration_logs.json', 'users.json']
  for root, dirs, _ in os.walk(dirpath):
    for channel_dir in dirs:
      for channel_root, _, files in os.walk(os.path.join(root, channel_dir)):
        for file in files:
          if file not in excluded and '.json' in file:
            load_messages_from_file(os.path.join(channel_root, file), user_name_map, channel_name_map, channel_dir)


def main():
  if len(sys.argv) != 2:
    sys.exit('Usage: import_db_dump.py export_dir')
  input_dir = sys.argv[1]
  user_file_path = '{}/users.json'.format(input_dir)
  channel_file_path = '{}/channels.json'.format(input_dir)
  user_name_map = parse_user_file(user_file_path)
  channel_name_map = parse_user_file(channel_file_path)
  walk_directory(input_dir, user_name_map, channel_name_map)

if __name__ == '__main__':
  main()