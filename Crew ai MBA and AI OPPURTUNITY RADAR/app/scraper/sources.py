from __future__ import annotations

from app.models import SourceMetadata


def get_source_catalog() -> list[SourceMetadata]:
    """Researcher agent output: normalized source metadata catalog."""
    return [
        # Business competitions & MBA prep
        SourceMetadata(
            source_name="Unstop Opportunities",
            category="business_competitions",
            scrape_type="html",
            url="https://unstop.com/all-opportunities",
            parsing_strategy="Parse listing cards and extract title/link/type labels.",
        ),
        SourceMetadata(
            source_name="Reskilll Hacks",
            category="ai_hackathons",
            scrape_type="html",
            url="https://reskilll.com/allhacks",
            parsing_strategy="Extract hackathon cards with title/date and outbound URL.",
        ),
        SourceMetadata(
            source_name="Kaggle Competitions",
            category="business_competitions",
            scrape_type="html",
            url="https://www.kaggle.com/competitions",
            parsing_strategy="Parse competition table cards and canonical links.",
        ),
        SourceMetadata(
            source_name="HackerEarth Hackathons",
            category="ai_hackathons",
            scrape_type="html",
            url="https://www.hackerearth.com/challenges/hackathon/",
            parsing_strategy="Extract challenge listing cards and timeline text.",
        ),
        SourceMetadata(
            source_name="Devpost Hackathons",
            category="ai_hackathons",
            scrape_type="html",
            url="https://devpost.com/hackathons",
            parsing_strategy="Parse card components and map challenge metadata.",
        ),
        SourceMetadata(
            source_name="Scaler Events",
            category="mba_webinars_events",
            scrape_type="html",
            url="https://www.scaler.com/events/",
            parsing_strategy="Parse events listing and infer webinar tags.",
        ),
        SourceMetadata(
            source_name="Analytics Vidhya Events",
            category="mba_webinars_events",
            scrape_type="html",
            url="https://www.analyticsvidhya.com/events/",
            parsing_strategy="Extract event cards and tags from listing page.",
        ),
        # AI courses & learning platforms
        SourceMetadata(
            source_name="DeepLearning.AI Short Courses",
            category="ai_courses",
            scrape_type="html",
            url="https://www.deeplearning.ai/",
            parsing_strategy="Extract short-course blocks and normalize provider fields.",
        ),
        SourceMetadata(
            source_name="Coursera ML Browse",
            category="ai_courses",
            scrape_type="html",
            url="https://www.coursera.org/browse/data-science/machine-learning",
            parsing_strategy="Extract course cards and parse duration/level text.",
        ),
        SourceMetadata(
            source_name="Udemy AI Courses",
            category="ai_courses",
            scrape_type="html",
            url="https://www.udemy.com/topic/artificial-intelligence/",
            parsing_strategy="Extract AI course cards from topic listing page.",
        ),
        SourceMetadata(
            source_name="edX Artificial Intelligence",
            category="ai_courses",
            scrape_type="html",
            url="https://www.edx.org/learn/artificial-intelligence",
            parsing_strategy="Extract AI program and course cards from edX browse page.",
        ),
        SourceMetadata(
            source_name="Fast.ai",
            category="ai_courses",
            scrape_type="html",
            url="https://www.fast.ai/",
            parsing_strategy="Parse course/release announcements from homepage sections.",
        ),
        SourceMetadata(
            source_name="Microsoft Learn AI",
            category="ai_courses",
            scrape_type="html",
            url="https://learn.microsoft.com/en-us/training/browse/?products=ai-services",
            parsing_strategy="Extract Microsoft AI training modules and learning paths.",
        ),
        SourceMetadata(
            source_name="Google Machine Learning",
            category="ai_courses",
            scrape_type="html",
            url="https://developers.google.com/machine-learning",
            parsing_strategy="Extract Google ML guides, courses, and resources.",
        ),
        SourceMetadata(
            source_name="Simplilearn AI Training",
            category="ai_certifications",
            scrape_type="html",
            url="https://www.simplilearn.com/artificial-intelligence-course-training",
            parsing_strategy="Extract AI certification and training program cards.",
        ),
        SourceMetadata(
            source_name="NVIDIA Deep Learning Institute",
            category="ai_certifications",
            scrape_type="html",
            url="https://www.nvidia.com/en-us/training/",
            parsing_strategy="Extract NVIDIA DLI courses and certification paths.",
        ),
        SourceMetadata(
            source_name="IBM SkillsBuild AI",
            category="ai_courses",
            scrape_type="html",
            url="https://skillsbuild.org/adult-learners/explore-learning/artificial-intelligence",
            parsing_strategy="Extract IBM SkillsBuild AI learning resources.",
        ),
        SourceMetadata(
            source_name="Kaggle Learn",
            category="ai_courses",
            scrape_type="html",
            url="https://www.kaggle.com/learn",
            parsing_strategy="Extract micro-courses from Kaggle Learn catalog.",
        ),
        # AI news & industry updates (RSS feeds)
        SourceMetadata(
            source_name="OpenAI News",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://openai.com/news/rss.xml",
            parsing_strategy="Parse OpenAI news RSS entries.",
        ),
        SourceMetadata(
            source_name="The Verge AI",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            parsing_strategy="Parse The Verge AI section RSS feed.",
        ),
        SourceMetadata(
            source_name="Hugging Face Blog",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://huggingface.co/blog/feed.xml",
            parsing_strategy="Use Hugging Face blog RSS feed.",
        ),
        SourceMetadata(
            source_name="VentureBeat AI",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://venturebeat.com/category/ai/feed/",
            parsing_strategy="Consume VentureBeat AI category RSS feed.",
        ),
        SourceMetadata(
            source_name="Towards Data Science",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://towardsdatascience.com/feed",
            parsing_strategy="Parse Towards Data Science Medium RSS feed.",
        ),
        SourceMetadata(
            source_name="MIT News - Artificial Intelligence",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://news.mit.edu/topic/artificial-intelligence2-rss.xml",
            parsing_strategy="Parse MIT AI topic RSS feed.",
        ),
        SourceMetadata(
            source_name="Google AI Blog",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://blog.research.google/feeds/posts/default",
            parsing_strategy="Parse Google Research blog Atom/RSS feed.",
        ),
        SourceMetadata(
            source_name="ArXiv cs.AI",
            category="ai_industry_updates",
            scrape_type="rss",
            url="https://rss.arxiv.org/rss/cs.AI",
            parsing_strategy="Parse latest AI research paper feed from arXiv.",
        ),
    ]
