from typing import List, Dict, Any
import asyncio
import aiohttp
import json
from datetime import datetime, timezone
from base64 import b64encode
from config import settings

async def fetch_reddit_data(keyword: str, max_retries: int = 3) -> List[str]:
    """Fetch relevant discussions from Reddit using official API endpoints."""
    discussions = set()  # Use set to avoid duplicates
    
    # Reddit API configuration
    BASE_URL = "https://oauth.reddit.com"
    
    async def get_access_token() -> str | None:
        """Get OAuth access token from Reddit if credentials are available"""
        if not settings.validate_reddit_credentials():
            print("[Reddit] No credentials configured, using public access")
            return None
            
        auth_url = "https://www.reddit.com/api/v1/access_token"
        auth_headers = settings.get_reddit_auth_headers()
        
        # Use application-only OAuth flow
        async with aiohttp.ClientSession() as session:
            data = {"grant_type": "client_credentials"}
            
            try:
                async with session.post(auth_url, headers=auth_headers, data=data) as resp:
                    if resp.status != 200:
                        print(f"[Reddit] Auth failed with status {resp.status}")
                        return None
                    result = await resp.json()
                    return result.get("access_token")
            except Exception as e:
                print(f"[Reddit] Auth error: {str(e)}")
                return None
                
    async def search_reddit(token: str | None, search_type: str) -> List[Dict]:
        """Search Reddit API with proper rate limiting"""
        headers = settings.get_reddit_auth_headers()
        base_url = BASE_URL if token else "https://www.reddit.com"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if search_type == "posts":
            endpoint = "/search.json"
            params = {
                "q": keyword,
                "sort": "relevance",
                "limit": 20,
                "t": "month",
                "restrict_sr": "false",  # Search all subreddits
                "include_facets": "false"  # Don't need faceted search results
            }
        else:  # subreddits
            endpoint = "/subreddits/search.json"
            params = {
                "q": keyword,
                "limit": 10,
                "include_over_18": "false"  # Safe for work content only
            }
            
        url = f"{base_url}{endpoint}"
        print(f"[Reddit] Querying URL: {url}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        try:
                            content_type = resp.headers.get('Content-Type', '')
                            if 'html' in content_type.lower():
                                print("[Reddit] Error: Received HTML instead of JSON")
                                print("[Reddit] This usually means we hit a rate limit or need authentication")
                                return []
                                
                            raw_text = await resp.text()
                            # Try to clean any potential HTML/script tags
                            if '<html' in raw_text.lower() or '<script' in raw_text.lower():
                                print("[Reddit] Warning: Found HTML content in response")
                                return []
                                
                            try:
                                data = json.loads(raw_text)
                            except json.JSONDecodeError:
                                print("[Reddit] Failed to parse JSON response")
                                print(f"[Reddit] Raw response preview: {raw_text[:200]}...")
                                return []
                                
                            if isinstance(data, dict):
                                if "data" in data and "children" in data["data"]:
                                    posts = data["data"]["children"]
                                    print(f"[Reddit] Found {len(posts)} posts in response")
                                    return posts
                                elif "error" in data:
                                    print(f"[Reddit] API error: {data.get('error', 'Unknown error')}")
                                    return []
                            
                            print("[Reddit] Invalid response structure")
                            print(f"[Reddit] Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                            return []
                            
                        except Exception as e:
                            print(f"[Reddit] Response processing error: {str(e)}")
                            return []
                    elif resp.status == 429:  # Rate limited
                        print(f"[Reddit] Rate limited, waiting...")
                        await asyncio.sleep(5)
                        return []
                    else:
                        print(f"[Reddit] Search failed with status {resp.status}")
                        try:
                            error_text = await resp.text()
                            print(f"[Reddit] Error response: {error_text[:200]}...")
                        except:
                            pass
                        return []
            except Exception as e:
                print(f"[Reddit] Search error: {str(e)}")
                return []

    async def fetch_comments(post_id: str, token: str | None) -> List[str]:
        """Fetch comments for a specific post"""
        comments_list = []
        base_url = BASE_URL if token else "https://www.reddit.com"
        comments_url = f"{base_url}/comments/{post_id}.json"
        headers = settings.get_reddit_auth_headers()
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        async with aiohttp.ClientSession() as session:
            try:
                print(f"[Reddit] Fetching comments for post {post_id}")
                async with session.get(comments_url, headers=headers) as resp:
                    if resp.status == 200:
                        try:
                            comments_data = await resp.json()
                            if isinstance(comments_data, list) and len(comments_data) > 1:
                                valid_comments = 0
                                for comment in comments_data[1].get("data", {}).get("children", [])[:5]:
                                    if not isinstance(comment, dict):
                                        continue
                                    body = str(comment.get("data", {}).get("body", "")).strip()
                                    if len(body) > 50:
                                        comments_list.append(body)
                                        valid_comments += 1
                                print(f"[Reddit] Added {valid_comments} comments from post {post_id}")
                        except json.JSONDecodeError as je:
                            print(f"[Reddit] Comment JSON decode error: {str(je)}")
                    else:
                        print(f"[Reddit] Failed to get comments, status: {resp.status}")
            except Exception as e:
                print(f"[Reddit] Error fetching comments: {str(e)}")
        
        return comments_list
                    
    # Main execution with retries
    for attempt in range(max_retries):
        try:
            print("\n=== Reddit Data Fetching ===")
            print(f"[Reddit] Attempt {attempt + 1} of {max_retries} to fetch data for keyword: '{keyword}'")
            
            # Try to get access token for authenticated access
            token = await get_access_token()
            if token:
                print("[Reddit] Successfully authenticated")
            else:
                print("[Reddit] Using public access")
            
            # Search posts with or without authentication
            print(f"[Reddit] Searching posts for '{keyword}'...")
            posts = await search_reddit(token, "posts")
            
            # Process posts
            valid_posts = 0
            for post in posts:
                if not isinstance(post, dict):
                    print(f"[Reddit] Invalid post format: {type(post)}")
                    continue
                    
                data = post.get("data", {})
                if not isinstance(data, dict):
                    print(f"[Reddit] Invalid post data format: {type(data)}")
                    continue
                
                # Add title if meaningful
                title = str(data.get("title", "")).strip()
                if len(title) > 10:
                    discussions.add(title)
                    valid_posts += 1
                    
                # Add selftext if meaningful
                selftext = str(data.get("selftext", "")).strip()
                if len(selftext) > 50:
                    discussions.add(selftext)
                    
                # Get comments if available
                num_comments = int(data.get("num_comments", 0))
                post_id = str(data.get("id", "")).strip()
                
                if num_comments > 0 and post_id:
                    comments = await fetch_comments(post_id, token)
                    for comment in comments:
                        discussions.add(comment)
                    
            print(f"[Reddit] Successfully processed {valid_posts} valid posts")
            
            # Convert set to list and check if we have enough data
            discussions_list = list(discussions)
            if len(discussions_list) >= 5:  # If we have at least 5 discussions
                print(f"\n[Reddit] Successfully fetched {len(discussions_list)} discussions")
                return discussions_list[:50]  # Return up to 50 unique discussions
            
            print(f"\n[Reddit] Found only {len(discussions_list)} discussions, trying next attempt...")
            if attempt < max_retries - 1:
                print(f"[Reddit] Waiting {2 ** attempt} seconds...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        except Exception as e:
            print(f"[Reddit] Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"[Reddit] Waiting {2 ** attempt} seconds before retry...")
                await asyncio.sleep(2 ** attempt)
            else:
                print("[Reddit] All attempts failed, using mock data")
                return get_mock_reddit_data(keyword)
    
    # If we get here, all attempts failed
    return get_mock_reddit_data(keyword)


def get_mock_reviews(keyword: str) -> List[str]:
    """Get mock Google Reviews data for hackathon demo."""
    mock_reviews = {
        "fitness": [
            "Great gym equipment but the classes are always full. Wish they had more slots available.",
            "Love the personal training options but it's quite expensive for what you get.",
            "The fitness tracking app is buggy and doesn't sync well with other devices.",
            "Amazing variety of equipment but the peak hours are way too crowded.",
            "The meal planning service needs more variety for different dietary restrictions."
        ],
        "cooking": [
            "The kitchen tools are high quality but hard to clean properly.",
            "Recipe app is good but needs more international cuisine options.",
            "Meal prep containers are durable but too bulky for small fridges.",
            "Great cooking classes but scheduling is inflexible for working professionals.",
            "The ingredient delivery service often misses items or substitutes without notice."
        ]
    }
    return mock_reviews.get(keyword.lower(), [
        f"Product related to {keyword} has quality issues that need addressing.",
        f"Service in the {keyword} category is inconsistent across providers.",
        f"Users want more customization options for {keyword} related products.",
        f"Price point is a major concern for most {keyword} solutions.",
        f"The market lacks innovative solutions in the {keyword} space."
    ])


def get_mock_reddit_data(keyword: str) -> List[str]:
    """Get mock Reddit data for hackathon demo or API fallback."""
    # Always include some generic discussions related to the keyword
    generic_discussions = [
        f"Looking for solutions in the {keyword} market",
        f"Frustrated with current {keyword} options available",
        f"Need help finding affordable {keyword} alternatives",
        f"Why is {keyword} industry so behind in technology?",
        f"Can't find good {keyword} resources for beginners"
    ]
    
    # Add specific discussions if we have them
    mock_discussions = {
        "fitness": [
            "Need help finding affordable home workout equipment that doesn't take up too much space",
            "Frustrated with current fitness apps - they don't understand my specific goals",
            "Looking for a community that combines mental and physical wellness",
            "Why are most fitness programs designed for people who are already fit?",
            "Can't find a good meal planning app that works with my dietary restrictions"
        ],
        "cooking": [
            "Why is it so hard to find recipes for single-person portions?",
            "Need help organizing my recipes and meal planning efficiently",
            "Looking for ways to reduce food waste while cooking at home",
            "Can't find good cooking classes that fit my work schedule",
            "Struggle with storing leftovers and meal prep in small apartment"
        ]
    }
    
    # Combine specific discussions (if any) with generic ones
    specific_discussions = mock_discussions.get(keyword.lower(), [])
    all_discussions = specific_discussions + generic_discussions
    
    # Return at least 5 discussions
    return all_discussions[:max(5, len(all_discussions))]


# Example usage
async def main():
    """Test the Reddit data fetching function"""
    keyword = "fitness"  # Change this to test different keywords
    print(f"Testing Reddit data fetch for keyword: {keyword}")
    
    try:
        discussions = await fetch_reddit_data(keyword)
        print(f"\nFetched {len(discussions)} discussions:")
        for i, discussion in enumerate(discussions[:10], 1):  # Show first 10
            print(f"{i}. {discussion[:100]}...")
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
