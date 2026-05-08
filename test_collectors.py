import asyncio
import logging
from app.collectors.rss import fetch_rss
from app.collectors.hackernews import fetch_hackernews
from app.collectors.github import fetch_github_trending
from app.collectors.reddit import fetch_reddit
from app.collectors.twitter import fetch_twitter
from app.collectors.arxiv import fetch_arxiv_papers
from app.collectors.devto import fetch_devto_articles
from app.collectors.producthunt import fetch_producthunt_tools

logging.basicConfig(level=logging.WARNING)

async def test_all_collectors():
    print("\n" + "="*70)
    print("TESTING ALL COLLECTORS")
    print("="*70 + "\n")
    
    collectors = {
        "📰 RSS Feeds": fetch_rss,
        "🔥 Hacker News": fetch_hackernews,
        "⭐ GitHub Trending": fetch_github_trending,
        "🔴 Reddit": fetch_reddit,
        "🐦 Twitter": fetch_twitter,
        "📄 ArXiv Papers": fetch_arxiv_papers,
        "📝 DEV.to Articles": fetch_devto_articles,
        "🚀 ProductHunt Tools": fetch_producthunt_tools,
    }
    
    results = {}
    total_items = 0
    
    for name, collector in collectors.items():
        try:
            print(f"Testing {name}...", end=" ", flush=True)
            items = await collector()
            count = len(items)
            results[name] = count
            total_items += count
            
            # Show sample
            if count > 0:
                print("[OK]")
                sample_title = items[0].get('title', 'N/A')[:60]
                print(f"  -> {count} items | {sample_title}")
            else:
                print("[SKIP] (not configured or no data)")
        except Exception as e:
            print(f"[ERROR] {str(e)[:40]}")
            results[name] = 0
    
    # Summary
    print("\n" + "="*70)
    print("COLLECTION SUMMARY")
    print("="*70)
    for name, count in results.items():
        status = "[OK]" if count > 0 else "[--]"
        print(f"{status} {name:25} : {count:3d} items")
    print("-"*70)
    print(f"   TOTAL ITEMS              : {total_items:3d} items")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all_collectors())
