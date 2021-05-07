from services import CreateOnDemandServer, ListServers, vpc_id
import json
import secrets
import os

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

create_result, status_code = CreateSFS.call(name='dxwind-wrf-sfs', ShareProto='NFS', ShareType='STANDARD', 
                                                      Size=100, az='cn-north-4b', vpc_id, nics,SecurityGroup=security_groups)
print(create_result, status_code)