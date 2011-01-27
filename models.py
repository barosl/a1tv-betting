from django.db import models

class Season(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self): return self.name

class Match(models.Model):
	name = models.CharField(max_length=50)
	season = models.ForeignKey(Season)
	score = models.CharField(max_length=20, blank=True)
	poll_key = models.CharField(max_length=50, db_index=True)
	reward = models.IntegerField()

	def __unicode__(self): return self.name

class Bettor(models.Model):
	name = models.CharField(max_length=50, db_index=True)
	points = models.IntegerField(default=0, db_index=True)

	def __unicode__(self): return self.name

class Bet(models.Model):
	match = models.ForeignKey(Match)
	score = models.CharField(max_length=20, db_index=True)
	bettors = models.ManyToManyField(Bettor)

	def __unicode__(self): return u'%s - %s' % (self.match, self.score)

class SeasonResult(models.Model):
	season = models.ForeignKey(Season)
	bettor = models.ForeignKey(Bettor)
	points = models.IntegerField(default=0, db_index=True)
