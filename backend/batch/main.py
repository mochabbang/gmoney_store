import os
import aiohttp
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()



async def fetch(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type:
                data = await response.json()
            else:
                data = await response.text()
                
            return data

async def main():
    params = {'KEY': os.getenv("ACCESS_KEY"), 'Type': 'json'}
  
    # 경기도 행정지역 명칭 불러오기  
    region_url = os.getenv("GGREGION_API_URL")
    region_response = await fetch(region_url, params)
    
    region_rsp_json = json.loads(region_response)
    
    region_raw_datas = region_rsp_json.get("GGADMINHIGHGBST")[-1].get("row")
    regions = [region_raw_data.get("SIGUN_NM") for region_raw_data in region_raw_datas]
    
    # 경기도 지역정보 조회
    gmoney_url = os.getenv("GMONEY_API_URL")
    params["pIndex"] = 1
    params["pSize"] = 1
    
    # 지역명,가맹점 건 수 수집
    gmoney_sigunstore_infos = []
    for region in regions:
        
        if region in ["의정부","남양주"]:
            region = f"{region}시"
            
        params["SIGUN_NM"] = region        
        
        gmoney_response = await fetch(gmoney_url, params)
        gmoney_rsp_json = json.loads(gmoney_response)
    
        storecnt = gmoney_rsp_json.get("RegionMnyFacltStus")[0].get("head")[0].get('list_total_count', 0)
        gmoney_sigunstore_info = {} 
        gmoney_sigunstore_info[region] = storecnt
        gmoney_sigunstore_infos.append(gmoney_sigunstore_info)
        
    # 지역, 가맹점 비동기 병렬로 1/n나누어 데이터셋 구성
    
asyncio.run(main())
