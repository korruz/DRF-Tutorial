from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course
from .permissions import IsOwnerOrReadOnly
from .serializers import CourseSerializer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # Django 的信号机制
def generate_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


"""一、函数式编程 Function Based View"""


@api_view(['GET', 'POST'])
@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
def course_list(request):
    """
    获取所有课程信息或新增一个课程
    :param request:
    :return:
    """
    if request.method == 'GET':
        s = CourseSerializer(instance=Course.objects.all(), many=True)
        return Response(data=s.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        s = CourseSerializer(data=request.data)  # 部分更新用 partial=True 属性
        if s.is_valid():
            s.save(teacher=request.user)
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((BasicAuthentication,))
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly, ])
def course_detail(request, pk):
    """
    获取、更新、删除一个课程
    :param request:
    :param pk:
    :return:
    """
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(data={"msg": "课程不存在"}, status=status.HTTP_404_NOT_FOUND)
    else:
        if request.method == 'GET':
            s = CourseSerializer(instance=course)
            return Response(data=s.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            s = CourseSerializer(instance=course, data=request.data, partial=True)
            if s.is_valid():
                s.save()
                return Response(data=s.data, status=status.HTTP_200_OK)
            else:
                return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            course.delete()
            return Response(data={"msg": "删除成功"}, status=status.HTTP_200_OK)


"""二、类视图 Class Based View"""


class CourseList(APIView):
    """
    获取所有课程信息或新增一个课程
    """

    @staticmethod
    def get(request):
        """
        获取所有课程信息
        :param request:
        :return:
        """
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        新增一个课程
        :param request:
        :return:
        """
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetail(APIView):
    """
    获取、更新、删除一个课程
    """
    permission_classes = (IsOwnerOrReadOnly,)

    # @staticmethod
    def get_object(self, pk):
        """
        :param pk:
        :return:
        """
        try:
            obj = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return
        # 非通用视图需要手动调用这个函数: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, pk):
        """
        获取一个课程
        :param request:
        :param pk:
        :return:
        """
        course = self.get_object(pk=pk)
        if not course:
            return Response(data={"msg": "课程不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(instance=course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        更新一个课程
        :param request:
        :param pk:
        :return:
        """
        course = self.get_object(pk=pk)
        if not course:
            return Response(data={"msg": "课程不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(instance=course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        删除一个课程
        :param request:
        :param pk:
        :return:
        """
        course = self.get_object(pk=pk)
        if not course:
            return Response(data={"msg": "课程不存在"}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response(data={"msg": "删除成功"}, status=status.HTTP_200_OK)


"""三、通用类视图 Generic Class Based View"""


class GCourseList(generics.ListCreateAPIView):
    """
    获取所有课程信息或新增一个课程
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class GCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    获取、更新、删除一个课程
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)


"""四、DRF 的视图集 viewsets"""


class CourseViewSet(viewsets.ModelViewSet):
    """
    获取、更新、删除一个课程
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
