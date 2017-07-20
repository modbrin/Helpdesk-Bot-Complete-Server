from django.db import models

class Article(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=200, default='')
	viewCount = models.PositiveIntegerField(default=0)
	likeCount = models.PositiveIntegerField(default=0)
	text = models.TextField(default='')
	keywords = models.TextField(default='')
	relevance = models.FloatField(default=0)

	def save(self, *args, **kwargs):
		self.relevance = self.likeCount/(self.viewCount + 1)
		super(Article, self).save(*args, **kwargs)

	

class User(models.Model):
	LANGUAGE_CHOICES = (
		('EN', 'English'),
		('RU', 'Russian'),
		)
	chatID = models.CharField(max_length=100, default='')
	userID = models.CharField(max_length=100, default='')
	ticketID = models.IntegerField(default=0)
	rating = models.IntegerField(default=0)
	activationDate = models.CharField(max_length=600, default='')
	messageContent = models.TextField(default='')
	messageAtt = models.CharField(max_length=200, default='')
	email = models.CharField(max_length=100, unique=True)
	preferredLanguage = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN')
	state = models.IntegerField(default=0)
	activationKey = models.CharField(max_length=100, default='')

class Feedback(models.Model):
	name = models.CharField(max_length=100, default='')
	email = models.CharField(max_length=100, default='')
	grade = models.IntegerField(default=0)
	text = models.TextField(default='')

class Contacts(models.Model):
	info = models.TextField(default='')

class Invite(models.Model):
	invite = models.CharField(max_length=200, unique=True)
	email = models.CharField(max_length=100, default='')
	is_valid = models.IntegerField(default=0)