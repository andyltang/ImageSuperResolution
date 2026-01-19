import os
import httpx

CAPTCHA_SECRET = os.environ["CAPTCHA_SECRET_KEY"]
VERIFICATION_URL = os.environ["CAPTCHA_VERIFICATION_URL"]

class CaptchaVerifier():

  @staticmethod
  async def verify(token):
    data = {
      "secret": CAPTCHA_SECRET,
      "response": token,
    }
    async with httpx.AsyncClient(timeout=5) as client:
      response = await client.post(
        VERIFICATION_URL,
        data=data,
      )
      result = response.json()

    return result.get("success") is True
