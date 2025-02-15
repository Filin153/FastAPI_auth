from common.services.send.mail import Mail
import asyncio

def main():
    mail = Mail()
    asyncio.run(mail._worker())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        print("Stop worker!")
