| 方法   | 端点                                                             | 参数                                  | 说明                   |
|------|----------------------------------------------------------------|-------------------------------------|----------------------|
| POST | http://127.0.0.1:5000/login                                    | code:用户的code                        | 获取openid             |
| GET  | http://127.0.0.1:5000/tests                                    | has_items(可选):True or False,获取每题的题目 | 获取所有题目,包括题项以及封面等信息   |
| GET  | http://127.0.0.1:5000/test/{{id}}                              | id:test的id                          | 获得单个题目               |
| GET  | http://127.0.0.1:5000/user/{{open_id}}/records                 | open_id                             | 获得用户所有答题记录           |
| GET  | http://127.0.0.1:5000/test/{{test_id}}/rank_list               | score:测试结果分数                        | 答题结束后获得排行榜           |
| POST | http://127.0.0.1:5000/user/{{open_id}}/records/add             | test_id<br/>item_id                 | 录音结束后传输              |
| GET  | http://127.0.0.1:5000/user/{{open_id}}/test/{{test_id}}/record |                                     | 获得特定题目的答题记录,在答题结束后请求 |

u

 