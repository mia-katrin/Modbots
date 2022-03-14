from mlagents_envs.environment import UnityEnvironment
import socket
import time

HIGHEST_WORKER_ID = 65535 - UnityEnvironment.BASE_ENVIRONMENT_PORT

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def is_worker_id_open(worker_id: int) -> bool:
    return not is_port_in_use(
        UnityEnvironment.BASE_ENVIRONMENT_PORT + worker_id
    )

start = time.time()
for _ in range(25):
    for id in range(0, HIGHEST_WORKER_ID):
        if not is_worker_id_open(id):
            print(id, "is not open")
print(time.time() - start)
