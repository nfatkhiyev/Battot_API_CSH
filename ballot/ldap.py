from ballot.routes import ldap
from csh_ldap import CSHMember


def get_groups(uid: str):
    member = get_member(uid)
    group_list = member.get("memberOf")
    group_list_string = []
    for group_dn in group_list:
        group_string = group_dn.split(",")[0][3:]
        group_list_string.append(group_string)

    return group_list_string


def is_member_of_group(uid: str, group: str):
    member = get_member(uid)
    group_list = member.get("memberOf")
    for group_dn in group_list:
        if group == group_dn.split(",")[0][3:]:
            return True
        return False


def get_member(uid: str):
    return ldap.get_member(uid, uid=True)
