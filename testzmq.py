import zmq

context = zmq.Context()
s = context.socket(zmq.REQ)
s.connect("tcp://%s:6497" % "megalodon")


import IPython;
IPython.embed()

def megasave(desc):
    print "got save command"
    s.send("acquire;%s" % desc)
    s.recv()
    print "returning"

