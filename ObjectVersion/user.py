#!/usr/bin/env python3
# user.py


class User:
  # Username: rgoldstein, Arn: arn:aws:iam::079704269206:user/rgoldstein, Created: 04/25/2024 PasswordLastUsed: 05/09/2024

  username = ""
  userid   = ""
  arn      = ""
  groups = []
  attached_user_policies = []
  inline_user_policies = []

  def __init__(self, username, userid, arn):
    self.username = username
    self.userid   = userid
    self.arn      = arn

  def show(self):
    print(f"UserName: {self.username}, UserId: {self.userid}, Arn: {self.arn}")

  def add_group(self, group):
    self.groups.append(group)

  def show_groups(self):
    for g in self.groups:
      g.show()

  def add_attached_policy(self, policy):
    self.attached_user_policies.append(policy)

  def add_inline_policy(self, policy):
    self.inline_user_policies.append(policy)

  def show_attached_user_policies(self):
    for a in self.attached_user_policies:
      a.show()

  def show_inline_user_policies(self):
    for a in self.inline_user_policies:
      a.show()


class Group:

  # 20: GroupName: devops-beginner,  GroupId: AGPARFDV6UGLOMCC4MNWD
  groupname = ""
  groupid   = ""
  arn       = ""

  def __init__(self, groupname, groupid, arn):
    self.groupname = groupname
    self.groupid   = groupid
    self.arn       = arn

  def show(self):
    print(f"GroupName: {self.groupname}, GroupId: {self.groupid}, Arn: {self.arn}")
    

class Policy:


    
rgoldstein = User("rgoldstein", "ABC123", "arn:aws:iam::079704269206:user/rgoldstein")
rgoldstein.show()

devops_beginner = Group("devops-beginner", "AGPARFDV6UGLOMCC4MNWD", "")
devops_beginner.show()

# GroupName: BaseConsole,  GroupId: AGPARFDV6UGLGRRENGNOQ
baseconsole = Group("BaseConsole", "AGPARFDV6UGLGRRENGNOQ", "")
baseconsole.show()

rgoldstein.add_group(devops_beginner)
rgoldstein.add_group(baseconsole)

print("--- listing groups for user {} ---".format(rgoldstein.username))
rgoldstein.show_groups()



