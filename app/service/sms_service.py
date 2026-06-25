import json
import random

from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredentialConfig
from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
from alibabacloud_dypnsapi20170525 import models as dypnsapi_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from app.core.config import settings


def create_sms_client() -> DypnsapiClient:
    """
    创建阿里云号码认证服务客户端。

    作用：
    1. 从 settings 获取 AK / SK
    2. 生成阿里云凭据 credential
    3. 设置号码认证服务地址
    4. 返回后续用于发送短信的 client
    """

    # 这一步就是：把你 .env 中的 AK / SK 传给阿里云 SDK
    credential_config = CredentialConfig(
        type="access_key",
        access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
    )

    # CredentialClient 相当于“签名工具”
    credential = CredentialClient(credential_config)

    # SDK 总配置
    config = open_api_models.Config(
        credential=credential
    )

    # 你调用的是号码认证服务 Dypnsapi
    config.endpoint = "dypnsapi.aliyuncs.com"

    # 返回真正能调接口的客户端对象
    return DypnsapiClient(config)


def generate_code() -> str:
    """生成 6 位短信验证码"""

    return str(random.randint(100000, 999999))


def ali_send_sms_code(phone: str, code: str) -> dict:
    """
    调用阿里云，向 phone 发送验证码。

    参数：
    - phone: 手机号，例如 18523318356
    - code: 你后端生成的验证码，例如 123456
    """

    client = create_sms_client()

    request = dypnsapi_models.SendSmsVerifyCodeRequest(
        scheme_name="验证码",
        country_code="86",
        phone_number=phone,

        # 这两个按你阿里云控制台里的实际内容写
        sign_name="速通互联验证码",
        template_code="100001",

        # 必须和阿里云模板变量名对应
        template_param=json.dumps({
            "code": code,
            "min": "5"
        }),

        # 验证码有效期：300 秒
        valid_time=300,

        # 不让阿里云把验证码返回给你的接口响应
        return_verify_code=False,

        # 1 表示数字验证码
        code_type=1,

        # 6 位验证码
        code_length=6,

        # 重复发送策略
        duplicate_policy=1,

        # 同一个手机号至少间隔 60 秒
        interval=60,

        # 发送失败自动重试
        auto_retry=1,
    )

    runtime = util_models.RuntimeOptions()

    try:
        response = client.send_sms_verify_code_with_options(
            request,
            runtime
        )

        body = response.body

        return {
            "success": body.code == "OK",
            "code": body.code,
            "message": body.message,
            "request_id": body.request_id,
        }

    except Exception as e:
        error_message = getattr(e, "message", str(e))

        raise RuntimeError(f"阿里云短信发送失败：{error_message}")