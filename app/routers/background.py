from fastapi import BackgroundTasks, APIRouter

router = APIRouter(prefix='/background')

def write_notification(email:str, message: str=""):
    with open('log.txt', 'w') as email_file:
        content = f'notification for {email}: {message}'
        email_file.write(content)


@router.post('/new-notification/{email}')
async def send_notification(email:str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {'message': 'the message is gonna be sent in the background'}