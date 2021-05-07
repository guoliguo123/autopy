from services import StartServers, ListServers

prefix = 'kunpeng-compute-node'

servers_info, status_code = ListServers.call(limit=50, name=prefix)
if not servers_info['count']:
    print('No servers found, skip start')
    exit(0)

# start servers
server_ids = [{'id': s['id']} for s in servers_info['servers']]
start_result, status_code = StartServers.call(server_ids)
print(start_result)

