import json,re,urllib.request
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t=='td' and self.row is not None:self.cell=''
 def handle_data(self,d):
  if self.cell is not None:self.cell+=d
 def handle_endtag(self,t):
  if t=='td' and self.cell is not None:self.row.append(self.cell.strip());self.cell=None
  if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
p=Path('rate.json');old=json.loads(p.read_text()) if p.exists() else {};now=datetime.now(timezone.utc).isoformat()
try:
 req=urllib.request.Request('https://rate.bot.com.tw/xrt?Lang=zh-TW',headers={'User-Agent':'SeoulTravelHandbook/1.0'})
 html=urllib.request.urlopen(req,timeout=30).read().decode('utf-8');parser=Table();parser.feed(html)
 row=next(r for r in parser.rows if any('KRW' in c for c in r))
 values=[x for x in row if re.fullmatch(r'\d+\.\d+|-',x)]
 rate=float(values[1]);assert 0<rate<1
 match=re.search(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}',html);assert match
 date=match.group().replace('/','-').replace(' ','T')+':00+08:00'
 result=dict(source='台灣銀行',kind='韓元現金賣出',rate=rate,publishedAt=date,checkedAt=now,status='ok',sourceUrl='https://rate.bot.com.tw/xrt?Lang=zh-TW',note='每小時嘗試更新；以實際掛牌時間為準。')
except Exception:
 result={**old,'checkedAt':now,'status':'error','note':'官方資料擷取失敗，保留上次報價；請開啟台銀官網核對。'}
p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
