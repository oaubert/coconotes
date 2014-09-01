from django.shortcuts import render
from rest_framework import generics
from rest_framework.renderers import UnicodeJSONRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

class CourseList(generics.ListCreateAPIView):
    model = Course
    serializer_class = CourseSerializer

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Course
    serializer_class = CourseSerializer

class VideoList(generics.ListCreateAPIView):
    model = Video
    serializer_class = VideoSerializer

class VideoDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Video
    serializer_class = VideoSerializer
