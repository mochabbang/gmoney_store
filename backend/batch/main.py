import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def post_data(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type:
                data = await response.json()
            else:
                data = await response.text()
                
            return data

async def main():
    url = 'https://openapi.gg.go.kr/RegionMnyFacltStus'
    params = {'KEY': os.getenv("ACCESS_KEY"), 'Type': 'json', 'pIndex':1, 'pSize':1}
    response = await post_data(url, params)
    print(f"Response: {response}")
    
asyncio.run(main())
