import sys

def invalid_file_callback():
    print('0 0')
    exit(0)

if sys.stdin is None:
    invalid_file_callback()
# todo: maybe i need more sophisticated readlines accounting for quoted \n
# lines = sys.stdin.readlines()

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
    return values.index('ean') if 'ean' in values else -1
    

column_ean = idx_ean_in_header(lines[0])
force_first_valid = False

if column_ean == -1:
    column_ean = 0
    force_first_valid = True
else:
    lines = lines[1:]

cnt_valid = 0
cnt_invalid = 0


# weight_factor_2 = [0, 2, 4, 6, 8, 9, 1, 3, 5, 7]
# weight_factor_3 = [0, 3, 6, 9, 2, 5, 8, 1, 4, 7]
# weight_factor_5_plus = [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]
# weight_factor_5_minus = [0, 5, 9, 4, 8, 3, 7, 2, 6, 1]

def verify_checksum(ean):
    sum = 0
    for i in range(len(ean) - 1):
        digit = int(ean[i])
        if i % 2 == 0:
            sum += digit
        else:
            sum += digit * 3
    sum = sum % 10
    if sum != 0:
        sum = 10 - sum
    return ean[-1] == str(sum)

def check_row(values, column_ean):
    if len(values) <= column_ean:
        return False
    ean = values[column_ean]
    if len(ean) == 0:
        return False
    while len(ean) < 13:
        ean = '0' + ean
    while len(ean) > 13 and ean[0] == '0':
        ean = ean[1:]
    if len(ean) != 13:
        return False
    if not ean.isdigit():
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
    
