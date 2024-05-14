# Django imports
from django.core.mail import EmailMultiAlternatives  # 用于发送邮件
from django.template.loader import render_to_string  # 用于加载和渲染模板
from django.utils.html import strip_tags  # 从HTML字符串中去除所有HTML标签

# Third party imports
from django_rq import job  # 用于将函数作为异步任务
from sentry_sdk import capture_exception  # 用于捕获并上报异常

# Module imports
from plane.db.models import User  # 导入User模型

# 使用django-rq的job装饰器来定义一个异步任务，队列名为"default"
@job("default")
def email_verification(first_name, email, token, current_site):
    """
    发送电子邮件验证链接。

    :param first_name: 用户的名字
    :param email: 用户的邮箱地址
    :param token: 用于验证的令牌
    :param current_site: 当前网站域名
    """
    try:
        # 构建电子邮件验证的相对链接
        realtivelink = "/request-email-verification/" + "?token=" + str(token)
        # 构建完整的验证URL
        abs_url = "http://" + current_site + realtivelink

        # 邮件发件人
        from_email_string = f"Team Plane <team@mailer.plane.so>"

        # 邮件主题
        subject = f"Verify your Email!"

        # 渲染邮件模板的上下文
        context = {
            "first_name": first_name,  # 用户名
            "verification_url": abs_url,  # 验证链接
        }

        # 加载并渲染HTML邮件模板
        html_content = render_to_string("emails/auth/email_verification.html", context)

        # 将HTML内容转换为纯文本内容
        text_content = strip_tags(html_content)

        # 创建邮件对象
        msg = EmailMultiAlternatives(subject, text_content, from_email_string, [email])
        # 添加HTML版本的邮件内容
        msg.attach_alternative(html_content, "text/html")
        # 发送邮件
        msg.send()
        return
    except Exception as e:
        # 捕获并上报异常
        capture_exception(e)
        return