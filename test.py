import deluge_cli

resp = deluge_cli.main('ls')
for el in list(resp):
    print(el)

# print(resp)
