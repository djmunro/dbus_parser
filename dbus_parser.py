import re
import sys
import json
import itertools

try:
    from collections import Counter
except ImportError:
    from Counter import *


#SPLIT_MESSAGES = re.compile(r'\n.?\w{3} \w+ +\d+ \d+:\d+:\d+ \d+[\r\s]*\n') # this works with the original log provided
#SPLIT_MESSAGES = re.compile(r'signal sender@|method call sender@|method return sender@')
STRIP_TIMESTAMP = re.compile(r'\[[^\\]*\] ')
SPLIT_MESSAGES = re.compile(r'^(signal sender|method call sender|method return sender)', re.MULTILINE)

# need to fix these... because sometimes there's not parameters for the functin
#MATCH_SIGNAL = re.compile(r'signal sender=(?P<sender>.*) -> dest=(?P<dest>.*) serial=(?P<serial>.*) path=(?P<path>.*) interface=(?P<interface>.*) member=(?P<member>.*)\n\s+string (?P<function>.*)\n\s+string (?P<params>.*)')
#MATCH_METHOD_CALL = re.compile(r'method call sender=(?P<sender>.*) -> dest=(?P<dest>.*) serial=(?P<serial>.*) path=(?P<path>.*) interface=(?P<interface>.*) member=(?P<member>.*)\n\s+string (?P<function>.*)\n\s+string (?P<params>.*)')
MATCH_SIGNAL = re.compile(r'signal sender=(?P<sender>.*) -> dest=(?P<dest>.*) serial=(?P<serial>.*) path=(?P<path>.*) interface=(?P<interface>.*) member=(?P<member>.*)\n\s+string (?P<function>.*)')
MATCH_METHOD_CALL = re.compile(r'method call sender=(?P<sender>.*) -> dest=(?P<dest>.*) serial=(?P<serial>.*) path=(?P<path>.*) interface=(?P<interface>.*) member=(?P<member>.*)\n\s+string (?P<function>.*)')
MATCH_METHOD_RETURN = re.compile(r'method return sender=(?P<sender>.*) -> dest=(?P<dest>.*) reply_serial=(?P<reply_serial>.*)')

MATCH_HELLO_METHOD_CALL = re.compile(r'method call sender=(?P<sender>.*) -> dest=(?P<dest>.*) serial=(?P<serial>.*) path=(?P<path>.*) interface=(?P<interface>.*) member=(?P<member>.*)')



def parse_message(text):
    signal = MATCH_SIGNAL.search(text)
    method_call = MATCH_METHOD_CALL.search(text)
    method_return = MATCH_METHOD_RETURN.search(text)
    HELLO_METHOD_CALL = MATCH_HELLO_METHOD_CALL.search(text)

    if signal:
        return signal.groupdict()
    if method_call:
        return method_call.groupdict()
    if method_return:
        return method_return.groupdict()
    if HELLO_METHOD_CALL:
        return HELLO_METHOD_CALL.groupdict()
    raise Exception('Cannot parse message:\n{}'.format(text))

#def parse_messages(text):
#    messages = SPLIT_MESSAGES.split('\n' + text)
#    return [parse_message(message) for message in messages if message.strip()]

def parse_messages(text):
    text = '\n'.join([STRIP_TIMESTAMP.sub('', line) for line in text.split('\n')])

    # join the separator and the following separated text
    parts = iter(SPLIT_MESSAGES.split(text))
    messages = []
    next(parts)  # skip anything before the first separator
    try:
        while True:
            messages.append(next(parts) + next(parts))
    except StopIteration:
        return [parse_message(message) for message in messages if message.strip()]
    return [parse_message(message) for message in messages if message.strip()]


def groupby_key(message):
    return message['function']

def process_group(group, items):
    items = list(items)
    return items[0]['function'], len(items), items[0]['path']

def process_method_group(group, items):
    items = list(items)
    return items[0]['function'], len(items), items[0]['sender'], items[0]['dest']

def print_grid(columns, values):
    # pop columns on top of values, since we want to print them as well
    values = [columns] + values

    # calculate the format string for printing a row
    row_format = ''
    for index in range(len(columns)):
        longest = max([len(str(row[index])) for row in values])
        row_format += '{:' + str(longest) + '} '

    # print the row!
    for row in values:
        print row_format.format(*row)
    print '\n'

def print_pretty_grid(columns, values, spacing=1, separator='|'):
    """
    >>> print_pretty_grid(
    ...    columns=('Function', 'Occurences', 'Sender'),
    ...    values=[
    ...        ('hey', 'world', 'foobar'),
    ...        ('this is', 'a test', 'my man!'),
    ...        ('roar', 'grr', 'zzzz'),
    ...    ]
    ... )
    Function   Occurences   Sender
    hey      | world      | foobar
    this is  | a test     | my man!
    roar     | grr        | zzzz
    """
    header_str = ''
    format_str = ''
    for index in range(len(columns)):
        longest = max([len(str(row[index])) for row in [columns] + values])
        header_str += '{:' + str(longest) + '}'
        format_str += '{:' + str(longest) + '}'
        if index != len(columns) - 1:
            header_str += ' ' * spacing
            format_str += ' ' * spacing
            if separator:
                header_str += ' ' * (len(separator) + spacing)
                format_str += separator + ' ' * spacing
    print header_str.format(*columns)
    for row in values:
        print format_str.format(*row)

if __name__ == '__main__':
    #import doctest
    #doctest.testmod()

    data = open(sys.argv[1], 'r').read()
    messages = parse_messages(data)

    function_messages = [x for x in messages if 'function' in x]
    invoke_messages = [x for x in messages if 'member' in x and (x['member'] == 'Invoke' or x['member'] == 'AddMatch')]
    emit_messages = [x for x in messages if 'member' in x and x['member'] == 'Emit']

    # Signal Data (EMIT)
    print 'Signals: (Member=Emit),Occurences,Path'
    grouped = itertools.groupby(sorted(emit_messages, key=groupby_key), groupby_key)
    for group, items in grouped:
        items = list(items)
        print '{func},{occurences},{path}'.format(
            func=items[0]['function'],
            occurences=len(items),
            path=items[0]['path']
        )

    # Method Data
    print '\nMethods: (Member=Invoke),Occurrence,Sender,Destination'
    grouped = itertools.groupby(sorted(invoke_messages, key=groupby_key), groupby_key)
    for group, items in grouped:
        items = list(items)
        print '{func},{occurences},{sender},{dest}'.format(
            func=items[0]['function'],
            occurences=len(items),
            sender=items[0]['sender'],
            dest=items[0]['dest']
        )

    # Service Data
    print '\nServices,Occurrence'
    service_counts = {}
    for message in messages:
        path = message.get('path')
        try:
            service_counts[path] += 1
        except KeyError:
            service_counts[path] = 1

    for k,v in service_counts.iteritems():
        if k != None:
            print '{},{}'.format(k, v)




# this is for the ['function'],['param'] keys.. we may want to do stuff json related later
# deserialize JSON
#MESSAGE_FUNCTION = '   string "favAllowed"'
#MESSAGE_PARAMETERS = '   string "{"isArtistAllowed":true,"isSongAllowed":true}"'
#function = json.loads(MESSAGE_FUNCTION[11:-2])
#parameters = json.loads(MESSAGE_PARAMETERS[11:-1])

# KEEPING
# Signal Data
#grouped = itertools.groupby(sorted(emit_messages, key=groupby_key), groupby_key)
#print_grid(values=[process_group(group, items) for group, items in grouped], columns=('Signals: (Member=Emit)', 'Occurences', 'Path'))

# Method Data
#grouped = itertools.groupby(sorted(invoke_messages, key=groupby_key), groupby_key)
#print_grid(values=[process_method_group(group, items) for group, items in grouped], columns=('Methods: (Member=Invoke)', 'Occurrence', 'Sender', 'Destination'))

# Service Data
#services = Counter((x['path']) for x in messages if 'path' in x)  # give me a Counter with all the serives from path=
#print_grid(values=[[service, occurence] for service, occurence in services.iteritems()], columns=('Services', 'Occurrence'))
