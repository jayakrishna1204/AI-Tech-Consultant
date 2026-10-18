
from task1_knowledge_brain.database import find_article_by_url

url = "https://example.com/internal-test/ai-video-editor"

article = find_article_by_url(url)

if article:
    print("Feedback entry found!")
    print("Title:", article["title"])
    print("Content:", article["content"])
else:
    print("Feedback entry not found.")
