import time
from main_app import *

time.sleep(0.1)


if 1:
    reset_reason = machine.reset_cause()
    print(reset_reason)
    user_main(reset_reason)

