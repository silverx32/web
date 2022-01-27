from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import aiofiles

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)

app = FastAPI()

acc = {
    1: {
        'name': 'jsy',
        'pw': 538364,
        'level': 1},
    2: {
        'name': 'zyh',
        'pw': 133233,
        'level': 1}
}


class User(BaseModel):
    id: int
    name: Optional[str] = None
    pw: int


@app.get('/')
async def root():
    return 'Welcome!'


@app.post('/login')
async def login(user: User):
    if user.id in acc:
        print(user)
        if user.pw == acc[user.id]['pw']:
            return '登陆成功'
        else:
            return '密码错误'
    else:
        return '无此账号'


@app.post('/register')
async def register(user: User):
    a = {}
    if user.id in acc:
        return '账号已存在'
    else:
        acc[user.id] = a
        a['name', 'pw', 'level'] = [user.name, user.pw, 1]
        print(acc)
        return '注册成功'


