import requests
from apig_sdk import signer
from os import environ
from urllib import parse
import secrets
import os
import json

AK = environ['AK'] if 'AK' in environ else 'YOUR_AK'
SK = environ['SK'] if 'SK' in environ else 'YOUR_SK'
project_id = environ['project_id'] if 'project_id' in environ else 'YOUR_project_id'
region = environ['region'] if 'region' in environ else 'YOUR_region'
sig = signer.Signer()
sig.Key = AK
sig.Secret = SK

vpc_id = '6de3f8c3-fa9c-40e6-ba12-52d6c5e31db0'


class BasicService:
    schema = 'https'
    _singleton = None

    def construct_request_params(self, *args, **kwargs):
        if kwargs:
            self.canonical_qs = parse.urlencode(kwargs)

    @classmethod
    def call(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = cls()
        cls._singleton.req_body = ''
        cls._singleton.construct_request_params(*args, **kwargs)
        request_url = f'{cls._singleton.__class__.url_base}{cls._singleton.canonical_uri}'
        if cls._singleton.canonical_qs:
            request_url = f'{request_url}?{cls._singleton.canonical_qs}'

        r = signer.HttpRequest(cls._singleton.http_method, request_url,
                               body=cls._singleton.req_body)
        sig.Sign(r)
        r.headers['X-Project-Id'] = project_id
        r.headers['Content-Type'] = 'application/json'
        # If uri already takes query string, then don't pass r.query to 'params' argument
        # or it will be handled twice, the value becomes a list with 2 same elements.
        res = requests.request(r.method, request_url, headers=r.headers, data=r.body)
        print('original res:', res.text, res.status_code)
        res_obj = res.text
        try:
            res_obj = res.json()
        except Exception:
            pass

        return res_obj, res.status_code


class EcsService(BasicService):
    schema = 'https'
    endpoint = f'ecs.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'


class ListServers(EcsService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/cloudservers/detail'
        self.canonical_qs = ''


class DeleteServers(EcsService):

    def __init__(self):
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/cloudservers/delete'
        self.canonical_qs = ''
        self.req_body = ''

    def construct_request_params(self, servers, delete_publicip=False, delete_volume=True):
        req_payload = {
            'servers': servers,
        }

        if delete_publicip:
            req_payload['delete_publicip'] = True
        if delete_volume:
            req_payload['delete_volume'] = True

        self.req_body = json.dumps(req_payload)
        print(json.dumps(req_payload, indent=2))


# Instance specs:
# https://support.huaweicloud.com/productdesc-ecs/ecs_01_0008.html
class CreateOnDemandServer(EcsService):

    def __init__(self):
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/cloudservers'
        self.canonical_qs = ''
        self.req_body = ''

    def construct_request_params(self, name, vpc_id, nics, root_vol, az='cn-north-4b',
                                 security_groups=[], image_ref='6c2df4f9-eea4-4943-82e4-b835db24302d',
                                 flavor_ref='kc1.8xlarge.4', dry_run=True, public_ip='', count=1,
                                 is_auto_rename=False, admin_pass='youshouldpasssomething!'):
        req_payload = {
            'server': {
                'imageRef': image_ref,
                'flavorRef': flavor_ref,
                'name': name,
                'vpcid': vpc_id,
                'nics': nics,
                'root_volume': root_vol,
                'count': count,
                'security_groups': security_groups,
                'availability_zone': az,
                'adminPass': admin_pass,
                'isAutoRename': is_auto_rename,
            },
            'dry_run': 'true' if dry_run else 'false',
        }
        if public_ip:
            req_payload['publicip'] = public_ip

        self.req_body = json.dumps(req_payload)
        # print(json.dumps(req_payload, indent=2))

class CreateSFS(EcsService):
    def __init__(self):
        #POST /v1/{project_id}/sfs-turbo/shares
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/sfs-turbo/shares'
        self.canonical_qs = ''
        self.req_body = ''
    def construct_request_params(self, name, ShareProto='NFS', ShareType, Size='100', az='cn-north-4b', VpcId, SubnetId,
                                        SecurityGroupId, CryptKeyId, DedicatedFlavor, MasterDedicatedHostId, 
                                        SlaveDedicatedHostId, DedicatedStorageId):
       req_payload = {
            "share": {
                "name": name, 
                "share_proto": ShareProto,
                "share_type": ShareType,
                "size": Size,
                "availability_zone": az, 
                "vpc_id": VpcId, 
                "subnet_id": SubnetId,
                "security_group_id": SecurityGroupId, 

            #"metadata": {
            #                   "crypt_key_id": CryptKeyId, 
            #                   "dedicated_flavor": DedicatedFlavor, 
            #                   "master_dedicated_host_id": MasterDedicatedHostId, 
            #                   "slave_dedicated_host_id": SlaveDedicatedHostId, 
            #                   "dedicated_storage_id": DedicatedStorageId
            #               }
                       }
        }
        self.req_body = json.dumps(req_payload)

class StopServers(EcsService):

    def __init__(self):
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/cloudservers/action'
        self.canonical_qs = ''
        self.req_body = ''

    def construct_request_params(self, servers, type='SOFT'):
        self.req_body = json.dumps(
            {
                'os-stop' : {
                    'servers': servers,
                    'type': type
                }
            }
        )

class StartServers(EcsService):

    def __init__(self):
        self.http_method = 'POST'
        self.canonical_uri = f'/v1/{project_id}/cloudservers/action'
        self.canonical_qs = ''
        self.req_body = ''

    def construct_request_params(self, servers):
        self.req_body = json.dumps(
            {
                'os-start' : {
                    'servers': servers
                }
            }
        )

class ImageService(BasicService):
    schema = 'https'
    endpoint = f'ims.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'


class ListImages(ImageService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v2/cloudimages'
        self.canonical_qs = ''

    # def construct_request_params(self, image_type='gold', visibility='public', protected='true'):
    #     self.canonical_qs = f'__imagetype={image_type}&visibility={visibility}&protected={protected}'


class VpcService(BasicService):
    schema = 'https'
    endpoint = f'vpc.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'


class ListVpcs(VpcService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/vpcs'
        self.canonical_qs = ''


class ListSubnets(VpcService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = f'/v1/{project_id}/subnets'
        self.canonical_qs = ''

    def construct_request_params(self, limit=10, marker='', vpc_id=''):
        self.canonical_qs = f'limit={limit}'
        if marker:
            self.canonical_qs += f'&marker={marker}'
        if vpc_id:
            self.canonical_qs += f'&vpc_id={vpc_id}'


class JobService(BasicService):
    schema = 'https'
    endpoint = f'ecs.{region}.myhuaweicloud.com'
    url_base = f'{schema}://{endpoint}'


class CheckJob(JobService):

    def __init__(self):
        self.http_method = 'GET'
        self.canonical_uri = ''
        self.canonical_qs = ''

    def construct_request_params(self, job_id):
        self.canonical_uri = f'/v1/{project_id}/jobs/{job_id}'  # end with job_id
