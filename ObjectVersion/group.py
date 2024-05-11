# group.py

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
    return f"GroupName: {self.groupname}, GroupId: {self.groupid}, Arn: {self.arn}"
    
    
devops-beginner = Group("devops-beginner", "AGPARFDV6UGLOMCC4MNWD", "")
print(devops-beginner.show())




