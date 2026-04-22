import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from pathlib import Path


SEARCH_KEYWORDS = [
    "site:jxau.edu.cn 江西农业大学 学生管理规定",
    "site:jxau.edu.cn 江西农业大学 学籍管理 规定",
    "site:jxau.edu.cn 江西农业大学 处分办法",
    "site:jxau.edu.cn 江西农业大学 规章制度"
]

MAX_URLS_PER_KEYWORD = 3
OUTPUT_FILE = Path("data/raw/jxau_real_rules.txt")
TIMEOUT_MS = 45000

FALLBACK_URLS = [
    "https://jwc.jxau.edu.cn/info/1311/9571.htm",
    "https://jwc.jxau.edu.cn/info/1641/1021.htm",
    "https://nongxue.jxau.edu.cn/info/1057/1313.htm",
    "https://jwc.jxau.edu.cn/gzzd/xjgl.htm",
]


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def extract_main_content(html: str, url: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
        tag.decompose()

    for element in soup.find_all(class_=re.compile(r'nav|menu|sidebar|footer|header|breadcrumb|toolbar|advertisement|sidebar|comment|share', re.I)):
        element.decompose()

    for element in soup.find_all(id=re.compile(r'nav|menu|sidebar|footer|header|breadcrumb|toolbar|advertisement|sidebar|comment|share', re.I)):
        element.decompose()

    main_content = []

    content_area = soup.find('div', class_=re.compile(r'content|article|main|text|detail|show', re.I))
    if content_area:
        for p in content_area.find_all('p'):
            text = p.get_text()
            text = clean_text(text)
            if len(text) > 15:
                main_content.append(text)
    else:
        for p in soup.find_all('p'):
            text = p.get_text()
            text = clean_text(text)
            if len(text) > 15:
                main_content.append(text)

    if not main_content:
        for div in soup.find_all('div'):
            classes = div.get('class', [])
            div_id = div.get('id', '')
            if any(nav in ' '.join(classes) + ' ' + div_id for nav in ['nav', 'menu', 'sidebar', 'footer', 'header']):
                continue
            text = div.get_text()
            text = clean_text(text)
            if 30 < len(text) < 2000:
                main_content.append(text)

    return '\n'.join(main_content)


async def search_bing(keyword: str, page: Page) -> list[str]:
    print(f"[搜索] 关键词: {keyword}")
    urls = []

    try:
        encoded_keyword = keyword.replace(' ', '+')
        search_url = f"https://www.bing.com/search?q={encoded_keyword}&setlang=zh-CN"
        print(f"      URL: {search_url}")

        await page.goto(search_url, timeout=TIMEOUT_MS, wait_until='domcontentloaded')
        await page.wait_for_load_state('networkidle', timeout=TIMEOUT_MS)
        await asyncio.sleep(3)

        selectors = [
            'li.b_algo h2 a',
            'div.b_title h2 a',
            'article h2 a',
            '.b_results li a',
            'div.sb_add sb_aPA',
            'a[href*="jxau.edu.cn"]',
        ]

        found_urls = set()

        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"      选择器 '{selector}' 匹配到 {len(elements)} 个元素")
            for elem in elements:
                href = await elem.get_attribute('href')
                if href and 'jxau.edu.cn' in href and href not in found_urls:
                    found_urls.add(href)

        for i, href in enumerate(list(found_urls)[:MAX_URLS_PER_KEYWORD]):
            if href.startswith('http://') or href.startswith('https://'):
                print(f"  [{i+1}] {href}")
                urls.append(href)
            else:
                print(f"  [跳过无效URL] {href}")
            await asyncio.sleep(0.5)

        if not urls:
            print("  [警告] 未找到 jxau.edu.cn 相关链接")

    except Exception as e:
        print(f"  [错误] 搜索失败: {type(e).__name__}: {e}")

    return urls


async def fetch_page_content(page: Page, url: str) -> tuple[str, str]:
    print(f"[抓取] 访问: {url}")
    content = ""
    title = ""

    try:
        await page.goto(url, timeout=TIMEOUT_MS, wait_until='domcontentloaded')
        await page.wait_for_load_state('networkidle', timeout=TIMEOUT_MS)
        await asyncio.sleep(2)

        title = await page.title()
        print(f"  [标题] {title[:80]}")

        html = await page.content()
        content = extract_main_content(html, url)

        if content:
            lines = [l for l in content.split('\n') if len(l) > 15]
            print(f"  [成功] 提取到 {len(lines)} 行有效内容 ({len(content)} 字符)")
        else:
            print(f"  [警告] 未提取到有效内容")

    except Exception as e:
        print(f"  [错误] 抓取失败: {type(e).__name__}: {e}")

    return title, content


async def main():
    print("=" * 60)
    print("江西农业大学规章制度采集脚本")
    print("=" * 60)

    all_rules = []
    all_urls = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="zh-CN"
        )
        page = await context.new_page()

        for keyword in SEARCH_KEYWORDS:
            print(f"\n[开始] 处理关键词: {keyword}")
            print("-" * 50)

            urls = await search_bing(keyword, page)
            all_urls.extend(urls)
            await asyncio.sleep(3)

        all_urls = list(dict.fromkeys(all_urls))

        if not all_urls:
            print("\n[备选] 搜索未获取到URL，使用预设的 Fallback URLs")
            all_urls = FALLBACK_URLS

        print(f"\n[汇总] 共获取 {len(all_urls)} 个唯一URL")

        for i, url in enumerate(all_urls, 1):
            print(f"\n[进度] ({i}/{len(all_urls)})")
            print("-" * 50)
            title, content = await fetch_page_content(page, url)

            if content:
                all_rules.append(f"\n{'='*60}")
                all_rules.append(f"来源: {url}")
                all_rules.append(f"标题: {title}")
                all_rules.append(f"{'='*60}\n")
                all_rules.append(content)

            await asyncio.sleep(3)

        await browser.close()

    if all_rules:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        header = f"""江西农业大学规章制度采集结果
采集时间: {timestamp}
数据来源: {len(all_urls)} 个网页
{'='*60}

"""

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write('\n'.join(all_rules))

        print(f"\n{'='*60}")
        print(f"[完成] 已保存到: {OUTPUT_FILE}")
        print(f"[统计] 共写入 {len(all_rules)} 个规则段落")
        print(f"{'='*60}")
    else:
        print("\n[警告] 未获取到任何有效内容")


if __name__ == "__main__":
    asyncio.run(main())
