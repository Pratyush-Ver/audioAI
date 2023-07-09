from ipcqueue import posixmq

q1 = posixmq.Queue('/telemetry',maxmsgsize=8192)
q2 = posixmq.Queue('/notify',maxmsgsize=8192)

q1.close()
q1.unlink()
q2.close()
q2.unlink()
