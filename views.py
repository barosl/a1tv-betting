# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from libs import naver_cafe
from django.conf import settings
from models import *
import re
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from libs import htmllib2
from django.core.urlresolvers import reverse

DEFAULT_SEASON = u'시즌 2'
DEFAULT_REWARD = 500

def index(req):
	seasons = []

	for season in Season.objects.all():
		season_reses = SeasonResult.objects.filter(season=season).order_by('-points')
		seasons.append([season.name, season_reses])

	return render_to_response('index.html', RequestContext(req, {
		'title': _(u'토토'),
		'seasons': seasons,
	}))

def update_matches(req):
	opener = naver_cafe.sign_in(settings.NAVER_USERNAME, settings.NAVER_PASSWORD)

	for article in naver_cafe.get_articles(opener):
		if article['type'] != 'poll': continue

		data = opener.open(article['url']).read().decode('utf-8', 'replace')
		poll_keys = re.findall(u'pollKey=([^&]+)', data)

		for poll_key in poll_keys:
			try: match = Match.objects.get(poll_key=poll_key)
			except Match.DoesNotExist:
				url = 'http://cafe.poll.naver.com/vote.nhn?pollKey=%s&serviceId=cafe' % poll_key
				data = opener.open(url).read().decode('utf-8', 'replace')
				name = re.search(u'<div class="wrap" style="width:490px;">([^<]*)', data).group(1)

				match = Match()
				match.name = name
				match.season = Season.objects.get(name=DEFAULT_SEASON)
				match.score = u''
				match.poll_key = poll_key
				match.reward = DEFAULT_REWARD
				match.save()

			url = 'http://cafe.poll.naver.com/voterDisplay.nhn?pollKey='+poll_key
			fp = opener.open(url)
			data = fp.read().decode('utf-8', 'replace')
			item_ids = re.findall(u'itemId=([0-9]+)', data)
			for item_id in item_ids:
				url = 'http://cafe.poll.naver.com/voterDisplay.nhn?pollKey=%s&itemId=%s&serviceId=' % (poll_key, item_id)
				data = opener.open(url).read().decode('utf-8', 'replace')

				name = htmllib2.unescape(re.search(u'<strong>([^<]+)', data).group(1))
				bettors = naver_cafe.get_bettors(opener, poll_key, item_id)
				mat = re.search(u'<\\s*([0-9]+)\\s*:\\s*([0-9]+)\\s*>', name)
				score = u'%s %s' % (mat.group(1), mat.group(2))

				try: bet = Bet.objects.get(match=match, score=score)
				except Bet.DoesNotExist:
					bet = Bet()
					bet.match = match
					bet.score = score
					bet.save()

				for name in bettors:
					try: bettor = Bettor.objects.get(name=name)
					except Bettor.DoesNotExist:
						bettor = Bettor()
						bettor.name = name
						bettor.save()

					try: bet.bettors.get(name=name)
					except Bettor.DoesNotExist: bet.bettors.add(bettor)

	return HttpResponse(_(u'경기 갱신 완료'))

def update_points(req):
	Bettor.objects.all().update(points=0)

	for season in Season.objects.all():
		bettor_points = {}
		bettor_objs = {}

		SeasonResult.objects.filter(season=season).delete()

		for match in Match.objects.filter(season=season):
			reward = match.reward

			try: bet = match.bet_set.get(score=match.score)
			except Bet.DoesNotExist: continue

			cnt = bet.bettors.count()
			for bettor in bet.bettors.all():
				name = bettor.name
				bettor_points[name] = bettor_points.get(name, 0) + float(reward)/cnt
				bettor_objs[name] = bettor

		res = bettor_points.items()
		res.sort(key=lambda x: x[1])

		for name, points in res:
			points = int(round(points))

			bettor = bettor_objs[name]
			bettor.points += points
			bettor.save()

			season_res = SeasonResult()
			season_res.season = season
			season_res.bettor = bettor
			season_res.points = points
			season_res.save()

	return HttpResponse(_(u'포인트 갱신 완료'))

def matches(req):
	if req.method == 'POST':
		if req.user.is_anonymous():
			return HttpResponseForbidden(_(u'권한이 없습니다.'))

		match_id = req.POST.get('match_id')
		score = req.POST.get('score')
		score = u' '.join(re.findall(u'[0-9]+', score))
		reward = req.POST.get('reward')

		if not match_id or not reward:
			return HttpResponseForbidden(_(u'잘못된 입력'))

		match = Match.objects.get(pk=match_id)
		match.score = score
		match.reward = reward
		match.save()

		return HttpResponseRedirect(reverse(globals()['matches']))

	matches = Match.objects.order_by('-pk')

	return render_to_response('matches.html', RequestContext(req, {
		'title': _(u'경기 목록'),
		'matches': matches,
	}))
