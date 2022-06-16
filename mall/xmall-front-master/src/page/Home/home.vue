<template>
  <div class="home">
  <div v-loading="loading" element-loading-text="1" style="min-height: 35vw;">
    <div class="banner" >
      <div class="bg" ref="bg"
        @mouseover="bgOver($refs.bg)" @mousemove="bgMove($refs.bg,$event)" @mouseout="bgOut($refs.bg)">
        <transition name="fade">
          <div v-for="(item, i) in banner" v-if="i===mark" :key="i" style="position:absolute" @click="linkTo(item)" @mouseover="stopTimer" @mouseout="startTimer">
            <img v-if="item.pic" class="img1" :src="item.pic"/>
            <img v-if="item.pic"  class="img2 a" :src="item.pic"/>
            <img v-if="item.pic"  class="img3 b" :src="item.pic"/>
          </div>
        </transition>
      </div>
      <div class="page">
        <ul class="dots">
          <li class="dot-active" v-for="(item, i) in banner" :class="{ 'dot':i!=mark }" :key="i" @click="change(i)"></li>
        </ul>
      </div>
    </div>

    <div>
      <div  class="activity-panel">
<!--        <ul class="box">-->
<!--          <li class="content"  v-for="(item,i) in home.hotProductList" :key="i"  @click="linkTo(item)">-->
<!--            <img class="i" :src="item.pic">-->
<!--            <a class="cover-link"></a>-->
<!--          </li>-->
<!--        </ul>-->
        <el-upload
        action="http://localhost:8085/product/delPic"
        list-type="picture-card"
        :on-success="handleAvatarSuccess"
        :on-preview="handlePictureCardPreview"
        :on-remove="handleRemove">
        <i class="el-icon-plus"></i>
      </el-upload>
        <el-dialog :visible.sync="dialogVisible">
          <img width="100%" :src="dialogImageUrl" alt="">
        </el-dialog>
        <div style="width: 16%;margin-top: 10px;">
          <el-alert
            title="⬆ 按这里上传喜欢的穿搭"
            type="success">
          </el-alert>
        </div>
      </div>
    </div>

    <div v-if="home.newProductList.length != 0">
      <section class="w mt30 clearfix">
        <y-shelf :title="'穿搭推荐'">
          <div slot="content" class="floors" >
            <mall-goods :msg="item" v-for="(item,j) in home.newProductList" :key="j"></mall-goods>
          </div>
        </y-shelf>
      </section>

    </div>

    <div>
<!--      <div  v-for="(iitem,j) in item" :key="j">-->
<!--        <section class="w mt30 clearfix">-->
<!--          <y-shelf :title="iitem.brandName">-->
<!--            <div slot="content">-->
<!--              <mall-goods :msg="iitem" ></mall-goods>-->
<!--            </div>-->
<!--          </y-shelf>-->
<!--        </section>-->
<!--      </div>-->

      <section class="w mt30 clearfix">
        <y-shelf :title="'热门推荐'">
          <div slot="content" class="floors" v-for="(item,i) in home" :key="i">
<!--            <div class="imgbanner"  @click="linkTo(item)">-->
<!--              <img v-lazy="item[0].pic">-->
<!--              <a class="cover-link"></a>-->
<!--            </div>-->
            <mall-goods :msg="iitem" v-for="(iitem,j) in item" :key="j"></mall-goods>
          </div>
        </y-shelf>
      </section>

      </div>
    </div>

    <div class="no-info" v-if="error">
      <div class="no-data">
        <img src="/static/images/error.png">
        <br> ??????...
      </div>
    </div>

<!--    <el-dialog-->
<!--      title="??"-->
<!--      :visible.sync="dialogVisible"-->
<!--      width="30%"-->
<!--      style="width:70%;margin:0 auto">-->
<!--      <span>??????XPay????????????????????????</span>-->
<!--      <span slot="footer" class="dialog-footer">-->
<!--        <el-button type="primary" @click="dialogVisible = false">????</el-button>-->
<!--      </span>-->
<!--    </el-dialog>-->
  </div>
</template>
<script>
  import { productHome } from '/api/index.js'
  import YShelf from '/components/shelf'
  import product from '/components/product'
  import mallGoods from '/components/mallGoods'
  import { setStore, getStore } from '/utils/storage.js'
  import 'element-ui/lib/theme-default/index.css'
  import axios from 'axios'

  export default {
    data () {
      return {
        dialogImageUrl: '',
        error: false,
        banner: [],
        mark: 0,
        bgOpt: {
          px: 0,
          py: 0,
          w: 0,
          h: 0
        },
        home: {
          hotProductList: [],
          newProductList: []
        },
        recommend: {
          ProductList: []
        },
        loading: true,
        notify: '1',
        dialogVisible: false,
        timer: ''
      }
    },
    methods: {
      handleAvatarSuccess (res, file) {
        let imgurl = res.data.url
        // 传往python后台获取图像推特以及图像box
        axios.defaults.headers.post['Content-Type'] = 'application/x-www=form-urlencoded'
        axios.get('http://127.0.0.1:5003/img/', {
          params: {
            'img': imgurl
          }
        }).then(res => {
          this.dialogImageUrl = res.data.result
          file.url = res.data.result
          console.log(this.dialogImageUrl)
          let imgPro = res.data.img_hash
          let map = {
            'hat': '',
            'clothes': '',
            'skirt': '',
            'pant': '',
            'glasses': '',
            'package': '',
            'shoe': ''
          }
          let index
          for (index in imgPro) {
            let value = imgPro[index]
            let key = index.split('-')[0]
            map[key] = value
          }
          axios.get('http://localhost:8085/product/img_pro', {
            params: {
              'hat': map['hat'],
              'clothes': map['clothes'],
              'skirt': map['skirt'],
              'pant': map['pant'],
              'glasses': map['glasses'],
              'package': map['package'],
              'shoe': map['shoe']
            },
            timeout: 60000
          }).then(res => {
            this.home.newProductList = res.data.data
            console.log(this.home.newProductList)
          })
        })
      },
      handleRemove (file, fileList) {
        console.log(file, fileList)
        alert(file.url)
      },
      handlePictureCardPreview (file) {
        this.dialogImageUrl = file.url
        this.dialogVisible = true
      },
      autoPlay () {
        this.mark++
        if (this.mark > this.banner.length - 1) {
          // ?????????????
          this.mark = 0
        }
      },
      play () {
        // ??2.5s??????
        this.timer = setInterval(this.autoPlay, 2500)
      },
      change (i) {
        this.mark = i
      },
      startTimer () {
        this.timer = setInterval(this.autoPlay, 2500)
      },
      stopTimer () {
        clearInterval(this.timer)
      },
      linkTo (item) {
        if (item.type === 0 || item.type === 2) {
          // ????
          this.$router.push({
            path: '/goodsDetails',
            query: {
              productId: item.productId
            }
          })
        } else {
          // ????
          window.location.href = item.fullUrl
        }
      },
      bgOver (e) {
        this.bgOpt.px = e.offsetLeft
        this.bgOpt.py = e.offsetTop
        this.bgOpt.w = e.offsetWidth
        this.bgOpt.h = e.offsetHeight
      },
      bgMove (dom, eve) {
        let bgOpt = this.bgOpt
        let X, Y
        let mouseX = eve.pageX - bgOpt.px
        let mouseY = eve.pageY - bgOpt.py
        if (mouseX > bgOpt.w / 2) {
          X = mouseX - (bgOpt.w / 2)
        } else {
          X = mouseX - (bgOpt.w / 2)
        }
        if (mouseY > bgOpt.h / 2) {
          Y = bgOpt.h / 2 - mouseY
        } else {
          Y = bgOpt.h / 2 - mouseY
        }
        dom.style['transform'] = `rotateY(${X / 50}deg) rotateX(${Y / 50}deg)`
        dom.style.transform = `rotateY(${X / 50}deg) rotateX(${Y / 50}deg)`
      },
      bgOut (dom) {
        dom.style['transform'] = 'rotateY(0deg) rotateX(0deg)'
        dom.style.transform = 'rotateY(0deg) rotateX(0deg)'
      },
      showNotify () {
        var value = getStore('notify')
        if (this.notify !== value) {
          this.dialogVisible = true
          setStore('notify', this.notify)
        }
      }
    },
    mounted () {
      productHome().then(res => {
        if (res.success === false) {
          this.error = true
          return
        }
        let data = res.data
        // this.home.homeFlashPromotion = data.homeFlashPromotion
        this.home.hotProductList = data.hotProductList
        // this.home.newProductList = data.newProductList
        // this.home.subjectList = data.subjectList
        // this.home.brandList = data.brandList
        this.loading = false
        this.banner = data.advertiseList
      })
      this.showNotify()
    },
    created () {
      this.play()
    },
    components: {
      YShelf,
      product,
      mallGoods
    }
  }
</script>
<style lang="scss" rel="stylesheet/scss" scoped>

  .avatar-uploader .el-upload {
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .avatar-uploader .el-upload:hover {
    border-color: #409EFF;
  }
  .avatar-uploader-icon {
    border: 1px dashed #d9d9d9;
    font-size: 28px;
    color: #8c939d;
    width: 178px;
    height: 178px;
    line-height: 178px;
    text-align: center;
  }
  .avatar {
    width: 178px;
    height: 178px;
    display: block;
  }


  .home {
    display: flex;
    flex-direction: column;
  }

  .no-info {
    padding: 100px 0;
    text-align: center;
    font-size: 30px;
    display: flex;
    flex-direction: column;
    .no-data{
      align-self: center;
    }
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .5s;
  }
  .fade-enter, .fade-leave-to {
    opacity: 0;
  }

  .page {
    position: absolute;
    width: 100%;
    top: 470px;
    z-index: 30;
    .dots {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      .dot-active {
        display: inline-block;
        width: 15px;
        height: 15px;
        background-color: whitesmoke;
        border-radius: 8px;
        margin-right: 10px;
        cursor: pointer;
      }
      .dot {
        opacity: 0.2;
      }
    }
  }

  .activity-panel {
    width: 1220px;
    margin: 0 auto;
    .box {
      overflow: hidden;
      position: relative;
      z-index: 0;
      margin-top: 25px;
      box-sizing: border-box;
      border: 1px solid rgba(0,0,0,.14);
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 3px 8px -6px rgba(0,0,0,.1);
    }
    .content {
      float: left;
      position: relative;
      box-sizing: border-box;
      width: 25%;
      height: 200px;
      text-align: center;
    }
    .content ::before{
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1;
      box-sizing: border-box;
      border-left: 1px solid #f2f2f2;
      border-left: 1px solid rgba(0,0,0,.1);
      width: 100%;
      height: 100%;
      content: "";
      pointer-events: none;
    }
    .i {
      width: 305px;
      height: 200px;
    }
    .cover-link {
      cursor: pointer;
      display: block;
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      z-index: 4;
      background: url(data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEHAAEALAAAAAABAAEAAAICTAEAOw==) repeat;
    }
    a {
      color: #5079d9;
      cursor: pointer;
      transition: all .15s ease-out;
      text-decoration: none;
    }
    a:hover {
      box-shadow: inset 0 0 38px rgba(0,0,0,.08);
      transition: all .15s ease;
    }
  }

  .banner, .banner span, .banner div {
    font-family: "Microsoft YaHei";
    transition: all .3s;
    transition-timing-function: linear;
  }

  .banner {
    cursor: pointer;
    perspective: 3000px;
    position: relative;
    z-index: 19;
    margin: 0 auto;
    width: 1220px;
  }

  .bg {
    position: relative;
    width: 1220px;
    height: 500px;
    margin: 20px auto;
    background-size: 100% 100%;
    border-radius: 10px;
    transform-style: preserve-3d;
    transform-origin: 50% 50%;
    transform: rotateY(0deg) rotateX(0deg);
    & div{
      position: relative;
      height: 100%;
      width: 100%;
    }
  }

  .img1 {
    display: block;
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    border-radius: 10px;
  }

  .img2 {
    display: block;
    position: absolute;
    width: 100%;
    height: 100%;
    bottom: 5px;
    left: 0;
    background-size: 95% 100%;
    border-radius: 10px;
  }

  .img3 {
    display: block;
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    border-radius: 10px;
  }

  .a {
    z-index: 20;
    transform: translateZ(40px);
  }

  .b {
    z-index: 20;
    transform: translateZ(30px);
  }

  .c {
    transform: translateZ(0px);
  }

  .sk_item {
    width: 170px;
    height: 225px;
    padding: 0 14px 0 15px;
    > div {
      width: 100%;
    }
    a {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      transition: all .3s;
      &:hover {
        transform: translateY(-5px);
      }
    }
    img {
      width: 130px;
      height: 130px;
      margin: 17px 0;
    }
    .sk_item_name {
      color: #999;
      display: block;
      max-width: 100%;
      _width: 100%;
      overflow: hidden;
      font-size: 12px;
      text-align: left;
      height: 32px;
      line-height: 16px;
      word-wrap: break-word;
      word-break: break-all;
    }
    .sk_item_price {
      padding: 3px 0;
      height: 25px;
    }
    .price_new {
      font-size: 18px;
      font-weight: 700;
      margin-right: 8px;
      color: #f10214;
    }
    .price_origin {
      color: #999;
      font-size: 12px;
    }
  }

  .box {
    overflow: hidden;
    position: relative;
    z-index: 0;
    margin-top: 29px;
    box-sizing: border-box;
    border: 1px solid rgba(0, 0, 0, .14);
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 3px 8px -6px rgba(0, 0, 0, .1);

  }

  ul.box {
    display: flex;
    li {
      flex: 1;
      img {
        display: block;
        width: 305px;
        height: 200px;
      }
    }
  }

  .mt30 {
    margin-top: 30px;
  }

  .hot {
    display: flex;
    > div {
      flex: 1;
      width: 25%;
    }
  }

  .floors {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    .imgbanner {
      width: 20%;
      height: 20%;
      .cover-link {
        cursor: pointer;
        display: block;
        position: absolute;
        top: 60px;
        left: 0;
        width: 50%;
        height: 430px;
        z-index: 4;
        background: url(data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEHAAEALAAAAAABAAEAAAICTAEAOw==) repeat;
      }
      .cover-link:hover {
        box-shadow: inset 0 0 38px rgba(0,0,0,.08);
        transition: all .15s ease;
      }
    }
    img {
      display: block;
      width: 100%;
      height: 100%;
    }
  }

</style>
