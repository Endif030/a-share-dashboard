#!/usr/bin/env python3
"""
A股复盘日报 - 独立HTML生成器
生成一个包含所有数据的完整HTML文件，可直接打开查看
"""

import json
import os
from datetime import datetime

class StandaloneHTMLGenerator:
    def __init__(self, base_dir="/root/.openclaw/workspace/skills/investment-daily"):
        self.base_dir = base_dir
        self.web_dir = f"{base_dir}/web"
        self.data_dir = f"{self.web_dir}/data"
    
    def load_json(self, filename):
        """加载JSON数据文件"""
        filepath = f"{self.data_dir}/{filename}"
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def generate_html(self):
        """生成完整的独立HTML文件"""
        
        # 加载数据
        latest = self.load_json("latest.json") or {}
        history = self.load_json("history_list.json") or []
        volume_trend = self.load_json("volume_trend.json") or {"dates": [], "volumes": []}
        index_trend = self.load_json("index_trend.json") or {"dates": [], "sh": []}
        sentiment = self.load_json("sentiment_trend.json") or {"dates": [], "limit_up": []}
        sectors = self.load_json("sector_heatmap.json") or []
        
        # 获取今日数据
        today_date = latest.get("date", datetime.now().strftime("%Y-%m-%d"))
        indices = latest.get("indices", {})
        total_amount = latest.get("total_amount", 0)
        market = latest.get("market_sentiment", {})
        
        # 构建HTML
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股复盘日报 - {today_date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header .date {{ color: #888; font-size: 1.1em; }}
        
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card-title {{
            font-size: 1.3em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .index-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}
        @media (max-width: 768px) {{
            .index-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        .index-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid;
        }}
        .index-card.up {{ border-left-color: #00c853; }}
        .index-card.down {{ border-left-color: #ff1744; }}
        
        .index-name {{ font-size: 0.9em; color: #888; margin-bottom: 8px; }}
        .index-value {{ font-size: 1.8em; font-weight: bold; margin-bottom: 8px; }}
        .index-change {{ font-size: 1.1em; font-weight: 600; }}
        .index-change.up {{ color: #00c853; }}
        .index-change.down {{ color: #ff1744; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
        }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
        }}
        
        .chart-container {{
            position: relative;
            height: 250px;
            margin-top: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        th {{ color: #888; font-weight: 500; font-size: 0.9em; }}
        tr:hover {{ background: rgba(255,255,255,0.02); }}
        
        .positive {{ color: #00c853; }}
        .negative {{ color: #ff1744; }}
        
        .sentiment-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        .sentiment-item {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .sentiment-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .sentiment-label {{ color: #888; font-size: 0.9em; }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 A股复盘日报</h1>
            <div class="date">{today_date} {self._get_weekday(today_date)}</div>
        </div>
        
        <!-- 指数行情 -->
        <div class="card">
            <div class="card-title">📈 主要指数行情</div>
            <div class="index-grid">
                {self._render_index_cards(indices)}
            </div>
        </div>
        
        <div class="grid">
            <!-- 量能趋势 -->
            <div class="card">
                <div class="card-title">💹 量能变化趋势</div>
                <div class="chart-container">
                    <canvas id="volumeChart"></canvas>
                </div>
                <div style="text-align: center; margin-top: 15px; font-size: 1.1em;">
                    今日成交额: <strong>{total_amount:.2f}</strong> 亿元
                </div>
            </div>
            
            <!-- 市场情绪 -->
            <div class="card">
                <div class="card-title">🎭 市场情绪</div>
                <div class="sentiment-grid">
                    <div class="sentiment-item">
                        <div class="sentiment-label">🟢 涨停家数</div>
                        <div class="sentiment-value" style="color: #00c853;">{market.get('limit_up', 0)}</div>
                    </div>
                    <div class="sentiment-item">
                        <div class="sentiment-label">🔴 跌停家数</div>
                        <div class="sentiment-value" style="color: #ff1744;">{market.get('limit_down', 0)}</div>
                    </div>
                    <div class="sentiment-item">
                        <div class="sentiment-label">📈 最高连板</div>
                        <div class="sentiment-value" style="color: #ffd700;">{market.get('max_height', 0)}连板</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <!-- 板块涨幅 -->
            <div class="card">
                <div class="card-title">🔥 板块涨幅 TOP10</div>
                <table>
                    <thead>
                        <tr><th>排名</th><th>板块</th><th>涨幅</th></tr>
                    </thead>
                    <tbody>
                        {self._render_sectors(latest.get('top_sectors', {}).get('gainers', [])[:10])}
                    </tbody>
                </table>
            </div>
            
            <!-- 涨停梯队 -->
            <div class="card">
                <div class="card-title">🚀 涨停梯队</div>
                <div class="chart-container">
                    <canvas id="ladderChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- 板块跌幅 -->
        <div class="card">
            <div class="card-title">❄️ 板块跌幅 TOP10</div>
            <table>
                <thead>
                    <tr><th>排名</th><th>板块</th><th>跌幅</th></tr>
                </thead>
                <tbody>
                    {self._render_sectors(latest.get('top_sectors', {}).get('losers', [])[:10], is_gainer=False)}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>简报由 claw 🦀 自动生成</p>
            <p>数据源：新浪财经 / 东方财富 / 财联社</p>
            <p>生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
    
    <script>
        // 量能趋势图
        const volumeCtx = document.getElementById('volumeChart').getContext('2d');
        new Chart(volumeCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(volume_trend.get('dates', []))},
                datasets: [{{
                    label: '成交额（亿元）',
                    data: {json.dumps(volume_trend.get('volumes', []))},
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#fff' }} }}
                }},
                scales: {{
                    x: {{ ticks: {{ color: '#888' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    y: {{ ticks: {{ color: '#888' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                }}
            }}
        }});
        
        // 涨停梯队图
        const ladder = {json.dumps(market.get('ladder', {}))};
        const ladderCtx = document.getElementById('ladderChart').getContext('2d');
        const ladderLabels = Object.keys(ladder).sort((a,b) => b-a).map(k => k + '连板');
        const ladderData = Object.keys(ladder).sort((a,b) => b-a).map(k => ladder[k]);
        
        new Chart(ladderCtx, {{
            type: 'bar',
            data: {{
                labels: ladderLabels,
                datasets: [{{
                    label: '家数',
                    data: ladderData,
                    backgroundColor: [
                        'rgba(255, 23, 68, 0.8)',
                        'rgba(255, 145, 0, 0.8)',
                        'rgba(255, 214, 0, 0.8)',
                        'rgba(0, 200, 83, 0.8)'
                    ],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ color: '#fff' }}, grid: {{ display: false }} }},
                    y: {{ ticks: {{ color: '#888' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def _get_weekday(self, date_str):
        """获取星期几"""
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return weekdays[dt.weekday()]
        except:
            return ''
    
    def _render_index_cards(self, indices):
        """渲染指数卡片"""
        html = ''
        for code, name in [('sh', '上证指数'), ('sz', '深证成指'), ('cy', '创业板指'), ('kc', '科创50')]:
            idx = indices.get(code, {})
            if not idx:
                continue
            is_up = idx.get('change_pct', 0) >= 0
            emoji = '🟢' if is_up else '🔴'
            html += f'''
                <div class="index-card {'up' if is_up else 'down'}">
                    <div class="index-name">{name}</div>
                    <div class="index-value">{idx.get('close', 0):.2f}</div>
                    <div class="index-change {'up' if is_up else 'down'}">
                        {emoji} {idx.get('change_pct', 0):+.2f}%
                    </div>
                    <div style="margin-top: 8px; color: #888; font-size: 0.85em;">
                        成交额: {idx.get('amount', 0):.0f}亿
                    </div>
                </div>
            '''
        return html
    
    def _render_sectors(self, sectors, is_gainer=True):
        """渲染板块列表"""
        html = ''
        for i, sector in enumerate(sectors, 1):
            change = sector.get('change', 0)
            css_class = 'positive' if change > 0 else 'negative'
            sign = '+' if change > 0 else ''
            html += f'''
                <tr>
                    <td>{i}</td>
                    <td><strong>{sector.get('name', '')}</strong></td>
                    <td class="{css_class}">{sign}{change:.2f}%</td>
                </tr>
            '''
        return html
    
    def save(self, output_file=None):
        """保存HTML文件"""
        if output_file is None:
            date_str = datetime.now().strftime("%Y%m%d")
            output_file = f"{self.web_dir}/report_{date_str}.html"
        
        html = self.generate_html()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML报告已生成: {output_file}")
        return output_file


def main():
    generator = StandaloneHTMLGenerator()
    output = generator.save()
    print(f"\n📄 文件大小: {os.path.getsize(output) / 1024:.1f} KB")
    print(f"🌐 你可以下载这个HTML文件到本地用浏览器打开查看")


if __name__ == "__main__":
    main()
