from opt_einsum import contract

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
contract_prompt = """以上是合同相关图片，利用orc识别出图片内容，再从内容中提取以下字段：合同类型，合同编号，购买方名称，销售方名称，合同总金额，签订日期，贸易类型。合同类型只有{"合同","订单"}默认"合同"，贸易类型只有{"货物贸易","服务贸易","货服贸易","其他"}，
                      相关字段要以json格式输出"""