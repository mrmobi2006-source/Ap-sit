from fastapi import FastAPI, Query
import httpx
import random

app = FastAPI(title="Shopify Gateway Bridge API")

# قائمة المواقع التي أرسلتها (يمكنك زيادة أو تعديل القائمة هنا)
SHOPIFY_SITES = [
    "https://cleetusm.myshopify.com",
    "https://demkoknives.myshopify.com",
    "https://doctoraromas.myshopify.com",
    "https://greatergoods-com.myshopify.com"
]

@app.get("/")
async def check_gateway(
    cc: str = Query(..., description="Card details in format card|mm|yyyy|cvv"),
    url: str = Query(None, description="Target site URL (Optional)"),
    proxy: str = Query(None, description="Proxy string (Optional)")
):
    try:
        # إذا لم يرسل البوت موقعاً محدداً، يتم اختيار موقع عشوائي من القائمة المتاحة
        target_url = url if url else random.choice(SHOPIFY_SITES)
        
        # فرز بيانات البطاقة
        cc_parts = cc.split('|')
        if len(cc_parts) != 4:
            return {"Response": "Invalid input format from bot", "Status": "Error", "Gate": "Unknown", "Price": "-"}
            
        card_num, month, year, cvv = cc_parts[0], cc_parts[1], cc_parts[2], cc_parts[3]

        # إعداد البروكسي إذا تم تمريره من البوت
        mounts = {}
        if proxy:
            # صياغة البروكسي البرمجية القياسية لـ httpx
            proxy_url = f"http://{proxy}"
            mounts = {"http://": proxy_url, "https://": proxy_url}

        # محاكاة الطلب البرمجي نحو بوابة الموقع المستهدف
        async with httpx.AsyncClient(mounts=mounts, timeout=30.0) as client:
            # هذه الخطوة هيكلية لإرسال الطلب، يمكنك استبدالها برابط الدفع الفعلي للموقع
            # هنا نقوم بطلب الصفحة الرئيسية للموقع كمثال لاختبار الاتصال والبروكسي
            response = await client.get(target_url)
            
            if response.status_code == 200:
                return {
                    "Response": "Connection established successfully",
                    "Status": "Approved",
                    "Gate": "Shopify_Generic",
                    "Price": "1.00$"
                }
            else:
                return {
                    "Response": f"Site returned status code {response.status_code}",
                    "Status": "Dead",
                    "Gate": "Shopify_Generic",
                    "Price": "-"
                }

    except httpx.RequestError as exc:
        return {"Response": f"Proxy or Connection Error: {exc}", "Status": "Error", "Gate": "Unknown", "Price": "-"}
    except Exception as e:
        return {"Response": f"Internal API Error: {str(e)}", "Status": "Error", "Gate": "Unknown", "Price": "-"}
