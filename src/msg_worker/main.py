from core.services.send.rabbitmq import send_msg
import asyncio

def main():
    while True:
        asyncio.run(send_msg())

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        print("Stop worker!")