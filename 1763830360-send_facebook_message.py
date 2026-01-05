import requests
import json
import time
import random
import re
from typing import Dict, Any, Optional


class CookieHandler:
    @staticmethod
    def to_dict(cookie_str: str) -> Dict[str, str]:
        return {k.strip(): v.strip() for item in cookie_str.split(";") 
                if "=" in item for k, v in [item.split("=", 1)]}


class NumberEncoder:
    @staticmethod
    def to_base36(num: int) -> str:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return "0"
        result = ""
        while num:
            num, remainder = divmod(num, 36)
            result = chars[remainder] + result
        return result


class UniqueIDGenerator:
    @staticmethod
    def generate() -> str:
        timestamp_ms = int(time.time() * 1000)
        random_bits = int(random.random() * 4294967295)
        binary_ts = bin(timestamp_ms)[2:]
        binary_rand = bin(random_bits)[2:].zfill(22)[-22:]
        return str(int(binary_ts + binary_rand, 2))
    
    @staticmethod
    def thread_format() -> str:
        ts = int(time.time() * 1000)
        rand1 = int(random.random() * 4294967295)
        rand2 = hex(int(random.random() * (2**31)))[2:]
        return f"<{ts}:{rand1}-{rand2}@mail.projektitan.com>"


class HTMLExtractor:
    @staticmethod
    def find_pattern(html: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, html)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_token(html: str) -> Optional[str]:
        patterns = [
            r'DTSGInitialData".*?"token":"([^"]+)"',
            r'"token":"([^"]+)"',
        ]
        for pattern in patterns:
            result = HTMLExtractor.find_pattern(html, pattern)
            if result:
                return result
        return None
    
    @staticmethod
    def extract_user_id(html: str) -> Optional[str]:
        patterns = [
            r'"actorID":"(\d+)"',
            r'"USER_ID":"(\d+)"',
            r'c_user=(\d+)',
        ]
        for pattern in patterns:
            result = HTMLExtractor.find_pattern(html, pattern)
            if result:
                return result
        return None
    
    @staticmethod
    def extract_revision(html: str) -> Optional[str]:
        pattern = r'client_revision["\s:]+(\d+)'
        return HTMLExtractor.find_pattern(html, pattern)
    
    @staticmethod
    def extract_jazoest(html: str) -> Optional[str]:
        pattern = r'jazoest=(\d+)'
        return HTMLExtractor.find_pattern(html, pattern)


class FacebookSession:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.token = None
        self.user_id = None
        self.revision = None
        self.jazoest = None
        
    def authenticate(self) -> bool:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "cookie": self.cookie,
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(
                "https://www.facebook.com/",
                headers=headers,
                cookies=CookieHandler.to_dict(self.cookie),
                timeout=30
            )
            
            html = response.text
            
            self.token = HTMLExtractor.extract_token(html)
            self.user_id = HTMLExtractor.extract_user_id(html)
            self.revision = HTMLExtractor.extract_revision(html) or "1000000"
            self.jazoest = HTMLExtractor.extract_jazoest(html) or "0"
            
            return bool(self.token and self.user_id)
        except:
            return False
    
    def get_info(self) -> Dict[str, str]:
        return {
            "token": self.token or "N/A",
            "user_id": self.user_id or "N/A",
            "revision": self.revision or "N/A",
            "jazoest": self.jazoest or "N/A"
        }


class MessagePayload:
    def __init__(self, session: FacebookSession):
        self.session = session
        self.request_counter = 0
    
    def build(self, recipient_id: str, text: str) -> Dict[str, Any]:
        self.request_counter += 1
        
        payload = {
            "fb_dtsg": self.session.token,
            "jazoest": self.session.jazoest,
            "__a": "1",
            "__user": self.session.user_id,
            "__req": NumberEncoder.to_base36(self.request_counter),
            "__rev": self.session.revision,
            "av": self.session.user_id,
        }
        
        payload.update({
            "specific_to_list[0]": f"fbid:{recipient_id}",
            "specific_to_list[1]": f"fbid:{self.session.user_id}",
            "other_user_fbid": recipient_id,
        })
        
        unique_id = UniqueIDGenerator.generate()
        
        payload.update({
            "body": text,
            "action_type": "ma-type:user-generated-message",
            "client": "mercury",
            "author": f"fbid:{self.session.user_id}",
            "timestamp": int(time.time() * 1000),
            "timestamp_absolute": "Today",
            "source": "source:chat:web",
            "source_tags[0]": "source:chat",
            "client_thread_id": f"root:{unique_id}",
            "offline_threading_id": unique_id,
            "message_id": unique_id,
            "threading_id": UniqueIDGenerator.thread_format(),
            "ephemeral_ttl_mode": "0",
            "manual_retry_cnt": "0",
            "ui_push_phase": "V3",
        })
        
        flags = [
            "is_unread", "is_cleared", "is_forward",
            "is_filtered_content", "is_filtered_content_bh",
            "is_filtered_content_account", "is_filtered_content_quasar",
            "is_filtered_content_invalid_app", "is_spoof_warning"
        ]
        
        for flag in flags:
            payload[flag] = "false"
        
        return payload


class FacebookMessenger:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.session = FacebookSession(cookie)
        self.payload_builder = None
        self.ready = False
    
    def login(self) -> bool:
        if self.session.authenticate():
            self.payload_builder = MessagePayload(self.session)
            self.ready = True
            return True
        return False
    
    def send_message(self, to_user_id: str, message_text: str) -> Dict[str, Any]:
        if not self.ready:
            return {"success": False, "error": "Not logged in"}
        
        payload = self.payload_builder.build(to_user_id, message_text)
        
        headers = {
            "accept": "*/*",
            "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.facebook.com",
            "referer": "https://www.facebook.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            "x-fb-lsd": self.session.token,
        }
        
        try:
            response = requests.post(
                "https://www.facebook.com/messaging/send/",
                headers=headers,
                data=payload,
                cookies=CookieHandler.to_dict(self.cookie),
                timeout=10
            )
            
            json_text = response.text.split("for (;;);", 1)[1] if "for (;;);" in response.text else response.text
            result = json.loads(json_text)
            
            if result.get("payload") and result["payload"].get("actions"):
                action = result["payload"]["actions"][0]
                return {
                    "success": True,
                    "message_id": action.get("message_id"),
                    "timestamp": action.get("timestamp")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("errorDescription", "Unknown error"),
                    "error_code": result.get("error", 0)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def account_info(self) -> Dict[str, str]:
        return self.session.get_info() if self.ready else {"error": "Not logged in"}


def main():
    cookie = "datr=xUTBZxeUkejwQCeQd_udjsd7; ps_l=1; ps_n=1; sb=0kTBZ7-FGQHaSifJhhY1hRt1; pas=100040226507152%3ARD3xgk8lp7; dpr=1.25; locale=vi_VN; c_user=100040226507152; ar_debug=1; fr=1f0HYG9yl4jGuZeHq.AWfp7X7wYpJ66DrTl_BeNUzDW7lU_ONxAhVeycxQN2Ed094xoXM.BpQ2Tq..AAA.0.0.BpQ2Tq.AWcTheVr-z2BOJvu_fidUaLaSnU; xs=39%3A24-lmE0PLhs5RA%3A2%3A1765737989%3A-1%3A-1%3A%3AAcybkw0ip2QFScIACqo0rqUyohmmYaypfhAmslcxbjw"
    
    print("Get token Facebook...")
    messenger = FacebookMessenger(cookie)
    
    if messenger.login():
        print("Login successful!\n")
        
        info = messenger.account_info()
        print(f"User ID: {info['user_id']}")
        print(f"Token: {info['token'][:40]}...")
        
        print("\nSending message...")

        send_message_uid = '100040226507152'

        content = "Xin chào!"

        result = messenger.send_message(send_message_uid, content)
        
        print("\n" + "="*50)
        if result["success"]:
            print("SUCCESS")
            print(f"Message ID: {result['message_id']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print("FAILED")
            print(f"Error: {result.get('error')}")
            if 'error_code' in result:
                print(f"Error Code: {result['error_code']}")
        print("="*50)
    else:
        print("Login failed!")


if __name__ == "__main__":
    main()