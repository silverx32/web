from typing import Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

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

post_item = {'fastapi': {'title': 'fastapi', 'body': 'nice'}}


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
    if user.id in acc:
        return '账号已存在'
    else:
        acc[user.id] = {'name': user.name, 'pw': user.pw, 'level': 1}
        print(acc)
        return '注册成功'


class Post(BaseModel):
    title: str
    body: str


@app.post('/post')
async def post_in(post: Post):
    post_item[post.title] = {'title':post.title ,'body':post.body}
    print(post_item[post.title])
    return '发帖成功'


@app.get('/post/{post_title}')
async def post_add(post_title: str):
    if post_title in post_item:
        return post_item[post_title]['body']
    pass


@app.delete('/users/{id}')
def delete_user(userid:int):
    if userid in acc:
        del acc[userid]
        return '已完成'
    else:
        raise HTTPException(status_code=404, detail="账号不存在")


@app.put('/users/{id}')
def update_pw(userid: int, name: Optional[str] = None, pw: Optional[int] = None):
    if userid in acc:
        if name is not None:
            acc[userid]['name'] = name
        if pw is not None:
            acc[userid]['pw'] = pw
        print(acc)
        return '已完成'
    else:
        raise HTTPException(status_code=404, detail="账号不存在")


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
