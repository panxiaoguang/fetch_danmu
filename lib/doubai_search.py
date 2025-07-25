import re
import httpx
from urllib import parse
import cn2an


async def get_platform_link(douban_id):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://movie.douban.com/subject/{douban_id}/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
    urls = re.findall(
        'https://www.douban.com/link2/\?url=(.*?)",.+ep:.+"(.*?)"', res.text
    )
    url_dict = {}
    for url in urls:
        if url[1] in url_dict.keys():
            url_dict[str(url[1])].append(parse.unquote(url[0]))
        else:
            url_dict[str(url[1])] = [parse.unquote(url[0])]

    return url_dict


async def douban_select(name: str, tv_num: str):
    if tv_num is None:
        tv_num = "一"
    else:
        try:
            tv_num = cn2an.an2cn(int(tv_num))
        except (ValueError, TypeError):
            # 如果转换失败，保持原样
            pass

    url = "https://frodo.douban.com/api/v2/search/weixin"

    params = {
        "q": name,
        "start": "0",
        "count": "20",
        "apiKey": "0ac44ae016490db2204ce0a042db2916",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/11581",
        "xweb_xhr": "1",
        "content-type": "application/json",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/99/page-frame.html",
        "accept-language": "zh-CN,zh;q=0.9",
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params, headers=headers)
        json_data = res.json().get("items", [])
        for i in json_data:
            data = i.get("target", {})
            # 只获取有播放链接的
            if i.get("layout") != "subject" or not data.get("has_linewatch"):
                continue
            d_tv_num = re.findall("第(.*?)季", data.get("title", ""))
            if not d_tv_num:
                d_tv_num = re.findall(f"{name}(\d+)", data.get("title", ""))
            if not d_tv_num:
                roman_num = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
                roman_num_str = "|".join(roman_num)
                _d_tv_num = re.findall(
                    f"{name}([{roman_num_str}]+)", data.get("title", "")
                )
                if _d_tv_num and _d_tv_num[0] in roman_num:
                    d_tv_num = [roman_num.index(_d_tv_num[0])]
            if not d_tv_num:
                d_tv_num = "一"
            else:
                d_tv_num = d_tv_num[0]
            try:
                d_tv_num = cn2an.an2cn(int(d_tv_num))
            except (ValueError, TypeError):
                pass
            if name.split(" ")[0] in data.get("title", "") and (
                tv_num == name or d_tv_num == tv_num
            ):
                return i


async def douban_get_first_url(target_id):
    url = f"https://frodo.douban.com/api/v2/tv/{target_id}?apiKey=0ac44ae016490db2204ce0a042db2916"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/11581",
        "xweb_xhr": "1",
        "content-type": "application/json",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/99/page-frame.html",
        "accept-language": "zh-CN,zh;q=0.9",
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
    json_data = res.json().get("vendors", [])
    url_list = []
    for item in json_data:
        if item.get("url") and "douban" not in item.get("url").split("?")[0]:
            url_list.append(item.get("url"))
            continue
        if item.get("uri"):
            url_list.append(item.get("uri"))
    return url_list
