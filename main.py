from datetime import datetime, timedelta
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Cookie, Response, BackgroundTasks, Request, Form
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()

acc = {
    1: {
        'name': 'jsy',
        'pw': 538364,
        'level': 1,
        'describe': 'Nothing'},
    2: {
        'name': 'zyh',
        'pw': 133233,
        'level': 1,
        'describe': 'Nothing'},
    0: {'name': 'quest'}
}

# 名字的列表
a = []
for i in acc:
    a.append(acc[i]['name'])

post_item = {
    'fastapi': {
        'owner': 2,
        'title': 'fastapi',
        'body': 'nice',
        'good': 0,
        'post_comment': {
            '我觉得可以': '有一说一，我觉得可以',
            '我觉得不行': '有一说一，我觉得不行'}
    },
    'jsy': {
        'owner': 1,
        'title': 'jsy',
        'body': 'good',
        'good': 0,
    }
}


class Items(BaseModel):
    id: int
    len: float
    creater: Optional[str] = None
    size: Optional[bytes] = None


class Post(BaseModel):
    title: str
    body: str


class NoLogin(Exception): ...


class WrongUser(Exception): ...


@app.exception_handler(NoLogin)
async def unicorn_exception(*args, **kwargs):
    return JSONResponse(
        status_code=233,
        content={'注意': '未登录'}
    )


@app.exception_handler(WrongUser)
async def unicorn_exception(*args, **kwargs):
    return JSONResponse(
        status_code=499,
        content={'注意': '非法用户'}
    )


# 登录cookie校验
def cookie_check(
        r: Request,
        userid: Optional[int] = None):
    if userid is None:
        if r.cookies.get('is_login') == 'quest' or r.cookies.get('is_login') is None:
            raise NoLogin()
        else:
            if r.cookies.get('is_login') in a:
                return True
            else:
                raise WrongUser()
    elif userid is not None:
        if r.cookies.get('is_login') == 'quest' or r.cookies.get('is_login') is None:
            raise NoLogin()
        elif r.cookies.get('is_login') == acc[userid]['name']:
            return True
        else:
            raise WrongUser()


@app.get('/')  # 首页
async def root():
    return 'Welcome!'


# 中间件，分配一个cookie：quest
@app.middleware('http')
async def cookie_add(request: Request, call_next):
    response = await call_next(request)
    if request.url.path != '/login' and request.url.path != '/register':
        re = request.cookies.get('is_login')
        if re is None:
            def quest(rsp: Response):
                rsp.set_cookie(key='is_login', value='quest')

            quest(response)
    return response


@app.post('/login')  # 登录
def login(
        r: Request,
        response: Response,
        userid: int = Form(...),
        password: int = Form(...), ):
    if r.cookies.get('is_login') == 'quest' or r.cookies.get('is_login') is None:
        if userid in acc:
            if password == acc[userid]['pw']:
                response.set_cookie(key='is_login', value=acc[userid]['name'])
                return '登陆成功'
            else:
                return '密码错误'
        else:
            return '无此账号'
    elif r.cookies.get('is_login') == acc[userid]['name']:
        return JSONResponse(content='您已登录')
    else:
        return JSONResponse(content='请先登出账号或清除Cookies')


@app.post('/users/{userid}/logout')  # 登出
async def logout(
        r: Request,
        response: Response,
        userid: int, ):
    if cookie_check(r, userid):
        response.set_cookie(key='is_login', value='quest')
        return '已退出登录'


@app.post('/register')  # 注册
async def register(
        response: Response,
        userid: int = Form(...),
        password: int = Form(...),
        username: str = Form(...)):
    if userid in acc:
        return '账号已存在'
    else:
        acc[userid] = {'name': username, 'pw': password, 'level': 1}
        response.set_cookie(key='is_login', value=acc[userid]['name'])
        print(acc[userid])
        return '注册成功'


@app.post('/post/{userid}/postin')  # 发帖
async def post_in(
        request: Request,
        userid: int,
        post_title: str = Form(...),
        post_body: str = Form(...), ):
    if cookie_check(request, userid):
        post_item[post_title] = {'title': post_title, 'body': post_body, 'good': 0}
        print(post_item[post_title])
        return '发帖成功'


@app.get('/post/{post_title}')  # 获取帖子信息
async def post_get(post_title: str):
    if post_title in post_item:
        return post_item[post_title]['body'], '点赞数:%s' % post_item[post_title]['good'], '评论：', \
               post_comment_get(post_title)
    else:
        raise HTTPException(status_code=404, detail='你所访问的页面不存在')


def post_comment_get(post_title: str):  # 获取评论
    if 'post_comment' in post_item[post_title]:
        return post_item[post_title]['post_comment']
    else:
        return '还没有评论哦'


@app.delete('/users/{userid}')  # 删除账户
def delete_user(
        userid: int,
        r: Request):
    if cookie_check(r):
        if userid in acc:
            del acc[userid]
            return '已完成'
        else:
            raise HTTPException(status_code=303, detail="账号不存在")


@app.put('/users/{userid}/account')  # 修改账户名字或密码
def update_pw(
        userid: int,
        r: Request,
        name: Optional[str] = Form(...),
        password: Optional[int] = Form(...)):
    if cookie_check(r, userid):
        if name is not None:
            acc[userid]['name'] = name
        if password is not None:
            acc[userid]['pw'] = password
        print(acc)
        return '已完成'


@app.put('/users/{userid}/describe')  # 修改简介
def update_ds(
        r: Request,
        userid: int,
        dscb: Optional[str] = Form(...)):
    if cookie_check(r, userid):
        if dscb is None:
            dscb = 'Nothing'
        acc[userid]['describe'] = dscb
        print(acc)
        return '已修改完成'


@app.post('/post/{post_title}/good')  # 帖子点赞
async def post_good(
        post_title: str,
        r: Request, ):
    if cookie_check(r):
        if post_title in post_item:
            post_item[post_title]['good'] += 1
            return '点赞成功，当前点赞数：%s' % post_item[post_title]['good']


@app.delete('/post/{post_title}')  # 删帖子
async def post_del(
        post_title: str,
        r: Request):
    if cookie_check(r):
        if post_title in post_item:
            del post_item[post_title]
            return '已完成'
        else:
            raise HTTPException(status_code=404, detail='无此贴')


@app.post('/post/{post_title}/{post_comment}')  # 跟帖评论
def post_comment(
        r: Request,
        post_title: str,
        post_comment_title: str,
        post_comment_body: str):
    if cookie_check(r):
        if post_title in post_item:
            post_item[post_title]['post_comment'] = {post_comment_title: post_comment_body}
            print(post_item[post_title]['post_comment'])
            return '评论成功'


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
