import os
import aiohttp
import asyncio
import json
from dotenv import load_dotenv
from supabase import create_client

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
  
    try:
        # 경기도 행정지역 명칭 불러오기  
        region_url = os.getenv("GGREGION_API_URL")
        region_response = await fetch(region_url, params)
        
        region_rsp_json = json.loads(region_response)
        
        region_raw_datas = region_rsp_json.get("GGADMINHIGHGBST")[-1].get("row")
        regions = [region_raw_data.get("SIGUN_NM") for region_raw_data in region_raw_datas]
        
        # 경기도 지역정보 조회
        gmoney_url = os.getenv("GMONEY_API_URL")
        
        # 지역명,가맹점 건 수 수집
        gmoney_sigun_infos = []
        for region in regions:
            if region in ["의정부","남양주"]:
                region = f"{region}시"
                
            print(region)    
            params["pIndex"] = 1
            params["pSize"] = 1
            params["SIGUN_NM"] = region        
            
            gmoney_response = await fetch(gmoney_url, params)
            gmoney_rsp_json = json.loads(gmoney_response)
    
            print(gmoney_rsp_json)
            storecnt = gmoney_rsp_json.get("RegionMnyFacltStus")[0].get("head")[0].get('list_total_count', 0)
            
            page_totalcnt = storecnt // 1000
            reminder_cnt = storecnt - (page_totalcnt * 1000)
            
            print(f"{region} : 호출페이지 - {page_totalcnt}, 잔여건 - {reminder_cnt}")    
            for i in range(page_totalcnt):
                params["pIndex"] = int(i) + 1
                params["pSize"] = 1000
                
                gmoney_response = await fetch(gmoney_url, params)
                gmoney_rsp_json = json.loads(gmoney_response)
                
                store_list= gmoney_rsp_json.get("RegionMnyFacltStus")[1].get("row")
                gmoney_sigun_infos.extend(store_list)
                #print(store_list)
                
                print(f"{region}-{i+1}번째 실행완료...")
                #sleep(2)
                
            if reminder_cnt > 0:
                params["pIndex"] = page_totalcnt + 1
                params["pSize"] = reminder_cnt
                
                gmoney_response = await fetch(gmoney_url, params)
                gmoney_rsp_json = json.loads(gmoney_response)
                
                store_list= gmoney_rsp_json.get("RegionMnyFacltStus")[1].get("row")
                gmoney_sigun_infos.extend(store_list)
                
                print(f"{region}-{reminder_cnt} 건 실행완료...")
                
            #sleep(5)
                
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_apikey = os.getenv("SUPABASE_APIKEY")
        supabase = create_client(supabase_url, supabase_apikey)
        response = supabase.table("GMONEY_STORE_TB").insert(gmoney_sigun_infos).execute()
        print(response)
    
        print("supabase 저장완료 끝!")    
            
    except Exception as e:
        raise e    
        
    
asyncio.run(main())
