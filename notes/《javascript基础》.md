# 《javascript基础》

## 1常用变量：弱语言，无需声明变量类型

### 关键字：let，const（常量）；

## 2 输出语句：

1. alert();
2. console.log();
3. document.write();

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<script>
    let a=100;
    a="hello world";
    a=true;
    alert(a);
    console.log(a);

    const PI=3.14;
    document.write(PI);
    </script>
</body>
</html>
```

## 3数据类型

### number ，boolean，string，null，undifined

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>

<script>
    alert(typeof "你好");
    alert(typeof 100);
    alert(typeof null);
    alert(typeof true);

    //模板字符串
    let name="qian";
    console.log(`i am ${name}`);
    </script>
</body>
</html>
```

## 4模板字符串

## ``

(` xxx xxx xxxx ${} xx`)

## 5函数

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<script>
    //函数
    function add(a, b) {
        return a + b;
    }
    let res=add(100,200);
    console.log(res);

    //匿名函数
    let add1 =function(a,b){
        return a + b;
    }
    let res2=add1(200,300);
    console.log(res2);

    let add3 =(a,b)=>{
        return a + b;
    }
    let res3=add3(200,600);
    console.log(res3);
    </script>
</body>
</html>
```

#### js是弱语言，函数、形参无需定义类型；

## 6自定义对象

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<script>
    user={
        name:"qyt",
        age:20,
        gender:"male",
        sing:function(){
            alert(this.name+"在唱歌");},
        dance:()=>{//使用箭头函数时，无法使用this.name
            alert(this.name+"在跳舞");
        }
    }
    user.sing();
    console.log(user.name);
    user.dance();
    </script>
</body>
</html>
```

