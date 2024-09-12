import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging

async def main():
    controller = Controller(Debugging(), hostname='localhost', port=1025)
    controller.start()
    print('SMTP server running at localhost:1025')
    try:
        while True:
            await asyncio.sleep(3600)  # Run for an hour, change as needed
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()

if __name__ == '__main__':
    asyncio.run(main())
