from services import CreateOnDemandServer, ListServers, vpc_id
import json
import secrets
import os

#prefix = 'dxwind-compute-node'
prefix = 'kunpeng-compute-node'
if os.path.exists('./prefix'):
    with open('./prefix', 'r') as f:
        prefix = f.read()

root_volume = {
    'volumetype': 'SSD',  # One of 'SSD', 'GPSSD', 'SAS'
    'size': 100,  # Unit: GB
}
#子网
nics = [
    {
        'subnet_id': 'bb64d226-14a4-4e13-afcb-ccda97cdf4e5'
    }
]
#安全组
security_groups = [
    {
        'id': '08bc3b69-08e8-449d-ab55-0f7d141c07a0'
    }
]

servers_info, status_code = ListServers.call(limit=50, name=prefix)
print(servers_info['count'])
max_id = 0
total_amount = 10
for server in servers_info['servers']:
    # print(server['name'], server['id'], server['addresses'][vpc_id][0]['addr'])
    server_id_num = int(str.split(server['name'], prefix)[-1])
    if max_id < server_id_num:
        max_id = server_id_num

print(max_id, servers_info['count'])
print(f'there are {total_amount-max_id} servers to create')
passwd = secrets.token_urlsafe(16)
if os.path.exists('./passwd'):
    with open('./passwd', 'r') as f:
        passwd = f.read()
else:
    with open('./passwd', 'w') as f:
        f.write(passwd)
print('create with passwd:', passwd)
num_servers_to_create = total_amount - max_id

publicip = {
    'eip': {
        'iptype': '5_bgp',
        'bandwidth': {
            'size': 300,
            'charge_mode': 'traffic',
            'share_type': 'PER'
        }

    }
}
#镜像
	
image_ref = '6c2df4f9-eea4-4943-82e4-b835db24302d'   # Customized image node-nwp (arm64)
#image_ref = '1a752e88-6fdc-426b-b764-f811664db62d'  # Customized image node-nwp (x86_64)
# image_ref = '6de3f8c3-fa9c-40e6-ba12-52d6c5e31db0'  # CentOS 7.5
if num_servers_to_create:
    name = f'{prefix}[1,1]'  # start from 1, the num takes 1 bit
    if max_id >= 1:
        name = f'{prefix}[{max_id+1},1]'
    try:
        create_result, status_code = CreateOnDemandServer.call(name, vpc_id, nics,
                                                               root_volume, security_groups=security_groups, image_ref=image_ref,
                                                               flavor_ref='kc1.8xlarge.4', dry_run=False , # public_ip=publicip,
                                                               count=num_servers_to_create, admin_pass=passwd)
        print(create_result)
    except Exception as e:
        print(e)

else:
    servers_info, status_code = ListServers.call(limit=60, name=prefix)
    for s in servers_info['servers']:
        print(s['addresses'][vpc_id][0]['addr'], '\t', s['name'])


