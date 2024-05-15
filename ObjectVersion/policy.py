#!/usr/bin/env python3
# user.py
from pprint import pprint

###########
# U S E R #
###########
class User:

  username                   = ""
  userid                     = ""
  arn                        = ""
  create_date                = ""
  pw_date                    = ""
  #groups                     = []
  #group_attached_policies    = []
  #group_inline_policies      = []
  #attached_policies          = []
  #inline_policies            = []

  def __init__(self, username, userid, arn, create_date, pw_date):
    self.username                   = username
    self.userid                     = userid
    self.arn                        = arn
    self.create_date                = create_date
    self.pw_date                    = pw_date
    self.groups                     = []
    self.group_attached_policies    = []
    self.group_inline_policies      = []
    self.inline_policies            = []
    self.attached_policies          = []

  def add_group(self, group):
    self.groups.append(group)

  def add_attached_policy(self, policy):
    self.attached_policies.append(policy)

  def add_inline_policy(self, policy):
    self.inline_policies.append(policy)


  def show(self):
    print(f"UserName: {self.username}, UserId: {self.userid}, Arn: {self.arn}, Created: {self.create_date}, PWDate: {self.pw_date}")

  def show_groups(self):
    # show groups to which user belongs
    for g in self.groups:
      g.show()

  def show_attached_policies(self):
    for a in self.attached_policies:
      a.show()

  def show_inline_policies(self):
    for a in self.inline_policies:
      a.show()

  def show_group_attached_policies(self):
    print(f"{self.username} attached policies")
    for gp in self.group_attached_policies:
      gp.show()

  def show_group_inline_policies(self):
    print(f"{self.username} inline policies")
    for gp in self.group_inline_policies:
      gp.show()

  def show_group_policies(self):
    print(f"{self.username} group policies:")
    self.show_group_inline_policies()
    self.show_group_attached_policies()


  def report_policies(self):
    print(f"Attached Policies")
    self.show_attached_policies()

    print(f"Inline Policies")
    self.show_inline_policies()

    print(f"Group Attached Policies")
    self.show_group_attached_policies()

    print(f"Group Inline Policies")
    self.show_group_inline_policies()


  def report_groups(self):
    print(f"Group Report: {self.username}:::")
    self.show_groups()


  def report(self):
    print(f"User Report: {self.username}:::")
    self.report_groups()
    self.report_policies()
    self.show_group_policies()


#############
# G R O U P #
#############
class Group:

  groupname = ""
  groupid   = ""
  arn       = ""
  #users     = []

  def __init__(self, groupname, groupid, arn):
    self.groupname = groupname
    self.groupid   = groupid
    self.arn       = arn
    self.users             = []
    self.attached_policies = []
    self.inline_policies   = []
    self.user_list = []

  def copy_attached_policies_to_user(self, userobj):
    for ap in self.attached_policies:
      userobj.group_attached_policies.append(ap)
      print(f"copied attachedp {ap.policyname} to {userobj.username}")
    print(f"{self.groupname} -> {userobj.username} = copied")

  def copy_inline_policies_to_user(self, userobj):
    for ilp in self.inline_policies:
      userobj.group_inline_policies.append(ilp)
      print(f"copied inlinep {ilp.policyname} to {userobj.username}")
    print(f"{self.groupname} -> {userobj.username} = copied")

  def userlist(self):
    for u in self.users:
      self.user_list.append(u)
    return self.user_list

  def show(self):
    print(f"GroupName: {self.groupname}, GroupId: {self.groupid}, Arn: {self.arn}")

  def show_users(self):
    for u in self.users:
      u.show()

  def show_inline_policies(self):
    print(f"showing inline policies for group {self.groupname}: ")
    for p in self.inline_policies:
      print(f"policy name: {p.policyname}")

  def show_attached_policies(self):
    print(f"showing attached policies for group {self.groupname}: ")
    for p in self.attached_policies:
      print(f"policy name: {p.policyname}")

  def report(self):
    print(f"Attached Group Policies for {self.groupname}")
    self.show_attached_policies()
 
    print(f"Group Members:")
    self.show_users()
    

###############
# P O L I C Y #
###############
class Policy:
  policyname         = ""
  policyid           = ""
  arn                = ""
  attachmentcount    = 0
  defaultversionid   = ""
  # not sure, do I want to save the policy document
  document           = ""

  def __init__(self, policyname, policyid, arn):
    self.policyname       = policyname
    self.policyid         = policyid
    self.arn              = arn
    self.attachmentcount  = 0
    self.defaultversionid = ""

  def show(self, nl=False):
    print(f"PolicyId: {self.policyid}, PolicyName: {self.policyname},  Arn: {self.arn},  AttachCount: {self.attachmentcount}, DefaultVerId: {self.defaultversionid}")

  def show_document(self):
    pprint(self.document)
      

    
