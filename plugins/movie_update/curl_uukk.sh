moviename=$1
curl 'http://uukk6.cn/v/api/getJuzi' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Cookie: Hm_lvt_cce07f87930c14786d9eced9c08d0e89=1699114247,1700320320,1700750079,1701444675; Hm_lpvt_cce07f87930c14786d9eced9c08d0e89=1701619211' \
  -H 'Origin: http://uukk6.cn' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data 'name='$moviename'&token=i69' \
  --compressed \
  --insecure
