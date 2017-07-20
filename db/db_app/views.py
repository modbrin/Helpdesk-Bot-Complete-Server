from db_app.models import Article, User, Contacts, Feedback, Invite
from db_app.serializers import ArticleSerializer, UserSerializer, ContactsSerializer, FeedbackSerializer, InviteSerializer
from django.http import Http404
from django.db.models import Q, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

class ArticleList(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, format=None):
		articles = Article.objects.all()
		serializer = ArticleSerializer(articles, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = ArticleSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetail(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get_object(self, pk):
		try:
			return Article.objects.get(pk=pk)
		except Article.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		article = self.get_object(pk)
		serializer = ArticleSerializer(article)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		article = self.get_object(pk)
		serializer = ArticleSerializer(article, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):	
		article = self.get_object(pk)
		article.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleSearch(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, keyword, format=None):
		values = keyword.split('&')
		queries = [Q(keywords__contains=value) for value in values]
		query = queries.pop()
		for item in queries:
			query |= item
		articles = Article.objects.filter(query).order_by('-relevance')[:2]
		serializer = ArticleSerializer(articles, many=True)
		return Response(serializer.data)

class UserSearch(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, email, format=None):
		try:
			user = User.objects.get(email=email)
			serializer = UserSerializer(user)
			return Response(serializer.data)
		except User.DoesNotExist:
			raise Http404
				

class ContactsDetail(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, format=None):
		contacts = Contacts.objects.all()
		serializer = ContactsSerializer(contacts, many=True)
		return Response(serializer.data)
	def put(self, request, format=None):
		DEFAULT_PK = 1
		if Contacts.objects.all().count() == 0:
			serializer = ContactsSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		info = Contacts.objects.get(pk=DEFAULT_PK)
		serializer = ContactsSerializer(info, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserList(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, format=None):
		users = User.objects.all()
		serializer = UserSerializer(users, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		user = self.get_object(pk)
		serializer = UserSerializer(user)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		user = self.get_object(pk)
		serializer = UserSerializer(user, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):	
		user = self.get_object(pk)
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class FeedbackList(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, format=None):
		feedback = Feedback.objects.all()
		serializer = FeedbackSerializer(feedback, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = FeedbackSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedbackDetail(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get_object(self, pk):
		try:
			return Feedback.objects.get(pk=pk)
		except Feedback.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		feedback = self.get_object(pk)
		serializer = FeedbackSerializer(feedback)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		feedback = self.get_object(pk)
		serializer = FeedbackSerializer(feedback, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):	
		feedback = self.get_object(pk)
		feedback.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class ViewIncrement(APIView):
	def get_object(self, pk):
		try:
			return Article.objects.get(pk=pk)
		except Article.DoesNotExist:
			raise Http404

	def post(self, request, pk, format=None):
		article = self.get_object(pk)
		article.viewCount = article.viewCount + 1
		serializer = ArticleSerializer(article, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(status=status.HTTP_200_OK)
		return Response(status=status.HTTP_204_NO_CONTENT)

class LikeIncrement(APIView):
	def get_object(self, pk):
		try:
			return Article.objects.get(pk=pk)
		except Article.DoesNotExist:
			raise Http404

	def post(self, request, pk, format=None):
		article = self.get_object(pk)
		article.likeCount = article.likeCount + 1
		serializer = ArticleSerializer(article, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(status=status.HTTP_200_OK)
		return Response(status=status.HTTP_204_NO_CONTENT)		

class InviteList(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get(self, request, format=None):
		invites = Invite.objects.all()
		serializer = InviteSerializer(invites, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = InviteSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InviteDetail(APIView):
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	def get_object(self, pk):
		try:
			return Invite.objects.get(pk=pk)
		except Invite.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		invite = self.get_object(pk)
		serializer = InviteSerializer(invite)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		invite = self.get_object(pk)
		serializer = InviteSerializer(invite, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):	
		invite = self.get_object(pk)
		invite.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)