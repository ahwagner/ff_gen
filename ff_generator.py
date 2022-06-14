import random
import csv
from collections import Counter
import argparse

__author__ = 'Alex H Wagner'


class Team:

    def __init__(self, manager, division):
        self.manager = manager
        self.division = division

    def __repr__(self):
        return '{0} ({1})'.format(self.manager, self.division)

    def __lt__(self, other):
        return self.manager < other.manager


class FantasyGenerator:

    def __init__(self, team_file, seed=None, season_length=14):
        with open(team_file) as f:
            reader = csv.DictReader(f, delimiter='\t')
            self.teams = [Team(x['Manager'], x['Team_Name']) for x in reader]
            self.teams.sort()
        self.seed = seed
        self.season_length = season_length
        self.match_counter = Counter()

    def draft_order(self):
        random.seed(self.seed)
        return random.sample(self.teams, len(self.teams))

    def schedule(self):
        random.seed(self.seed * 2)
        self.match_counter = Counter()
        schedule = list()
        if len(self.teams) % 2:
            rotation = random.sample(self.teams + [Team('BYE', 'Nobody')], len(self.teams) + 1)
        else:
            rotation = random.sample(self.teams, len(self.teams))
        for i in range(self.season_length):
            available = rotation.copy()
            week = list()
            while available:
                team_1 = available.pop(0)
                best_available = self.best_matches(team_1, available)
                n = len(best_available)
                team_2 = best_available.pop(i % n)
                available.remove(team_2)
                match = FantasyGenerator.match(team_1, team_2)
                week.append(match)
                self.match_counter[match] += 1
            schedule.append(week)
        return schedule

    def best_matches(self, team_1, available):
        best_value = 50
        best_available = []
        for team_2 in available:
            match = FantasyGenerator.match(team_1, team_2)
            match_count = self.match_counter[match]
            if match_count < best_value:
                best_value = match_count
                best_available = [team_2]
            elif match_count == best_value:
                best_available.append(team_2)
        return best_available

    @staticmethod
    def match(team_1, team_2):
        first, second = sorted((team_1, team_2))
        match = '{0} vs. {1}'.format(first, second)
        return match


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Fantasy Draft Order and Schedules')
    parser.add_argument('managers', type=str, help='A file with a tab-separated manager name and division on each line')
    parser.add_argument('seeds', type=str, help='A file with input expressions for seed generation')
    args = parser.parse_args()
    generate = FantasyGenerator(managers_file=args.managers, seeds_file=args.seeds)
    s = generate.schedule()
    print('---SCHEDULE---')
    for i, week in enumerate(s):
        print('Week {0}:'.format(i + 1))
        for match in week:
            print('\t{0}'.format(match))
    print('---DRAFT ORDER---')
    for team in generate.draft_order():
        print(team)
