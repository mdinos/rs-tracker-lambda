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

def lambda_handler(event=None, context=None):
    """
        Handle main functionality
        :param event: Event object from AWS events - does nothing in this script
        :param context: Context object from AWS events - ditto above
    """
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
    """
        :returns: An ordered list of skills, in the order that the RS API 
                  returns them.
    """
    skills = [
        'total', 'attack', 'defence', 'strength', 'hitpoints',
        'range', 'prayer', 'magic', 'cooking', 'woodcutting',
        'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
        'mining', 'herblore', 'agility', 'thieving', 'slayer',
        'farming', 'runecrafting', 'hunter', 'construction' ]
    log.debug('[\u2714] Returning skills')
    return skills

def check_username_validity(username: str):
    full_length = len(username)
    username = ''.join(letter for letter in username if letter not in [' ', '-', '_'])
    reduced_length = len(username)

    if username.isalnum() and 1 <= reduced_length<= 12 - (full_length - reduced_length):
        return True
    else:
        return False

def get_raw_hiscores_data(username: str):
    """ 
        Fetch hiscores data from RS hiscores site
        :param username: A (preferably valid) rs username

        :returns: User's raw statistics
        :rtype: list
    """
    if not check_username_validity(username):
        raise ValueError('Your username is invalid, it must be between 1 and 12 characters and \
                          contain only alphanumeric characters spaces, hypens or underscores')
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
    """
        Used as a unique identifier for the generated filename.
        :returns: The present date and time (UTC) as a string.
    """
    date = datetime.now(timezone.utc).astimezone().isoformat()[:19]
    log.debug('[\u2714] Date: ' + date)
    return date
    
def generate_dict_entries(stats_list: list, skills: list):
    """
        :param stats_list: a list of user's statistics, as recieved from get_raw_hiscores_data
        :param skills: A list of RS skills, ordered by get_skills

        :returns: A generator object containing dictionary entries of each
                  skill.
        :rtype: generator
    """
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

def get_filename(date: str, username: str):
    """
        :returns: A fully formed filename from components in the format username_date_stats.json
        :rtype: string
    """
    filename = username + '_' + date + '_stats.json'
    log.debug('[\u2714] Filename: ' + filename)
    return filename

def upload_to_s3(filename: str, stats_dict: dict, bucket='rs-tracker-lambda'):
    """
        :param filename: A fully formed filename generated from the get_filename() function
        :param stats_dict: A stats dictionary as generated in lambda_handler() function
        :param bucket: S3 bucket to which to upload the file to.
    """
    log.debug('[-] Attempting to connect to S3 bucket {}.'.format(bucket))
    client = boto3.client('s3')
    log.debug('[-] S3 Client established.')
    try:
        tmpfile = open('/tmp/' + filename, 'w')
        log.debug('[\u2714] Created file at /tmp/{}'.format(filename))
        tmpfile.write(json.dumps(stats_dict, indent=4))
        tmpfile.close()
        log.debug('[\u2714] Written to temporary file /tmp/{}'.format(filename))
        with open('/tmp/' + filename, 'rb') as file:
            client.upload_fileobj(file, bucket, username + '/' + filename)
        log.debug('[\u2714] Object successfilly uploaded to S3.')
        os.remove('/tmp/' + filename)
        log.debug('[\u2714] Temporary file deleted.')
    except Exception as e:
        log.error('[\u2718] An error occurred: {}'.format(e))
        raise e
