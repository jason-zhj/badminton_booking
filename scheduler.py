import getpass
import pickle
import os
from booking import make_booking

USER_PROFILE_PATH = "profile"
BOOKING_DETAIL_PATH = "bkdetail"
NON_EMPTY_VALIDATOR = lambda x:len(x)>0

VENUE_INFO = {
    "badminton_northhill":{
        "courts": list(range(1,7)),
        "time_slots": {
            i: "{}:00-{}:00".format(i+7,i+8)
            for i in range(1,15) # 14 time slots
        }
    },
    "badminton_wave":{
        "courts": list(range(1,5)),
        "time_slots":{
            i: "{}:30-{}:30".format(i+8,i+9)
            for i in range(1,13) # 12 slots
        }
    },
    "tennis_src":{
        "courts": list(range(1,7)),
        "time_slots":{
            i: "{}:{}-{}:{}".format(
                int((6 * 60 + 45 + 45 * i)/60), # 06:45 + 45 * i
                (6 * 60 + 45 + 45 * i) % 60,
                int((6 * 60 + 45 + 45 * (i+1))/60), # 07:30 + 45 * i
                (6 * 60 + 45 + 45 * (i+1)) % 60,
            )
            for i in range(1,20) # 19 slots
        }
    },
    "tennis_hall7":{
        "courts": list(range(1,5)),
        "time_slots":{
            i: "{}-{}:{}-{}".format(
                int((8 * 60 + 15 + 45 * i)/60), # 08:15 + 45 * i
                (8 * 60 + 15 + 45 * i) % 60,
                int((8 * 60 + 15 + 45 * (i+1))/60), # 09:00 + 45 * i
                (8 * 60 + 15 + 45 * (i+1)) % 60,
            )
            for i in range(1,17) # 16 slots
        }
    }
}

def encode_pass(message):
    result = ''
    for i in range(0, len(message)):
        result = result + chr(ord(message[i]) - 2)
    return result

def input_with_validation(prompt_str,validator=None):
    "validator is a callable, which returns true or false"
    user_input = input(prompt_str)
    while (validator is not None and not validator(user_input)):
        print("Invalid Input!")
        user_input = input(prompt_str)
    return user_input

def input_password():
    "input password with confirmation"
    print("enter your password:")
    p1 = getpass.getpass()
    print("confirm your password:")
    p2 = getpass.getpass()
    while (p1!=p2):
        print("Two passwords don't match!")
        print("enter your password:")
        p1 = getpass.getpass()
        print("confirm your password:")
        p2 = getpass.getpass()
    return p1

def decode_pass(message):
    result = ''
    for i in range(0, len(message)):
        result = result + chr(ord(message[i]) + 2)
    return result

def load_user_profile(profile_path):
    with open(profile_path,"rb") as f:
        profile = pickle.load(f)
        profile["password"] = decode_pass(message=profile["password"])
        return profile

def record_user_profile(save_profile_to):
    domain = input_with_validation(prompt_str="enter your domain (student/staff):",validator=lambda x:x in ["student","staff"])
    username = input_with_validation(prompt_str="enter your username: ",validator=NON_EMPTY_VALIDATOR)
    password = input_password()
    matric_name = "NRIC" if domain == "staff" else "Matric Number"
    matric = input_with_validation(prompt_str="enter your {}:".format(matric_name),validator=NON_EMPTY_VALIDATOR)
    profile = {
        "domain":domain,
        "username": username,
        "password": encode_pass(message=password),
        "matric":matric
    }
    with open(save_profile_to,"wb") as f:
        pickle.dump(profile,f)
    # return the profile
    profile["password"] = password
    return profile

def input_venue():
    venue_code = {
        1: "badminton_northhill",
        2: "badminton_wave",
        3: "tennis_src",
        4: "tennis_hall7"
    }
    venue = input_with_validation(
        prompt_str="""choose the venue you want to book:
(1) Badminton @ Northhill
(2) Badminton @ Wave
(3) Tennis @ SRC
(4) Tennis @ Hall 7
enter 1/2/3/4:""",
        validator=lambda x:x.strip() in ["1","2","3","4"]
    )
    return venue_code[int(venue)]

def date_validator(date_str):
    # check day
    day = date_str[:2]
    if (not day.isdigit() or int(day) not in range(1,32)): return False
    # check hyphen
    if (not date_str[2] == "-" or not date_str[6] == "-"): return False
    # check month
    month = date_str[3:6]
    if (not month in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]): return False
    # check year
    year = date_str[7:].strip()
    if (not year.isdigit() or len(year) != 4): return False
    return True

def input_court_no(venue):
    courts = VENUE_INFO[venue]["courts"]
    court_no = input_with_validation(prompt_str="enter the court number ({}):".format("/".join([str(c) for c in courts])),
                                     validator=lambda x:x.isdigit() and int(x) in courts)
    return int(court_no)

def input_slot_no(venue):
    time_slots = VENUE_INFO[venue]["time_slots"]
    for key,value in time_slots.items():
        print("({}): {}".format(key,value))
    slot_no = input_with_validation(prompt_str="enter a slot number: ",validator=lambda x:x.isdigit() and int(x) in time_slots.keys())
    return int(slot_no)

def record_booking_detail(save_to):
    venue = input_venue()
    date = input_with_validation(prompt_str="enter the date to book (e.g. 05-Oct-2017):", validator=date_validator)
    court_no = input_court_no(venue=venue)
    slot_no = input_slot_no(venue=venue)
    save_receipt_to = input_with_validation(prompt_str="Where do you want to save the booking receipt (html file)? enter a file name: ",validator=NON_EMPTY_VALIDATOR)
    booking_detail = {
        "venue": venue, "date": date, "court_no":court_no, "slot_no": slot_no,
        "save_receipt_to":os.path.join(os.path.dirname(__file__),save_receipt_to)
    }
    with open(save_to,"wb") as f:
        pickle.dump(booking_detail,f)
    return booking_detail

def create_schedule_command(target_date):
    "return a command string if the scheduling is necessary, otherwise return None"
    import datetime
    date_str = str(datetime.datetime.now())[:10]
    task_name = "Booking Task[{}]".format(date_str)
    file_to_execute = os.path.join(os.path.dirname(os.path.abspath(__file__)),"book.bat")
    # exe_command = 'cmd.exe /K "cd /d {} & book.bat"'.format(os.path.dirname(__file__))
    book_date = datetime.datetime.strptime(target_date, "%d-%b-%Y") + datetime.timedelta(days=-7)
    if (datetime.datetime.now() > book_date):
        print("Oops, seems like the required booking can already be done on the NTU website")

        return None,None

    print("file_to_execute is {}".format(file_to_execute))

    command = 'SchTasks /Create /SC ONCE /TN "{}" /TR "{}" /ST 00:00 /SD {}'.format(
        task_name,
        file_to_execute,
        book_date.strftime("%m/%d/%Y")
    )

    # write to book.bat
    batch_content = 'cmd /K "cd /d {} & python booking.py >> booking_result.txt"'.format(os.path.dirname(os.path.abspath(__file__)))
    with open("book.bat","w") as f:
        f.write(batch_content)
    return command, book_date.strftime("%m/%d/%Y")

def make_schedule():
    # check whether user profile is created
    if (not os.path.exists(USER_PROFILE_PATH)):
        profile = record_user_profile(save_profile_to=USER_PROFILE_PATH)
    else:
        profile = load_user_profile(profile_path=USER_PROFILE_PATH)
    # record booking detail
    print("Current user: {}".format(profile["username"]))
    booking_detail = record_booking_detail(save_to=BOOKING_DETAIL_PATH)
    # schedule the booking
    command, date_to_exe = create_schedule_command(target_date=booking_detail["date"])
    if (command is None):
        # no need to schedule, book it now
        book_now = input_with_validation(prompt_str="Do you want to book it now? [y/n]:",
                                         validator=lambda x: x in ["y", "n"])
        if (book_now):
            make_booking(profile_path=USER_PROFILE_PATH,bdetail_path=BOOKING_DETAIL_PATH)
        return
    else:
        # create schedule
        print("Scheduling task to run at 00:00 on {}...".format(date_to_exe))
        print("Please make sure your PC is not logged off at that time")
        os.system(command)

if __name__ == "__main__":
    make_schedule()