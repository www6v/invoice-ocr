from datetime import datetime

def format_date(date_string):
    try:
        # 常见的输入格式处理
        formats = [
            '%Y%m%d',         # 20240309
            '%Y-%m-%d',       # 2024-03-09
            '%Y/%m/%d',       # 2024/03/09
            '%Y.%m.%d',       # 2024.03.09
            '%d/%m/%Y',       # 09/03/2024
            '%m/%d/%Y',       # 03/09/2024
            '%Y-%m-%d %H:%M:%S'  # 2024-03-09 12:30:45
        ]
        
        # 尝试不同的格式解析
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        raise ValueError("无法识别的日期格式")
        
    except Exception as e:
        return str(e)

# 使用示例
dates = [
    "",
    "20240309",
    "2024-03-09",
    "2024/03/09",
    "2024.03.09",
    "09/03/2024",
    "03/09/2024",
    "2024-03-09 12:30:45"
]


if __name__ == "__main__":
    for date in dates:
        formatted_date = format_date(date)
        print(f"原始日期: {date} -> 格式化后: {formatted_date}")