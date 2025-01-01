import os
software_path = os.path.abspath(os.path.dirname(__file__))

def get_software_path(n):
    return os.path.join(software_path, n)

SoftwareWbsdcard=os.path.join(software_path, "wbsdcard")
SoftwareNes=os.path.join(software_path, "nes")
