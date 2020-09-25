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

def get_out(elevator, response):
    elevator_id = elevator['id']
    elevator_status = elevator['status']
    if elevator_status == 'UPWARD' or elevator_status == 'DOWNWARD':
        return {'elevator_id': elevator_id, 'command': 'STOP'}, response
    elif elevator_status == 'STOPPED':
        return {'elevator_id': elevator_id, 'command': 'OPEN'}, response
    elif elevator_status == 'OPENED':
        elevator_floor = elevator['floor']
        elevator_passengers = elevator['passengers']
        stack = []
        for passenger in elevator_passengers:
            if passenger['end'] == elevator_floor:
                stack.append(passenger['id'])
                response['elevators'][elevator_id]['passengers'].remove(passenger)
        return {'elevator_id': elevator_id, 'command': 'EXIT', 'call_ids': stack}, response


def get_in(elevator, calls, response):
    elevator_id = elevator['id']
    elevator_status = elevator['status']
    if elevator_status == 'UPWARD' or elevator_status == 'DOWNWARD':
        return {'elevator_id': elevator_id, 'command': 'STOP'}, response
    elif elevator_status == 'STOPPED':
        return {'elevator_id': elevator_id, 'command': 'OPEN'}, response
    elif elevator_status == 'OPENED':
        elevator_floor = elevator['floor']
        len_passengers = len(elevator['passengers'])
        stack = []
        for call in calls:
            if call['start'] == elevator_floor:
                stack.append(call['id'])
                response['calls'].remove(call)
                if len_passengers + len(stack) >= 8:
                    break
        return {'elevator_id': elevator_id, 'command': 'ENTER', 'call_ids': stack}, response


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


def action(i, response):
    uri = url + '/action'
    elevator = response['elevators'][i]
    calls = response['calls']

    elevator_floor = elevator['floor']
    elevator_passengers = elevator['passengers']
    is_full = False
    if len(elevator_passengers) >= 8:
        is_full = True

    # 승객 중 현재 층에서 내릴 사람 있는지 확인
    if elevator['passengers']:
        for passenger in elevator['passengers']:
            if passenger['end'] == elevator_floor:
                # 내리는 함수
                # print('-----get_out접근-----')
                elevator_cmd, response = get_out(elevator, response)
                return elevator_cmd, response
    
    # 승객 중 현재 층에서 탈 사람 있는지 확인
    if is_full == False:
        for call in calls:
            if call['start'] == elevator_floor:
                # print('-----get_in접근-----')
                elevator_cmd, response = get_in(elevator, calls, response)
                return elevator_cmd, response
    
    # 위나 아래로 가야하는 상황 
    target_floor = 99
    # 현재 대기된 call 중 더 가까운 층이 있다면
    if is_full == False:
        for call in calls:
            if abs(call['start'] - elevator_floor) <= abs(target_floor - elevator_floor):
                target_floor = call['start']
    # 이미 타고 있는 승객 층에 더 가까운 층이 있다면
    for passenger in elevator_passengers:
        if abs(passenger['end'] - elevator_floor) <= abs(target_floor - elevator_floor):
            target_floor = passenger['end']
    # 다른 곳으로 이동하는 함수
    elevator_cmd = get_move(elevator, target_floor)
    # print('-----get_move접근-----')
    return elevator_cmd, response


def post_action(token, commands):
    uri = url + '/action'
    return requests.post(uri, headers={'X-Auth-Token': token}, json={'commands': commands}).json()


def p0_simulator():
    user = 'tester_KH'
    problem = 2
    count = 4

    ret = start(user, problem, count)
    print('ret', ret)
    token = ret['token']
    print('Token for %s is %s' % (user, token))

    is_end = False
    while is_end == False:
        commands = []
        response = oncalls(token)
        for i in range(4):
            command, response = action(i, response)
            commands.append(command)
        
        # print(commands)
        result = post_action(token, commands)

        if result['timestamp'] % 300 == 0:
            print(result['timestamp'])
            pprint(result)
        is_end = result['is_end']

    print('Token for %s is %s' % (user, token))

if __name__ == '__main__':
    p0_simulator()
