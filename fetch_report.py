import yfinance as yf
import datetime
import os
import requests

# ========== 【这里改你的配置】 ==========
WORKBUDDY_WEBHOOK = "在这里粘贴你WorkBuddy小程序的推送webhook地址"
LOG_FILE = "tech_log.md"
TIME_ZONE = "Asia/Shanghai"
# 跟踪标的配置
SYMBOLS = [
    {"name": "纳斯达克综合", "code": "^IXIC"},
    {"name": "纳指100", "code": "^NDX"},
    {"name": "英伟达", "code": "NVDA"},
    {"name": "微软", "code": "MSFT"},
    {"name": "AMD", "code": "AMD"},
    {"name": "台积电ADR", "code": "TSM"},
    {"name": "韩国KOSPI", "code": "^KS11"},
    {"name": "韩国KOSDAQ", "code": "^KQ11"},
    {"name": "三星电子", "code": "005930.KS"},
    {"name": "SK海力士", "code": "000660.KS"},
]
# =======================================

def get_quote(ticker_code):
    try:
        tk = yf.Ticker(ticker_code)
        hist = tk.history(period="2d")
        if len(hist) < 2:
            return None
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        close = latest["Close"]
        prev_close = prev["Close"]
        change = close - prev_close
        pct = change / prev_close * 100
        return {
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "change": round(change, 2),
            "pct": round(pct, 2)
        }
    except Exception as e:
        print(f"拉取 {ticker_code} 失败: {e}")
        return None

def build_markdown(date_str):
    lines = []
    lines.append(f"# 美韩科技股增量趋势日志 | {date_str}")
    lines.append("> 说明：美股为隔夜收盘；韩股为当日盘中/收盘数据；自动环比前一交易日；仅行情汇总，不构成投资建议")
    lines.append("")
    lines.append("|品种|最新收盘|前收|涨跌|涨跌幅%|")
    lines.append("| ---- | ---- | ---- | ---- | ---- |")

    success_list = []
    for item in SYMBOLS:
        res = get_quote(item["code"])
        if res is None:
            lines.append(f"|{item['name']}|❌获取失败|-|-|-|")
            continue
        row = f"|{item['name']}|{res['close']}|{res['prev_close']}|{res['change']}|{res['pct']}|"
        lines.append(row)
        success_list.append(row)
    lines.append("\n---\n")
    md_content = "\n".join(lines)
    return md_content

def append_to_log(md):
    # 增量追加模式，历史全部保留，形成趋势台账
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            old = f.read()
    else:
        old = ""
    new_full = md + "\n\n" + old
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(new_full)
    return md

def push_workbuddy(content):
    payload = {
        "title": "【每日美韩科技行情】",
        "content": content
    }
    try:
        r = requests.post(WORKBUDDY_WEBHOOK, json=payload, timeout=15)
        print("推送返回：", r.text)
    except Exception as e:
        print("推送失败：", e)

if __name__ == "__main__":
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report_md = build_markdown(today)
    append_to_log(report_md)
    push_workbuddy(report_md)
