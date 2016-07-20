def get_users(guest):
    users = {}
    content = guest.cat('/etc/passwd').split("\n")

    for line in content:
        user = line.split(":")
        if len(user) < 6:
            continue
        users[user[0]] = {
                'uid': int(user[2]),
                'gid': int(user[3]),
                'description': user[4],
                'home': user[5],
                'shell': user[6]}
    return users


def get_groups(guest):
    groups = {}
    content = guest.cat('/etc/group').split("\n")

    for line in content:
        group = line.split(":")
        if len(group) < 2:
            continue

        groups[group[0]] = {'gid': int(group[2]), 'users': []}

        if len(group) > 2:
            groups[group[0]]['users'] = group[3].split(',')
    return groups
