import os
from google import genai

client = genai.Client(
    api_key=("YOUR API KEY")
)

def summarize_article(article):
    prompt = f"""
    Summarize the following Philippine government news article.

    Return ONLY plain text.

    Use this exact format:

    Summary:
    Write one paragraph between 100 and 150 words.

    Key Points:
    - First key point
    - Second key point
    - Third key point

    IMPORTANT:
    - Do NOT use Markdown.
    - Do NOT use #, ##, ###.
    - Do NOT use ** or *.
    - Do NOT use code blocks.
    - Return plain text only.

    Article:

    {article}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        print(f"Gemini Error: {e}")
        return article
