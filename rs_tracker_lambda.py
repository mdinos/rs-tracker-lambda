import boto3
import requests
import os
from datetime import datetime, timezone
import pprint
import json
import logging

log = logging.getLogger('rs_tracker_lambda')
log.setLevel(logging.DEBUG)

username = os.environ['username']

def lambda_handler(event, context):
    stats_list = get_raw_highscores_data(username)
    log.debug('got data')
    date = get_date()
    stats_dict = {
        'date': date,
        'stats': []
    }
    skills = get_skills()

    dict_entries = generate_dict_entries(stats_list, skills)
    while True:
        try:
            entry = next(dict_entries)
            stats_dict['stats'].append(entry)
        except:
            break

    filename = get_filename(date, username)

    log.debug('about to connect to s3')
    client = boto3.client('s3')
    log.debug('connected to s3')
    tmpfile = open('/tmp/' + filename, 'w')
    tmpfile.write(json.dumps(stats_dict, indent=4))
    tmpfile.close()
    log.debug('written to file')
    with open('/tmp/' + filename, 'rb') as file:
        client.upload_fileobj(file, 'rs-tracker-lambda', username + '/' + filename)

    log.debug('written file to s3')

def get_skills():
    skills = [
        'total', 'attack', 'defence', 'strength', 'hitpoints',
        'range', 'prayer', 'magic', 'cooking', 'woodcutting',
        'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
        'mining', 'herblore', 'agility', 'thieving', 'slayer',
        'farming', 'runecrafting', 'hunter', 'construction' ]
    log.debug('got skills')
    return skills

def get_raw_highscores_data(username):
    log.debug('start get_raw_highscores_data ' + username)
    rs = requests.Session()
    stats = rs.get('https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=' + username)
    log.debug('stats got')
    stats_list = stats.text.split('\n')
    log.debug(stats_list)

    return stats_list

def get_date():
    date = datetime.now(timezone.utc).astimezone().isoformat()[:20]
    log.debug('date: ' + date)
    return date
    
def generate_dict_entries(stats_list, skills):
    for i, skill in enumerate(skills):
        skill_split = stats_list[i].split(',')
        for i, entry in enumerate(skill_split):
            skill_split[i] = int(entry)

        dict_entry = {
            'rank': skill_split[0],
            'level': skill_split[1],
            'experience': skill_split[2],
            'skill': skill
        }

        yield dict_entry

def get_filename(date, username):
    filename = username + '_' + date + '_stats.json'
    log.debug('filename: ' + filename)
    return filename

lambda_handler('event', 'context')