with open('day01.txt') as f:
    lines = f.read().splitlines()


def check_msg(msg):
    byte_length = len(msg.encode('utf-8'))
    char_length = len(msg)
    valid_sms = byte_length <= 160
    valid_tweet = char_length <= 140
    cost = 0
    if valid_sms:
        cost += 11
    if valid_tweet:
        cost += 7
    if valid_sms and valid_tweet:
        cost -= 5  # discount!
    return cost

print(sum(check_msg(m) for m in lines))
