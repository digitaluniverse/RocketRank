from bs4 import BeautifulSoup
import json
import asyncio
from playwright.async_api import async_playwright
import tempfile
import random
import os

base_url = "https://api.tracker.gg/api/v2/rocket-league/standard"
base_2 = "https://rocketleague.tracker.network/rocket-league"

# List of user-agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    # Add more user-agent strings as needed
]

async def create_browser(headless=True):
    proxy_host = os.environ.get('PROXY_HOST')
    proxy_port = os.environ.get('PROXY_PORT')
    proxy_username = os.environ.get('PROXY_USERNAME')
    proxy_password = os.environ.get('PROXY_PASSWORD')

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless, proxy={
        "server": f"http://{proxy_host}:{proxy_port}",
        "username": proxy_username,
        "password": proxy_password
    })
    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS)  # Rotate user-agent
    )
    return browser, playwright, context

async def getData(username, platform, needsPlatformIdentifier=False):
    browser, playwright, context, page = None, None, None, None
    try:
        browser, playwright, context = await create_browser(headless=True)
        page = await context.new_page()

        data_link = f'{base_2}/profile/{platform}/{username}/overview'
        data_url = f'{base_url}/profile/{platform}/{username}'

        # Navigate to the page with an increased timeout and wait for the loading indicator to disappear
        await page.goto(data_link, wait_until='domcontentloaded', timeout=60000)  # Increased timeout to 60 seconds
        await page.wait_for_selector('.content--loading', state='hidden', timeout=60000)  # Increased timeout to 60 seconds

        # Take a screenshot for debugging (optional)
        screenshot_path = tempfile.mktemp(suffix=".png")
        await page.screenshot(path=screenshot_path)

        # Check if the page has loaded properly
        content = await page.content()
        if 'recent matches' not in content:
            print('The expected text is not found in the page content.')

        # Use try/catch within the evaluated script
        json_data = await page.evaluate(f"""
            fetch('{data_url}')
                .then(response => response.ok ? response.json() : Promise.reject('Failed to load'))
                .catch(error => console.error('Fetch error:', error))
        """)
        if json_data is None:
            raise ValueError("JSON data is None, fetch might have failed or returned no data.")
        return json_data

    except Exception as e:
        print(f"An error occurred during the request: {e}")
        return None

    finally:
        if page:
            await page.close()
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

def getRankData(data):
    
    segments = data['segments']
    rank_data = []
    for segment in segments:
        if segment['type'] == 'playlist':
            stats = segment['stats']
            gametype = segment['metadata']['name']
            tier = stats['tier']['metadata']['name']
            division = stats['division']['metadata']['name']
            mmr = stats['rating']['value']
            rank = f'{gametype} | {tier} {division} | mmr: {mmr}'
            rank_data.append(rank)
    return rank_data

def formatRank( tier, division, mmr,hiddenOptions):
    rank = f" {tier} {division}"
    if "div" in hiddenOptions:
        rank = f" {tier}"
    full_rank = f"{rank} ({mmr})"
    if "mmr" in hiddenOptions:
        full_rank = f" {rank}"
        if "div" in hiddenOptions:
            full_rank = rank
    
    return full_rank


def formatRank(tier, division, mmr, hiddenOptions):
    # Implement the logic to format the rank string based on hidden options
    # This is a placeholder function body; you will need to replace it with your actual formatting logic
    rank_str = f"{tier} {division} (MMR: {mmr})"
    if "div" in hiddenOptions:
        rank_str = f"{tier} (MMR: {mmr})"
    return rank_str

def getFilteredRankData(data, hiddenPlaylists, hiddenOptions):
    playlist = {}

    segments = data['segments']
    rank_data = []
    for segment in segments:
        if segment['type'] == 'playlist':
            stats = segment['stats']
            gametype = segment['metadata']['name']
            tier = stats['tier']['metadata']['name']
            division = stats['division']['metadata']['name']
            mmr = stats['rating']['value']
            if "Ranked" in gametype:
                gametype = gametype.replace("Ranked ", "")
            if "Tournament" in gametype:
                gametype = "Tournaments"
            showPlaylist = True
            for game in hiddenPlaylists:
                if game.lower() == gametype.lower():
                    showPlaylist = False
                    break
            print(f"show {gametype} {showPlaylist}")
            if showPlaylist:
                full_rank = formatRank(tier, division, mmr, hiddenOptions)
                playlist[gametype] = full_rank
    rank_data = ' | \n'.join(f"{key}: {value}" for key, value in playlist.items())
    return rank_data

def checkPlatform(platform):
    validPlatform = True
    if platform in ['xbox', 'xboxone', 'xb']:
            platform = 'xbl'
            platname = 'xbox'
    elif platform in ['ps', 'playstation', 'ps4', 'psn','ps5']:
        platform = 'psn'
        platname = 'playstation'
    elif platform in ['epic','fortnite','epic']:
        platform = 'epic'
        platname = 'epic'
    elif platform in ['steam','pc','og']:
        platform = 'steam'
        platname = 'steam'
    else:
        validPlatform = False
        platname = None
    return platform,platname,validPlatform