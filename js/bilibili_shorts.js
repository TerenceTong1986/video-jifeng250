/**
 * B站短剧/漫剧源 (免cookie)
 * - 搜索: wbi search/type?search_type=video (可搜UP主搬运的短剧/漫剧全集)
 * - 详情: x/web-interface/view (分P列表)
 * - 播放: x/player/playurl?qn=64&fnval=1 (mp4直链, 免cookie已验证)
 * 2026-08-27 免cookie验证通过; 
 * 注意: 旧接口 x/web-interface/search/type 会被412, 必须用 wbi 接口
 */
var rule = {
    title: 'B站短剧',
    host: 'https://api.bilibili.com',
    url: '/x/web-interface/wbi/search/type?search_type=video&keyword=fyclass&page=fypage',
    detailUrl: '/x/web-interface/view?bvid=fyid',
    searchUrl: '/x/web-interface/wbi/search/type?search_type=video&keyword=**&page=fypage',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com'
    },
    timeout: 8000,
    class_name: '短剧&漫剧&AI漫剧&动漫&沙雕动画&科幻动漫&玄幻动漫&都市动漫&战神&神医&赘婿&逆袭&重生&穿越&甜宠&总裁&玄幻&都市&搞笑&热门榜',
    class_url: '短剧&漫剧&AI漫剧&动漫&沙雕动画&科幻动漫&玄幻动漫&都市动漫&战神&神医&赘婿&逆袭&重生&穿越&甜宠&总裁&玄幻&都市&搞笑&B站热门',
    limit: 5,
    一级: `js:
    // input 已是完整URL: https://api.bilibili.com/x/web-interface/wbi/search/type?search_type=video&keyword=%E7%9F%AD%E5%89%A7&page=1
    let u = input.indexOf('http') === 0 ? input : 'https://api.bilibili.com' + input;
    let html = request(u);
    let jo = JSON.parse(html);
    let videos = [];
    if (jo.code === 0 && jo.data && jo.data.result) {
        jo.data.result.forEach(function (v) {
            videos.push({
                vod_id: v.bvid,
                vod_name: v.title.replace(/<[^>]*>/g, ''),
                vod_pic: (v.pic || '').replace(/^\\/\\//, 'https://'),
                vod_remarks: v.duration,
                vod_actor: v.author,
                vod_content: (v.description || '') + '\\n播放:' + v.play + ' 弹幕:' + v.video_review
            });
        });
    }
    VODS = videos;
    `,
    二级: `js:
    let u = input.indexOf('http') === 0 ? input : 'https://api.bilibili.com' + input;
    let html = request(u);
    let jo = JSON.parse(html);
    let d = jo.data;
    let pages = d.pages || [];
    VOD = {
        vod_id: d.bvid,
        vod_name: d.title,
        vod_pic: (d.pic || '').replace(/^\\/\\//, 'https://'),
        vod_actor: d.owner ? d.owner.name : '',
        vod_content: d.desc || '',
        vod_remarks: d.duration + '分',
        vod_play_from: 'B站',
        vod_play_url: pages.map(function (p) {
            return p.part + ' $ ' + d.bvid + '+' + p.cid;
        }).join('#')
    };
    `,
    搜索: `js:
    // input 形如: https://api.bilibili.com/x/web-interface/wbi/search/type?search_type=video&keyword=某某&page=1
    let u = input.indexOf('http') === 0 ? input : 'https://api.bilibili.com' + input;
    let html = request(u);
    let jo = JSON.parse(html);
    let videos = [];
    if (jo.code === 0 && jo.data && jo.data.result) {
        jo.data.result.forEach(function (v) {
            videos.push({
                vod_id: v.bvid,
                vod_name: v.title.replace(/<[^>]*>/g, ''),
                vod_pic: (v.pic || '').replace(/^\\/\\//, 'https://'),
                vod_remarks: v.duration,
                vod_actor: v.author
            });
        });
    }
    VODS = videos;
    `,
    lazy: `js:
    // input: bvid+cid, 如 BV1Pogf6vEhQ+40347242275
    let ids = input.split('+');
    let bvid = ids[0];
    let cid = ids[1];
    let url = 'https://api.bilibili.com/x/player/playurl?bvid=' + bvid + '&cid=' + cid + '&qn=64&fnval=1';
    let html = request(url);
    let jo = JSON.parse(html);
    if (jo.code === 0 && jo.data && jo.data.durl) {
        let durl = jo.data.durl;
        let urls = durl.map(function (u) { return u.url; }).join(',');
        input = {
            parse: 0,
            url: urls,
            header: JSON.stringify({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com'
            })
        };
    } else {
        input = '';
    }
    `
}