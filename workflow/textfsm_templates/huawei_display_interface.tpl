Value INTERFACE (\S+)
Value STATE (\S+)
Value PROTOCOL (\S+)

Start
  ^(?P<INTERFACE>GigabitEthernet\S+)\s+(?P<STATE>up|down)\s+(?P<PROTOCOL>up|down) -> Record