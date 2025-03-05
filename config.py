zy_pattern = r'.*专用.*'
pt_pattern = r'.*普通*'
dz_pattern = r'电子.*(?:普通|专用).*发票'
code_pattern = r'\d{8,20}'
y_m_d_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
hans_num_pattern = r'[零壹贰叁肆伍陆柒捌玖拾佰仟万亿圆元角分整]+'
letter_num_pattern = r'[A-Za-z0-9]+'
amt_num_pattern = r"\b\d+(?:\.\d+)?\b"
dir_path = '/data/ocr-file/'
min_pixels = 256 * 28 * 28
max_pixels = 1280 * 28 * 28
json_pattern = r'```json(.*?)```'
schema = ["invoice-type","invoice-no","invoice-code","invoice-date","invoice-buyer-id","invoice-buyer","invoice-amt-num","invoice-seller","invoice-seller-id","invoice-amt-chn","invoice-amt-not-tax","invoice-amt-tax"]
contract_prompt = """
                    ##  任务
                        你是一位合同关键信息抽取专家，专注于从内容中抽取合同类型，合同编号，购买方名称，销售方名称，合同总金额，签订日期，贸易类型，并以json格式输出。

                    ## 技能
                        ### 技能 1：抽取合同类型
                        1. 类型只有{"合同"，"定单"}。根据内容或标题判定具体类型，无法判断时选择默认值 "合同"。

                        ### 技能 2：抽取合同编号
                        1. 精准提取合同编号信息。

                        ### 技能 3：抽取购买方名称
                        1. 精准提取合同中的购买方名称。

                        ### 技能 4：抽取销售方名称
                        1. 精准提取合同中的销售方名称。

                        ### 技能 5：抽取合同总金额
                        1. 精准提取合同的总金额，优先提取大写金额，同时提取到大写金额和小写金额时只保留大写金额，未提取到时输出默认值0。

                        ### 技能 6：抽取签订日期
                        1. 精准提取合同的签订日期。

                        ### 技能 7：抽取贸易类型
                        1. 类型只有{"货物贸易","服务贸易","货服贸易","其他"}。
                        2. 请根据交付物品的类型推测具体类型，如服装/钢材/机器设备等实体物品为"货物贸易", 咨询费/培训/系统设计/软件开发等非实体物品为"服务贸易"，既有实体物品又有非实体物品则为"货服贸易"，无法判定时选择默认值 "其他"。
                    
                    ## 输出
                        按照json格式输出，key为合同类型，合同编号，购买方名称，销售方名称，合同总金额，签订日期，贸易类型。
                    ## 示例：
                        {"合同类型": "xxxx",
                        "合同编号": "XXXXXX",
                        "购买方名称": "XXXX公司",
                        "销售方名称": "YYYY公司",
                        "合同总金额": "xxxx",
                        "签订日期": "xxx",
                        "贸易类型": "xxxx"}
                """
