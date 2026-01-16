#! /usr/bin/env python3

# arguments handling #########################################################

import sys
import getopt
import textwrap


DEFAULTS = {
	"country":  '',
	"min_elo":  1000,
	"max_elo":  3000,
	"gender":   '',
	"min_year": 1900,
	"max_year": 2025,
}

def exit_usage(name, message=None, code=0):
	if message:
		sys.stderr.write("%s\n" % message)
	sys.stderr.write(textwrap.dedent("""\
	Usage: %(name)s [-hc:e:g:y:] <suffix>
		-h  --help             print this help message then exit
		-c  --country <XXX>    keep players from country <XXX> (defaults to %(country)s)
		-e  --elo [min]-[max]  keep players with highest ELO between <min> and <max> (defaults to %(min_elo)s-%(max_elo)s)
		-g  --gender [M|F]     keep players matching gender (defaults to %(gender)s)
		-y  --year [min]-[max] keep players with birthyear between <min> and <max> (defaults to %(min_year)s-%(max_year)s)
		<suffix>               use 'xxx-<suffix>.tsv' filenames for output
	""") % dict(name=name, **DEFAULTS))
	sys.exit(code)


prog_name, *args = sys.argv
try:
	options, args = getopt.getopt(args, "hc:e:g:y:",
	                              ["help", "country=", "elo=", "gender=", "year="])
except getopt.GetoptError as message:
	exit_usage(prog_name, message, 1)

try:
	suffix, = args
except:
	exit_usage(prog_name, "one argument is expected", 1)


country = DEFAULTS["country"]
min_elo = DEFAULTS["min_elo"]
max_elo = DEFAULTS["max_elo"]
gender =  DEFAULTS["gender"]
min_year = DEFAULTS["min_year"]
max_year = DEFAULTS["max_year"]

def parse_range(r, di, da):
	i, a = r.replace('+', '-').split('-')
	return int(i or di), int(a or da)

for opt, value in options:
	if opt in ["-h", "--help"]:
		exit_usage(prog_name)
	elif opt in ["-c", "--country"]:
		country = value
	elif opt in ["-e", "--elo"]:
		min_elo, max_elo = parse_range(value, min_elo, max_elo)
	elif opt in ["-g", "--gender"]:
		assert value in 'FM'
		gender = value
	elif opt in ["-y", "--year"]:
		min_year, max_year = parse_range(value, min_year, max_year)


# matching players ##########################################################

players_id = set()

players_i = open('players.tsv')
players_o = open('players-%s.tsv' % suffix, 'w')

headers = next(players_i)
assert headers == "#id	name	fed	sex	birthyear	max_rating	month\n"
print(headers, end='', file=players_o)

for line in players_i:
	pid, name, fed, sex, birthyear, max_rating, month = line.strip().split('\t')
	if country and fed != country:
		continue
	if not min_elo <= int(max_rating) <= max_elo:
		continue
	if gender and sex != gender:
		continue
	if not min_year <= int(birthyear) <= max_year:
		continue
	print(pid, name, fed, sex, birthyear, max_rating, month, sep='\t', file=players_o)
	players_id.add(pid)


# matching ratings

ratings_i = open('ratings.tsv')
ratings_o = open('ratings-%s.tsv' % suffix, 'w')

headers = next(ratings_i)
assert headers == "#id	month	rating	games\n"
print(headers, end='', file=ratings_o)

for line in ratings_i:
	pid, month, rating, games = line.strip().split('\t')
	if pid not in players_id:
		continue
	print(pid, month, rating, games, sep='\t', file=ratings_o)
	