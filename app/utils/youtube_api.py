import os
import requests

API_KEY = os.getenv("YOUTUBE_API_KEY")

DSA_QUERY_MAP = {
    "trees": "binary tree data structure traversal inorder preorder postorder dfs bfs tutorial",
    "graph": "graph data structure bfs dfs dijkstra shortest path tutorial",
    "stack": "stack data structure push pop implementation tutorial",
    "queue": "queue data structure circular priority queue tutorial",
    "linked list": "linked list singly doubly circular implementation dsa",
    "heap": "heap data structure min heap max heap priority queue tutorial"
}

def build_smart_query(user_query: str):
    """
    Converts raw input into DSA-focused YouTube search query
    """
    key = user_query.lower().strip()

    if key in DSA_QUERY_MAP:
        return DSA_QUERY_MAP[key]

    return f"{user_query} data structure dsa tutorial explanation implementation"


def fetch_youtube_videos(query, max_results=3):
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={query}&maxResults={max_results}&type=video&key={API_KEY}"
    )

    response = requests.get(url).json()

    videos = []

    for item in response.get("items", []):
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]

        videos.append({
            "title": snippet["title"],
            "videoId": video_id,
            "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": snippet["thumbnails"]["high"]["url"],
            "channel": snippet["channelTitle"]
        })

    return videos


def is_relevant(title: str):
    keywords = [
        "data structure", "dsa", "binary", "tree",
        "graph", "dfs", "bfs", "traversal",
        "algorithm", "implementation", "leetcode"
    ]

    title = title.lower()
    return any(k in title for k in keywords)

def score(video):
    title = video["title"].lower()
    s = 0

    if "tutorial" in title:
        s += 3
    if "dsa" in title:
        s += 3
    if "inorder" in title or "dfs" in title:
        s += 2
    if "animated" in title:
        s += 1

    # penalize irrelevant content
    if "cut" in title or "wood" in title:
        s -= 10

    return s


def recommend_dsa_videos(user_query: str):

    smart_query = build_smart_query(user_query)

    videos = fetch_youtube_videos(smart_query)

    filtered = [v for v in videos if is_relevant(v["title"])]

    ranked = sorted(filtered, key=score, reverse=True)

    return {
        "original_query": user_query,
        "smart_query": smart_query,
        "results": ranked
    }

if __name__ == "__main__":
    query = input("Enter topic (e.g., trees): ")
    result = recommend_dsa_videos(query)

    print("\nSMART QUERY USED:", result["smart_query"])
    print("\nTOP VIDEOS:\n")

    for v in result["results"]:
        print("Title:", v["title"])
        print("URL:", v["videoUrl"])
        print("Channel:", v["channel"])
        print("-" * 50)
