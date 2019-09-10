import numpy as np

import json

a = np.arange(1028*9).reshape(1028,9)
a = np.random.rand(1028*9).reshape(1028,9).round(2)
j = json.dumps(a.tolist())


Result = {
    "Name" : "A",
    "Prop" : { "Fix" : 1,"Choice" :0},
    "ID"   : 0,
    "Data" : a.tolist()
}

J  = json.dumps(Result)

with open("tester.json", mode='w') as f:
    f.write(J)

with open("tester.json", mode='r') as f:
    r = f.read()
    r  = json.loads(r)
    print(r)
    print(np.array(r["Data"]))



