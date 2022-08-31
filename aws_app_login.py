from common_lib.common_base import valid_mandatory_parameters,get_input_parameter_value
from common_lib.common_error import BadUserInputError
from common_lib.selenium_aws_app_login import SeleniumAwsAppLogin
from os.path import dirname, abspath
from dotenv import load_dotenv
import os, sys
from common_lib.enum_browser_type import BrowserType

path = dirname(abspath(__file__)) + '/.env'
load_dotenv(path)



def start(argv):
    if (('-h' in argv) or ('-?' in argv)):
        print("""
        python3 aws_configure_sso_accounts.py -url AWS_SSO_START_URL 
        Program to load a csv to a mysql table
        Parameters:
            -url AWS_SSO_START_URL  --> mandatory
            -b BROWSER              --> optional, value most be CHROME or EDGE or FIREFOX if not set will asume CHROME

            For execution, it requires the following environment variables set
            - AWS_USERNAME
            - AWS_PASSWORD
            - OTP_2FA_DEVICE_ID, if it is necessary for aws logon

            -h or -? help
        """)
    
    elif not valid_mandatory_parameters(argv, ['-url']):
        raise BadUserInputError(
        """Input error. To run, aws_configure_sso_accounts.py -url AWS_SSO_START_URL 
                -b CHROME|EDGE|FIREFOX 
                [-h|-?]""")

    else:
        aws_start_url:str = get_input_parameter_value(argv,'-url')
        aws_username:str = None if "AWS_USERNAME" not in os.environ else os.environ["AWS_USERNAME"]
        if aws_username is None:
            raise BadUserInputError("The environment variable AWS_USERNAME not found")

        aws_password:str = None if "AWS_PASSWORD" not in os.environ else os.environ["AWS_PASSWORD"]
        if aws_password is None:
            raise BadUserInputError("The environment variable AWS_PASSWORD not found")

        otp_2fa_devide_id = None if "OTP_2FA_DEVICE_ID" not in os.environ else os.environ["OTP_2FA_DEVICE_ID"]

        browser_param = get_input_parameter_value(argv,'-b')
        browser = BrowserType.CHROME if browser_param is None else BrowserType[browser_param]


        aws_sso_login = SeleniumAwsAppLogin(aws_start_url=aws_start_url,
                                    aws_username=aws_username,
                                    aws_password=aws_password,
                                    otp_2fa_devide_id=otp_2fa_devide_id,
                                    browser=browser)
        aws_sso_login.login()
start(sys.argv)
