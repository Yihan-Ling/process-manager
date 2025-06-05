from time import sleep

def run_until():
    var = 0
    while  var<15:
        # print(var)
        var += 1
        sleep(1)
    print("d_one exits")
        

if __name__ == "__main__":
    run_until()