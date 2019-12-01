# Zimbra Permissions Inspector

This CLI utility allows you to query sending permissions on a Zimbra server.

You can retrieve sending permissions for a particular Zimbra Distribution List
(ZDL) or get a complete list of 'Send as' permissions. The most basic query,
list all the existing ZDLs (both dynamic and static).  

### Requirements
Make sure you meet the following requirements:
 * Make sure to [setup the Zimbra LDAP admin user](https://wiki.zimbra.com/wiki/Setting_zimbra_admin_password_in_LDAP), 
on your Zimbra server.
 * You need the [python-ldap](https://pypi.python.org/pypi/python-ldap/) package.     

Tested on Zimbra v8.8.12

### Installation
You can install it with `pip`:
```
pip install zimbra-permissions-inspector
```

### Usage
Help output:
```
usage: zimbra-permissions-inspector.py [-h] [-l ZDL] [-sa] [-v]
                                       SERVER BASEDN LDAP_ADMIN

Query sending permissions on a Zimbra server

positional arguments:
  SERVER             URI formatted address of the Zimbra server
  BASEDN             Specify the searchbase or base DN of the Zimbra LDAP
                     server
  LDAP_ADMIN         Admin user of the Zimbra LDAP server

optional arguments:
  -h, --help         show this help message and exit
  -l ZDL, --zdl ZDL  Query which Zimbra accounts have permissions to send
                     mails to the given ZDL
  -sa, --sendas      Query 'send as' permissions on both Zimbra accounts and
                     ZDLs
  -v, --version      Show current version
```
Note that positional arguments are mandatory!.

##### Usage examples
If no optional arguments are given, it'll list all the existing ZDLs (both dynamic and static):
```
zimbra-permissions-inspector ldap://zimbra.somecorp.com dc=somecorp,dc=com uid=zimbra,cn=admins,cn=zimbra 
```
Query which Zimbra accounts have permissions to send mails to a ZDL ("Zimbra Distribution Lists") named "my-zdl-list":
```
zimbra-permissions-inspector ldap://zimbra.somecorp.com dc=somecorp,dc=com uid=zimbra,cn=admins,cn=zimbra -l zdl-list 
```
Get a list of "send as" permissions:
```
zimbra-permissions-inspector ldap://zimbra.somecorp.com dc=somecorp,dc=com uid=zimbra,cn=admins,cn=zimbra -sa 
```

