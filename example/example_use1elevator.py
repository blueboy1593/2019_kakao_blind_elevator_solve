import requests
from pprint import pprint

url = 'http://localhost:8000'


def start(user, problem, count):
    uri = url + '/start' + '/' + user + '/' + str(problem) + '/' + str(count)
    print('start', user, problem, count, uri)
    return requests.post(uri).json()


def oncalls(token):
    uri = url + '/oncalls'
    # print('-----oncalls-----')
    return requests.get(uri, headers={'X-Auth-Token': token}).json()

def get_out(elevator):
    elevator_id = elevator['id']
    elevator_status = elevator['status']
    if elevator_status == 'UPWARD' or elevator_status == 'DOWNWARD':
        return {'elevator_id': elevator_id, 'command': 'STOP'}
    elif elevator_status == 'STOPPED':
        return {'elevator_id': elevator_id, 'command': 'OPEN'}
    elif elevator_status == 'OPENED':
        elevator_floor = elevator['floor']
        elevator_passengers = elevator['passengers']
        stack = []
        for passenger in elevator_passengers:
            if passenger['end'] == elevator_floor:
                stack.append(passenger['id'])
        return {'elevator_id': elevator_id, 'command': 'EXIT', 'call_ids': stack}


def get_in(elevator, calls):
    elevator_id = elevator['id']
    elevator_status = elevator['status']
    if elevator_status == 'UPWARD' or elevator_status == 'DOWNWARD':
        return {'elevator_id': elevator_id, 'command': 'STOP'}
    elif elevator_status == 'STOPPED':
        return {'elevator_id': elevator_id, 'command': 'OPEN'}
    elif elevator_status == 'OPENED':
        elevator_floor = elevator['floor']
        len_passengers = len(elevator['passengers'])
        stack = []
        for call in calls:
            if call['start'] == elevator_floor:
                stack.append(call['id'])
                if len_passengers + len(stack) >= 8:
                    break
        return {'elevator_id': elevator_id, 'command': 'ENTER', 'call_ids': stack}


def get_move(elevator, target_floor):
    elevator_id = elevator['id']
    elevator_status = elevator['status']
    elevator_floor = elevator['floor']
    if elevator_status == 'OPENED':
        return {'elevator_id': elevator_id, 'command': 'CLOSE'}
    else:
        if target_floor >= elevator_floor:
            if elevator_status == 'STOPPED' or elevator_status == 'UPWARD':
                return {'elevator_id': elevator_id, 'command': 'UP'}
            else:
                return {'elevator_id': elevator_id, 'command': 'STOP'}
        elif target_floor < elevator_floor:
            if elevator_status == 'STOPPED' or elevator_status == 'DOWNWARD':
                return {'elevator_id': elevator_id, 'command': 'DOWN'}
            else:
                return {'elevator_id': elevator_id, 'command': 'STOP'}


def action(token, response):
    uri = url + '/action'
    # print(response)
    elevator0 = response['elevators'][0]
    calls = response['calls']

    # 0번 엘리베이터 로직
    elevator0_status = elevator0['status'] 
    elevator0_floor = elevator0['floor']
    elevator0_passengers = elevator0['passengers']
    is_full0 = False
    if len(elevator0_passengers) >= 8:
        is_full0 = True

    # 승객 중 현재 층에서 내릴 사람 있는지 확인
    if elevator0['passengers']:
        for passenger in elevator0['passengers']:
            if passenger['end'] == elevator0_floor:
                # 내리는 함수
                # print('-----get_out접근-----')
                elevator0_cmd = get_out(elevator0)
                return requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': [elevator0_cmd]}).json()
    
    # 승객 중 현재 층에서 탈 사람 있는지 확인
    if is_full0 == False:
        for call in calls:
            if call['start'] == elevator0_floor:
                # print('-----get_in접근-----')
                elevator0_cmd = get_in(elevator0, calls)
                return requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': [elevator0_cmd]}).json()
    
    # 위나 아래로 가야하는 상황 
    target_floor = 99
    # 현재 대기된 call 중 더 가까운 층이 있다면
    if is_full0 == False:
        for call in calls:
            if abs(call['start'] - elevator0_floor) <= abs(target_floor - elevator0_floor):
                target_floor = call['start']
    # 이미 타고 있는 승객 층에 더 가까운 층이 있다면
    for passenger in elevator0_passengers:
        if abs(passenger['end'] - elevator0_floor) <= abs(target_floor - elevator0_floor):
            target_floor = passenger['end']
    # 다른 곳으로 이동하는 함수
    elevator0_cmd = get_move(elevator0, target_floor)
    # print('-----get_move접근-----')
    # print(elevator0_cmd)
    return requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': [elevator0_cmd]}).json()

def p0_simulator():
    user = 'tester_kanghyun'
    problem = 1
    count = 1

    ret = start(user, problem, count)
    print('ret', ret)
    token = ret['token']
    print('Token for %s is %s' % (user, token))

    is_end = False
    while is_end == False:
        response = oncalls(token)
        result = action(token, response)
        if response['timestamp'] % 300 == 0:
            print(response['timestamp'])
            pprint(response)
            pprint(result)
        is_end = result['is_end']
    print('Token for %s is %s' % (user, token))

if __name__ == '__main__':
    p0_simulator()
