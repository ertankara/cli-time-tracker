class Action:
    def __init__(self, fn, description):
        self.fn = fn
        self.description = description


flags = {
    '--help': 'help',
    '-h': 'help',
    '--time': 'add_time',
    '-t': 'add_time'
}

flag_keys = flags.keys()


def get_corresponding_flag_action(given_flag):
    if given_flag in flag_keys:
        target_flag_action = flags[given_flag]
        flags_to_actions[target_flag_action].fn(given_flag)
    else:
        print(f'Unknown flag was received {given_flag}')


def display_help_msg(_):
    print('Helper flag recieved')


flags_to_actions = {
    'help': Action(display_help_msg, 'Display available helper methods')
}
