import random
import csv
from collections import Counter
from itertools import cycle
import argparse

__author__ = 'Alex H Wagner'


class Team:

    def __init__(self, manager, institution):
        self.manager = manager
        self.institution = institution
        self.division = None

    def __repr__(self):
        return '{0}'.format(self.manager)

    def __lt__(self, other):
        return self.manager < other.manager


class FantasyGenerator:

    NCH = 'East'
    WUSTL = 'West'

    def __init__(self, managers_file_path, seed=None, season_length=14, weeks=14, assign_pis=False):
        with open(managers_file_path) as f:
            reader = csv.DictReader(f, delimiter=',')
            self.teams = [Team(x['Manager'], x['Institution']) for x in reader]
            self.teams.sort()
        random.seed(seed)
        self.assign_pis = assign_pis
        self.draft_order = None
        self.schedule = list()
        self.season_length = season_length
        self.match_counter = Counter()
        self.generate_divisions()
        self.generate_draft_order()
        self.generate_schedule(weeks)

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
        # Clears divisions, hard-code PIs to respective divisions if assign_pis == True
        pi_count = 0
        for team in self.teams:
            team.division = None
            if self.assign_pis and team.manager in ['Obi Griffith', 'Malachi Griffith']:
                team.division = self.WUSTL
                pi_count += 1
            if self.assign_pis and 'Alex Wagner' == team.manager:
                team.division = self.NCH
                pi_count += 1
        if self.assign_pis:
            assert pi_count == 3

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

    def _add_intradivisional(self, wustl, nch):
        assert len(wustl) == len(nch)
        l = len(wustl)
        wustl_cycle = cycle(wustl)
        nch_cycle = cycle(nch)

        for _ in range(l - 1):
            matchups = list()
            for __ in range(l // 2):
                matchups.append((next(wustl_cycle), next(wustl_cycle)))
                matchups.append((next(nch_cycle), next(nch_cycle)))
            if l % 2 == 1:
                matchups.append((next(wustl_cycle), next(nch_cycle)))
            next(wustl_cycle)
            next(nch_cycle)
            self.schedule.append(matchups)

    def _add_interdivisional(self, wustl, nch):
        assert len(wustl) == len(nch)
        l = len(wustl)
        wustl_cycle = cycle(wustl)
        nch_cycle = cycle(nch)
        for _ in range(l):
            matchups = list()
            for __ in range(l):
                matchups.append((next(wustl_cycle), next(nch_cycle)))
            next(wustl_cycle)
            self.schedule.append(matchups)

    def generate_schedule(self, weeks):
        # All teams should compete intra-divisional more than inter-divisonal
        # First, random sample teams
        divisions = {self.NCH: list(), self.WUSTL: list()}
        for team in self.teams:
            divisions[team.division].append(team)
        assert len(divisions) == 2  # assuming one each, NCH and WUSTL for now
        wustl_div = random.sample(divisions[self.WUSTL], len(divisions[self.WUSTL]))
        nch_div = random.sample(divisions[self.NCH], len(divisions[self.NCH]))
        assert len(wustl_div) == len(nch_div)  # if not this, need to add "BYE"
        while len(self.schedule) < weeks:
            if len(wustl_div) % 2 == 0:
                self._add_intradivisional(wustl_div, nch_div)
                self._add_interdivisional(wustl_div, nch_div)
            else:
                self._add_intradivisional(wustl_div, nch_div)
        self.schedule = self.schedule[:weeks]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Fantasy Draft Order and Schedules')
    parser.add_argument('managers', type=str, help='A file with a tab-separated manager name and division on each line')
    parser.add_argument('seed', type=int, help='A league-generated seed for reproducing the schedule and draft order')
    parser.add_argument('--assign_pis', action='store_true', help='If set, always assigns lab PIs to respective league divisions')
    args = parser.parse_args()
    fg = FantasyGenerator(managers_file_path=args.managers, seed=args.seed, assign_pis=args.assign_pis)
    print('---DIVISIONS---')
    for team in fg.teams:
        print('{}: {}'.format(team.manager, team.division))
    print('---SCHEDULE---')
    for i, week in enumerate(fg.schedule):
        print('Week {0}:'.format(i + 1))
        for match in week:
            print('\t{0}'.format(match))
    print('---PRE-DRAFT GAMES INITIAL ORDER---')
    for team in fg.draft_order:
        print(team)
