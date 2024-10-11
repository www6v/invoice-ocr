# API 文档

## 发票类型
- 电子发票（增值税专用发票）
- 电子发票（普通发票）
- xxx增值税专用发票
- xxx增值税电子专用发票
- xxx增值税普通发票
- xxx增值税电子普通发票
- 
## 接口描述

- **接口名称：** `extract-key-info`
- **接口描述：** `提取图片、pdf格式的发票与合同关键信息，并json格式化输出`
- **请求方法：** `POST`
- **请求URL：** `http://101.237.37.102:9999/api/v1/extract-key-info`

## 请求头

- **Content-Type：** `application/json` 
- **Authorization：** `Bearer {token}` 

## 请求参数

- **请求格式：** `JSON`
- **请求参数：**

| 参数名 | 类型   | 是否必填 | 默认值 | 描述               |  
| ------ | ------ | -------- | ------ | ------------------ |  
| flowId | String | 是       | 无     | 请求流id，用来追溯        |  
| taskType | String    | 是       | 无      | 任务类型，发票/合同/名单        |  
| fileId | String  | 是       | 无     | 文件id        |  
| content | String  | 是       | 无     | base64编码的文件内容        |  
| fileType | String  | 是       | 无     | png/jpg/pdf/doc/docx/ofd        |  

- **请求示例：**

  ```json
  {
      "flowId":"1234",
      "taskType": "001",
      "fileId": "abc",
      "content":"base64",
      "fileType":"png"
  }
  ```

## 响应参数-根据不同任务类型，参数res内容不同
- **响应格式：** `JSON`
- **响应参数：**

| 参数名       | 类型     | 描述        |
|-----------|--------|-----------|
| flowId    | String | 工作流id     |
| taskType  | String | 任务类型      |
| result    | Dict   | ocr结果     |
| retStatus | Int    | 0:成功，1:失败 |
| retMsg    | String | 失败原因      |

- **发票任务相应示例：**

| result字段 | 类型     | 描述              |
|----|--------|-----------------|
| invoiceNo | String | 发票号码            |
| invoiceCode | String | 发票代码            |
| invoiceType | String | 发票类型            |
| invoiceDate | String | 开票日期 yyyy-mm-dd |
| buyerName | String | 购方名称            |
| sellerName | String | 销方名称            |
| buyerSocialNo | String | 购方名称统信码         |
| sellerSocialNo | String | 销方名称统信码         |
| invoiceAmt | String | 价税合计            |
| invoiceAmtNoTax | String | 不含税金额           |
| invRemark | String | 备注              |

  ```json
      {
          "flowId": 202408260000101001,
          "taskType": "001",
          "retStatus": 0,
          "retMsg": "处理成功",
          "result": {
          "invoiceList": [
          {
          "invoiceType": "IT01", 
          "invoiceNo":"1724728701055109881",
          "invoiceCode":"172472870105",
          "invoiceDate":"2024-07-03",
          "buyerName":"河北省安装工程有限公司",
          "buyerSocialNo":"93021102229301211X"
          "sellerName":"佛山市兴海铜铝业有限公司",
          "sellerSocialNo":"91091102495523091",
          "invoiceAmt":1000000
          "invoiceAmtNoTax":970873.79,
          "invRemark":""
          },
          {
          "invoiceType": "IT01", 
          "invoiceNo":"1724728701056109882",
          "invoiceCode":"1724728701056",
          "invoiceDate":"2024-07-03",
          "buyerName":"河北省安装工程有限公司",
          "buyerSocialNo":"93021102229301211X"
          "sellerName":"佛山市兴海铜铝业有限公司",
          "sellerSocialNo":"91091102495523091",
          "invoiceAmt":1000000,
          "invoiceAmtNoTax":970873.79,
          "invRemark":""}]
          }
      }
  ```
  
- **合同任务响应示例：**

| res字段      | 类型     | 描述      |
|------------|--------|---------|
| contractNo         | String | 合同编号    |
| contractType       | String | 合同类型    |
| contractDate  | String | 合同日期    |
| buyerName  | String | 购方名称    |
| sellerName | String | 销方名称    |
| buyerSocialNo    | String | 购方名称统信码 |
| sellerSocialNo   | String | 销方名称统信码 |
| contractTradeType   | String | 交易类型    |
| contractAmt   | String | 交易金额    |

  ```json
      {
      "flowId": 202408260000101001,
      "taskType": "001",
      "retStatus": 0,
      "retMsg": "处理成功",
      "result": {
      "contract": {
      "contractNo": "123456(GP)",
      "contractType": "合同",
      "contractDate": "2024-06-23",
      "contractTradeType": "货物贸易",
      "contractAmt": 5000000,
      "buyerName": "河北省安装工程有限公司",
      "buyerSocialNo": "",
      "sellerName": "佛山市兴海铜铝业有限公司",
      "sellerSocialNo": ""}}
      }
  ```

- **名单任务相应示例：**

| res字段      | 类型     | 描述          |
|------------|--------|-------------|
| no         | String | 名单序号        |
| custList       | String | 公司类型        |
| brhList  | String | 机构类型        |
| name    | String | 名称          |
| code   | String | 代码（统信码/机构码） |

  ```json
   {
    "flowId": 202408260000101001,
    "taskType": "001",
    "retStatus": 0,
    "retMsg": "处理成功",
    "result": {
    "custList": [
        {
        "no":"1",
        "name": "天元建设集团有限公司",
        "code": "913713001682510225"},
        {
        "no":"2",
        "name": "金科地产集团股份有限公司",
        "code": "91500000202893468X"}],
    "brhList": [
        {
        "no":"1",
        "name": "郑州银行股份有限公司",
        "code": "313491000232",}]
    }
    }
    ```

## 错误码

| 错误码 | 描述                   | 解决方案             |
| ------ | ---------------------- | -------------------- |
| 400    | Bad Request             | 检查请求参数是否正确 |
| 401    | Unauthorized            | 检查认证信息         |
| 403    | Forbidden               | 权限不足             |
| 500    | Internal Server Error   | 服务器内部错误       |

## 注意事项

- **参数校验：** 参数的类型和格式必须符合要求。
- **认证与授权：** 如果接口需要认证，请确保提供正确的Token。
- **速率限制：** 每个用户每分钟最多调用 `N` 次。
