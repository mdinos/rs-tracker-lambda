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
bucket = os.environ['bucket']

def lambda_handler(event, context):
    stats_list = get_raw_hiscores_data(username)
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
        except StopIteration:
            break

    filename = get_filename(date, username)
    upload_to_s3(filename, stats_dict, bucket)

def get_skills():
    skills = [
        'total', 'attack', 'defence', 'strength', 'hitpoints',
        'range', 'prayer', 'magic', 'cooking', 'woodcutting',
        'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
        'mining', 'herblore', 'agility', 'thieving', 'slayer',
        'farming', 'runecrafting', 'hunter', 'construction' ]
    log.debug('[\u2714] Returning skills')
    return skills

def get_raw_hiscores_data(username):
    log.debug('[-] Attempting to get {}\'s statistics.'.format(username))
    stats = requests.get('https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=' + username)
    if stats.status_code != 200:
        log.debug('[\u2718] Response from RS status code [{}]'.format(stats.status_code))
        return None
    log.debug('[\u2714] Sucessfully recieved stats')
    stats_list = stats.text.split('\n')
    log.debug(stats_list)
    return stats_list

def get_date():
    date = datetime.now(timezone.utc).astimezone().isoformat()[:19]
    log.debug('[\u2714] Date: ' + date)
    return date
    
def generate_dict_entries(stats_list, skills):
    for i, skill in enumerate(skills):
        skill_split = stats_list[i].split(',')
        log.debug('[\u2714] Extrapolated stats to list ' + skill)
        for i, entry in enumerate(skill_split):
            skill_split[i] = int(entry)

        dict_entry = dict(
            skill = skill,
            rank = skill_split[0],
            level = skill_split[1],
            experience = skill_split[2]
        )
        log.debug('[\u2714] Successfully generated {} dictionary.'.format(skill))

        yield dict_entry

def get_filename(date, username):
    filename = username + '_' + date + '_stats.json'
    log.debug('[\u2714] Filename: ' + filename)
    return filename

def upload_to_s3(filename, stats_dict, bucket='rs-tracker-lambda'):
    log.debug('[-] Attempting to connect to S3 bucket {}.'.format(bucket))
    client = boto3.client('s3')
    log.debug('[-] S3 Client established.')
    try:
        tmpfile = open('/tmp/' + filename, 'w')
        log.debug('[\u2714] Created file at /tmp/{}'.format(filename))
        tmpfile.write(json.dumps(stats_dict, indent=4))
        log.debug('[\u2714] Written to temporary file /tmp/{}'.format(filename))
        tmpfile.close()
        with open('/tmp/' + filename, 'rb') as file:
            client.upload_fileobj(file, bucket, username + '/' + filename)
        log.debug('[\u2714] Object successfilly uploaded to S3.')
        os.remove('/tmp/' + filename)
        log.debug('[\u2714] Temporary file deleted.')
    except Exception as e:
        log.error('[\u2718] An error occurred: {}'.format(e))
        raise e
