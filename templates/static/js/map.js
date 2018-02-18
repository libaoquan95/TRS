// 百度地图API功能
// 创建Map实例
var map = new BMap.Map("map", {});
// 初始化地图,设置中心点坐标和地图级别
map.centerAndZoom(new BMap.Point(124.000, 37.500), 5);
//启用滚轮放大缩小
map.enableScrollWheelZoom();
map.enableInertialDragging();
map.enableContinuousZoom();
// 设置不显示高速路网
map.setMapStyle({
    styleJson: [{
        "featureType": "highway",
            "elementType": "all", 
            "stylers": {
                "visibility": "off"
        }
    }]
});
// 添加城市列表
map.addControl(new BMap.CityListControl({
    anchor: BMAP_ANCHOR_BOTTOM_RIGHT,
    offset: new BMap.Size(10, 20),
}));
// 添加定位控件
map.addControl(new BMap.GeolocationControl({
    anchor: BMAP_ANCHOR_BOTTOM_RIGHT,
    offset: new BMap.Size(10, 60),
}));

lons = document.getElementById("photoDataLon").innerText;
lats = document.getElementById("photoDataLat").innerText;

lons = lons.replace(/None,/g, "");
lats = lats.replace(/None,/g, "");

lonArray = lons.split(",");
latArray = lats.split(",");

var points = [];
for (var i=0; i<lonArray.length-1; i++) {
    points.push(new BMap.Point(lonArray[i], latArray[i]));
}

points = GpsToBaiduPoints(points);

var markers = [];
for (var i=0; i<lonArray.length-1; i++) {
    markers.push(new BMap.Marker(points[i]));
}
var markerClusterer = new BMapLib.MarkerClusterer(map, {markers:markers});

// 坐标转换，GPS坐标 -> 百度地图坐标
/**
*   地图位置计算工具(将GPS坐标转换成百度地图坐标)
*    参考文档：http://bbs.lbsyun.baidu.com/forum.php?mod=viewthread&tid=10923&qq-pf-to=pcqq.group
*
*    使用示例：批量转换坐标位置
*    
*    var transferedData = GpsToBaiduPoints(prePoints);
*    $.each(transferedData,function(index,point){
*       console.log(point);
*    });
*
*-------------------以下是提供的一个简单的访问接口-------------------------
*    参数: points:new BMap.Point(lng,lat)的集合
*    返回值:resultPoints:转换后 BMap.point点集
*    function GpsToBaiduPoints(points){
*        var resultPoints = [];
*        $.each(points,function(index,point){
*            //世界大地坐标转为百度坐标
*            var _t = wgs2bd(point.lat,point.lng);
*            var _BPoint = new BMap.Point(_t[1], _t[0]);
*            resultPoints.push(_BPoint);
*        });
*        return resultPoints;
*    }
*/
//默认提供一个接口直接调用
function GpsToBaiduPoints(points){
    var resultPoints = [];
    $.each(points,function(index,point){
        var _t = wgs2bd(point.lat,point.lng);
        var _BPoint = new BMap.Point(_t[1], _t[0]);
        resultPoints.push(_BPoint);
    });
    return resultPoints;
}

//////////////////////////////////////////
//////////////转换核心代码/////////////////
//////////////////////////////////////////
var pi = 3.14159265358979324;
var a = 6378245.0;
var ee = 0.00669342162296594323;
var x_pi = 52.3598775598298873;


//世界大地坐标转为百度坐标
function wgs2bd(lat,lon) {
    var wgs2gcjR = wgs2gcj(lat, lon);
    var gcj2bdR = gcj2bd(wgs2gcjR[0], wgs2gcjR[1]);
    return gcj2bdR;
}

function gcj2bd(lat,lon) {
    var pi = 3.14159265358979324;
    var a = 6378245.0;
    var ee = 0.00669342162296594323;
    var x_pi = 52.3598775598298873;
    
    var x = lon, y = lat;
    var z = Math.sqrt(x * x + y * y) + 0.00002 * Math.sin(y * x_pi);
    var theta = Math.atan2(y, x) + 0.000003 * Math.cos(x * x_pi);
    var bd_lon = z * Math.cos(theta) + 0.0065;
    var bd_lat = z * Math.sin(theta) + 0.006;
    var result = [];
    result.push(bd_lat);
    result.push(bd_lon);
    return result;
}

function bd2gcj(lat,lon) {
    var pi = 3.14159265358979324;
    var a = 6378245.0;
    var ee = 0.00669342162296594323;
    var x_pi = 52.3598775598298873;
    
    var x = lon - 0.0065, y = lat - 0.006;
    var z = Math.sqrt(x * x + y * y) - 0.00002 * Math.sin(y * x_pi);
    var theta = Math.atan2(y, x) - 0.000003 * Math.cos(x * x_pi);
    var gg_lon = z * Math.cos(theta);
    var gg_lat = z * Math.sin(theta);
    var result = [];
    result.push(gg_lat);
    result.push(gg_lon);
    return result;
}

function wgs2gcj(lat,lon) {
    var pi = 3.14159265358979324;
    var a = 6378245.0;
    var ee = 0.00669342162296594323;
    var x_pi = 52.3598775598298873;

    var dLat = transformLat(lon - 105.0, lat - 35.0);
    var dLon = transformLon(lon - 105.0, lat - 35.0);
    var radLat = lat / 180.0 * pi;
    var magic = Math.sin(radLat);
    magic = 1 - ee * magic * magic;
    var sqrtMagic = Math.sqrt(magic);
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi);
    dLon = (dLon * 180.0) / (a / sqrtMagic * Math.cos(radLat) * pi);
    var mgLat = lat + dLat;
    var mgLon = lon + dLon;
    var result = [];
    result.push(mgLat);
    result.push(mgLon);
    return result;
}

function transformLat(lat,lon) {
    var pi = 3.14159265358979324;
    var a = 6378245.0;
    var ee = 0.00669342162296594323;
    var x_pi = 52.3598775598298873;
    
    var ret = -100.0 + 2.0 * lat + 3.0 * lon + 0.2 * lon * lon + 0.1 * lat * lon + 0.2 * Math.sqrt(Math.abs(lat));
    ret += (20.0 * Math.sin(6.0 * lat * pi) + 20.0 * Math.sin(2.0 * lat * pi)) * 2.0 / 3.0;
    ret += (20.0 * Math.sin(lon * pi) + 40.0 * Math.sin(lon / 3.0 * pi)) * 2.0 / 3.0;
    ret += (160.0 * Math.sin(lon / 12.0 * pi) + 320 * Math.sin(lon * pi  / 30.0)) * 2.0 / 3.0;
    return ret;
}

function transformLon(lat,lon) {
    var pi = 3.14159265358979324;
    var a = 6378245.0;
    var ee = 0.00669342162296594323;
    var x_pi = 52.3598775598298873;
    
    var ret = 300.0 + lat + 2.0 * lon + 0.1 * lat * lat + 0.1 * lat * lon + 0.1 * Math.sqrt(Math.abs(lat));
    ret += (20.0 * Math.sin(6.0 * lat * pi) + 20.0 * Math.sin(2.0 * lat * pi)) * 2.0 / 3.0;
    ret += (20.0 * Math.sin(lat * pi) + 40.0 * Math.sin(lat / 3.0 * pi)) * 2.0 / 3.0;
    ret += (150.0 * Math.sin(lat / 12.0 * pi) + 300.0 * Math.sin(lat / 30.0 * pi)) * 2.0 / 3.0;
    return ret;
}