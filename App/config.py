config = {
  "name": "Mock(TraderVersion)",
  "data":       "../Data/DAT_MS_GBPAUD_M1_201908.csv",
  "dir_json" :  "C:\\Users\\kaz38\\Downloads\\",
  "ID_json"  :  "UserID"
  #"data": "../Data/GBPAUD_M1_201908.csv",
}

ssbo_location ={
    "vis" :   0,    # visualize buffer
    "ac" :    1,    # atomic counter
    "dprop":  2,    # draw property
    "_rates": 3,    # input data
    "asset":  4,    # output
    "io":     5,    # inout
}


param_range =[
            [5,60,1],[5,100,1],[5,50,1.2],[12,120,1],[12,120,1],[21,210,1],[0.005,0.01,0.001],[0.1,0.5,0.05]
        ]