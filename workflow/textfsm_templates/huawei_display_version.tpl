Value OS_VERSION (\S+)
Value UPTIME (.+)

Start
  ^VRP\s+(?P<OS_VERSION>\S+) -> Record
  ^Uptime\s+is\s+(?P<UPTIME>.+) -> Record