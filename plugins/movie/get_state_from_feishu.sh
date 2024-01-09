WK_DIR=$(dirname $(readlink -f $0))
python=`which python`
tat=$($python $WK_DIR/get_feishu_tat.py)
curl --location --request GET 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/Uz9tsZ7fHhV3Fgt7jWMcBl8VnNg/values/47b15e!B2:C30?valueRenderOption=ToString&dateTimeRenderOption=FormattedString' \
--header 'Authorization: Bearer '${tat}