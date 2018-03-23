import requests
import pickle

USER_PROFILE_PATH = "profile"
BOOKING_DETAIL_PATH = "bkdetail"

FCODES = {
	"badminton_northhill":"BB",
	"badminton_wave":"BS",
    "tennis_hall7":"TQ",
    "tennis_src":"TN"
}

P_INFOS = {
	"badminton_northhill":"3BB26",
	"badminton_wave":"3BS24",
    "tennis_hall7":"1TQ22",
	"tennis_src":"1TN26",
}

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

def load_booking_detail(file_path):
    with open(file_path,"rb") as f:
        detail = pickle.load(f)
        return detail

def login_phase_one(s,username,domain="STUDENT"):
    data = {
        "Domain":domain,
        "UserName": username,
        "bOption": "OK",
        "nocookie":"",
        "p2":"https://wis.ntu.edu.sg/pls/webexe88/srce_smain_s.Notice_O",
        "t":1
    }

    headers = {
        "Origin":"https://sso.wis.ntu.edu.sg",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
        "Content-Type":"application/x-www-form-urlencoded",
        "Referer":"https://sso.wis.ntu.edu.sg/webexe88/owa/sso_login1.asp?t=1&p2=https://wis.ntu.edu.sg/pls/webexe88/srce_smain_s.Notice_O&extra=&pg=",
    }
    response = s.post("https://sso.wis.ntu.edu.sg/webexe88/owa/sso_login2.asp",data=data,headers=headers)


def login_phase_two(s,username,password,domain="STUDENT"):
    data = {
        "Domain": domain,
        "UserName": username,
        "PIN":password,
        "bOption": "OK",
        "nocookie": "",
        "p2": "https://wis.ntu.edu.sg/pls/webexe88/srce_smain_s.Notice_O",
        "t": 1
    }

    headers = {
        "Origin": "https://sso.wis.ntu.edu.sg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://sso.wis.ntu.edu.sg/webexe88/owa/sso_login2.asp",
    }

    response = s.post("https://sso.wis.ntu.edu.sg/webexe88/owa/sso.asp",data=data,headers=headers)

    if (str(response.content).find("Verification completed")!=-1):
        print ("Login successful")
    else:
        print ("Login failed")
    return response.cookies

def book_ticket(s,court_type,court_no,date,slot_no,frmk,matric,save_confirmation_to):

    data = {
        "P_info":P_INFOS[court_type],
        "bOption":"Confirm",
        "fcode":FCODES[court_type], # court type
        "fcourt":court_no, # court no.
        "fdate":date, #"29-Sep-2016",
        "floc":"{}{}".format(FCODES[court_type],str(court_no).zfill(2)), # court type + no.
        "frmfrom":"selfbook",
        "frmk":frmk,
        "ftype":2,
        "noaguest":0,
        "opmode":1,
        "p1":matric, # matric
        "p2":"",
        "paytype":"CC",
        "rptype":1,
        "sno":slot_no, # time slot number
        "stype":"D"
    }

    headers = {
        "Origin": "https://wis.ntu.edu.sg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://wis.ntu.edu.sg/pls/webexe88/srce_sub1.srceb$sel32",
    }

    response = s.post("https://wis.ntu.edu.sg/pls/webexe88/srce_sub1.srceb$sel33", data=data, headers=headers)
    response_content = str(response.content)
    if (response_content.find("Official Permit")!=-1):
        print ("Booking success")
        with open(save_confirmation_to,"wb") as f:
            f.write(response.content)
    else:
        print ("Booking failed")
        print (response_content)

def get_frmk(s,court_type,court_no,date,slot_no,matric):
    data={
        "p1":matric,
        "p2":"",
        "p_info":P_INFOS[court_type],
        "p_rec":"3{}2{}{}{}{}".format(FCODES[court_type],FCODES[court_type],str(court_no).zfill(2),date,slot_no)
    }

    headers = {
        "Origin": "https://wis.ntu.edu.sg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = s.post("https://wis.ntu.edu.sg/pls/webexe88/srce_sub1.srceb$sel32", data=data, headers=headers)
    # retrieve frmk from html
    pattern = "NAME=\"frmk\" VALUE=\""
    response_content=str(response.content)
    if (response_content.find(pattern)==-1):
        print ("FRMK cannot be found")
        print(response_content)
    slice = response_content[response_content.find(pattern)+len(pattern):]
    frmk = slice[:slice.find("\"")]
    return frmk


def make_booking(profile_path,bdetail_path):
    profile = load_user_profile(profile_path=profile_path)
    booking_detail = load_booking_detail(file_path=bdetail_path)

    session = requests.Session()
    # login
    matric = profile["matric"]
    username = profile["username"]
    domain = profile["domain"]
    login_phase_one(session,username=username,domain=domain)
    cookies = login_phase_two(session,username=username,domain=domain,password=profile["password"])

    # make booking
    court_type = booking_detail["venue"]
    court_no = booking_detail["court_no"]
    date = booking_detail["date"]
    slot_no = booking_detail["slot_no"]
    frmk = get_frmk(s=session,court_type=court_type,court_no=court_no,date=date,slot_no=slot_no,matric=matric)
    book_ticket(s=session,court_type=court_type,court_no=court_no,date=date,
                slot_no=slot_no,frmk=frmk,matric=matric,save_confirmation_to=booking_detail["save_receipt_to"])

if __name__ == "__main__":
    make_booking(profile_path=USER_PROFILE_PATH,bdetail_path=BOOKING_DETAIL_PATH)