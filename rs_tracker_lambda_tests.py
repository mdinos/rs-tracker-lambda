import rs_tracker_lambda
from unittest import TestCase
from mock import patch, MagicMock
from types import GeneratorType
import json
import requests
import os

class LambdaHandler(TestCase):

    def setUp(self):
        pass


class GetSkills(TestCase):

    def test_get_skills_function(self):
        self.assertEqual(rs_tracker_lambda.get_skills(), [
            'total', 'attack', 'defence', 'strength', 'hitpoints',
            'range', 'prayer', 'magic', 'cooking', 'woodcutting',
            'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
            'mining', 'herblore', 'agility', 'thieving', 'slayer',
            'farming', 'runecrafting', 'hunter', 'construction'])

class GetHiScores(TestCase):

    def test_get_raw_hs_data(self):
        data = rs_tracker_lambda.get_raw_hiscores_data('woofythedog')
        self.assertEqual(len(data), 35)
        self.assertEqual(type(data), list)

    def test_bad_username(self):
        data = rs_tracker_lambda.get_raw_hiscores_data('theoldnite')
        self.assertEqual(data, None)

    def test_invalid_username_with_non_alphanumeric_chars(self):
        with self.assertRaises(ValueError):
            rs_tracker_lambda.get_raw_hiscores_data('hello:there:')

    def test_invalid_username_with_escape_string(self):
        with self.assertRaises(ValueError):
            rs_tracker_lambda.get_raw_hiscores_data('\nhellothe')

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            rs_tracker_lambda.get_raw_hiscores_data('thisis13chars')
    
    def test_empty_username(self):
        with self.assertRaises(ValueError):
            rs_tracker_lambda.get_raw_hiscores_data('')
    
    def test_valid_length(self):
        data = rs_tracker_lambda.get_raw_hiscores_data('disis12chars')
        self.assertEqual(data, None)

    def test_length_check_with_hyphens(self):
        data = rs_tracker_lambda.get_raw_hiscores_data('woofy-dog_-')
        self.assertEqual(data, None)

    def test_lynx_titan(self):
        # Lynx Titan has maxed out stats, so these values won't ever change.
        data = rs_tracker_lambda.get_raw_hiscores_data('Lynx Titan')
        self.assertEqual(data[0:24], 
                            ['1,2277,4600000000', 
                                '15,99,200000000', 
                                '27,99,200000000', 
                                '18,99,200000000', 
                                '7,99,200000000', 
                                '7,99,200000000', 
                                '11,99,200000000', 
                                '32,99,200000000', 
                                '158,99,200000000', 
                                '15,99,200000000', 
                                '12,99,200000000', 
                                '9,99,200000000', 
                                '49,99,200000000', 
                                '4,99,200000000', 
                                '3,99,200000000', 
                                '25,99,200000000', 
                                '5,99,200000000', 
                                '24,99,200000000', 
                                '12,99,200000000', 
                                '2,99,200000000', 
                                '19,99,200000000', 
                                '7,99,200000000', 
                                '4,99,200000000', 
                                '4,99,200000000'])

class SkillsGenerator(TestCase):
    def setUp(self):
        self.skills = rs_tracker_lambda.get_skills()
        self.hiscores_data = rs_tracker_lambda.get_raw_hiscores_data('woofythedog')
        self.generator = rs_tracker_lambda.generate_dict_entries(self.hiscores_data, self.skills)
        self.counter = 0
    
    def _check_level_valid(self, level_string):
        if 1 <= int(level_string) <= 99:
            return True
        else:
            return False

    def test_generator_returned(self):
        self.assertEqual(type(self.generator), GeneratorType)

    def test_skills_generator_response(self):
        while True:
            try:
                print('Counter value: {}'.format(self.counter))
                result = next(self.generator)
                self.assertEqual(result['skill'], self.skills[self.counter])
                print(result['level'])
                if self.counter != 0:
                    self.assertEqual(self._check_level_valid(result['level']), True)
                self.counter += 1
            except StopIteration:
                break
        self.assertEqual(self.counter, 24)