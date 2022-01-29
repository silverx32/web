from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

acc = {
    1: {
        'name': 'jsy',
        'pw': 538364,
        'level': 1,
        'login': 0},
    2: {
        'name': 'zyh',
        'pw': 133233,
        'level': 1,
        'login': 0}
}

post_item = {
    'fastapi': {
        'title': 'fastapi',
        'body': 'nice',
        'good': 0}
}


class User(BaseModel):
    id: int
    name: Optional[str] = None
    pw: int


class Post(BaseModel):
    title: str
    body: str


def check_login(userid: int):
    if userid in acc and acc[userid]['login'] == 1:
        return True
    else:
        raise HTTPException(status_code=233, detail='请登录')


@app.get('/')
async def root():
    return 'Welcome!'


@app.post('/login')
async def login(user: User):
    if user.id in acc:
        if acc[user.id]['login'] == 1:
            return '已经登录'
        else:
            print(user)
            if user.pw == acc[user.id]['pw']:
                acc[user.id]['login'] = 1
                return '登陆成功,登录码login=%s' % acc[user.id]['login']
            else:
                return '密码错误'
    else:
        return '无此账号'


@app.post('/{userid}logout')
async def logout(userid: int):
    if userid in acc:
        if acc[userid]['login'] == 1:
            acc[userid]['login'] = 0
            return '已退出登录,登陆码login=%s' % acc[userid]['login']
        else:
            return '未登录'
    else:
        return '无此账号'


@app.post('/register')
async def register(user: User):
    if user.id in acc:
        return '账号已存在'
    else:
        acc[user.id] = {'name': user.name, 'pw': user.pw, 'level': 1, 'login': 0}
        print(acc)
        return '注册成功'


@app.post('/post')
async def post_in(userid: int, post: Post):
    if check_login(userid):
        post_item[post.title] = {'title': post.title, 'body': post.body, 'good': 0}
        print(post_item[post.title])
        return '发帖成功'


@app.get('/post/{post_title}')
async def post_add(post_title: str):
    if post_title in post_item:
        return post_item[post_title]['body'], '点赞数:%s' % post_item[post_title]['good']


@app.delete('/users/{id}')
def delete_user(userid: int):
    if check_login(userid):
        if userid in acc:
            del acc[userid]
            return '已完成'
        else:
            raise HTTPException(status_code=404, detail="账号不存在")


@app.put('/users/{id}')
def update_pw(userid: int, name: Optional[str] = None, pw: Optional[int] = None):
    if check_login(userid):
        if userid in acc:
            if name is not None:
                acc[userid]['name'] = name
            if pw is not None:
                acc[userid]['pw'] = pw
            print(acc)
            return '已完成'
        else:
            raise HTTPException(status_code=404, detail="账号不存在")


@app.post('/post/{post_title}/good')
async def post_good(userid: int, post_title: str):
    if check_login(userid):
        if post_title in post_item:
            post_item[post_title]['good'] = post_item[post_title]['good'] + 1
            return '点赞成功，当前点赞数：%s' % post_item[post_title]['good']


@app.delete('/post/{post_title}')
async def post_del(userid: int, post_title: str):
    if check_login(userid):
        if post_title in post_item:
            del post_item[post_title]
            return '已完成'
        else:
            raise HTTPException(status_code=404, detail='无此贴')


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
