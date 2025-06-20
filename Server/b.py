import json

with open("service-account-key.json") as f:
    data = json.load(f)
    print(data["private_key"][:30])  # in thử vài ký tự đầu của private key
