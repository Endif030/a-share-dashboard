#!/usr/bin/env python3
"""
A股复盘网页数据生成器
将存档的JSON数据转换为网页可用的格式
"""

import json
import glob
import os
from datetime import datetime, timedelta
from pathlib import Path

class WebDataGenerator:
    """生成网页展示所需的数据"""
    
    def __init__(self, base_dir="/root/.openclaw/workspace/skills/investment-daily"):
        self.base_dir = base_dir
        self.archive_dir = f"{base_dir}/archive"
        self.web_dir = f"{base_dir}/web"
        
        # 确保目录存在
        os.makedirs(f"{self.web_dir}/data", exist_ok=True)
    
    def load_daily_data(self, date_str):
        """加载某日的数据"""
        year = date_str[:4]
        month = date_str[5:7]
        day = date_str[8:10]
        
        json_file = f"{self.archive_dir}/data/{year}/{month}/{day}.json"
        
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_history_dates(self, days=30):
        """获取最近N天的日期列表"""
        dates = []
        today = datetime.now()
        
        for i in range(days):
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            data = self.load_daily_data(date_str)
            if data:
                dates.append(date_str)
        
        return dates
    
    def generate_index_data(self):
        """生成指数行情数据"""
        dates = self.get_history_dates(30)
        
        result = {
            "dates": [],
            "sh": [],  # 上证指数
            "sz": [],  # 深证成指
            "cy": [],  # 创业板指
            "kc": []   # 科创50
        }
        
        for date_str in reversed(dates):  # 从早到晚排序
            data = self.load_daily_data(date_str)
            if data and "indices" in data:
                result["dates"].append(date_str[5:])  # 只显示 MM-DD
                result["sh"].append(data["indices"].get("sh", {}).get("change_pct", 0))
                result["sz"].append(data["indices"].get("sz", {}).get("change_pct", 0))
                result["cy"].append(data["indices"].get("cy", {}).get("change_pct", 0))
                result["kc"].append(data["indices"].get("kc", {}).get("change_pct", 0))
        
        return result
    
    def generate_volume_data(self):
        """生成成交量趋势数据"""
        dates = self.get_history_dates(30)
        
        result = {
            "dates": [],
            "volumes": [],
            "changes": []  # 环比变化
        }
        
        prev_volume = None
        for date_str in reversed(dates):
            data = self.load_daily_data(date_str)
            if data and "total_amount" in data:
                volume = data["total_amount"]
                result["dates"].append(date_str[5:])
                result["volumes"].append(round(volume, 2))
                
                if prev_volume and prev_volume > 0:
                    change = (volume - prev_volume) / prev_volume * 100
                    result["changes"].append(round(change, 2))
                else:
                    result["changes"].append(0)
                
                prev_volume = volume
        
        return result
    
    def generate_sentiment_data(self):
        """生成市场情绪数据"""
        dates = self.get_history_dates(30)
        
        result = {
            "dates": [],
            "limit_up": [],
            "limit_down": [],
            "max_height": []
        }
        
        for date_str in reversed(dates):
            data = self.load_daily_data(date_str)
            if data and "market_sentiment" in data:
                sentiment = data["market_sentiment"]
                result["dates"].append(date_str[5:])
                result["limit_up"].append(sentiment.get("limit_up", 0))
                result["limit_down"].append(sentiment.get("limit_down", 0))
                result["max_height"].append(sentiment.get("max_height", 0))
        
        return result
    
    def generate_sector_heatmap(self):
        """生成板块热度数据"""
        # 获取最近7天的板块数据
        dates = self.get_history_dates(7)
        
        sector_changes = {}
        
        for date_str in dates:
            data = self.load_daily_data(date_str)
            if data and "top_sectors" in data:
                for sector in data["top_sectors"].get("gainers", []):
                    name = sector["name"]
                    change = sector["change"]
                    if name not in sector_changes:
                        sector_changes[name] = []
                    sector_changes[name].append(change)
        
        # 计算平均涨幅
        result = []
        for name, changes in sector_changes.items():
            avg_change = sum(changes) / len(changes)
            result.append({
                "name": name,
                "avg_change": round(avg_change, 2),
                "days": len(changes)
            })
        
        # 按涨幅排序
        result.sort(key=lambda x: x["avg_change"], reverse=True)
        
        return result[:20]  # 返回前20
    
    def generate_latest_summary(self):
        """生成最新日报摘要"""
        dates = self.get_history_dates(1)
        if not dates:
            return None
        
        latest_date = dates[0]
        data = self.load_daily_data(latest_date)
        
        if not data:
            return None
        
        # 格式化数据
        summary = {
            "date": latest_date,
            "indices": {},
            "total_amount": data.get("total_amount", 0),
            "market_sentiment": data.get("market_sentiment", {}),
            "top_sectors": data.get("top_sectors", {"gainers": [], "losers": []})
        }
        
        # 转换指数数据
        for code, name in [("sh", "上证指数"), ("sz", "深证成指"), 
                           ("cy", "创业板指"), ("kc", "科创50")]:
            if code in data.get("indices", {}):
                idx = data["indices"][code]
                summary["indices"][code] = {
                    "name": name,
                    "close": idx.get("close", 0),
                    "change_pct": idx.get("change_pct", 0),
                    "change_val": idx.get("change_val", 0),
                    "amount": idx.get("amount", 0) / 100000000  # 转换为亿
                }
        
        return summary
    
    def generate_all_data(self):
        """生成所有数据文件"""
        print("🔄 生成网页数据...")
        
        # 1. 指数趋势数据
        index_data = self.generate_index_data()
        with open(f"{self.web_dir}/data/index_trend.json", 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 指数趋势: {len(index_data['dates'])} 天数据")
        
        # 2. 成交量数据
        volume_data = self.generate_volume_data()
        with open(f"{self.web_dir}/data/volume_trend.json", 'w', encoding='utf-8') as f:
            json.dump(volume_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成交量趋势: {len(volume_data['dates'])} 天数据")
        
        # 3. 市场情绪数据
        sentiment_data = self.generate_sentiment_data()
        with open(f"{self.web_dir}/data/sentiment_trend.json", 'w', encoding='utf-8') as f:
            json.dump(sentiment_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 情绪趋势: {len(sentiment_data['dates'])} 天数据")
        
        # 4. 板块热度
        sector_data = self.generate_sector_heatmap()
        with open(f"{self.web_dir}/data/sector_heatmap.json", 'w', encoding='utf-8') as f:
            json.dump(sector_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 板块热度: {len(sector_data)} 个板块")
        
        # 5. 最新摘要
        latest_data = self.generate_latest_summary()
        if latest_data:
            with open(f"{self.web_dir}/data/latest.json", 'w', encoding='utf-8') as f:
                json.dump(latest_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 最新数据: {latest_data['date']}")
        
        # 6. 历史列表
        history_dates = self.get_history_dates(365)
        history_list = []
        for date_str in history_dates:
            data = self.load_daily_data(date_str)
            if data and "indices" in data:
                sh_change = data["indices"].get("sh", {}).get("change_pct", 0)
                history_list.append({
                    "date": date_str,
                    "sh_change": round(sh_change, 2),
                    "volume": round(data.get("total_amount", 0), 0)
                })
        
        with open(f"{self.web_dir}/data/history_list.json", 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
        print(f"✅ 历史列表: {len(history_list)} 条记录")
        
        print("\n🎉 数据生成完成！")
        return True


def main():
    """主函数"""
    generator = WebDataGenerator()
    generator.generate_all_data()


if __name__ == "__main__":
    main()
