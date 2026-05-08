import asyncio
from datetime import date
from app.graph.builder import build_graph

async def preview_newsletter():
    """Show sample formatted newsletter output."""
    
    graph = build_graph()
    config = {"configurable": {"thread_id": "preview"}}
    
    initial_state = {
        "raw_news": [],
        "merged_news": [],
        "unique_news": [],
        "filtered_news": [],
        "ranked_news": [],
        "summaries": [],
        "newsletter": "",
        "errors": [],
        "metadata": {}
    }
    
    result = await graph.ainvoke(initial_state, config=config)
    newsletter = result.get("newsletter", "")
    
    print("\n" + "="*70)
    print("NEWSLETTER PREVIEW")
    print("="*70)
    print(newsletter)
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(preview_newsletter())
