flags = {
    '--help': 'help',
    '-h': 'help'
}


def get_corresponding_flag_action(given_flag):
    for f in flags.keys():
        if f == given_flag:
            flags_to_fns[flags[f]](given_flag)
            break

    print('Unknown flag was received')


def display_help_msg(_):
    pass


flags_to_fns = {
    'help': display_help_msg
}
