# Copyright 2019 by tuxedoar@gmail.com .

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import getpass
from distutils.version import LooseVersion
from _version import __version__
import ldap


def main():
    """ Call appropriate functions according to the invoked arguments  """
    m = menu_handler()
    server = m.SERVER
    basedn = m.BASEDN
    adminuser = m.LDAP_ADMIN

    try:
        creds = getpass.getpass('\nPlease, enter your Zimbra credentials: ')
        ldap_data = connect_to_zimbra_ldap(server, basedn, adminuser, creds)
        get_zdl_data(ldap_data, chosen_list=False)
    except (KeyboardInterrupt, ldap.SERVER_DOWN, ldap.UNWILLING_TO_PERFORM, \
            ldap.INVALID_CREDENTIALS) as e:
        sys.exit(e)

    if m.zdl:
        get_users(ldap_data)
    elif m.sendas:
        get_sendas_permissions(ldap_data)
    # If no optional arguments are given, show existing ZDLs!.
    else:
        get_lists(ldap_data)


def menu_handler():
    """ Handle and return command line arguments """
    parser = argparse.ArgumentParser(
      description='Query sending permissions on a Zimbra server')
    parser.add_argument('SERVER', help='URI formatted address of the Zimbra server')
    parser.add_argument('BASEDN', help='Specify the searchbase or base DN of the Zimbra LDAP server')
    parser.add_argument('LDAP_ADMIN', help='Admin user of the Zimbra LDAP server')
    parser.add_argument('-l', '--zdl', required=False, action='store',
                        help='Query which Zimbra accounts have permissions to send mails to the given ZDL')
    parser.add_argument('-sa', '--sendas', required=False, action='store_true',
                        help="Query 'send as' permissions on both Zimbra accounts and ZDLs")
    parser.add_argument('-v', '--version', action='version',
                          version="%(prog)s {version}".format(version=__version__),
                           help='Show current version')

    args = parser.parse_args()
    return args


def connect_to_zimbra_ldap(server, basedn, adminuser, creds):
    """ Connect to the LDAP Zimbra server """
    l = ldap.initialize(server)
    l.simple_bind_s(adminuser, creds)

    ldap_data = l.search_s(basedn, ldap.SCOPE_SUBTREE, 'objectClass=*')

    return ldap_data


def get_dynamic_static_lists(attrs, objectclass, authorized_id, lists):
    """ Collect both static and dynamic ZDL data """
    # Dynamic Lists!.
    if objectclass == "zimbraGroup":
        zdl_list_type = "dynamic"
        key_value = "cn"
    # Static lists!.
    elif objectclass == "zimbraDistributionList":
        zdl_list_type = "static"
        key_value = "uid"

    for attr in attrs:
        # Contains a list with the different types of objectClass.
        decoded_oc = [a.decode() for a in attr.get("objectClass")]
        if objectclass in decoded_oc:
            list_name = attr[key_value][0].decode()
            idsauth = attr.get("zimbraACE", "")
            for authorized in idsauth:
                authorized_id.append((list_name, authorized.decode()))
            lists.append((list_name, zdl_list_type))


def get_zdl_data(ldap_data, chosen_list=False):
    """Retrieve and return ZDL and related accounts data.
    chosen_list=<bool> argument identifies if the -l CLI argument is invoked or not.
    """
    attrs = [i[1] for i in ldap_data]

    authorized_id = []
    lists = []
    authorized_accounts = []

    get_dynamic_static_lists(attrs, "zimbraGroup", authorized_id, lists)
    get_dynamic_static_lists(attrs, "zimbraDistributionList", authorized_id, lists)

    if chosen_list:
        for authorized in authorized_id:
            if chosen_list in authorized:
                if not "-sendToDistList" in authorized[1] and "sendToDistList" in authorized[1]:
                    permission = authorized[1].split(" ")
                    authorized = permission[0]
                    authorized_accounts.append(authorized)

    return (lists, authorized_id, authorized_accounts)


def get_users(ldap_data):
    """ Identify which Zimbra accounts have sending permissions to provided ZDL  """
    m = menu_handler()
    chosen_list = m.zdl
    zdl_data = get_zdl_data(ldap_data, chosen_list)
    authorized_accounts = zdl_data[2]
    attrs = [i[1] for i in ldap_data]

    # Check that chosen_list exist!!.
    zdl_lists = [l[0] for l in zdl_data[0]]
    if not chosen_list in zdl_lists:
        print("\nSorry, list not found: {}\n".format(chosen_list))
        sys.exit()

    # Check that authorized_accounts is not empty.
    if not authorized_accounts:
        print("\nSorry, no permissions were found in list: {}!\n".format(chosen_list))
        sys.exit()

    print("\nAuthorized accounts to send mails to %s :\n " % (chosen_list))

    for attr in attrs:
        zimbraid = attr.get("zimbraId")
        uid = attr.get("uid")
        if zimbraid and uid:
            for authorized in authorized_accounts:
                if authorized in zimbraid[0].decode():
                    print(uid[0].decode())


def zimbraid_to_uid(ldap_data, target_zimbraid):
    """ Given a ZimbraId value, returns its corresponding UID """
    attrs = [i[1] for i in ldap_data]
    for attr in attrs:
        decoded_oc = [a.decode() for a in attr.get("objectClass")]
        if "inetOrgPerson" in decoded_oc and attr.get("uid"):
            zimbraid = attr.get("zimbraId")[0].decode()
            uid = attr.get("uid")[0].decode()
            if target_zimbraid == zimbraid:
                return uid


def get_sendas_permissions(ldap_data):
    """ Outputs 'Send as' permissions """
    attrs = [i[1] for i in ldap_data]
    sendas_auth_accounts = []

    # 'Send as' permissions for ZDLs!.
    zdl_data = get_zdl_data(ldap_data, chosen_list=False)
    authorized_id = zdl_data[1]

    for props in authorized_id:
        if "sendAsDistList" in props[1]:
            sendasperms = props[1].split(" ")
            authorized_id = sendasperms[0]
            zdl = props[0]
            sendas_auth_accounts.append((authorized_id, zdl))

    # 'Send as' permissions for Zimbra accounts!
    for props in attrs:
        decoded_oc = [a.decode() for a in props.get("objectClass")]
        if "inetOrgPerson" in decoded_oc and props.get("zimbraACE"):
            zimbraace = props["zimbraACE"][0].decode().split(" ")
            #zimbraid = props.get("zimbraId")[0].decode()
            uid = props.get("uid")[0].decode()
            if "sendAs" in zimbraace:
                sendas_auth_accounts.append((zimbraace[0], uid))

    print("\nZimbra 'Send as' permissions: \n\nPERMISSION OWNER\tTARGET\n")
    for sendas_permission in sendas_auth_accounts:
        user_with_permission = zimbraid_to_uid(ldap_data, sendas_permission[0])
        print("{:<24}{:<20}".format(user_with_permission, sendas_permission[1]))


def get_lists(ldap_data):
    """ Print all existing ZDLs  """
    zdl_data = get_zdl_data(ldap_data, chosen_list=False)
    zdl_lists = zdl_data[0]

    # Print each list and its type (static or dynamic).
    for l in zdl_lists:
        print("%s ( %s )" % (l[0], l[1]))


if __name__ == "__main__":
    main()
