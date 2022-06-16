import random
import csv
from collections import Counter
import argparse

__author__ = 'Alex H Wagner'


class Team:

    def __init__(self, manager, institution):
        self.manager = manager
        self.institution = institution
        self.division = None

    def __repr__(self):
        return '{0} ({1})'.format(self.manager, self.division)

    def __lt__(self, other):
        return self.manager < other.manager


class FantasyGenerator:

    NCH = 'East'
    WUSTL = 'West'

    def __init__(self, managers_file_path, seed=None, season_length=14):
        with open(managers_file_path) as f:
            reader = csv.DictReader(f, delimiter=',')
            self.teams = [Team(x['Manager'], x['Institution']) for x in reader]
            self.teams.sort()
        random.seed(seed)
        self.draft_order = None
        self.schedule = None
        self.season_length = season_length
        self.match_counter = Counter()
        self.generate_divisions()
        self.generate_draft_order()
        self.generate_schedule()

    def _assign_institution_to_division(self, institution, division):
        for team in self.teams:
            if team.institution == institution:
                team.division = division
        return

    def _balance_divisions(self, div1, div2):
        div_size = len(self.teams) / 2
        d = {
            None: [],
            div1: [],
            div2: []
        }
        for team in self.teams:
            d[team.division].append(team)
        div1_openings = div_size - len(d[div1])
        unassigned_teams = d[None]
        random.shuffle(unassigned_teams)
        for i, team in enumerate(unassigned_teams):
            if i < div1_openings:
                team.division = div1
            else:
                team.division = div2

    def _clear_divisions(self):
        for team in self.teams:
            team.division = None

    def generate_divisions(self):
        self._clear_divisions()
        c = Counter([x.institution for x in self.teams])
        assert sorted(c.keys()) == ['NCH', 'WUSTL']
        if c['NCH'] == c['WUSTL']:
            self._assign_institution_to_division('NCH', self.NCH)
            self._assign_institution_to_division('WUSTL', self.WUSTL)
        elif c['NCH'] < c['WUSTL']:
            self._assign_institution_to_division('NCH', self.NCH)
            self._balance_divisions(self.NCH, self.WUSTL)
        else:
            self._assign_institution_to_division('WUSTL', self.WUSTL)
            self._balance_divisions(self.NCH, self.WUSTL)


    def generate_draft_order(self):
        self.draft_order = random.sample(self.teams, len(self.teams))
        return

    def generate_schedule(self):
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
    parser.add_argument('seed', type=int, help='A league-generated seed for reproducing the schedule and draft order')
    args = parser.parse_args()
    fg = FantasyGenerator(managers_file_path=args.managers, seed=args.seed)
    print('---SCHEDULE---')
    for i, week in enumerate(fg.schedule):
        print('Week {0}:'.format(i + 1))
        for match in week:
            print('\t{0}'.format(match))
    print('---DRAFT ORDER---')
    for team in fg.draft_order:
        print(team)
