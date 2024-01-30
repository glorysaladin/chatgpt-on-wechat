#! coding: utf-8
import requests
url= "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
#应用凭证里的 app id 和 app secret
post_data = {"app_id": "cli_a5106f4b1279d013", "app_secret":"qVgiOT2ypsOXMDoifAdwAhNc6jzpPKUg"}

proxies = {"http":None, "https":None}
r = requests.post(url, data=post_data, proxies=proxies)
tat = r.json()["tenant_access_token"]
print(tat)
