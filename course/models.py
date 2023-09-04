from django.contrib.auth import get_user_model
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="课程名称", verbose_name="名称")
    introduction = models.TextField(help_text="课程简介", verbose_name="简介")
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, help_text="课程讲师",
                                verbose_name="讲师")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="课程价格", verbose_name="价格")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间", verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间", verbose_name="更新时间")

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name
        ordering = ("price",)

    def __str__(self):
        return self.name
