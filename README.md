# hoyo-news-server

米哈游新闻获取服务器

相关项目：[hoyo-news-web](https://github.com/orilights/hoyo-news-web)

新闻数据默认缓存 1 小时，第一次请求需要全量获取数据，可能会消耗较多时间

## 请求示例

`/<game>/<channal>`

路径参数：

`game`：要获取新闻的游戏，可选值：`genshin`, `starrail`, `honkai3`, `zzz`, `wd`, `honkai2`, `mihoyo`

`channal`：要获取新闻的渠道，可选值：`web_cn`, `web_os`, `bbs_cn_1`, `bbs_cn_2`, `bbs_cn_3`

查询参数：

- (可选)`force_refresh`：是否强制更新数据，可选值：`0`, `1`，默认为`0`

响应示例：

```json
{
    "code": 0,
    "msg": null,
    "data": [
        {
            "id": 122096,
            "createTime": "2024-01-28 23:39:30",
            "startTime": "2024-01-31 10:00:00",
            "title": "「神铸赋形」祈愿：「法器·鹤鸣余音」「法器·千夜浮梦」概率UP！",
            "cover": "https://fastcdn.mihoyo.com/content-v2/hk4e/122096/84688fc7a094fd0757e6f9ab78c17afe_1614695288761725973.jpg",
            "video": null
        },
        ...
    ],
    "update": 1706866847
}
```
