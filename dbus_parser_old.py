import enum as enum
import re
import itertools

try:
    from collections import Counter
except ImportError:
    from Counter import *

messages = []

@enum.unique
class MESSAGE_TYPE(enum.Enum):
    METHOD_CALL = 1
    METHOD_RETURN = 2
    ERROR = 3
    SIGNAL = 4
    STRING = 5

class DataReport(object):

    def __init__(self, messages):
        self._umsg = []
        self._messages = messages

    @classmethod
    def by_key(self, dict, key, val):
        return next(x for x in dict if x[key] == val)

    def _occurences(self):
        """
        >>> report = DataReport(
        ...     [
        ...         {
        ...             'type':'METHOD_CALL',
        ...             'func':'foobar2'
        ...         },
        ...         {
        ...             'type':'METHOD_RETURN',
        ...             'func':'foobar'
        ...         },
        ...         {
        ...             'type':'METHOD_CALL',
        ...             'func':'foobar2'
        ...         }
        ...     ]
        ... )
        >>> report._umsg = [{'type':'METHOD_CALL', 'func':'foobar2'}]
        >>> report._occurences()
        >>> print report._umsg
        [{'type': 'METHOD_CALL', 'occurrence': 2, 'func': 'foobar2'}]
        """
        for message in self._messages:
            try:
                msg = self.by_key(self._umsg, 'func', message['func'])
                if msg: #we found a value for func already in _signals, lets increment it!
                    try:
                        msg['occurrence'] += 1
                    except KeyError:
                        msg['occurrence'] = 1

            except StopIteration:
                pass


def process_line(message):
    mtype = message_type(message)

    if mtype is MESSAGE_TYPE.STRING:
        add_token(message)
    elif mtype is -1:
        pass
    else:
        add_message(mtype, message)

def message_type(message):
    """
    >>> message = 'method call sender=:1.26 -> dest=com.harman.service.iPodTagger serial=84 path=/com/harman/service/iPodTagger; interface=com.harman.ServiceIpc; member=Invoke'
    >>> message_type(message).name
    'METHOD_CALL'
    >>> message = 'method return sender=:1.35 -> dest=:1.19 reply_serial=1770 string...'
    >>> message_type(message).name
    'METHOD_RETURN'
    >>> message = 'signal sender=:1.35 -> dest=(null destination) serial=10212 path=/com/harman/service/Navigation; interface=com.harman.ServiceIpc; member=Emit'
    >>> message_type(message).name
    'SIGNAL'
    >>> message = 'nWed Dec  2 13:08:37 2015'
    >>> message_type(message)
    -1
    """
    try:
        if "method call" in message:
            return MESSAGE_TYPE.METHOD_CALL
        elif "method return" in message:
            return MESSAGE_TYPE.METHOD_RETURN
        elif "error" in message:
            return MESSAGE_TYPE.ERROR
        elif  re.search(r'\S*string', message):
            return MESSAGE_TYPE.STRING
        elif "signal" in message:
            return MESSAGE_TYPE.SIGNAL
        else:
            return -1
    except UnicodeDecodeError:
        pass

def add_token(message):
    last_message = messages[-1]

    try:
        last_message['payload'] += message
    except KeyError:
		last_message['payload'] = message

def add_message(mtype ,message):
    """
    Adds message to list with keys of message and type and their respective values.

    >>> message = 'method call sender=:1.26 -> dest=com.harman.service.iPodTagger serial=84 path=/com/harman/service/iPodTagger; interface=com.harman.ServiceIpc; member=Invoke'
    >>> mtype = MESSAGE_TYPE.METHOD_CALL
    >>> add_message(mtype, message)
    >>> print(messages)
    [{'sender': ':1.26', 'dest': 'com.harman.service.iPodTagger', 'member': 'Invoke', 'interface': 'com.harman.ServiceIpc;', 'serial': 84, 'type': 'METHOD_CALL'}]
    """
    if mtype is MESSAGE_TYPE.METHOD_CALL: messages.append(method_call(message))
    if mtype is MESSAGE_TYPE.METHOD_RETURN: messages.append(method_return(message))
    if mtype is MESSAGE_TYPE.ERROR: return
    if mtype is MESSAGE_TYPE.SIGNAL: messages.append(signal(message))

def method_call(message):
    return {
        'type':MESSAGE_TYPE.METHOD_CALL.name,
        'sender':sender(message),
        'dest':destination(message),
        'serial':serial(message),
        'interface':interface(message),
        'member':member(message)
    }

def method_return(message):
    return {
        'type':MESSAGE_TYPE.METHOD_RETURN.name,
        'sender':sender(message),
        'dest':destination(message),
        'reply_serial':reply_serial(message),
    }

def signal(message):
    return {
        'type':MESSAGE_TYPE.SIGNAL.name,
        'sender':sender(message),
        'dest':destination(message),
        'serial':serial(message),
        'path':path(message),
        'interface':interface(message),
        'member':member(message)
    }

def sender(message):
    return message.split("sender=")[1].split(" ")[0]

def destination(message):
    return message.split("dest=")[1].split(" ")[0]

def serial(message):
    return int(message.split("serial=")[1].split(" ")[0])

def path(message):
    if (message.count("path=") > 0):
        return message.split("path=")[1].split(" ")[0]
    else:
        return None

def interface(message):
    if (message.count("interface=") > 0):
        return message.split("interface=")[1].split(" ")[0]
    else:
        return None

def member(message):
    if (message.count("member=") > 0):
        return message.split("member=")[1].split(" ")[0]
    else:
        return None

def reply_serial(message):
    if (message.count("reply_serial=") > 0):
        return int(message.split("reply_serial=")[1].split(" ")[0])
    else:
        return None







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








def main():
    with open('dbusTraceMonitor.log') as fp:
        for line in fp:
            process_line(line)

    function_messages = [x for x in messages if 'function' in x]

    for i in messages:
        print i



    grouped = itertools.groupby(sorted(function_messages, key=groupby_key), groupby_key)

    for group, items in grouped:
        items = list(items)

        print '{func:<30}{occurences:<15}{path}'.format(
            func=items[0]['function'],
            occurences=len(items),
            path=items[0]['path']
        )


    #grouped = itertools.groupby(sorted(function_messages, key=groupby_key), groupby_key)
    #print_grid(values=[process_group(group, items) for group, items in grouped], columns=('Signals: (Member=Emit)', 'Occurences', 'Path'))

    # Method Data
    #grouped = itertools.groupby(sorted(function_messages, key=groupby_key), groupby_key)
    #print_grid(values=[process_method_group(group, items) for group, items in grouped], columns=('Methods: (Member=Invoke)', 'Occurrence', 'Sender', 'Destination'))

    # Service Data
    services = Counter((x['path']) for x in messages if 'path' in x)  # give me a Counter with all the serives from path=
    print_grid(values=[[service, occurence] for service, occurence in services.iteritems()], columns=('Services', 'Occurrence'))



if __name__ == '__main__':
    import doctest
    doctest.testmod()

    main()
    '''
    for i in messages:
        try:
            if i['type'] == 'SIGNAL':
                print i
        except KeyError:
            pass
    '''
