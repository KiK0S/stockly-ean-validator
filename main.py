import sys

def invalid_file_callback():
    print('0 0')
    exit(0)

if sys.stdin is None:
    invalid_file_callback()

# kudos to https://stackoverflow.com/a/16549381
# sys.stdin.reconfigure(encoding='utf-8')
def read_lines():
    lines = []
    is_quoted = False
    current_line = ''
    while True:
        c = sys.stdin.read(1)
        if len(c) == 0:
            break
        if c == '"':
            is_quoted = not is_quoted
            current_line += c
        elif c == '\n' and not is_quoted:
            lines.append(current_line)
            current_line = ''
        else:
            current_line += c
    if is_quoted:
        current_line = 'broken line'
    if current_line != '':
        lines.append(current_line)
    return lines

try:
    lines = read_lines()
except:
    invalid_file_callback()

lines = [line.strip() for line in lines if len(line.strip()) > 0]
if len(lines) == 0:
    invalid_file_callback()

def parse_values(line):
    '''
    Returns a list of values that were comma-separated in the line.
    '''
    res = []
    current_token = ''
    inside_quotes = False
    for c in line:
        if c == '"':
            inside_quotes = not inside_quotes
        elif c == ',' and not inside_quotes:
            res.append(current_token)
            current_token = ''
        else:
            current_token += c
    res.append(current_token)
    return res

def idx_ean_in_header(line):
    '''
    Returns the index of the ean column in the header.
    If the ean column is not found, returns -1.
    '''
    values = parse_values(line)
    lookup_result = -1
    for i, v in enumerate(values):
        if v == 'ean':
            lookup_result = i
            break
    return lookup_result
    

column_ean = idx_ean_in_header(lines[0])
force_first_valid = False

if column_ean == -1:
    column_ean = 0
    force_first_valid = True
else:
    lines = lines[1:]

cnt_valid = 0
cnt_invalid = 0


rev_modulo = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]
def verify_checksum(ean):
    sum = 0
    #       ... , 1 3, 1 3
    for i in range(2, len(ean)+1):
        if not ean[-i].isdigit():
            return False
        digit = ord(ean[-i]) - ord('0')
        if i % 2 == 1:
            sum += digit
        else:
            sum += digit * 3
    if not ean[-1].isdigit():
        return False
    return rev_modulo[sum % 10] == ord(ean[-1]) - ord('0')

def check_row(values, column_ean):
    if len(values) <= column_ean:
        return False
    ean = values[column_ean]
    if len(ean) == 0:
        return False
    for i in range(14, len(ean)+1):
        if ean[-i] != '0':
            return False
    return verify_checksum(ean)


for i in range(len(lines)):
    values = parse_values(lines[i])
    is_valid = check_row(values, column_ean)
    if i == 0 and force_first_valid and not is_valid:
        invalid_file_callback()
    if is_valid:
        cnt_valid += 1
    else:
        cnt_invalid += 1

print(f'{cnt_valid} {cnt_invalid}')
    

# start_num = 1000000
# for num in range(start_num, 10 * start_num):
#     if verify_checksum(str(num)) != new_verify_checksum(str(num)):
#         print('Wrong behavior on', num)
#         print(verify_checksum(str(num)), new_verify_checksum(str(num)))
#         break
# print('OK')