moviename=$1
curl 'https://v.funletu.com/search' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://pan.funletu.com' \
  -H 'Referer: https://pan.funletu.com/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data '{"style":"get","datasrc":"search","query":{"id":"","datetime":"","commonid":1,"parmid":"","fileid":"","reportid":"","validid":"","searchtext":"'$moviename'"},"page":{"pageSize":10,"pageIndex":1},"order":{"prop":"id","order":"desc"},"message":"请求资源列表数据"}' \
  --compressed
