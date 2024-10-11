import os
import openai
from dotenv import load_dotenv

load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_guidelines_summary():
    with open("data/wcag.txt", "r", encoding="utf-8") as file:
        summary = file.read()
    return summary

def generate_code(prompt, code, guidelines):
    full_prompt = f"""
당신은 웹 접근성 전문가입니다. 아래의 웹 콘텐츠 접근성 지침 요약을 참고하여, 사용자가 제공한 HTML 코드를 '{prompt}' 요청에 따라 수정하세요.

웹 콘텐츠 접근성 지침 요약:
{guidelines}

사용자 제공 코드:
{code}

수정된 코드만 제공하세요.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=2048,
        temperature=0,
        n=1,
        stop=None,
    )
    generated_code = response.choices[0].message.content.strip()
    return generated_code

def generate_explanation(original_code, modified_code):
    explanation_prompt = f"""
다음은 사용자가 제공한 원본 코드입니다:

원본 코드:
{original_code}

그리고 다음은 수정된 코드입니다:

수정된 코드:
{modified_code}

수정 사항을 간략히 설명해주세요.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": explanation_prompt}],
        max_tokens=500,
        temperature=0,
        n=1,
        stop=None,
    )
    explanation = response.choices[0].message.content.strip()
    return explanation