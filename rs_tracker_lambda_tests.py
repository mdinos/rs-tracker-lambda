import rs_tracker_lambda
from unittest import TestCase
from mock import patch, MagicMock
from types import GeneratorType
import json
import requests
import os

class GetSkills(TestCase):

    def test_get_skills_function(self):
        self.assertEqual(rs_tracker_lambda.get_skills(), [
            'total', 'attack', 'defence', 'strength', 'hitpoints',
            'range', 'prayer', 'magic', 'cooking', 'woodcutting',
            'fletching', 'fishing', 'firemaking', 'crafting', 'smithing',
            'mining', 'herblore', 'agility', 'thieving', 'slayer',
            'farming', 'runecrafting', 'hunter', 'construction']
                         )

class GetHiScores(TestCase):
    def setUp(self):
        self.username = 'woofythedog'

    def test_get_raw_hs_data(self):
        data = rs_tracker_lambda.get_raw_hiscores_data(self.username)
        self.assertEqual(len(data), 35)
        self.assertEqual(type(data), list)

class SkillsGenerator(TestCase):
    def setUp(self):
        self.skills = rs_tracker_lambda.get_skills()
        self.hiscores_data = rs_tracker_lambda.get_raw_hiscores_data('woofythedog')
        self.generator = rs_tracker_lambda.generate_dict_entries(self.hiscores_data, self.skills)
        self.counter = 0
    
    def check_level_valid(self, level_string):
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
                    self.assertEqual(self.check_level_valid(result['level']), True)
                self.counter += 1
            except StopIteration:
                break
        self.assertEqual(self.counter, 24)