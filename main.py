from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Cookie, Response, Header, Request
from pydantic import BaseModel

app = FastAPI()

acc = {
    1: {
        'name': 'jsy',
        'pw': 538364,
        'level': 1, },
    2: {
        'name': 'zyh',
        'pw': 133233,
        'level': 1, }
}

post_item = {
    'fastapi': {
        'title': 'fastapi',
        'body': 'nice',
        'good': 0,
        'post_comment': {
            '我觉得可以': '有一说一，我觉得可以',
            '我觉得不行': '有一说一，我觉得不行'}
    },
    'jsy': {
        'title': 'jsy',
        'body': 'good',
        'good': 0,
    }
}


class User(BaseModel):
    id: int
    name: Optional[str] = None
    pw: int


class Post(BaseModel):
    title: str
    body: str


@app.get('/')  # 首页
async def root():
    return 'Welcome!'


@app.post('/login')  # 登录
async def login(user: User, response: Response):
    if user.id in acc:
        print(user)
        if user.pw == acc[user.id]['pw']:
            await set_cookie(response, acc[user.id]['name'])
            return '登陆成功'
        else:
            return '密码错误'
    else:
        return '无此账号'


async def set_cookie(response: Response, user_name):
    response.set_cookie(key=user_name, value='login')
    return {'message': 'welcome'}


@app.post('/{userid}logout')  # 登出
async def logout(userid: int):
    if userid in acc:
        if acc[userid]['login'] == 1:
            acc[userid]['login'] = 0
            return '已退出登录,登陆码login=%s' % acc[userid]['login']
        else:
            return '未登录'
    else:
        return '无此账号'


@app.post('/register')  # 注册
async def register(user: User):
    if user.id in acc:
        return '账号已存在'
    else:
        acc[user.id] = {'name': user.name, 'pw': user.pw, 'level': 1, 'login': 0}
        print(acc)
        return '注册成功'


@app.post('/post')  # 发帖
async def post_in(userid: int, post: Post):
    if check_login(userid):
        post_item[post.title] = {'title': post.title, 'body': post.body, 'good': 0}
        print(post_item[post.title])
        return '发帖成功'


@app.get('/post/{post_title}')  # 获取帖子信息
async def post_get(post_title: str):
    if post_title in post_item:
        return post_item[post_title]['body'], '点赞数:%s' % post_item[post_title]['good'], '评论：', \
               post_comment_get(post_title)


def post_comment_get(post_title: str):  # 获取评论
    if 'post_comment' in post_item[post_title]:
        return post_item[post_title]['post_comment']
    else:
        return '还没有评论哦'


@app.delete('/users/{id}')  # 删除账户
def delete_user(userid: int):
    if check_login(userid):
        if userid in acc:
            del acc[userid]
            return '已完成'
        else:
            raise HTTPException(status_code=404, detail="账号不存在")


@app.put('/users/{id}')  # 修改账户名字或密码
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


@app.post('/post/{post_title}/good')  # 帖子点赞
async def post_good(userid: int, post_title: str):
    if check_login(userid):
        if post_title in post_item:
            post_item[post_title]['good'] += 1
            return '点赞成功，当前点赞数：%s' % post_item[post_title]['good']


@app.delete('/post/{post_title}')  # 删帖子
async def post_del(userid: int, post_title: str):
    if check_login(userid):
        if post_title in post_item:
            del post_item[post_title]
            return '已完成'
        else:
            raise HTTPException(status_code=404, detail='无此贴')


@app.post('/post/{post_title}/{post_comment}')  # 跟帖评论
def post_comment(userid: int, post_title: str, post_comment_title: str, post_comment_body: str):
    if check_login(userid):
        if post_title in post_item:
            post_item[post_title]['post_comment'] = {post_comment_title: post_comment_body}
            print(post_item[post_title]['post_comment'])
            return '评论成功'


def check_login(userid: int):
    if userid in acc and acc[userid]['login'] == 1:
        return True
    else:
        raise HTTPException(status_code=233, detail='请登录')


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
